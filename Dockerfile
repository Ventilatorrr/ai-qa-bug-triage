# Python 3.14.2 matches the environment the pinned requirements are tested with.
FROM python:3.14.2-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# The application serves ./frontend relative to this directory.
WORKDIR /app

COPY requirements.txt requirements-ai.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-ai.txt

COPY app ./app
COPY frontend ./frontend

RUN useradd --create-home --uid 10001 appuser
USER appuser

EXPOSE 8000

# DATABASE_NAME (an absolute path on the persistent disk) and JWT_SECRET_KEY are supplied
# at runtime. One worker keeps the in-process Demo limiter and SQLite writes consistent.
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
