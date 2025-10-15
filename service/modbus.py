import logging
from datetime import datetime
from typing import Any, List

from aiogram import Bot
from pymodbus import ModbusException
from pymodbus.client import AsyncModbusTcpClient, ModbusBaseClient
from sqlalchemy.orm import sessionmaker

from config import ALL_SENSORS, PUMPS_IDS, Alerts, settings

logger = logging.getLogger(__name__)

REG_START = 16384
REG_LEN = 41

Uzas, Shifters = [], []
GSensors = [0] * 5
Tanks = [0] * 3
Bypasses = [0] * 4
isConnected = False


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


async def process_data(client: ModbusBaseClient, data: List):
    global Uzas, Shifters, GSensors, Tanks, Bypasses
    ts = datetime.now().replace(microsecond=0)
    alerts = []

    sensors = [
        {
            "name": n,
            "value": round(v, 1),
            "timestamp": ts,
        }
        for n, v in zip(ALL_SENSORS, words_to_floats(client, data[:12]))
    ]

    for i in range(len(sensors)):
        if sensors[i]["value"] > 30 and sensors[i]["value"] != GSensors[i]:
            alerts.append((Alerts.GAS, sensors[i]))

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

    tanks = convert_to_bin(data[28], 3)[-1:-4:-1]
    for i in range(len(tanks)):
        if tanks[i] and tanks[i] != Tanks[i]:
            alerts.append((Alerts.TANK, {"num": i + 1}))

    bypasses = convert_to_bin(data[29], 4)
    for i in range(len(bypasses)):
        if bypasses[i] and bypasses[i] != Bypasses[i]:
            alerts.append((Alerts.BYPASS, {"pump": PUMPS_IDS[i]}))

    Uzas = convert_to_bin(data[32], 6)
    Shifters = data[35:]
    GSensors = [s["value"] for s in sensors]
    Tanks = tanks
    Bypasses = bypasses

    return {"pumps": pumps, "sensors": sensors, "alerts": alerts}


async def poll_registers(bot: Bot, db_pool: sessionmaker) -> dict | None:
    global isConnected
    from service.message import handle_alerts

    async with AsyncModbusTcpClient(
        settings.modbus.host,
        port=settings.modbus.port,
        timeout=3,
        retries=1,
        reconnect_delay=0.5,
        reconnect_delay_max=0.5,
    ) as client:
        isConnected = client.connected
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
            result = await process_data(client, hold_regs.registers)
            await handle_alerts(bot, db_pool, result["alerts"])
            return result

        except ModbusException as exc:
            logger.error(f"Ошибка протокола Modbus: {exc}")
            return
