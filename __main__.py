from CROUStillantAPI.app import app
from dotenv import load_dotenv
from os import environ


load_dotenv(dotenv_path=f".env")


if __name__ == '__main__':
    app.run(host=environ.get('API_HOST', '0.0.0.0'), port=int(environ.get('API_PORT', 5000)), debug=environ.get("API_DEBUG", False))
