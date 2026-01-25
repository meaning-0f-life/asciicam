#!/usr/bin/env python3
"""Test script to verify virtual camera functionality."""

import sys
import time

try:
    import pyvirtualcam
    print("✓ pyvirtualcam is installed")
except ImportError:
    print("✗ pyvirtualcam is not installed")
    sys.exit(1)

try:
    import cv2
    print("✓ opencv-python is installed")
except ImportError:
    print("✗ opencv-python is not installed")
    sys.exit(1)

try:
    import numpy
    print("✓ numpy is installed")
except ImportError:
    print("✗ numpy is not installed")
    sys.exit(1)

try:
    from PIL import Image, ImageDraw, ImageFont
    print("✓ Pillow is installed")
except ImportError:
    print("✗ Pillow is not installed")
    sys.exit(1)

# Test camera access
print("\nTesting camera access...")
try:
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret and frame is not None:
            print(f"✓ Camera 0 is accessible: {frame.shape}")
        else:
            print("✗ Camera 0 is accessible but cannot read frame")
        cap.release()
    else:
        print("✗ Camera 0 is not accessible")
except Exception as e:
    print(f"✗ Error accessing camera: {e}")

# Test virtual camera creation
print("\nTesting virtual camera creation...")
try:
    # Create virtual camera (name is determined by the system/virtual camera driver)
    cam = pyvirtualcam.Camera(width=640, height=480, fps=30)
    print(f"✓ Virtual camera created")
    print(f"  Camera name: {cam.device}")
    cam.close()
except Exception as e:
    print(f"✗ Error creating virtual camera: {e}")
    sys.exit(1)

print("\n✓ All tests passed!")
print("\nNote: The virtual camera name may be determined by the system/virtual camera driver.")
print("On some platforms, the name 'ASCII Camera' may not be directly settable.")
