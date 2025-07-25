from aiogram_dialog import DialogManager

from config import GasRooms


async def gas_rooms_getter(dialog_manager: DialogManager, **kwargs):
    rooms = list(GasRooms)
    pages = len(rooms)
    curr_page = await dialog_manager.find("gs_rooms_scroll").get_page()
    path = rooms[curr_page]

    return {
        "pages": pages,
        "path": path,
    }
