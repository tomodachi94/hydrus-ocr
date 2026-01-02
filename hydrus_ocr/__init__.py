"""
Programmatic interface to hydrus_ocr.
"""
from io import BytesIO

# manipulate images
from PIL import Image, ImageFilter
import pyocr

from hydrus_api import Client

from hydrus_ocr.errors import MissingToolError

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


class HydrusOCR():
    def __init__(self, api_url, access_key, tag_service_key, ocr_language) -> None:
        self.api_url: str = api_url
        self.access_key: str = access_key
        self.hydrus_client: Client = Client(access_key)
        self.tag_service_key: str = tag_service_key
        self.ocr_language: str = ocr_language

    def remove_ocr_service_tag(self, file_id: int, tag: str) -> None:
        """
        Removes a tag from an item in the program's tag service.
        """
        self.hydrus_client.add_tags(
            file_ids=[file_id],
            service_keys_to_actions_to_tags={self.tag_service_key: {1: [tag]}}
            )

    def add_ocr_service_tag(self, file_id: int, tag: str) -> None:
        """
        Adds a tag to an item inside of the program's tag service.
        """
        self.hydrus_client.add_tags(
                file_ids=[file_id],
                service_keys_to_tags={self.tag_service_key: [tag]}
                )

    def find_images(self):
        """
        Finds all images with the 'ocr wanted' tag set in our tag service.
        """
        tags = ["ocr wanted", "-ocr rejected"]
        return self.hydrus_client.search_files(tags,
                                               tag_service_key=self.tag_service_key)

    def get_image(self, file_id: int) -> Image:
        """
        Retrieves an image from Hydrus and converts it to an Image object.
        """
        file = self.hydrus_client.get_file(file_id=file_id)
        if file.headers["Content-Type"] in valid_file_types:
            return Image.open(BytesIO(file.content))
        else:
            self.remove_ocr_service_tag(file_id, "ocr wanted")
            self.add_ocr_service_tag(file_id, "ocr rejected")
            return None

    def ocr_image(self, image: Image) -> str:
        """
        OCR the image file using Tesseract.
        """
        image.filter(ImageFilter.SHARPEN)
        tool = pyocr.get_available_tools()[0]
        if not tool:
            raise MissingToolError(MissingToolError.__doc__)

        return tool.image_to_string(
                image,
                lang=self.ocr_language,
                builder=pyocr.builders.TextBuilder()
                )

    def write_ocr_to_hydrus(self, file_id: int, text: str) -> None:
        """
        Sets the 'ocr' note in a Hydrus file to the 'text' parameter,
        and mark OCR as completed.
        """
        notes = {'ocr': text}
        self.hydrus_client.set_notes(notes, file_id=file_id)
        self.add_ocr_service_tag(file_id, "ocr completed")
        self.remove_ocr_service_tag(file_id, "ocr wanted")

    def process_image(self, file_id: int) -> None:
        """
        Run all of the processing steps on a specific image.
        """
        image = self.get_image(file_id)
        if image:
            text = self.ocr_image(image)
            self.write_ocr_to_hydrus(file_id, text)
        else:
            pass
