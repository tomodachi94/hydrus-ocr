"""
Retrieve files from Hydrus Network and run them through OCR.

See ../README.md for more details, including documentation.
"""
import os
import sys
import io
from time import sleep

# interact with the Hydrus client API
import hydrus_api as hydrus

# manipulate images
from PIL import Image, ImageFilter
import pyocr

# read environment variables from .env
# useful for development and some deployment scenarios
from dotenv import load_dotenv

load_dotenv()

# Configuration
hydrus_api_url: str = os.getenv("HYDRUS_OCR_API_URL")
access_key: str = os.getenv("HYDRUS_OCR_ACCESS_KEY")
tag_service_key: str = os.getenv("HYDRUS_OCR_TAG_SERVICE_KEY")
loop_delay: int = int(os.getenv("HYDRUS_OCR_LOOP_DELAY"))
ocr_language: str = os.getenv("HYDRUS_OCR_LANGUAGE")

# determine if we want to run in "singular run mode" or "daemon mode"
# "singular run mode" runs the program once then exits
# "daemon mode" runs the program continuously
if sys.argv[1] and (sys.argv[1] == "singular"):
    daemon: bool = False
elif sys.argv[1] and (sys.argv[1] == "daemon"):
    daemon: bool = True
else:
    raise Exception("Please specify the 'daemon' or 'singular' subcommand.")

# This is a list of all filetypes supported by both PIL and Hydrus
valid_file_types = [
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/tiff",
        "image/qoi",
        "image/x-icon",
        "image/bmp",
        "image/heif",
        "image/heic",
        "image/avif"
        ]

# Initialize the client with values from configuration
hydrus_client: hydrus.Client = hydrus.Client(access_key, hydrus_api_url)


def remove_ocr_service_tag(file_id: int, tag: str) -> None:
    """
    Removes a tag from an item in the program's tag service.
    """
    hydrus_client.add_tags(
            file_ids=[file_id],
            service_keys_to_actions_to_tags={tag_service_key: {1: [tag]}}
            )


def add_ocr_service_tag(file_id: int, tag: str) -> None:
    """
    Adds a tag to an item inside of the program's tag service.
    """
    hydrus_client.add_tags(
            file_ids=[file_id],
            service_keys_to_tags={tag_service_key: [tag]}
            )


def find_images():
    """
    Finds all images with the 'ocr wanted' tag set in our tag service.
    """
    tags = ["ocr wanted", "-ocr rejected"]
    return hydrus_client.search_files(tags, tag_service_key=tag_service_key)


def get_image(file_id: int) -> Image:
    """
    Retrieves an image from Hydrus and converts it to an Image object.
    """
    file = hydrus_client.get_file(file_id=file_id)
    if file.headers["Content-Type"] in valid_file_types:
        return Image.open(io.BytesIO(file.content))
    else:
        remove_ocr_service_tag(file_id, "ocr wanted")
        add_ocr_service_tag(file_id, "ocr rejected")
        return None


def ocr_image(image: Image) -> str:
    """
    OCR the image file using Tesseract.
    """
    image.filter(ImageFilter.SHARPEN)
    tool = pyocr.get_available_tools()[0]
    return tool.image_to_string(
            image,
            lang=ocr_language,
            builder=pyocr.builders.TextBuilder()
            )


def write_ocr_to_hydrus(file_id: int, text: str) -> None:
    """
    Sets the 'ocr' note in a Hydrus file to the 'text' parameter,
    and mark OCR as completed.
    """
    notes = {'ocr': text}
    hydrus_client.set_notes(notes, file_id=file_id)
    add_ocr_service_tag(file_id, "ocr completed")
    remove_ocr_service_tag(file_id, "ocr wanted")


def mainloop():
    """
    Run the program using the functions defined above.
    """
    run = True
    while run:
        for i in find_images()["file_ids"]:
            image = get_image(i)
            if image:
                text = ocr_image(image)
                write_ocr_to_hydrus(i, text)
            else:
                pass

        # If we're not in daemon mode, exit immediately after first run
        if not daemon:
            run = False
        else:
            sleep(loop_delay)


if __name__ == "__main__":
    mainloop()
