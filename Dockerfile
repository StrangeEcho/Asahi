FROM python:3.9-slim as base

ENV PYTHONUNBUFFERED=1


FROM base as builder


RUN apt-get update \
    && apt-get install -y git \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

COPY . /app/

COPY requirements.txt /requirements.txt

RUN pip install --target=/dependencies -r /requirements.txt


FROM base as final

# Copy Dependencies from builder stage
COPY --from=builder /dependencies /usr/local

ENV PYTHONPATH=/usr/local

# Copy application files to container
COPY . /app/

WORKDIR /app/

# The file must exist to be overriden
RUN touch /app/config.toml

ENTRYPOINT [ "python3", "/app/src/__main__.py" ]