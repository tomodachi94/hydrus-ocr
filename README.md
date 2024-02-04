# hydrus-ocr

This project runs [OCR](https://en.wikipedia.org/wiki/Optical_character_recognition) on images located in [Hydrus Network](https://hydrusnetwork.github.io/hydrus/) using an external daemon and a third-party library.

> [!WARNING]
> I am not liable if this destroys your data. **[Make backups regularly](https://hydrusnetwork.github.io/hydrus/getting_started_installing.html#backing_up)**.


## Setup

### In Hydrus
1. Create a tag service in Hydrus. It can be called whatever you like, but we recommend `ocr` so you remember what it's for. Save the service key for later.
2. [Enable the client API](https://hydrusnetwork.github.io/hydrus/client_api.html#enabling_the_api).
3. Create a client API access key (documented above). Give it the `edit file notes`, `edit file tags`, and `search for and fetch files` permissions. Save the service key for later.

### In your server environment
1. Install `hydrus-ocr` and its Python dependencies with `pip install https://github.com/tomodachi94/hydrus-ocr/releases/download/v0.1.0/hydrus_ocr-0.1.0-py3-none-any.whl`.
2. Install either [`tesseract`/`libtesseract`](https://github.com/tesseract-ocr/tesseract?tab=readme-ov-file#installing-tesseract) or [`cuneiform`](https://launchpad.net/cuneiform-linux) and ensure it is available on your `$PATH`.
3. Copy `env.example` to `.env` (or to another place where you can set environment variables) and fill in the values.
4. Run the daemon using `python3 -m hydrus_ocr daemon`. If you want to get fancy, you can configure it to start up automatically with `systemd`, but that is outside of the scope of these docs.
    * If you only want to run this once (e.g. for running this with `cron`), run `python3 -m hydrus_ocr singular`.

## Usage
1. Select a file (or a bunch of files!) and right-click them. Select `manage > tags`, select `ocr` (or the name you selected for the tag service), and add the `ocr wanted` tag to the file(s). Apply the changes.
2. Wait for the daemon to do its job. Depending on the number of files queued, it could take a bit to OCR the files.
3. Profit. Check the notes for the file; look for a note titled `ocr`.


## Configuration
This program is configured entirely through environment variables. Here's what they do:
* `HYDRUS_OCR_ACCESS_KEY`: The access key for the client API. This is a long hexadecimal string.
* `HYDRUS_OCR_API_URL`: The base URL for the client API. This looks like `http://localhost:45869` by default.
* `HYDRUS_OCR_TAG_SERVICE_KEY`: The service key for the tag service. This is a long hexadecimal string.
* `HYDRUS_OCR_LOOP_DELAY`: This controls the frequency at which the program checks for files to OCR. The default value causes a check every 10 seconds; increase or decrease depending on how many requests your Hydrus server can handle at once.
* `HYDRUS_OCR_LANGUAGE`: The language to OCR the text in (defaults to English). See the [Tesseract documentation](https://tesseract-ocr.github.io/tessdoc/Data-Files) for a full list of languages. Make sure to install the language(s) you want if it isn't available by default. Multiple languages are supported by separating each with a plus (like `eng+deu+jpn`).

## Errors
This is a glossary of all possible user-caused errors.

### `MissingToolError`
The program couldn't find Tesseract or Cuneiform. See [§ Installation](#installation) for more information.

### `MissingKeyError`
The program couldn't find the client API access key and/or the tag service key. See [§ Configuration](#configuration) for more information.

## FAQ
### Why should I trust you?
You shouldn't. You should read the source code yourself. I've tried to make the code as easy-to-read as possible, with docstrings for all (internal) functions and comments for ambiguous lines of code.

### Why does this exist?
I use Hydrus to store a large repository of screenshots of chat logs. I wanted to find a way to search their text, and this is the result.

### What are the limitations of this program?
It does not use threading to OCR multiple files at once.

[Threading](https://github.com/tomodachi94/hydrus-ocr/issues/2) is planned for the future. Subscribe to the relevant GitHub issue for updates.

### Why is the quality of the text so bad?
This program uses Tesseract to do most of the heavy lifting. Tesseract is notoriously bad at OCRing specific types of images, as well as images of lower quality.

### Why is this separate from Hydrus?
Aside from the fact that this would likely be rejected in a PR, OCR can be a resource-intensive operation, and I didn't want to risk the stability of my Hydrus application.

