
#include <iostream>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>
#include <cstring>
#include <stdexcept>

class PCA9685 {
private:
    int i2c_fd;
    static constexpr int I2C_ADDR = 0x40;
    static constexpr const char* I2C_DEVICE = "/dev/i2c-1";  // Using bus 1 where we found the device
    
    // PCA9685 registers
    static constexpr uint8_t MODE1 = 0x00;
    static constexpr uint8_t PRESCALE = 0xFE;
    static constexpr uint8_t LED0_ON_L = 0x06;
    
    // Servo pulse lengths
    static constexpr int PULSE_0_DEG = 375;    // Pulse length for 0 degrees
    static constexpr int PULSE_90_LEFT = 150;  // Pulse length for 90 degrees left

    bool writeRegister(uint8_t reg, uint8_t value) {
        uint8_t buffer[2] = {reg, value};
        if (write(i2c_fd, buffer, 2) != 2) {
            std::cerr << "Failed to write to register 0x" << std::hex << (int)reg 
                     << " with value 0x" << (int)value << std::endl;
            return false;
        }
        return true;
    }

    uint8_t readRegister(uint8_t reg) {
        uint8_t value;
        write(i2c_fd, &reg, 1);
        read(i2c_fd, &value, 1);
        return value;
    }

public:
    PCA9685() {
        std::cout << "Opening I2C device " << I2C_DEVICE << "..." << std::endl;
        i2c_fd = open(I2C_DEVICE, O_RDWR);
        if (i2c_fd < 0) {
            throw std::runtime_error("Failed to open I2C device");
        }

        std::cout << "Setting I2C slave address to 0x" << std::hex << I2C_ADDR << "..." << std::endl;
        if (ioctl(i2c_fd, I2C_SLAVE, I2C_ADDR) < 0) {
            close(i2c_fd);
            throw std::runtime_error("Failed to acquire bus access/talk to slave");
        }

        // Initialize PCA9685
        std::cout << "Initializing PCA9685..." << std::endl;
        
        // Reset the device
        writeRegister(MODE1, 0x00);  // Normal mode
        usleep(5000);  // Wait for oscillator

        std::cout << "Setting frequency to 50Hz..." << std::endl;
        setFrequency(50);  // 50Hz for servos
        
        std::cout << "Initialization complete." << std::endl;
    }

    void setFrequency(float freq) {
        float prescaleval = 25000000.0;    // 25MHz
        prescaleval /= 4096.0;             // 12-bit
        prescaleval /= freq;
        prescaleval -= 1.0;

        uint8_t prescale = static_cast<uint8_t>(prescaleval + 0.5);
        
        uint8_t oldmode = readRegister(MODE1);
        uint8_t newmode = (oldmode & 0x7F) | 0x10;    // Sleep
        
        std::cout << "Setting prescale value to " << (int)prescale << " for " << freq << "Hz" << std::endl;

        writeRegister(MODE1, newmode);        // Go to sleep
        writeRegister(PRESCALE, prescale);    // Set prescale
        writeRegister(MODE1, oldmode);        // Restore old mode
        
        usleep(5000);
        writeRegister(MODE1, oldmode | 0x80); // Restart
    }

    void setPWM(uint8_t channel, uint16_t on, uint16_t off) {
        std::cout << "Setting channel " << (int)channel << " to on=" << on << ", off=" << off << std::endl;
        writeRegister(LED0_ON_L + 4 * channel, on & 0xFF);
        writeRegister(LED0_ON_L + 4 * channel + 1, on >> 8);
        writeRegister(LED0_ON_L + 4 * channel + 2, off & 0xFF);
        writeRegister(LED0_ON_L + 4 * channel + 3, off >> 8);
    }

    // Simple test sequence
    void testSequence() {
        std::cout << "\nRunning test sequence on first servo..." << std::endl;
        
        // Center position
        std::cout << "Moving to center position..." << std::endl;
        setPWM(0, 0, PULSE_0_DEG);
        sleep(2);
        
        // Left position
        std::cout << "Moving to left position..." << std::endl;
        setPWM(0, 0, PULSE_90_LEFT);
        sleep(2);
        
        // Back to center
        std::cout << "Returning to center..." << std::endl;
        setPWM(0, 0, PULSE_0_DEG);
        sleep(2);
        
        std::cout << "Test sequence complete.\n" << std::endl;
    }

    void runFullSequence() {
        std::cout << "Starting full sequence..." << std::endl;
        
        while (true) {
            // One
            std::cout << "\nOne - Only Index up" << std::endl;
            setPWM(0, 0, PULSE_90_LEFT);  // Thumb down
            setPWM(1, 0, PULSE_0_DEG);    // Index up
            setPWM(2, 0, PULSE_90_LEFT);  // Middle down
            setPWM(3, 0, PULSE_90_LEFT);  // Ring down
            setPWM(4, 0, PULSE_90_LEFT);  // Pinky down
            sleep(1);

            // Two
            std::cout << "Two - Index and Middle up" << std::endl;
            setPWM(0, 0, PULSE_90_LEFT);  // Thumb down
            setPWM(1, 0, PULSE_0_DEG);    // Index up
            setPWM(2, 0, PULSE_0_DEG);    // Middle up
            setPWM(3, 0, PULSE_90_LEFT);  // Ring down
            setPWM(4, 0, PULSE_90_LEFT);  // Pinky down
            sleep(1);

            // Three
            std::cout << "Three - Index, Middle, and Ring up" << std::endl;
            setPWM(0, 0, PULSE_90_LEFT);  // Thumb down
            setPWM(1, 0, PULSE_0_DEG);    // Index up
            setPWM(2, 0, PULSE_0_DEG);    // Middle up
            setPWM(3, 0, PULSE_0_DEG);    // Ring up
            setPWM(4, 0, PULSE_90_LEFT);  // Pinky down
            sleep(1);

            // Four
            std::cout << "Four - All fingers up except Thumb" << std::endl;
            setPWM(0, 0, PULSE_90_LEFT);  // Thumb down
            setPWM(1, 0, PULSE_0_DEG);    // Index up
            setPWM(2, 0, PULSE_0_DEG);    // Middle up
            setPWM(3, 0, PULSE_0_DEG);    // Ring up
            setPWM(4, 0, PULSE_0_DEG);    // Pinky up
            sleep(2);

            // Reset
            std::cout << "Reset position" << std::endl;
            for (int i = 0; i < 5; i++) {
                setPWM(i, 0, PULSE_0_DEG);
            }
            sleep(2);
        }
    }

    ~PCA9685() {
        if (i2c_fd >= 0) {
            close(i2c_fd);
        }
    }
};

int main() {
    try {
        std::cout << "Starting PCA9685 servo control program..." << std::endl;
        PCA9685 controller;
        
        // Run test sequence first
        controller.testSequence();
        
        // If test successful, run full sequence
        controller.runFullSequence();
        
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
    return 0;
}