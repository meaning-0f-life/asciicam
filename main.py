from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Label, Button, Select
from textual.containers import VerticalScroll
import pyperclip

from camera import Camera, VIRTUAL_CAM_AVAILABLE, list_available_cameras, get_camera_name


class AsciiCamApp(App):
    BINDINGS = [
        ("q", "quit", "Quit application"),
        ("s", "toggle_stream", "Toggle Virtual Stream"),
        ("c", "change_camera", "Change Camera"),
    ]
    CSS_PATH = "asciicamera.tcss"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Registry of widgets you can reference by string
        self.items: dict[str, Label] = {
            "previewlabel": Label("", id="previewlabel"),
        }
        self.streaming = False
        self.camera = None
        self.selected_camera_index = 0
        self.available_cameras = []

    async def on_mount(self) -> None:
        """Called when the app starts. Sets up periodic updates."""
        self.set_interval(1 / 30, self.update_frame)
        self.title = "ASCIICAM"
        self.sub_title = "Opening camera..."
        
        # Find available cameras
        try:
            self.available_cameras = list_available_cameras()
        except Exception as e:
            self.sub_title = f"Camera error: {str(e)}"
            return
        
        # Open camera 0 by default (typically the default webcam)
        self.selected_camera_index = 0
        try:
            self.camera = Camera(self.selected_camera_index)
            camera_name = self.available_cameras[0]['name'] if self.available_cameras else f"Camera {self.selected_camera_index}"
            self.sub_title = f"Camera: {camera_name} | Press 'c' to change camera"
        except Exception as e:
            self.sub_title = f"Error opening camera 0: {str(e)}"
        
        # Check if virtual camera is available
        if not VIRTUAL_CAM_AVAILABLE:
            self.sub_title += " | Virtual camera not available"

    def compose(self) -> ComposeResult:
        """Called to add widgets to the app."""
        yield Header()
        yield Footer()
        
        # Create camera selection dropdown
        camera_options = []
        for camera in self.available_cameras:
            camera_name = camera['name']
            camera_options.append((camera_name, camera['index']))
        
        # Show camera selection if cameras are available
        if camera_options:
            yield Select(
                options=camera_options,
                prompt="Select Camera",
                id="camera_select"
            )
        else:
            # Show message if no cameras found
            yield Label("No cameras detected", id="no_camera_label")
        
        # Create button container
        buttons = []
        buttons.append(Button("Copy ASCII", id="copybtn"))
        
        # Add virtual camera controls if available
        if VIRTUAL_CAM_AVAILABLE:
            buttons.append(Button("Start Virtual Stream", id="startstreambtn"))
            buttons.append(Button("Stop Virtual Stream", id="stopstreambtn"))
        
        yield VerticalScroll(
            self.items["previewlabel"],
            *buttons,
        )

    async def update_frame(self) -> None:
        """Periodically called to update camera frames."""
        try:
            if self.camera:
                ascii_frame = self.camera.get_ascii_camera()
                self.items["previewlabel"].update(ascii_frame)
            else:
                self.items["previewlabel"].update("Select a camera to start")
        except Exception as e:
            self.items["previewlabel"].update(f"Error: {str(e)}")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "copybtn":
            try:
                if self.camera:
                    ascii_frame = self.camera.get_ascii_camera()
                    pyperclip.copy(str(ascii_frame))
                    self.sub_title = "Copied to clipboard!"
                else:
                    self.sub_title = "No camera selected"
            except Exception as e:
                self.sub_title = f"Error copying: {str(e)}"
        
        elif event.button.id == "startstreambtn":
            try:
                if self.camera:
                    self.camera.start_virtual_stream(width=200, fps=15, camera_name="ASCII Camera")
                    self.streaming = True
                    self.sub_title = "Virtual stream 'ASCII Camera' started! Use in Zoom/other apps."
                else:
                    self.sub_title = "No camera selected"
            except Exception as e:
                self.sub_title = f"Error starting stream: {str(e)}"
        
        elif event.button.id == "stopstreambtn":
            try:
                if self.camera:
                    self.camera.stop_virtual_stream()
                    self.streaming = False
                    self.sub_title = "Virtual stream stopped."
                else:
                    self.sub_title = "No camera selected"
            except Exception as e:
                self.sub_title = f"Error stopping stream: {str(e)}"

    async def on_select_changed(self, event: Select.Changed) -> None:
        """Handle camera selection change."""
        if event.select.id == "camera_select":
            self.selected_camera_index = event.value
            try:
                # Close existing camera if any
                if self.camera:
                    self.camera.camera.release()
                
                # Open new camera
                self.camera = Camera(self.selected_camera_index)
                camera_name = self.available_cameras[self.selected_camera_index]['name'] if self.selected_camera_index < len(self.available_cameras) else f"Camera {self.selected_camera_index}"
                self.sub_title = f"Camera: {camera_name} | Press 'c' to change camera"
            except Exception as e:
                self.sub_title = f"Error opening camera: {str(e)}"
    
    async def action_change_camera(self) -> None:
        """Cycle through available cameras."""
        if not self.available_cameras:
            self.sub_title = "No cameras available"
            return
        
        # Find next camera index
        next_index = (self.selected_camera_index + 1) % len(self.available_cameras)
        
        try:
            # Close existing camera if any
            if self.camera:
                self.camera.camera.release()
            
            # Open new camera
            self.selected_camera_index = next_index
            self.camera = Camera(self.selected_camera_index)
            camera_name = self.available_cameras[next_index]['name']
            self.sub_title = f"Camera: {camera_name} | Press 'c' to change camera"
        except Exception as e:
            self.sub_title = f"Error opening camera: {str(e)}"
    
    async def action_toggle_stream(self) -> None:
        """Toggle virtual camera stream on/off."""
        if not VIRTUAL_CAM_AVAILABLE:
            self.sub_title = "Virtual camera not available"
            return
            
        if self.streaming:
            try:
                if self.camera:
                    self.camera.stop_virtual_stream()
                    self.streaming = False
                    self.sub_title = "Virtual stream stopped."
            except Exception as e:
                self.sub_title = f"Error stopping stream: {str(e)}"
        else:
            try:
                if self.camera:
                    self.camera.start_virtual_stream(width=200, fps=15, camera_name="ASCII Camera")
                    self.streaming = True
                    self.sub_title = "Virtual stream 'ASCII Camera' started! Use in Zoom/other apps."
            except Exception as e:
                self.sub_title = f"Error starting stream: {str(e)}"

    async def on_shutdown(self) -> None:
        """Called when the app is shutting down."""
        try:
            if self.camera:
                self.camera.stop_virtual_stream()
                self.camera.camera.release()
        except:
            pass


if __name__ == "__main__":
    app = AsciiCamApp()
    app.run()

