import logging
from typing import List

from pymodbus import ModbusException
from pymodbus.client import AsyncModbusTcpClient

from config import settings

logger = logging.getLogger(__name__)

REG_START = 16384
REG_LEN = 41


def process_data(client: AsyncModbusTcpClient, data: List):
    pass


async def poll_registers() -> dict | None:
    async with AsyncModbusTcpClient(
        settings.modbus.host,
        port=settings.modbus.port,
        timeout=3,
        retries=1,
        reconnect_delay=0.5,
        reconnect_delay_max=0.5,
    ) as client:
        if not client.connected:
            logger.error("Нет соединения с ПР!")
            return

        try:
            hold_regs = await client.read_holding_registers(
                REG_START,
                count=REG_LEN,
            )
            if hold_regs.isError():
                logger.error(f"Чтение регистров завершилось ошибкой: {hold_regs}")
                return
            return process_data(client, hold_regs.registers)

        except ModbusException as exc:
            logger.error(f"Ошибка протокола Modbus: {exc}")
            return
