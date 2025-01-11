from sanic_ext import openapi


class Image:
    image = openapi.Binary(
        description="Une image",
    )
