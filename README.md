<div align="center">
  <img src="https://github.com/maagic6/SDIMV/assets/80424597/f7824981-4b88-4abf-9361-06d9e05b9954" width="20%" height="20%">
</div>
<h1 align="center">
SDIMV
</h1>

<p align="center">
  <a href="https://github.com/maagic6/SDIMV/releases/tag/v1.2.0"><img alt="Release" src="https://img.shields.io/badge/Release-v1.2.0-brightgreen"></a>
  <a href="https://github.com/maagic6/SDIMV/releases"><img alt="Downloads" src="https://img.shields.io/github/downloads/maagic6/SDIMV/total"></a>
  <a href="https://opensource.org/licenses/MIT"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-brightgreen.svg"></a>
</p>

<p align="center">Standalone program for viewing metadata of stable diffusion generated images</p>

<div align="center">
  <img src="https://github.com/maagic6/SDIMV/assets/80424597/de9f6f55-5d01-4987-ba18-199ea1befa30" width="60%" height="60%">
</div>

Download (Windows)
-----------
Download from [releases](https://github.com/maagic6/SDIMV/releases)

Features
-----------
- Supports AUTOMATIC1111 web UI, NovelAI, and ComfyUI* png images
- Supports AUTOMATIC1111 web UI jpg images
- Supports PixAI mp4 animations
- Supports viewing of webp images
- Resizing and rearranging of UI
- Drag and drop images/folders
  
> *Note: SDIMV has not been tested on many ComfyUI images so expect bugs/crashes

<div align="left">
  <img src="https://github.com/maagic6/SDIMV/assets/80424597/8f7bba43-f372-4844-90d6-f904f8ef24de" width="60%" height="60%">
</div>

<div align="left">
  <img src="https://github.com/maagic6/SDIMV/assets/80424597/312f82af-887b-495a-af9d-bad0d92105ff" width="60%" height="60%">
</div>

~~Build (Linux/MacOS)~~ (need to handle platform-specific code + update requirements.txt first)
-----------
```python
pip install -r requirements.txt
pip install pyinstaller
pyinstaller SDIMV.spec~~
```
~~Executable can be found in /dist after building~~

Acknowledgements
-----------
- [sleepycherryi](https://github.com/sleepycherryi) for icon
- [PyQt-Frameless-Window](https://github.com/zhiyiYo/PyQt-Frameless-Window/tree/PyQt6) used for implementing custom titlebar
