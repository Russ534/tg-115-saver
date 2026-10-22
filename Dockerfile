FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

ENV SAVER_CONFIG=/data/config.json
VOLUME ["/data"]
CMD ["python", "-m", "src.main"]
