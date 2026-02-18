# 1. Base image
FROM python:3.9-slim

# 2. Set working directory
WORKDIR /app

# 3. Copy files
COPY . .

# 4. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Expose the port Cloud Run expects (8080)
EXPOSE 8080

# 6. Run the application
# We explicitly set the server address to 0.0.0.0 (required for external access)
# and the port to 8080 (required by Cloud Run)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "8", "--timeout", "0", "app:create_app()"]