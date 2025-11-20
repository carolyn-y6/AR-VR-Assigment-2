import serial
import re
import time
from collections import deque

# Configuration
PORT = 'COM3'
BAUDRATE = 115200
BUFFER_SIZE = 50

# Data buffer for smoothing
data_buffer = deque(maxlen=BUFFER_SIZE)

# Pattern to match: Y:45.2,P:10.5,R:-2.1
pattern = re.compile(r'Y:([-\d.]+),P:([-\d.]+),R:([-\d.]+)')

# Serial connection
ser = None

def connect():
    """Establish serial connection to Arduino"""
    global ser
    try:
        print(f"Connecting to {PORT} at {BAUDRATE} baud...")
        ser = serial.Serial(PORT, BAUDRATE, timeout=1.0)
        time.sleep(2)  # Wait for connection to stabilize
        if ser.in_waiting:
            ser.reset_input_buffer()  # Clear stale data
        print("Connected successfully!")
        return True
    except serial.SerialException as e:
        print(f"Connection error: {e}")
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
            else:
                print(f"Warning: Data out of range - Y:{yaw}, P:{pitch}, R:{roll}")
                return None
        return None
    except ValueError as e:
        print(f"Parse error: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_smoothed_data():
    """Get smoothed data from buffer"""
    if len(data_buffer) == 0:
        return None
    
    avg_yaw = sum(d[0] for d in data_buffer) / len(data_buffer)
    avg_pitch = sum(d[1] for d in data_buffer) / len(data_buffer)
    avg_roll = sum(d[2] for d in data_buffer) / len(data_buffer)
    
    return (avg_yaw, avg_pitch, avg_roll)

def read_loop():
    """Main reading loop"""
    if not ser or not ser.is_open:
        print("Not connected!")
        return
    
    print("Reading data... (Press Ctrl+C to stop)")
    print("-" * 40)
    
    try:
        while True:
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    data = parse_data(line)
                    
                    if data:
                        # Add to buffer
                        data_buffer.append(data)
                        
                        # Get smoothed data
                        smoothed = get_smoothed_data()
                        if smoothed:
                            yaw, pitch, roll = smoothed
                            print(f"Y:{yaw:.1f}, P:{pitch:.1f}, R:{roll:.1f}")
                            
                except serial.SerialException as e:
                    print(f"Read error: {e}")
                    break
                except Exception as e:
                    print(f"Error: {e}")
            
            time.sleep(0.01)  # Small delay
            
    except KeyboardInterrupt:
        print("\nStopped by user")
    finally:
        if ser and ser.is_open:
            ser.close()
            print("Disconnected")

if __name__ == '__main__':
    if connect():
        read_loop()
    else:
        print("Failed to connect. Exiting.")
