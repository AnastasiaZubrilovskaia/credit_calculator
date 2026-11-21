from decimal import Decimal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    base_rate: Decimal = Decimal("20.0")
    insurance_cost: Decimal = Decimal("100000.00")
    insurance_rate_discount: Decimal = Decimal("3.0")
    salary_rate_discount: Decimal = Decimal("1.0")

    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="CALCULATOR_", extra="ignore")


settings = Settings()