import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import threading
import time

try:
    import pyvirtualcam
    VIRTUAL_CAM_AVAILABLE = True
except ImportError:
    VIRTUAL_CAM_AVAILABLE = False
    print("Warning: pyvirtualcam not available. Virtual camera streaming will not work.")
    print("Install with: pip install pyvirtualcam")


def list_available_cameras():
    """List all available cameras in the system."""
    available = []
    for i in range(10):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                # Try to get camera info
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
                # Try to get camera name from OpenCV
                camera_name = f"Camera {i}"
                try:
                    # Some systems support getting camera name
                    name_prop = cap.get(cv2.CAP_PROP_NAME)
                    if name_prop and str(name_prop).strip():
                        camera_name = str(name_prop)
                except:
                    pass
                
                available.append({
                    'index': i,
                    'width': width,
                    'height': height,
                    'name': camera_name
                })
            cap.release()
    return available


def get_camera_name(camera_index):
    """Get a descriptive name for a camera."""
    try:
        cap = cv2.VideoCapture(camera_index)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                is_real = frame.mean() > 10
                cap.release()
                return f"Camera {camera_index}" if is_real else f"Virtual Camera {camera_index}"
            cap.release()
    except:
        pass
    return f"Camera {camera_index}"


class VirtualCameraStreamer:
    """Streams ASCII characters to a virtual camera device."""
    
    def __init__(self, camera, width=200, fps=30, camera_name="ASCII Camera"):
        """
        Initialize virtual camera streamer.
        
        Args:
            camera: Camera object to capture from
            width: Width of ASCII art in characters
            fps: Frames per second for virtual camera
            camera_name: Name of the virtual camera device
        """
        self.camera = camera
        self.width = width
        self.fps = fps
        self.camera_name = camera_name
        self.is_streaming = False
        self.stream_thread = None
        self.virtual_cam = None
        self.frame_count = 0
        self._cached_font = None
        
    def _create_ascii_frame(self, ascii_art):
        """Convert ASCII art to an image frame."""
        # Calculate dimensions based on ASCII art
        lines = ascii_art.split('\n')
        if not lines:
            return None
            
        # Use a monospace font for consistent character sizing
        # Create a larger image for better visibility
        char_width = 8
        char_height = 12
        img_width = len(lines[0]) * char_width if lines[0] else 100
        img_height = len(lines) * char_height
        
        # Create a black background
        img = Image.new('RGB', (img_width, img_height), color='black')
        draw = ImageDraw.Draw(img)
        
        # Use cached font if available, otherwise load and cache it
        if self._cached_font is None:
            # Try to use a monospace font, fallback to default
            for font_path in ["/System/Library/Fonts/Monaco.ttf",
                            "/System/Library/Fonts/Courier New.ttf",
                            "/System/Library/Fonts/Courier.dfont"]:
                try:
                    self._cached_font = ImageFont.truetype(font_path, 10)
                    break
                except:
                    continue
            if self._cached_font is None:
                self._cached_font = ImageFont.load_default()
        font = self._cached_font
        
        # Draw ASCII text
        y = 0
        for line in lines:
            if line.strip():  # Only draw non-empty lines
                #draw.text((0, y), line, fill='white', font=font)
                draw.text((100, y + 6), line, fill='white', font=font)
            y += char_height
        
        # Convert to numpy array for OpenCV
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        return frame
    
    def start_streaming(self):
        """Start streaming ASCII to virtual camera."""
        if not VIRTUAL_CAM_AVAILABLE:
            raise RuntimeError("pyvirtualcam is not installed. Cannot start virtual camera stream.")
        
        if self.is_streaming:
            return
            
        self.is_streaming = True
        self.stream_thread = threading.Thread(target=self._stream_loop, daemon=True)
        self.stream_thread.start()
        
    def stop_streaming(self):
        """Stop streaming ASCII to virtual camera."""
        self.is_streaming = False
        if self.stream_thread:
            self.stream_thread.join(timeout=2)
        if self.virtual_cam:
            self.virtual_cam.close()
            self.virtual_cam = None
            
    def _stream_loop(self):
        """Main streaming loop."""
        try:
            # Get initial frame to determine dimensions
            ascii_art = self.camera.get_ascii_camera(width=self.width)
            frame = self._create_ascii_frame(ascii_art)
            
            if frame is None:
                print("Failed to create initial frame")
                return
                
            height, width = frame.shape[:2]
            
            # Initialize virtual camera
            # Note: pyvirtualcam may not support custom camera names directly on all platforms
            # The camera name is determined by the system/virtual camera driver
            # On macOS with OBS, the virtual camera is named "OBS Virtual Camera"
            # On Windows with OBS, the virtual camera is named "OBS Virtual Camera"
            # On Linux with OBS, the virtual camera is named "OBS Virtual Camera"
            # The camera_name parameter is used for display purposes only
            self.virtual_cam = pyvirtualcam.Camera(width=width, height=height, fps=self.fps)
            print(f"Virtual camera started: {width}x{height} @ {self.fps}fps")
            print(f"Camera name: {self.camera_name}")
            print("Streaming ASCII art to virtual camera...")
            print(f"You can now use '{self.camera_name}' in Zoom, OBS, or other applications.")
            
            frame_count = 0
            while self.is_streaming:
                try:
                    # Get ASCII frame
                    ascii_art = self.camera.get_ascii_camera(width=self.width)
                    
                    # Convert to video frame
                    frame = self._create_ascii_frame(ascii_art)
                    
                    if frame is not None:
                        # Send frame to virtual camera
                        self.virtual_cam.send(frame)
                        self.virtual_cam.sleep_until_next_frame()
                        frame_count += 1
                        
                        # Print status every 30 frames
                        if frame_count % 30 == 0:
                            print(f"Streaming... {frame_count} frames sent")
                    
                    # Small delay to control frame rate
                    # time.sleep(1.0 / self.fps)
                    
                except Exception as e:
                    print(f"Error in streaming loop: {e}")
                    break
                    
        except Exception as e:
            print(f"Error starting virtual camera: {e}")
        finally:
            if self.virtual_cam:
                self.virtual_cam.close()
                self.virtual_cam = None
            self.is_streaming = False
            print("Virtual camera stream stopped.")


