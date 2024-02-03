"""
Retrieve files from Hydrus Network and run them through OCR.

See ../README.md for more details, including documentation.
"""
import os
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

# Initialize the client with values from configuration
hydrus_client: hydrus.Client = hydrus.Client(access_key, hydrus_api_url)


def find_images():
    """
    Finds all images with the 'ocr wanted' tag set in our tag service.
    """
    tags = ["ocr wanted"]
    return hydrus_client.search_files(tags, tag_service_key=tag_service_key)


def get_image(file_id: int) -> Image:
    """
    Retrieves an image from Hydrus and converts it to an Image object.
    """
    file = hydrus_client.get_file(file_id=file_id)
    print(file.raw)
    return Image.open(io.BytesIO(file.content))


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
    hydrus_client.add_tags(
        file_ids=[file_id],
        service_keys_to_tags={tag_service_key: ["ocr completed"]}
        )
    hydrus_client.add_tags(
        file_ids=[file_id],
        service_keys_to_actions_to_tags={tag_service_key: {1: ["ocr wanted"]}}
    )


def mainloop():
    """
    Run the program using the functions defined above.
    """
    while True:
        for i in find_images()["file_ids"]:
            image = get_image(i)
            text = ocr_image(image)
            write_ocr_to_hydrus(i, text)

        sleep(loop_delay)


if __name__ == "__main__":
    mainloop()
