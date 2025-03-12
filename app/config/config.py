# Configuration file

# Imports
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Short URL API"
    test_mode: bool
    db_uri: str = "sqlite:///database/database.sqlite"
    model_config = SettingsConfigDict(env_file=".env")
