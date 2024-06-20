# Usa la imagen base de Python
FROM python:3.9-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo requirements.txt al contenedor
#COPY requirements.txt .
COPY . .

# Instala las dependencias del proyecto
RUN pip install --no-cache-dir -r requirements.txt



# Expone el puerto 8010 para acceder a la aplicación externamente
EXPOSE 8010

# Ejecuta el comando para iniciar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]