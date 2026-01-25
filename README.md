# asciicam

A live camera feed for your terminal with virtual camera streaming support.

![Screenshot of asciicam](./asciicam.png)

## Features
- **Live camera Feed**: Stream video from your webcam in real-time
- **ASCII Conversion**: Converts frames to grayscale ASCII art.
- **Terminal UI**: Built with [textual](https://textual.textualize.io/) for smooth display in the terminal.
- **Copy to Clipboard**: Easily copy ASCII frames using [pyperclip](https://pypi.org/project/pyperclip/)
- **Camera Selection**: Choose from available cameras in the system
- **Virtual Camera Streaming**: Stream ASCII art as a virtual video device named "ASCII Camera" that can be used in Zoom, OBS, and other video applications

## Virtual Camera Streaming

The virtual camera feature allows you to stream ASCII art as a video feed that can be used by other applications like Zoom, Microsoft Teams, OBS Studio, and more. The virtual camera is named "ASCII Camera" and appears as a separate video device in your system.

**Note**: On some platforms (especially macOS with OBS Studio), the virtual camera may be named "OBS Virtual Camera" instead of "ASCII Camera". The actual camera name is determined by the virtual camera driver and may vary depending on your system configuration.

### How to Use

1. **Install the required dependencies**:
   ```bash
   pip install pyvirtualcam Pillow
   ```
   
   **Note**: On macOS, you may need to install additional software:
   - Install [OBS Studio](https://obsproject.com/) with the virtual camera plugin
   - Or use [CamTwist](http://camtwist.it/) or similar virtual camera software

2. **Start the application**:
   ```bash
   uv run main.py
   ```

3. **Select a camera**:
   - Choose a camera from the dropdown menu
   - The application will automatically detect and use the selected camera

4. **Start the virtual stream**:
   - Click the "Start Virtual Stream" button in the UI
   - Or press `S` to toggle the stream on/off
   - The virtual camera will be named "ASCII Camera" (or "OBS Virtual Camera" on some platforms)

5. **Use in other applications**:
   - In Zoom/Teams/OBS, select "ASCII Camera" as the video source
   - The ASCII art will be displayed as a video feed

### Virtual Camera Settings

The virtual camera streams at:
- **Resolution**: 100 characters wide (scaled to video resolution)
- **Frame rate**: 15 FPS
- **Format**: RGB video
- **Name**: "ASCII Camera" (or "OBS Virtual Camera" on some platforms)

You can adjust these settings in the [`camera.py`](camera.py:1) file by modifying the parameters in the [`start_virtual_stream()`](camera.py:263) method.

## Installation
Download the latest release [here](https://github.com/arcathrax/asciicam/releases).

## Development
### Set up development environment

**Install [uv](https://docs.astral.sh/uv/guides/install-python/)**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Clone repository**
```bash
git clone https://github.com/arcathrax/asciicam.git ~/Downloads/asciicam
```

**Run application**
```bash
cd ~/Downloads/asciicam
uv run main.py
```

### Generating a binary

**Go to repo**
```bash
cd ~/Downloads/asciicam
```

**Create and enter venv**
```bash
python -m venv venv
source venv/bin/activate
```

**Install dependencies**
```bash
pip install opencv-python textual pyperclip pyvirtualcam Pillow pyinstaller
```

**Generate binaries**
Note that here the `asciicamera.tcss` also gets added to the binary.
```bash
pyinstaller asciicam.spec
```

The binary is now under in the `dist` folder and called `main`.

## Usage

### Basic Usage
1. Run the application: `uv run main.py`
2. Select a camera from the dropdown menu
3. View the ASCII camera feed in your terminal
4. Press `S` to toggle virtual camera streaming on/off
5. Use the virtual camera "ASCII Camera" in Zoom, OBS, or other video applications

### Keyboard Shortcuts
- `Q`: Quit the application
- `S`: Toggle virtual camera stream on/off

### UI Controls
- **Camera Selection**: Choose from available cameras in the system
- **Copy ASCII**: Copy the current ASCII frame to clipboard
- **Start Virtual Stream**: Start streaming ASCII as a virtual video device named "ASCII Camera"
- **Stop Virtual Stream**: Stop the virtual camera stream

## Platform Support

### macOS
- Requires OBS Studio with virtual camera plugin or CamTwist
- Virtual camera streaming may require additional setup
- The virtual camera will be named "ASCII Camera" (or "OBS Virtual Camera" on some platforms)

### Windows
- Requires OBS Studio with virtual camera plugin
- Virtual camera should work out of the box with OBS
- The virtual camera will be named "ASCII Camera" (or "OBS Virtual Camera" on some platforms)

### Linux
- Requires OBS Studio with virtual camera plugin
- May require additional configuration depending on distribution
- The virtual camera will be named "ASCII Camera" (or "OBS Virtual Camera" on some platforms)

## Troubleshooting

### Virtual camera not available
If the virtual camera option is not available in the UI:
1. Ensure `pyvirtualcam` is installed: `pip install pyvirtualcam`
2. Check if your platform supports virtual cameras
3. Install OBS Studio or similar virtual camera software

### Virtual camera not appearing in Zoom/other apps
1. Make sure the virtual camera is started in asciicam
2. Restart the target application (Zoom, Teams, etc.)
3. Check if the virtual camera device "ASCII Camera" is available in your system settings

### Virtual camera shows "camera with line through it" icon
This happens when OBS Studio cannot access your real camera. To fix:

**On macOS:**
1. Open `System Settings` → `Privacy & Security` → `Camera`
2. Ensure OBS Studio has permission to access the camera
3. Restart OBS Studio and asciicam

**On Windows:**
1. Open `Settings` → `Privacy` → `Camera`
2. Ensure OBS Studio has permission to access the camera
3. Restart OBS Studio and asciicam

### Camera selection not working
If you can't select a camera:
1. **Check available cameras**:
   ```bash
   python3 -c "from camera import list_available_cameras; print(list_available_cameras())"
   ```

2. **Ensure camera is connected**:
   - Check if your camera is physically connected
   - Try other applications (Zoom, FaceTime) to verify camera works

3. **Restart the application**:
   - Close asciicam completely
   - Restart it to refresh the camera list

### Performance issues
- Reduce the ASCII width in [`camera.py`](camera.py:1) for better performance
- Lower the frame rate in the virtual stream settings
- Close other applications to free up system resources

### Custom Camera Name
The virtual camera is named "ASCII Camera" by default. On some platforms, the camera name may be determined by the virtual camera driver and cannot be changed directly. For example, on macOS with OBS Studio, the virtual camera will be named "OBS Virtual Camera". The `camera_name` parameter is used for display purposes only and does not affect the actual camera name in the system.

### Camera not detected
If no cameras are detected:
1. Check if your camera is connected and working
2. Try other applications (Zoom, FaceTime) to verify camera works
3. On macOS, check System Information → Camera
4. Restart your computer

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
