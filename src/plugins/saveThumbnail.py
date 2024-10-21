import os
import httpx

from uuid import uuid4


class SaveThumbnailPlugin:
    def __init__(self):
        if not os.path.exists("__temp__"):
            os.mkdir("__temp__")

    def save_thumbnail(self, thumbnail: str) -> str:
        # Get file extension from URL
        extension = thumbnail.split("/")[-1].split(".")[1].split("?")[0]
        saved_filename = f"__temp__/{uuid4()}.{extension}"

        # Save thumbnail to local storage
        with open(saved_filename, "wb") as f:
            with httpx.stream("GET", thumbnail) as response:
                for chunk in response.iter_bytes():
                    f.write(chunk)

        return os.path.abspath(saved_filename)

    def remove_thumbnail(self, saved_thumbnail: str) -> bool:
        os.remove(saved_thumbnail)
        return True
