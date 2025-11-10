from pydantic import BaseSettings

class Settings(BaseSettings):
    MYSQL_URI: str = 'sqlite:///./dev.db'
    OPENAI_API_KEY: str | None = None
    HUGGINGFACEHUB_API_TOKEN: str | None = None
    FAISS_PATH: str = './data/faiss.index'
    BACKEND_PORT: int = 8000

    class Config:
        env_file = '.env'

settings = Settings()