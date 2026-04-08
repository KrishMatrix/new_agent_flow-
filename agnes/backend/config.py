import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    app_name: str = "Agnes — AI Supply Chain Manager"
    debug: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
