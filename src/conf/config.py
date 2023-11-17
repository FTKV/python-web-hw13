from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    api_host: str = "localhost"
    api_port: int = 8000
    secret_key: str
    algorithm: str
    sqlalchemy_database_url_sync: str
    sqlalchemy_database_url_async: str
    redis_host: str
    redis_port: int
    mail_server: str
    mail_port: int
    mail_username: str
    mail_password: str
    mail_from: str
    mail_from_name: str
    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
