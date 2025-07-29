FROM python:3.11-slim

WORKDIR /app

# Create directory for models
RUN mkdir -p models/trained

# Copy model files
COPY models/trained/*.pkl models/trained/

# Copy API requirements and install dependencies
COPY src/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy API code
COPY src/api/ .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]