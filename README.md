# SD Image Metadata Viewer

Standalone program for viewing metadata of stable diffusion generated images

Currently supports AUTOMATIC1111 web UI and NovelAI images

<img src="https://github.com/maagic6/sd_image/assets/80424597/26ce22f8-c6f1-45ee-8739-9475e3fc6111" width=20% height=20%>

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
