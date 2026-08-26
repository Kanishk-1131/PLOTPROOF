from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    app_env: str = "development"

    database_url: str = "sqlite:///./plotproof.db"
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret: str = "change_this_later_super_secret_jwt_key_plotproof"

    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
