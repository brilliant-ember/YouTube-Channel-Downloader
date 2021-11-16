# YouTube-Channel-Downloader

## How to use

1. Make sure to have Python3 with the required packeges downloaded, we need PyTube, and Selenium packages. The exact versions are in the `requirements.txt` file
2. Download the source code from this github repo.
3. Open the `Launcher.py` file and edit the channel_url to put your channel link instead of mine, make sure it is the right format. The channel url format guidlines are below.
4. Open a terminal window in the directory of the source code, terminal is also known as Command Line Prompt 
5. Run the following command `python3 Launcher.py` to start the download
6. A firefox browser window will pop up and will automatically go through the channel, **don't close it**.
7. You can press `ctrl c` in the terminal window to stop the download, and you can resume it later if you want running the same command you used to start the download the first time
8. If you run into erros read the terminal error message it will give you a useful hint that you can google to solve the issue
9. You can refer to the video tutorial below of me using the downloader to backup my own channel


## Channel url format guidlines

Channel url must be in on of these forms

- https://www.youtube.com/user/channel_name
- https://www.youtube.com/channel/special_code_for_channel
- https://www.youtube.com/c/channel_name
  
Make sure there's no '/featured' or '/vidoes' or '/' anything at the end of the link

Examples of valid channel urls

- https://www.youtube.com/user/FireSymphoney
- https://www.youtube.com/channel/UCVryWqJ4cSlbTSETBHpBUWw
- https://www.youtube.com/c/iforce2d


## Notes
- Right now the maximum video quality is 720p
- Run unit tests `python3 tests/Downloader_test.py`
