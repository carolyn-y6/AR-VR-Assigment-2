import serial
import re
import time
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
from collections import deque
import math

# Configuration
PORT = 'COM3'  # Change to your Arduino port
BAUDRATE = 115200
BUFFER_SIZE = 10  # Smaller buffer for smoother real-time visualization
TARGET_FPS = 60
FRAME_TIME = 1.0 / TARGET_FPS

# Data buffer for smoothing
data_buffer = deque(maxlen=BUFFER_SIZE)

# Pattern to match: Y:45.2,P:10.5,R:-2.1
pattern = re.compile(r'Y:([-\d.]+),P:([-\d.]+),R:([-\d.]+)')

# Serial connection
ser = None

# Current orientation data (yaw, pitch, roll in degrees)
current_yaw = 0.0
current_pitch = 0.0
current_roll = 0.0

# Lock for thread-safe data access
import threading
data_lock = threading.Lock()

def connect():
    """Establish serial connection to Arduino"""
    global ser
    try:
        print(f"Connecting to {PORT} at {BAUDRATE} baud...")
        ser = serial.Serial(PORT, BAUDRATE, timeout=0.1)
        time.sleep(2)  # Wait for connection to stabilize
        
        # 清空所有旧数据
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        # 读取并丢弃初始的几行数据（可能是旧数据）
        for _ in range(10):
            if ser.in_waiting > 0:
                ser.readline()
            time.sleep(0.1)
        
        print("Connected successfully!")
        return True
    except serial.SerialException as e:
        print(f"Connection error: {e}")
        print("Make sure Arduino IDE Serial Monitor is closed!")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def parse_data(line):
    """Parse incoming data to extract Yaw, Pitch, Roll"""
    try:
        line = line.strip()
        match = pattern.match(line)
        if match:
            yaw = float(match.group(1))
            pitch = float(match.group(2))
            roll = float(match.group(3))
            
            # Data validation: check reasonable ranges
            if -180 <= yaw <= 180 and -90 <= pitch <= 90 and -180 <= roll <= 180:
                return (yaw, pitch, roll)
        return None
    except (ValueError, AttributeError):
        return None
    except Exception:
        return None

def read_serial_data():
    """Read data from serial port in background thread"""
    global current_yaw, current_pitch, current_roll, ser
    
    if not ser or not ser.is_open:
        return
    
    try:
        latest_data = None
        while ser.in_waiting > 0:
            try:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    data = parse_data(line)
                    if data:
                        latest_data = data
            except Exception:
                continue
        
        if latest_data:
            yaw, pitch, roll = latest_data
            # 添加到缓冲区进行平滑
            data_buffer.append(latest_data)
            
            # 计算平滑后的数据（平均值）
            if len(data_buffer) > 0:
                avg_yaw = sum(d[0] for d in data_buffer) / len(data_buffer)
                avg_pitch = sum(d[1] for d in data_buffer) / len(data_buffer)
                avg_roll = sum(d[2] for d in data_buffer) / len(data_buffer)
                
                with data_lock:
                    current_yaw = avg_yaw
                    current_pitch = avg_pitch
                    current_roll = avg_roll
    except Exception:
        pass  # Ignore read errors to keep animation smooth

def euler_to_rotation_matrix(yaw, pitch, roll):
    """
    Convert Euler angles (in degrees) to rotation matrix
    Order: Yaw (Y-axis) -> Pitch (X-axis) -> Roll (Z-axis)
    """
    # Convert to radians
    yaw_rad = math.radians(yaw)
    pitch_rad = math.radians(pitch)
    roll_rad = math.radians(roll)
    
    # Rotation matrices
    # Yaw rotation around Y-axis
    Ry = np.array([
        [np.cos(yaw_rad), 0, np.sin(yaw_rad)],
        [0, 1, 0],
        [-np.sin(yaw_rad), 0, np.cos(yaw_rad)]
    ])
    
    # Pitch rotation around X-axis
    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(pitch_rad), -np.sin(pitch_rad)],
        [0, np.sin(pitch_rad), np.cos(pitch_rad)]
    ])
    
    # Roll rotation around Z-axis
    Rz = np.array([
        [np.cos(roll_rad), -np.sin(roll_rad), 0],
        [np.sin(roll_rad), np.cos(roll_rad), 0],
        [0, 0, 1]
    ])
    
    # Combined rotation: R = Rz * Rx * Ry
    R = Rz @ Rx @ Ry
    return R

def create_cube():
    """Create a wireframe cube centered at origin"""
    # Cube vertices (centered at origin, size 2)
    vertices = np.array([
        [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],  # Bottom face
        [-1, -1,  1], [1, -1,  1], [1, 1,  1], [-1, 1,  1]   # Top face
    ])
    
    # Cube edges (connections between vertices)
    edges = [
        [0, 1], [1, 2], [2, 3], [3, 0],  # Bottom face
        [4, 5], [5, 6], [6, 7], [7, 4],  # Top face
        [0, 4], [1, 5], [2, 6], [3, 7]   # Vertical edges
    ]
    
    return vertices, edges

def update_cube(frame):
    """Update function for animation"""
    global current_yaw, current_pitch, current_roll
    
    # Read serial data
    read_serial_data()
    
    # Get current orientation
    with data_lock:
        yaw = current_yaw
        pitch = current_pitch
        roll = current_roll
    
    # Clear previous plot
    ax.clear()
    
    # Get cube vertices and edges
    vertices, edges = create_cube()
    
    # Apply rotation
    R = euler_to_rotation_matrix(yaw, pitch, roll)
    rotated_vertices = vertices @ R.T
    
    # Draw cube edges
    for edge in edges:
        points = rotated_vertices[edge]
        ax.plot3D(*points.T, 'c-', linewidth=2)
    
    # Draw vertices
    ax.scatter(*rotated_vertices.T, c='c', s=50)
    
    # Set axis properties
    ax.set_xlim([-2, 2])
    ax.set_ylim([-2, 2])
    ax.set_zlim([-2, 2])
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(f'3D Cube Rotation\nYaw: {yaw:.1f}° | Pitch: {pitch:.1f}° | Roll: {roll:.1f}°', y=1.05)
    
    # Set equal aspect ratio
    ax.set_box_aspect([1, 1, 1])
    
    return ax

def main():
    """Main function"""
    global ax, ser
    
    # Connect to Arduino
    if not connect():
        print("Failed to connect. Exiting.")
        return
    
    # Create figure and 3D axis
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Set initial view
    ax.view_init(elev=20, azim=45)
    
    print("Starting visualization...")
    print("Rotate your Arduino to see the cube rotate!")
    print("Press Ctrl+C to stop")
    
    try:
        # Create animation
        # interval in milliseconds for ~30 FPS
        anim = FuncAnimation(fig, update_cube, interval=int(FRAME_TIME * 1000), 
                           blit=False, cache_frame_data=False)
        
        # Show plot
        plt.tight_layout()
        plt.show()
        
    except KeyboardInterrupt:
        print("\nStopped by user")
    finally:
        if ser and ser.is_open:
            ser.close()
            print("Disconnected from Arduino")

if __name__ == '__main__':
    main()

