# 1. Base image: Python
FROM python:3.11.5

# 2. Environment settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TF_CPP_MIN_LOG_LEVEL=2

# 3. Working directory inside container
WORKDIR /app

# 4. Install Python dependencies
COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


# 5. Copy Flask app and model
COPY flask_app/ flask_app/

# 6. Expose Flask port
EXPOSE 5000

# 7. Run the app
CMD ["python", "-m", "flask_app.app"]
