from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class BaseConfig(BaseSettings):
    DB_URL: Optional[str] = "mongodb://localhost:27017"
    DB_NAME: Optional[str] = "lrmis_db"
    SECRET_KEY: Optional[str] = "lrmis_secret_key_2025"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = BaseConfig()
