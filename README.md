# Conversational Assistant for Citizen Assemblies

⚠️ DEV repo derived from [chatbot_assistant_for_citizen](https://github.com/briandaya/chatbot_assistant_for_citizen_assemblies), functional prototype of my final degree project (TFG)

Brianda Yáñez-Arrondo 2024

[![en](https://img.shields.io/badge/lang-en-blue.svg)](https://github.com/briandaya/dev_chatbot_assistant_for_citizen_assemblies/blob/main/README.md)
[![es](https://img.shields.io/badge/lang-es-red.svg)](https://github.com/briandaya/dev_chatbot_assistant_for_citizen_assemblies/blob/main/README.es.md)

## Project Description

This project is a prototype of a conversational assistant designed to support participation in Citizen Assemblies by facilitating access to specialized information and encouraging the contrast of perspectives. It utilizes large language models (LLMs) and open-source technologies such as Docker, Weaviate, LlamaIndex, and Streamlit. Below are links with more information.

⚠️ Warning
This project is under development and may contain errors or unexpected behavior. If you encounter any issues or have suggestions for improvement, please do not hesitate to contact me. I am open to collaborations and discussions on potential improvements.

![image](https://github.com/user-attachments/assets/04cd321e-2e68-4adc-968c-4f42001d9138)

## Installation

### Prerequisites

- Docker and Docker Compose must be installed.

### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/briandaya/dev_chatbot_assistant_for_citizen_assemblies.git
   cd dev_chatbot_assistant_for_citizen_assemblies
   ```

2. Copy and modify the environment configuration file:
   ```bash
   cp services/config.env.example services/config.env
   ```

3. Build and start the Docker containers:
   ```bash
   docker-compose -f docker-compose-watch.yml up --build
   ```

## Project Usage

Access the user interface at `http://localhost:8511` to interact with the conversational assistant. The orchestrator exposes an API for integration with other platforms.

## Main Technologies Used

- **Docker** for container management.
- **Weaviate** as a vector database.
- **LlamaIndex** for LLM integration.
- **Streamlit** for the user interface.

## Project Challenges and Future

Future development will focus on improving the assistant's reliability and responsiveness, as well as expanding its applicability to other use cases. More details on the challenges and next phases are available in the links below 👇.

## Collaborations

This project was developed in collaboration with [Deliberativa](https://deliberativa.org/) and will continue to be developed by Simbiótica, a cooperative focused on ethical and responsible technological solutions. I am a co-founder of Simbiótica, which will launch in the fall of 2024.

## Relevant Links

- [Project Report (Memoria)](https://drive.google.com/file/d/15chRPKXqdmKBtf4jqpUAn-FyHuK9HTDL/view?usp=drive_link)
- [Prototype Presentation Video](https://youtu.be/m-UZKEovhro)
- [Medium Article](https://medium.com/@briandaya/desarrollo-de-agentes-conversacionales-confiables-para-asambleas-ciudadanas-innovando-para-la-6b86dd0fc424)
- [LinkedIn Profile](https://www.linkedin.com/in/briandayanez/)

