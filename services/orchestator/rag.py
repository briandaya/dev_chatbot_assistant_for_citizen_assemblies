#from config import *
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.weaviate import WeaviateVectorStore
from llama_index.embeddings.text_embeddings_inference import TextEmbeddingsInference
from llama_index.core import VectorStoreIndex, Settings, ChatPromptTemplate
from llama_index.core.llms import ChatMessage, MessageRole
from duckduckgo_search import DDGS
from llama_index.readers.web import SimpleWebPageReader, BeautifulSoupWebReader
from llama_index.core.node_parser import HTMLNodeParser, SimpleNodeParser
from llama_index.core import StorageContext

from fastapi import HTTPException
import weaviate
import os
import logging
import yaml

# Set up logging
logging.basicConfig(level=logging.INFO)

#---------------------------------------------
# Load environment variables from config.env file, from the docker compose configuration

EMBED_MODEL_NAME = os.getenv('EMBED_MODEL_NAME')
EMBED_BASE_URL = os.getenv('EMBED_BASE_URL')
EMBED_TIMEOUT = int(os.getenv('EMBED_TIMEOUT'))
EMBED_BATCH_SIZE = int(os.getenv('EMBED_BATCH_SIZE'))
LLM_MODEL_NAME = os.getenv('LLM_MODEL_NAME')
LLM_KEEP_ALIVE = int(os.getenv('LLM_KEEP_ALIVE'))
LLM_REQUEST_TIMEOUT = int(os.getenv('LLM_REQUEST_TIMEOUT'))
LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE'))
LLM_BASE_URL = os.getenv('LLM_BASE_URL')

WEAVIATE_HOST = os.getenv('WEAVIATE_HOST')
WEAVIATE_PORT = os.getenv('WEAVIATE_PORT')
WEAVIATE_GRPC_PORT = os.getenv('WEAVIATE_GRPC_PORT')
WEAVIATE_URL = os.getenv('WEAVIATE_URL')

INDEX_NAME = os.getenv('INDEX_NAME')
INDEX_NAME_TEMP = os.getenv('INDEX_NAME_TEMP')

CHUNK_SIZE = int(os.getenv('CHUNK_SIZE'))
CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP'))
#---------------------------------------------
#
# ---- Functions to set up the models --------
# 
# Function to set up the embeddings model
def setup_embedding_model():
    return TextEmbeddingsInference(
        model_name=EMBED_MODEL_NAME,
        base_url=EMBED_BASE_URL,
        timeout=EMBED_TIMEOUT, 
        embed_batch_size=EMBED_BATCH_SIZE
    )

# Function to set up the LLM model
def setup_llm_model():
    return Ollama(
        model=LLM_MODEL_NAME, 
        keep_alive=LLM_KEEP_ALIVE, 
        request_timeout=LLM_REQUEST_TIMEOUT, 
        temperature=LLM_TEMPERATURE, 
        base_url=LLM_BASE_URL
    )

# Function to configure settings for LLM and embedding model
def configure_settings(llm_model, embed_model):
    Settings.llm = llm_model
    Settings.embed_model = embed_model

def load_custom(code):
    file_path = f'custom_{code}.yml'
    with open(file_path, 'r', encoding='utf-8') as file:
        templates = yaml.safe_load(file)
    return templates

# ---------------------------------------------


# Get the templates from the YAML file
custom_templates = load_custom('ES_01')
# List of sites to search
sites = custom_templates['SITES']

# Function to connect to Weaviate
def connect_to_weaviate():
    print(f"Conectando a Weaviate en {WEAVIATE_URL}")
    # It's necessary to indicate the grpc data especially if in docker compose it's redirected from a different port
    return weaviate.connect_to_custom(
                http_host=WEAVIATE_HOST,
                http_port=WEAVIATE_PORT,
                http_secure=False,
                grpc_host= WEAVIATE_HOST,
                grpc_port=WEAVIATE_GRPC_PORT,
                grpc_secure=False,
            )

