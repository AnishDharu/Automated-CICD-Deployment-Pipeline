FROM python:3.12-slim

# Prevents Python from writing .pyc files and enables real-time logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first (layer caching — rebuild only when requirements change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Create a non-root user (security best practice, Trivy will flag root)
RUN adduser --disabled-password --no-create-home appuser
USER appuser

EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
