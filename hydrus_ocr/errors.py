"""
Shared exceptions used in hydrus_ocr.
"""


class HydrusOCRError(Exception):
    """
    Thrown when something goes wrong with hydrus_ocr.

    This should only be thrown if there's no way that the daemon can continue.
    """
    pass


class MissingTokenError(HydrusOCRError):
    """
    The Hydrus client key or the tag service key were not properly set.

    The user probably didn't configure the daemon correctly;
    please see hydrus_ocr's documentation, as well as the manual for the system
    where this was hosted.
    """


class MissingToolError(HydrusOCRError):
    """
    hydrus_ocr couldn't find an OCR engine on the system.

    The user probably didn't install tesseract or cuneiform correctly;
    please see hydrus_ocr's documentation, as well as the manual for the system
    where this was hosted.
    """
