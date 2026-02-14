import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Flask
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://zeule:zeule_dev@localhost:5432/zeule")
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis / Celery
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL

    # AI / LLM
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")

    # Research
    SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY", "")
    REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
    REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
    REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "zeule/1.0")

    # Design
    IDEOGRAM_API_KEY = os.getenv("IDEOGRAM_API_KEY", "")
    BANNERBEAR_API_KEY = os.getenv("BANNERBEAR_API_KEY", "")
    GAMMA_API_KEY = os.getenv("GAMMA_API_KEY", "")

    # Platforms
    GHL_API_KEY = os.getenv("GHL_API_KEY", "")
    GHL_LOCATION_ID = os.getenv("GHL_LOCATION_ID", "")
    META_ADS_ACCESS_TOKEN = os.getenv("META_ADS_ACCESS_TOKEN", "")
    META_ADS_ACCOUNT_ID = os.getenv("META_ADS_ACCOUNT_ID", "")
    META_AD_LIBRARY_ACCESS_TOKEN = os.getenv("META_AD_LIBRARY_ACCESS_TOKEN", "")
    HOTMART_CLIENT_ID = os.getenv("HOTMART_CLIENT_ID", "")
    HOTMART_CLIENT_SECRET = os.getenv("HOTMART_CLIENT_SECRET", "")
    SPARKTORO_API_KEY = os.getenv("SPARKTORO_API_KEY", "")
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

    # Assets
    ASSETS_DIR = os.getenv("ASSETS_DIR", "./assets")

    # Pipeline defaults
    DEFAULT_PRODUCTS_PER_DAY = 15
    MAX_RETRIES = 3
    RETRY_DELAY_SECONDS = 5


settings = Settings()
