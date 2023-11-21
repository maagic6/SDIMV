<h1 align="center">
SDIMV
</h1>

<p align="center">Standalone program for viewing metadata of stable diffusion generated images</p>

<p align="center">Currently supports AUTOMATIC1111 web UI and NovelAI images</p>

<div align="center">
  <img src="https://github.com/maagic6/SDIMV/assets/80424597/f81e71f1-b355-4e81-a199-29073d5b72a4" width="40%" height="40%">
</div>


Usage
-----------
Download EXE from [releases](https://github.com/maagic6/SDIMV/releases)

- **Drag and drop onto the executable:**
   - Open by dragging and dropping images onto the executable

- **Add images from within the GUI:**
   - Drag images directly into the GUI

- **Right-click to add/remove:**
  - Right-click on items in the list menu to access options

Build (for Linux/MacOS)
-----------
```python
pip install -r requirements.txt
pip install pyinstaller
pyinstaller SDIMV.spec
```
Executable can be found in /dist after building