class Camera:
    ASCII_CHARS = "@%#*+=-:. "  # Characters from dark to light

    def __init__(self, camera_index=0):
        """
        Initialize camera with specific index.
        
        Args:
            camera_index: Index of the camera to use (default: 0)
        """
        self.camera_index = camera_index
        self.camera = cv2.VideoCapture(camera_index)
        if not self.camera.isOpened():
            raise Exception(f"Cannot open camera at index {camera_index}")
        
        # Get camera info
        width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"Camera {camera_index} opened: {width}x{height}")
        
        self.virtual_streamer = None
        self.camera_lock = threading.Lock()

    def get_image(self):
        with self.camera_lock:
            ret, frame = self.camera.read()
            if not ret:
                raise Exception("Can't receive frame.")
            return frame
        if not ret:
            raise Exception("Can't receive frame.")
        return frame

    def resize_image(self, image, new_width=100):
        height, width = image.shape
        ratio = height / width
        new_height = int(new_width * ratio * 0.55)  # Adjust height ratio for ASCII
        resized_image = cv2.resize(image, (new_width, new_height))
        return resized_image

    def grayify(self, image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def pixels_to_ascii(self, image):
        ascii_str = ""
        for pixel_row in image:
            for pixel in pixel_row:
                pixel_val = int(pixel)
                ascii_str += self.ASCII_CHARS[pixel_val * len(self.ASCII_CHARS) // 256]
            ascii_str += "\n"
        return ascii_str

    def get_ascii_camera(self, width=200):
        image = self.get_image()
        gray_image = self.grayify(image)
        resized_image = self.resize_image(gray_image, new_width=width)
        ascii_art = self.pixels_to_ascii(resized_image)
        return ascii_art
    
    def start_virtual_stream(self, width=200, fps=30, camera_name="ASCII Camera"):
        """
        Start streaming ASCII to virtual camera.
        
        Args:
            width: Width of ASCII art in characters
            fps: Frames per second for virtual camera
            camera_name: Name of the virtual camera device
        """
        if not VIRTUAL_CAM_AVAILABLE:
            raise RuntimeError("pyvirtualcam is not installed. Cannot start virtual camera stream.")
        
        if self.virtual_streamer is None:
            self.virtual_streamer = VirtualCameraStreamer(self, width=width, fps=fps, camera_name=camera_name)
        
        self.virtual_streamer.start_streaming()
        
    def stop_virtual_stream(self):
        """Stop streaming ASCII to virtual camera."""
        if self.virtual_streamer:
            self.virtual_streamer.stop_streaming()
            
    def is_streaming(self):
        """Check if virtual camera is currently streaming."""
        if self.virtual_streamer:
            return self.virtual_streamer.is_streaming
        return False

# Example usage:
if __name__ == "__main__":
    cam = Camera()
    try:
        # Test regular ASCII output
        print("Testing regular ASCII output (press Ctrl+C to stop):")
        for i in range(5):
            ascii_frame = cam.get_ascii_camera()
            print(ascii_frame)
            time.sleep(0.5)
        
        # Test virtual camera streaming
        if VIRTUAL_CAM_AVAILABLE:
            print("\nStarting virtual camera stream...")
            cam.start_virtual_stream(width=100, fps=15)
            print("Streaming for 10 seconds...")
            time.sleep(10)
            cam.stop_virtual_stream()
            print("Stopped virtual camera stream.")
        else:
            print("\nVirtual camera streaming not available (pyvirtualcam not installed)")
            
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        cam.stop_virtual_stream()
        cam.camera.release()
        cv2.destroyAllWindows()
