# Dockerfile
# Use uma imagem base oficial do Python.
FROM python:3.9-slim

# Defina o diretório de trabalho no contêiner.
WORKDIR /app

# Copie o arquivo de dependências primeiro para aproveitar o cache do Docker.
COPY requirements.txt ./

# Instale as dependências.
RUN pip install --no-cache-dir -r requirements.txt

# Copie o resto do código do aplicativo.
COPY . .

# Exponha a porta que o Streamlit usa.
EXPOSE 8501

# O comando para executar o aplicativo.
CMD ["streamlit", "run", "app.py"]
