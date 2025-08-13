import logging
from datetime import datetime
from typing import Any, List

from pymodbus import ModbusException
from pymodbus.client import AsyncModbusTcpClient, ModbusBaseClient

from config import GS_PROBE, GS_PUMP, PUMPS_IDS, settings


logger = logging.getLogger(__name__)

REG_START = 16384
REG_LEN = 41

Uzas, Shifters = [], []


def convert_to_bin(num: int, width: int) -> list[int]:
    return [int(b) for b in f"{num:0{width}b}"[::-1]]


def words_to_floats(client: ModbusBaseClient, words: list[int]) -> List[float | Any]:
    return [
        client.convert_from_registers(
            words[i : i + 2],
            data_type=client.DATATYPE.FLOAT32,
            word_order="little",
        )
        for i in range(0, len(words), 2)
    ]


def process_data(client: ModbusBaseClient, data: List):
    global Uzas, Shifters
    ts = datetime.now().replace(microsecond=0)

    sensors = [
        {
            "name": n,
            "value": v,
            "timestamp": ts,
        }
        for n, v in zip(GS_PUMP + GS_PROBE, words_to_floats(client, data[:12]))
    ]

    pumps = [
        {
            "name": n,
            "pressure": round(p, 1),
            "enable": c,
            "timestamp": ts,
            "permission": perm,
            "work": round(w / 60),
        }
        for n, p, w, perm, c in zip(
            PUMPS_IDS,
            words_to_floats(client, data[12:22]),
            data[22:27],
            convert_to_bin(data[33], 5),
            convert_to_bin(data[34], 5),
        )
    ]

    Uzas = convert_to_bin(data[32], 6)
    Shifters = data[35:]

    return {"pumps": pumps, "sensors": sensors}


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
