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


class Alerts(StrEnum):
    GAS = "gas_alert"
    TANK = "tank_overflow"
    BYPASS = "bypass_warning"


GS_PUMP = ["5.1", "5.2", "5.4", "5.3"]
GS_PROBE = ["3.8", "4.1"]
ALL_SENSORS = GS_PUMP + GS_PROBE
PUMPS_IDS = ["H-1.1", "H-1.2", "H-3", "H-2.1", "H-2.2"]
PUMPS_DESCS = ("АИ-92", "АИ-95/98", "Внутр.", "ДТ", "ДТ")
