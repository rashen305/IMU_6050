import serial
import time
import csv

# Configure the serial connection
port = 'COM6'  # Change this to your Arduino's COM port
baud_rate = 9600  # Match the Serial.begin rate in your Arduino code

try:
    # Open serial port
    ser = serial.Serial(port, baud_rate, timeout=2)
    print(f"Connected to {port} at {baud_rate} baud")
    time.sleep(2)  # Give Arduino time to reset
    
    # Send a character to activate the Arduino program
    print("Sending initialization character to Arduino...")
    ser.write(b'a')  # Send any character to start the Arduino program
    time.sleep(2)    # Give Arduino time to process and initialize
    
    # Create and open CSV file with headers
    csv_filename = 'imu_data.csv'
    with open(csv_filename, 'w', newline='') as csvfile:
        # Create CSV writer
        csv_writer = csv.writer(csvfile)
        
        # Write header
        csv_writer.writerow(['Time (ms)', 'Yaw', 'Pitch', 'Roll'])
        print(f"Recording data to {csv_filename}. Press Ctrl+C to stop...")
        
        # Start time for timestamps
        start_time = time.time()
        
        # Clear any initialization messages
        while ser.in_waiting:
            ser.readline()
        
        while True:
            try:
                # Read a line from serial
                raw_data = ser.readline()
                
                # Try to decode as string
                try:
                    line = raw_data.decode('utf-8').strip()
                    
                    print(f"Raw line: {line}")  # Debug output to see what's coming in
                    
                    # Check if line has expected format (ypr data)
                    if line.startswith('ypr'):
                        # Split the string into components
                        parts = line.split('\t')
                        
                        # Make sure we have all expected parts
                        if len(parts) == 4:  # 'ypr' and three values
                            yaw = float(parts[1])
                            pitch = float(parts[2])
                            roll = float(parts[3])
                            
                            # Current time in milliseconds
                            current_time = int((time.time() - start_time) * 1000)
                            
                            # Write to CSV
                            csv_writer.writerow([current_time, yaw, pitch, roll])
                            csvfile.flush()  # Ensure data is written immediately
                            
                            # Print to console
                            print(f"Time: {current_time}ms, Yaw: {yaw}, Pitch: {pitch}, Roll: {roll}")
                    
                except UnicodeDecodeError:
                    # If we can't decode as UTF-8, skip this line
                    print("Received malformed data, skipping...")
                
            except KeyboardInterrupt:
                print("\nRecording stopped by user")
                break
            except Exception as e:
                print(f"Error: {e}")
                # Continue instead of breaking to handle temporary errors
                continue

except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    print("Tips to fix:")
    print("1. Make sure the Arduino is connected to this computer")
    print("2. Check that no other program is using the port (like Arduino IDE Serial Monitor)")
    print("3. Verify the correct COM port number in Device Manager")
    print("4. Try restarting your Arduino")

finally:
    # Close the serial port if it's open
    if 'ser' in locals() and ser.is_open:
        print("Closing serial connection...")
        ser.close()
        print("Done")