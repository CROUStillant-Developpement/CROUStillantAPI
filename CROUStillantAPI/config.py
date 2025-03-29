from sanic.config import Config


class AppConfig(Config):
    API_VERSION = "1.1.0"
    API_TERMS_OF_SERVICE = "https://api.croustillant.bayfield.dev/terms"
    API_CONTACT_EMAIL = "croustillant@bayfield.dev"

    OAS = True
    OAS_UI_DEFAULT = "scalar"
    OAS_UI_SCALAR = True
    OAS_PATH_TO_SCALAR_HTML = "scalar.html"
    OAS_UI_REDOC = False
    OAS_UI_SWAGGER = False
    OAS_URI_TO_JSON = "/openapi.json"
    OAS_URL_PREFIX = "/"

    CORS_ORIGINS = "*"
    CORS_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]

    FALLBACK_ERROR_FORMAT = "json"
