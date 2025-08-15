from pathlib import Path
from typing import Sequence
from PIL import Image, ImageDraw, ImageFont

from config import GS_PROBE, GS_PUMP, PUMPS_IDS, GasRooms
from db.models import GasSensor, Pump
from service import modbus

POINTS = {
    GasRooms.PUMP: dict(
        zip(GS_PUMP, [(550, 230), (930, 230), (90, 500), (1080, 1080)])
    ),
    GasRooms.PROBE: dict(zip(GS_PROBE, [(630, 260), (160, 670)])),
}

SHIFTERS = {0: "--------"}
SHIFTERS.update(dict(zip(range(1, 6), PUMPS_IDS)))


def draw_gassensors(sensors: Sequence[GasSensor]):
    font = ImageFont.truetype(font=Path("fonts/Ubuntu-R.ttf"), size=44)

    for room in GasRooms:
        image = Image.open(Path(f"images/templates/{room}.png"))
        draw = ImageDraw.Draw(image)
        for sensor in sensors:
            if sensor.name in POINTS[room]:
                draw.text(
                    POINTS[room][sensor.name],
                    f"{sensor.name}:   {round(sensor.value, 1)}%",
                    font=font,
                    fill="black",
                )
        image.save(Path(f"images/{room}.png"))


def draw_uzas_and_pumps(output: str, pumps: Sequence[Pump]):
    def get_font(size: int) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(font=Path("fonts/Ubuntu-R.ttf"), size=size)

    bg_img = Image.new("RGBA", (1500, 800), (255, 255, 255))
    draw = ImageDraw.Draw(bg_img)
    shifters = [SHIFTERS[i] for i in modbus.Shifters]
    uza_font = get_font(48)
    shft_font = get_font(38)
    pump_font = get_font(58)
    val_font = get_font(48)

    x, y = 30, 70
    for num, cond in enumerate(modbus.Uzas, start=1):
        draw.rounded_rectangle(
            (x, y, x + 200, y + 90),
            radius=10,
            fill="green" if cond else "red",
            outline="black",
            width=3,
        )
        draw.text((x + 40, y + 20), f"УЗА-{num}", font=uza_font)
        draw.text((x + 50, y + 130), shifters[num - 1], fill="black", font=shft_font)
        x += 245

    x, y = 20, 400
    for i in range(5):
        draw.rectangle((x, y, x + 270, y + 380), outline="black", width=3)
        draw.rounded_rectangle(
            (x + 30, y - 40, x + 250, y + 50),
            radius=10,
            fill="green" if pumps[i].enable else "grey",
            outline="black",
            width=3,
        )
        draw.text((x + 80, y - 30), PUMPS_IDS[i], font=pump_font)
        draw.text(
            (x + 60, y + 100), f"{pumps[i].pressure} бар", fill="black", font=val_font
        )
        draw.text(
            (x + 60, y + 190), f"{pumps[i].temperature} °C", fill="black", font=val_font
        )
        draw.text((x + 60, y + 280), f"{pumps[i].work} ч.", fill="black", font=val_font)
        x += 300

    bg_img.save(output)
