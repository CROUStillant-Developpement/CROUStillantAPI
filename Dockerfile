FROM sanicframework/sanic:lts-py3.11

RUN apk add --no-cache git

COPY . ./CROUStillantAPI

WORKDIR /CROUStillantAPI

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 7000

CMD ["python", "__main__.py"]