# Function to initialize the query engine for Chat+RAG from Weaviate documents
def initialize_query_engine(weaviate_client, index_name, text_key="text"):
    vector_store = WeaviateVectorStore(weaviate_client=weaviate_client, 
                                       index_name=index_name,
                                       text_key=text_key)
    index = VectorStoreIndex.from_vector_store(vector_store)

    # Custom Text QA Prompt
    if index_name == INDEX_NAME:
        basic_content = custom_templates['BASIC_CONTENT_DOCS']
    else:
        basic_content = custom_templates['BASIC_CONTENT_WEB']   
    #basic_content = custom_templates['BASIC_CONTENT_DOCS'] if index_name == INDEX_NAME else custom_templates['BASIC_CONTENT_WEB']
    
    qa_prompt_str = custom_templates['QA_PROMPT_STR']

    chat_text_qa_msgs = [
        ChatMessage(
            role=MessageRole.SYSTEM,
            content=basic_content,
        ),
        ChatMessage(role=MessageRole.USER, content=qa_prompt_str),
    ]
    text_qa_template = ChatPromptTemplate(chat_text_qa_msgs)

    # Custom Refine Prompt
    refine_prompt_str = custom_templates['REFINE_PROMPT_STR']
    
    chat_refine_msgs = [
        ChatMessage(
            role=MessageRole.SYSTEM,
            content=refine_prompt_str,
        ),
        ChatMessage(role=MessageRole.USER, content=refine_prompt_str),
    ]
    refine_template = ChatPromptTemplate(chat_refine_msgs)

    # With chat_mode='context', for each chat interaction:
    # - first retrieve text from the index using the user message
    # - set the retrieved text as context in the system prompt
    # - return an answer to the user message
    return index.as_query_engine(#chat_mode="context",
                                 text_qa_template=text_qa_template,
                                 #refine_template=refine_template,
                                 similarity_top_k=5
                                 ) 

# ---------------------------------------------

# Get the keywords from the LLM model for a given query, to use in a web search
def get_keywords_from_llm(query, llm_model):
    messages = [
        ChatMessage(role="system", content="""
                    You are designed to extract the relevant terms to perform a web search from the user query. 
                    Total terms must not exceed 5 words
                    You must respond only with the search terms separated by spaces,
                    in the same language as the user query.
                    """),
        ChatMessage(role="user", content='¿Qué son las estelas que dejan los aviones en el cielo?'),
        ChatMessage(role="assistant", content="estelas aviones cielo"),
        ChatMessage(role="user", content='¿Qué son las macrogranjas?'),
        ChatMessage(role="assistant", content="macrogranjas"),
    ]
    messages.append(ChatMessage(role="user", content=query))
    keywords = llm_model.chat(messages).message.content
    return keywords

# Search function with DuckDuckGo, using the query constructed with the OR blocks
def search_with_site_filter(keywords, sites, max_results=20):
    site_query = " OR ".join([f"({keywords} site:{site})" for site in sites])
    params = {
        "keywords": site_query,
        "region": '',
        "max_results": max_results,
    }
    with DDGS() as ddg:
        results = list(ddg.text(**params))
    return results

# Function to load documents from URLs
def load_documents_from_urls(urls,html_to_text):
    unique_urls = list(set(urls))  # Remove duplicate URLs
    if html_to_text:
        # Use BeautifulSoupWebReader to load data
        loader = BeautifulSoupWebReader()
        documents = loader.load_data(urls=unique_urls)
    else:
        # Not in use, but just in case
        documents = SimpleWebPageReader(html_to_text=html_to_text).load_data(unique_urls)
    return documents

# Function to set up vector store and storage context
def setup_vector_store_and_context(weaviate_client, index_name, embed_model):
    if weaviate_client.collections.exists(index_name):
        print(f"Eliminando la colección existente: {index_name}")
        weaviate_client.collections.delete(index_name)
    print(f"Configurando y construyendo el índice: {index_name}")
    vector_store = WeaviateVectorStore(weaviate_client=weaviate_client, 
                                       index_name=index_name, 
                                       embed_model=embed_model,
                                       text_key="text")
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return storage_context

# Function to get keywords from LLM and search in internet
def web_search(question, llm_model, html_to_text=True):
    # Get keywords from LLM
    logging.info(f"Getting keywords from LLM...")
    keywords = get_keywords_from_llm(question, llm_model)
    # Get the URLs and titles from the search results
    logging.info(f"Searching in internet...")
    results = search_with_site_filter(keywords, sites)
    # Get the URLs and titles from the search results
    url_title_dict = {result['href']: result['title'] for result in results}    # Load the documents from the URLs
    urls = [result['href'] for result in results]
    documents = load_documents_from_urls(urls, html_to_text)
    logging.info(f"Results: {len(documents)}")
    return documents, url_title_dict

