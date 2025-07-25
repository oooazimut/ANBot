from enum import StrEnum

from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ModbusSettings(BaseModel):
    host: str
    port: int


class Settings(BaseSettings):
    bot_token: SecretStr
    passwd: SecretStr
    db_name: str
    modbus: ModbusSettings

    @property
    def sqlite_async_dsn(self):
        return f"sqlite+aiosqlite:///{self.db_name}"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )


settings = Settings()


class GasRooms(StrEnum):
    PUMP = "Насосная"
    PROBE = "Пробная"
