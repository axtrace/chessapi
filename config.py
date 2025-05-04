from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_KEY: str
    API_KEY_NAME: str = "X-API-Key"

    class Config:
        env_file = ".env"

settings = Settings()