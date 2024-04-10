# Usar una imagen base con Python 3.11
FROM python:3.11

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos de tu proyecto al contenedor
COPY . /app

# Instalar las dependencias
RUN pip install -r dependencies.txt

# Exponer el puerto si es necesario
EXPOSE 8000

# Comando para ejecutar tu aplicación
CMD ["uvicorn", "server.__main__:app", "--host", "0.0.0.0", "--port", "8000"]
