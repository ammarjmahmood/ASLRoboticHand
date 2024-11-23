import smbus
import time
import sys
import termios
import tty
import threading
from pynput import keyboard

class RoboticHand:
    def __init__(self):
        # PCA9685 setup
        self.bus = smbus.SMBus(1)
        self.I2C_ADDR = 0x40
        
        # Servo positions
        self.STRAIGHT = 375
        self.BENT = 150
        
        # Initialize controller
        self.init_controller()
        
        # Track positions and active keys
        self.positions = [self.STRAIGHT] * 5
        self.pressed_keys = set()
        
        # Movement step
        self.step = 10
        
        # Threading lock for I2C access
        self.lock = threading.Lock()

    def init_controller(self):
        """Initialize the PCA9685"""
        with self.lock:
            self.bus.write_byte_data(self.I2C_ADDR, 0x00, 0x00)
            time.sleep(0.05)
            
            prescale = int(25000000.0 / 4096.0 / 50.0 - 1)
            old_mode = self.bus.read_byte_data(self.I2C_ADDR, 0x00)
            self.bus.write_byte_data(self.I2C_ADDR, 0x00, (old_mode & 0x7F) | 0x10)
            self.bus.write_byte_data(self.I2C_ADDR, 0xFE, prescale)
            self.bus.write_byte_data(self.I2C_ADDR, 0x00, old_mode)
            time.sleep(0.05)
            self.bus.write_byte_data(self.I2C_ADDR, 0x00, old_mode | 0x80)

    def move_servo(self, channel, value):
        """Move a servo to a position"""
        value = max(self.BENT, min(self.STRAIGHT, value))
        channel = 4 * channel
        
        with self.lock:
            self.bus.write_byte_data(self.I2C_ADDR, 0x06 + channel, 0)
            self.bus.write_byte_data(self.I2C_ADDR, 0x07 + channel, 0)
            self.bus.write_byte_data(self.I2C_ADDR, 0x08 + channel, value & 0xFF)
            self.bus.write_byte_data(self.I2C_ADDR, 0x09 + channel, value >> 8)

    def reset_all(self):
        """Reset all fingers to straight position"""
        for i in range(5):
            self.positions[i] = self.STRAIGHT
            self.move_servo(i, self.STRAIGHT)
            time.sleep(0.1)

    def on_press(self, key):
        """Handle key press events"""
        try:
            # Convert key to string if it's a character
            k = key.char if hasattr(key, 'char') else str(key)
            self.pressed_keys.add(k)
        except AttributeError:
            pass

    def on_release(self, key):
        """Handle key release events"""
        try:
            # Remove released key from set
            k = key.char if hasattr(key, 'char') else str(key)
            self.pressed_keys.discard(k)
        except AttributeError:
            pass
        
        # Stop if 'esc' is pressed
        if key == keyboard.Key.esc:
            return False

def print_instructions():
    print("\nRobotic Hand Multi-Finger Control")
    print("================================")
    print("Thumb  controls: Q/A - up/down")
    print("Index  controls: W/S - up/down")
    print("Middle controls: E/D - up/down")
    print("Ring   controls: R/F - up/down")
    print("Pinky  controls: T/G - up/down")
    print("Space: Reset all fingers")
    print("ESC: Quit")
    print("\nYou can press multiple keys simultaneously!")

def main():
    hand = RoboticHand()
    print_instructions()

    # Start keyboard listener
    listener = keyboard.Listener(
        on_press=hand.on_press,
        on_release=hand.on_release)
    listener.start()

    # Main control loop
    try:
        while listener.is_alive():
            # Process all currently pressed keys
            for key in hand.pressed_keys.copy():  # Use copy to avoid modification during iteration
                if key in 'qwert':  # Up movements
                    finger = {'q': 0, 'w': 1, 'e': 2, 'r': 3, 't': 4}[key]
                    hand.positions[finger] = min(hand.STRAIGHT, hand.positions[finger] + hand.step)
                    hand.move_servo(finger, hand.positions[finger])
                
                elif key in 'asdfg':  # Down movements
                    finger = {'a': 0, 's': 1, 'd': 2, 'f': 3, 'g': 4}[key]
                    hand.positions[finger] = max(hand.BENT, hand.positions[finger] - hand.step)
                    hand.move_servo(finger, hand.positions[finger])
                
                elif key == 'space':
                    hand.reset_all()

            time.sleep(0.01)  # Small delay to prevent CPU overuse

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up
        hand.reset_all()
        listener.stop()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)