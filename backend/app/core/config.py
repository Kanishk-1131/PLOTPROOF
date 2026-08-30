from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    app_env: str = "development"

    database_url: str = "sqlite:///./plotproof.db"
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret: str = "change_this_later_super_secret_jwt_key_plotproof"

    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "plotproofadmin"
    minio_secret_key: str = "change_this_to_a_strong_password"
    minio_bucket: str = "plotproof-documents"
    max_upload_size_mb: int = 50

    clamav_host: str = "localhost"
    clamav_port: int = 3310

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )



settings = Settings()
