# Asistente Conversacional para Asambleas Ciudadanas

⚠️ DEV repo derivado de [chatbot_assistant_for_citizen](https://github.com/briandaya/chatbot_assistant_for_citizen_assemblies), prototipo funcional de mi TFG

Brianda Yáñez-Arrondo 2024

[![en](https://img.shields.io/badge/lang-en-blue.svg)](https://github.com/briandaya/dev_chatbot_assistant_for_citizen_assemblies/blob/main/README.md)
[![es](https://img.shields.io/badge/lang-es-red.svg)](https://github.com/briandaya/dev_chatbot_assistant_for_citizen_assemblies/blob/main/README.es.md)


## Descripción del Proyecto

Este proyecto es un prototipo de asistente conversacional diseñado para apoyar la participación en Asambleas Ciudadanas, facilitando el acceso a información especializada y fomentando el contraste de perspectivas. Utiliza modelos de lenguaje de gran tamaño (LLMs) y tecnologías open source como Docker, Weaviate, LlamaIndex y Streamlit. Abajo hay enlaces con más información.

⚠️ Advertencia
Este proyecto está en desarrollo y puede contener errores o comportamientos inesperados. Si encuentras algún problema o tienes sugerencias para mejorar, no dudes en ponerte en contacto conmigo. Estoy abierta a colaboraciones y discusiones sobre posibles mejoras.


![image](https://github.com/user-attachments/assets/04cd321e-2e68-4adc-968c-4f42001d9138)


## Instalación

### Requisitos Previos

- Docker y Docker Compose deben estar instalados.

### Pasos de Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/briandaya/dev_chatbot_assistant_for_citizen_assemblies.git
   cd dev_chatbot_assistant_for_citizen_assemblies
   ```

2. Copia y modifica el archivo de configuración de entorno:
   ```bash
   cp services/config.env.example services/config.env
   ```

3. Construye y levanta los contenedores Docker:
   ```bash
   docker-compose -f docker-compose-watch.yml up --build
   ```

## Uso del Proyecto

Accede a la interfaz de usuario en `http://localhost:8511` para interactuar con el asistente conversacional. El orquestador expone una API para la integración con otras plataformas.

## Principales tecnologías Utilizadas

- **Docker** para la gestión de contenedores.
- **Weaviate** como base de datos vectorial.
- **LlamaIndex** para la integración con LLMs.
- **Streamlit** para la interfaz de usuario.

## Desafíos y Futuro del Proyecto

El desarrollo futuro se centrará en mejorar la confiabilidad y la capacidad de respuesta del asistente, así como en su expansión a otros casos de uso. Más detalles sobre los desafíos y próximas fases están disponibles en los enlaces 👇.

## Colaboraciones

Este proyecto se desarrolló en colaboración con [Deliberativa](https://deliberativa.org/) y tendrá continuidad desarrollado desde Simbiótica, una cooperativa enfocada en soluciones tecnológicas éticas y responsables, de la que soy cofundadora y que echará a andar en otoño de 2024.

## Enlaces de Interés

- [Memoria del proyecto](https://drive.google.com/file/d/15chRPKXqdmKBtf4jqpUAn-FyHuK9HTDL/view?usp=drive_link)
- [Video de presentación del prototipo](https://youtu.be/m-UZKEovhro)
- [Artículo en Medium](https://medium.com/@briandaya/desarrollo-de-agentes-conversacionales-confiables-para-asambleas-ciudadanas-innovando-para-la-6b86dd0fc424)
- [Perfil de LinkedIn](https://www.linkedin.com/in/briandayanez/)



