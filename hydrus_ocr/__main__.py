"""
Retrieve files from Hydrus Network and run them through OCR.

See ../README.md for more details, including documentation.
"""
import os
import sys
import threading
from time import sleep

from . import HydrusOCR
from .errors import MissingTokenError, NoSubcommandError

# Configuration
hydrus_api_url: str = os.getenv("HYDRUS_OCR_API_URL", "http://localhost:45869")
loop_delay: int = int(os.getenv("HYDRUS_OCR_LOOP_DELAY", "10"))
ocr_language: str = os.getenv("HYDRUS_OCR_LANGUAGE", "eng")

# These values have no possible fallback values.
# if either are set to None, mistakes were made.
access_key: str = os.getenv("HYDRUS_OCR_ACCESS_KEY")
tag_service_key: str = os.getenv("HYDRUS_OCR_TAG_SERVICE_KEY")

if not (access_key and tag_service_key):
    raise MissingTokenError(MissingTokenError.__doc__)

# determine if we want to run in "singular run mode" or "daemon mode"
# "singular run mode" runs the program once then exits
# "daemon mode" runs the program continuously
if sys.argv[1] and (sys.argv[1] == "singular"):
    DAEMON_MODE: bool = False
elif sys.argv[1] and (sys.argv[1] == "daemon"):
    DAEMON_MODE: bool = True
else:
    raise NoSubcommandError(NoSubcommandError.__doc__)

ocr_client = HydrusOCR(hydrus_api_url, access_key, tag_service_key, ocr_language)

def mainloop():
    """
    Run the program using the HydrusOCR class.
    """
    run = True
    while run:
        for i in ocr_client.find_images()["file_ids"]:
            threading.Thread(target=ocr_client.process_image, args=(i,)).start()

        # If we're not in daemon mode, exit immediately after first run
        if not DAEMON_MODE:
            run = False
        else:
            sleep(loop_delay)


if __name__ == "__main__":
    mainloop()
