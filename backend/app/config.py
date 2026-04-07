import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "airaware-dev-key")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@db:5432/airaware",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AQI_API_URL = os.getenv("AQI_API_URL", "https://api.waqi.info/feed/geo:{lat};{lon}/")
    AQI_API_TOKEN = os.getenv("AQI_API_TOKEN", "")
    MAPPLS_API_KEY = os.getenv("MAPPLS_API_KEY", "")
    MAPPLS_ROUTE_URL_TEMPLATE = os.getenv(
        "MAPPLS_ROUTE_URL_TEMPLATE",
        "https://apis.mappls.com/advancedmaps/v1/{api_key}/route_adv/driving/{origin};{destination}",
    )
