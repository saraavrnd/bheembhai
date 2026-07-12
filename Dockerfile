FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN pip install --no-cache-dir uv==0.11.19

COPY . /app

RUN uv sync --frozen --group dev

EXPOSE 8000

CMD ["uv", "run", "beembhai-api"]
