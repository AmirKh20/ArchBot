# ArchBot
Archive your files and make PDF of your images

## usage
1- clone the repository then install the requirements:
```bash
    $ pip3 install -r requirements.txt
    # apt install zip rar graphicsmagick
```
2- set `BOT_TOKEN`, `FLASK_PORT`, `API_HASH`, `API_ID` in `.env` file

3- then run both `ArchFileBot.py` and `FileDownloader.py` scripts

NOTE: if you don't want to download files with >=20 MB size ignore the last two environment variables and don't run `FileDownloader.py`
