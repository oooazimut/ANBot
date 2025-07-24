from typing import Optional

from aiogram.enums import ContentType
from aiogram_dialog.api.entities import MediaId
from aiogram_dialog.api.protocols import MediaIdStorageProtocol


class MediaIdStorage(MediaIdStorageProtocol):
    async def get_media_id(
            self,
            path: Optional[str],
            url: Optional[str],
            type: ContentType,
    ) -> Optional[MediaId]:
        return None

    async def save_media_id(
            self,
            path: Optional[str],
            url: Optional[str],
            type: ContentType,
            media_id: MediaId,
    ) -> None:
        return None