# Function to parse and index the documents in Weaviate
def parse_and_index_documents(documents, weaviate_client, embed_model):
    # Parse the documents
    logging.info(f"Parsing documents...")       
    parser_text = SimpleNodeParser.from_defaults(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    nodes_text = parser_text.get_nodes_from_documents(documents)
    logging.info(f"Parsing process completed. /nDocuments processed: {len(documents)}. /nNodes generated: {len(nodes_text)}.")       
    # WEAVIATE - Set up vector store and storage context
    storage_context = setup_vector_store_and_context(weaviate_client, INDEX_NAME_TEMP, embed_model)
    # Build the index with parsed nodes
    index = VectorStoreIndex(nodes_text, storage_context=storage_context, show_progress=True)
    logging.info(f"Index {INDEX_NAME_TEMP} built.")

# ---------------------------------------------

# Main function to get the result for a given question
def get_result_for_question(question):
    # Initialize models and settings
    embed_model = setup_embedding_model()
    llm_model = setup_llm_model()
    configure_settings(llm_model, embed_model)

    # Connect to Weaviate
    logging.info(f"Iniciando la conexión a weaviate: {WEAVIATE_URL}")
    weaviate_client = connect_to_weaviate()
    logging.info(f"Conectado a weaviate")

    # Initialize query engine
    query_engine = initialize_query_engine(weaviate_client, INDEX_NAME)

    # Query the engine
    result = query_engine.query(question)
    
    logging.info(f"De WEAVIATE FULL result: {result}")
    logging.info(f"De WEAVIATE FULL result: {result.metadata.values()}")
    logging.info(f"De WEAVIATE FULL nodes: {result.source_nodes}")

    result_md = result.response
    sources = ""
    # Check if the response from Weaviate is sufficient
    if "realice una pregunta adecuada" in result_md:
        # Inappropriate question
        logging.info("Se ha considerado que la pregunta no es adecuada o malicioasa.")
        result_md = "Por favor, realice una pregunta adecuada."
    elif not result_md or "no tengo información para esa pregunta" in result_md:
        # No relevant information found in Weaviate, search in internet
        logging.info("No relevant information found in Weaviate. Searching in internet...")
        # Search in internet
        web_documents, url_title_dict = web_search(question, llm_model)
        # Parse and index the documents in Weaviate
        parse_and_index_documents(web_documents, weaviate_client, INDEX_NAME_TEMP)

        # Initialize query engine for temporary index (to store the results from web search)
        query_engine = initialize_query_engine(weaviate_client, INDEX_NAME_TEMP)
        # Query the engine (WEAVIATE)
        result = query_engine.query(question)
        result_md = result.response
        logging.info(f"result.response: {result_md}")

        sources = ""
        if "realice una pregunta adecuada" in result_md:
            logging.info("Se ha considerado que la pregunta no es adecuada o malicioasa.")
            result_md = "Por favor, realice una pregunta adecuada."
        elif not result_md or "no tengo información para esa pregunta" in result_md:
            logging.info("No hay suficiente información en los Documentos ni en los sitios de búsqueda")
            result_md = "No se pudo obtener una respuesta a partir de la información disponible."
        else:
            sources = " \n> Respuesta elaborada a partir de información extraída de los siguientes sitios determinados por la organización: \n"
            unique_urls = set(info['URL'] for info in result.metadata.values())
            for url in unique_urls:
                title = url_title_dict.get(url, "")
                sources += f">- [{title}]({url})\n"
            logging.info(f"sources: {sources}")
            result_md = result_md + sources            
    else:
        # Response from Weaviate is sufficient
        sources = " \n> Respuesta elaborada a partir de información extraída de los siguientes documentos facilitados por la organización: \n"
        dict_files = custom_templates['DICT_FILES']
        
        unique_file_names = set(info['file_name'] for info in result.metadata.values())
        for name in unique_file_names:
            title = dict_files.get(name, "").get('title')
            url = dict_files.get(name, "").get('url')
            sources += f">- [{title}]({url})\n"

        logging.info(f"sources: {sources}")
        result_md = result_md + sources

    result_md = result_md + \
    "> \n> Puede consultar información del proceso y las temáticas en la página web de la organización.\
    [\[ES\]](https://participa.gencat.cat/processes/assembleaclima?locale=es) | \
    [\[CAT\]](https://participa.gencat.cat/processes/assembleaclima)"

    # Close Weaviate client
    weaviate_client.close()
    
    return result_md

