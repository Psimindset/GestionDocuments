FROM python:3.10

LABEL maintainer="admin@Gestiondocuments.com"

RUN mkdir -p /app/uploads /app/outputs /app/templates

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5800

CMD ["python", "mod_srv.py"]