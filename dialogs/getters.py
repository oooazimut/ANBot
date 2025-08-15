from pathlib import Path
from aiogram_dialog import DialogManager

from config import PUMPS_IDS, GasRooms


async def gas_rooms_getter(dialog_manager: DialogManager, **kwargs):
    rooms = list(GasRooms)
    pages = len(rooms)
    curr_page = await dialog_manager.find("gs_rooms_scroll").get_page()
    path = Path(f"images/{rooms[curr_page]}.png")
    room = rooms[curr_page]

    return {
        "pages": pages,
        "path": path,
        "room": room,
    }


async def archive_getter(dialog_manager: DialogManager, **kwargs):
    archive: str = dialog_manager.dialog_data["archive"]
    titles = list(GasRooms) if "gs" in archive else PUMPS_IDS
    curr_page = await dialog_manager.find("archive_scroll").get_page()
    title = titles[curr_page]
    return {
        "pages": len(titles),
        "path": Path(f"images/{title}.png"),
        "title": title,
    }
