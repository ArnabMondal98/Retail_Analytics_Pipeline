# Use official Python runtime
FROM python:3.11-slim
# Set working directory
WORKDIR /app
# Copy python requirements
COPY requirements.txt .
# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
# Copy all backend code
COPY . .
# Expose port for FastAPI
EXPOSE 8000
# Start FastAPI server
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
