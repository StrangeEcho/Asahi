# Running with Docker

## Building the image

1. Clone the repository
2. run `docker build -t kurisu:latest .`

## Running with Docker

You can run Kurisu in docker with either docker compose or using the Docker CLI. It's recommended to use docker-compose in production.

### Docker CLI

```
    docker run \
    --name kurisu \
    -v kurisu-data:/app/src/data \
    -v "/path/to/config.tom:/app/src/data/config.toml:ro" \
    kurisu:latest
```

Or, for long term use:

```
    docker run -d 
    --name kurisu \
    --restart unless-stopped \
    -v kurisu-data:/app/src/data \
    -v "/path/to/config.tom:/app/src/data/config.toml:ro" \
    kurisu:latest
```

To update, build the new image, shut down the previous container, run `docker rm kurisu` to remove it, and run the command again.

### Docker Compose

A basic docker compose configuration is provided in the git repository and can be run with `docker-compose up`

If you plan to run the bot long term in production, you should use the following config file and `docker-compose up -d` to run in detached mode.

```yaml
version: '3.7'

services:
  kurisu:
    image: kurisu:latest
    restart: unless-stopped
    volumes:
    # Your database will be saved in a docker volume named 'kurisu-data'
     - kurisu-data:/app/src/data
     # Change to the location of your config if it's located elsewhere
     - ./config.toml:/app/src/data/config.toml:ro

volumes:
  kurisu-data: {}
```

To update, build the new image and run `docker-compose up` again.
