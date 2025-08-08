from pathlib import Path
from typing import Sequence
from PIL import Image, ImageDraw, ImageFont

from config import GS_PROBE, GS_PUMP, GasRooms
from db.models import GasSensor
from service import modbus

points = {
    GasRooms.PUMP: dict(
        zip(GS_PUMP, [(550, 230), (930, 230), (90, 500), (1080, 1080)])
    ),
    GasRooms.PROBE: dict(zip(GS_PROBE, [(630, 260), (160, 670)])),
}


def draw_gassensors(sensors: Sequence[GasSensor]):
    font = ImageFont.truetype(font=Path("fonts/Ubuntu-R.ttf"), size=44)

    for room in GasRooms:
        image = Image.open(Path(f"images/templates/{room}.png"))
        draw = ImageDraw.Draw(image)
        for sensor in sensors:
            if sensor.name in points[room]:
                draw.text(
                    points[room][sensor.name],
                    f"{sensor.name}:   {round(sensor.value, 1)}%",
                    font=font,
                    fill="black",
                )
        image.save(Path(f"images/{room}.png"))


def draw_uzas_and_pumps(output: str):
    bg_img = Image.new("RGBA", (1000, 800), (255, 255, 255))
    x, y = 10, 10

    for cond in modbus.Uzas:
        path = str(Path(f"images/templates/uza{cond}.png"))
        bg_img.paste(path, (x, y), path)
        x += 245

    bg_img.save(output)
