from config import *
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.weaviate import WeaviateVectorStore
from llama_index.embeddings.text_embeddings_inference import TextEmbeddingsInference
from llama_index.core import VectorStoreIndex, Settings, ChatPromptTemplate
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.agent import ReActAgent
from llama_index.tools.duckduckgo import DuckDuckGoSearchToolSpec

import weaviate
import os
import logging
import yaml

logging.basicConfig(level=logging.INFO)


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
        templates = yaml.load(file)
    return templates

# Get the templates from the YAML file
custom_templates = load_custom('ES_01')

# Lista de sitios donde deseas realizar la búsqueda
sites = custom_templates['SITES']

# Function to initialize the query engine
def initialize_query_engine(weaviate_client, index_name, text_key="content"):
    vector_store = WeaviateVectorStore(weaviate_client=weaviate_client, 
                                       index_name=index_name,
                                       text_key=text_key)
    index = VectorStoreIndex.from_vector_store(vector_store)

    # Custom Text QA Prompt
    qa_prompt_str = custom_templates['QA_PROMPT_STR']
    
    basic_content = custom_templates['BASIC_CONTENT']
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
            content=basic_content,
        ),
        ChatMessage(role=MessageRole.USER, content=refine_prompt_str),
    ]
    refine_template = ChatPromptTemplate(chat_refine_msgs)

    return index.as_query_engine(text_qa_template=text_qa_template,
                                 refine_template=refine_template,
                                 similarity_top_k=5)

# Query construction with OR blocks
def build_duckduckgo_query(query, sites):
    blocks = [f"({query} site:{site})" for site in sites]
    duckduckgo_query = " OR ".join(blocks)
    return duckduckgo_query

# Main function to get the result for a given question
def get_result_for_question(question):
    # Initialize models and settings
    embed_model = setup_embedding_model()
    llm_model = setup_llm_model()
    configure_settings(llm_model, embed_model)

    # Connect to Weaviate
    WEAVIATE_URL = os.getenv('WEAVIATE_URL', 'http://weaviate:8090/')
    logging.info(f"Iniciando la conexión a weaviate: {WEAVIATE_URL}")
    weaviate_client = weaviate.connect_to_local(host=WEAVIATE_HOST, port=WEAVIATE_PORT)
    logging.info(f"Conectado a weaviate")

    # Initialize query engine
    query_engine = initialize_query_engine(weaviate_client, INDEX_NAME)

    # Query the engine
    result = query_engine.query(question)
    result_md = result.response
    logging.info(f"result.response: {result_md}")
    
    # Check if the response from Weaviate is sufficient
    if not result_md or "no tengo información para esa pregunta" in result_md:
        logging.info("No se encontraron resultados suficientes en Weaviate, utilizando DuckDuckGo...")
        duckduckgo_tools = DuckDuckGoSearchToolSpec().to_tool_list()
        agent = ReActAgent(duckduckgo_tools, llm=llm_model, memory=None)

        # Construction of the DuckDuckGo query
        duckduckgo_query = build_duckduckgo_query(question, sites)
        logging.info(f"duckduckgo_query: {duckduckgo_query}")

        # Query the agent
        agent_response = agent.chat(duckduckgo_query)

        # Extract the sources from the agent's response
        sources = "Fuentes: \n"
        for tool_output in agent_response.sources:
            if tool_output.tool_name == "duckduckgo_full_search":
                for item in tool_output.raw_output:
                    sources += f"- [{item['title']}]({item['href']})\n"
        result_md = agent_response.response + "\n" + sources
    else:            
        sources = "Fuentes: \n"
        unique_file_names = set(info['file_name'] for info in result.metadata.values())
        for name in unique_file_names:
            sources += f"- {name}\n"
        
        logging.info(f"sources: {sources}")
        result_md = result_md + sources


    # Close Weaviate client
    weaviate_client.close()
    
    return result

