FROM python:3.11-slim

WORKDIR /app

# Copy backend folder into container
COPY backend /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set Python path
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
