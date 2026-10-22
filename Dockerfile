FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

COPY . ./CROUStillantAPI

WORKDIR /CROUStillantAPI

RUN git submodule update --init --recursive

RUN git submodule foreach git pull origin main

RUN uv sync --frozen

EXPOSE 7000

CMD ["uv", "run", "__main__.py"]
