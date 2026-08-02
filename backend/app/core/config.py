from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

APP_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Every tunable value lives here, not scattered across the code.
    Values can be overridden with environment variables prefixed
    APP_ (e.g. APP_FUZZY_THRESHOLD=75), which is how Docker/CI will
    tune this without touching code.
    """

    model_config = SettingsConfigDict(env_prefix="APP_")

    merchant_db_path: Path = APP_DIR / "data" / "merchant_db.json"
    fuzzy_threshold: int = 80
    tfidf_threshold: float = 0.3
    cors_allowed_origins: list[str] = ["http://localhost:4200"]
    business_lifestyle_mapping_path: Path = APP_DIR / "data" / "business_lifestyle_mapping.json"
    category_model_bundle_path: Path = APP_DIR / "data" / "models" / "category_model_bundle.pkl"


settings = Settings()
