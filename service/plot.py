from collections import defaultdict
from pathlib import Path
from typing import Sequence
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from config import GS_PROBE, GS_PUMP, GasRooms
from db.models import GasSensor, Pump


def plot_pumps(pumps: Sequence[Pump]):
    sorted_pumps = defaultdict(list)
    for pump in pumps:
        sorted_pumps[pump.name].append(pump)

    for pump in sorted_pumps.keys():
        plt.clf()
        ax = plt.gca()
        times = [p.timestamp for p in sorted_pumps[pump]]
        pressures = [p.pressure for p in sorted_pumps[pump]]
        plt.plot(times, pressures, label="давление")
        date_format = mdates.DateFormatter("%H:%M")
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
        ax.xaxis.set_major_formatter(date_format)
        # start_of_day = dt.datetime.combine(
        #     dt.date.fromisoformat(chosen_date), dt.time.min
        # )
        # end_of_day = start_of_day + dt.timedelta(days=1)
        # ax.set_xlim(start_of_day, end_of_day)
        plt.legend()
        plt.title(f"Насос: {pump}")
        plt.tight_layout()
        plt.savefig(Path(f"images/{pump}.png"))
        plt.close()


def plot_gs(gs: Sequence[GasSensor]):
    data = dict(zip([i.value for i in GasRooms], (GS_PUMP, GS_PROBE)))
    sorted_sensors = defaultdict(list)
    for sensor in gs:
        sorted_sensors[sensor.name].append(sensor)
    times = [s.timestamp for s in sorted_sensors[GS_PUMP[0]]]
    for room in data.keys():
        plt.clf()
        for sn in data[room]:
            values = [s.value for s in sorted_sensors[sn]]
            plt.scatter(times, values, s=10, label=f"{sn}")

        ax = plt.gca()
        date_format = mdates.DateFormatter("%H:%M")
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
        ax.xaxis.set_major_formatter(date_format)
        plt.legend()
        plt.title(f"Помещение: {room}")
        plt.tight_layout()
        plt.savefig(Path(f"images/{room}.png"))
        plt.close()
