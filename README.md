# Personal-Virtual-Assistant
This can do all your basic task and able to make its own library so that not to go on web again when that problem come

This project is a voice assistant script `source.py` that uses microphone/audio libraries and performs web searches.

Quick setup (Windows PowerShell):

1. Activate the project's virtual environment (if present):

```powershell
& "E:/File Address/Scripts/Activate.ps1"
```

2. Install dependencies:

```powershell
"E:/File Address/Scripts/python.exe" -m pip install -r "E:/File Address/requirements.txt"
```

Notes:
- `pyaudio` may fail to install via pip on Windows. If installation fails, download a prebuilt wheel
  matching your Python version/architecture from https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio and install it with `pip install <wheel-file>`.
- If you don't have a microphone or want to test without audio, run `source.py` with text input modifications described in the file comments.

Run the assistant:

```powershell
"E:/File Address/Scripts/python.exe" "E:/File Address/source.py"
```

If you want me to add a non-microphone test mode to `source.py`, tell me and I will patch it in.
