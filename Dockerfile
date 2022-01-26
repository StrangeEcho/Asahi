FROM python:3.10-slim as base

ENV PYTHONUNBUFFERED=1


FROM base as builder


RUN apt-get update \
    && apt-get install -y git gcc \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

COPY . /app/

COPY requirements.txt /requirements.txt

RUN pip install --no-cache-dir --target=/dependencies -r /requirements.txt


FROM base as final

# Copy Dependencies from builder stage
COPY --from=builder /dependencies /usr/local

ENV PYTHONPATH=/usr/local

# Copy application files to container
COPY . /app/

WORKDIR /app/

ENTRYPOINT [ "python3", "/app/src/__main__.py" ]
