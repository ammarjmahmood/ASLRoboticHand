#include <iostream>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>
#include <vector>
#include <string>
#include <sstream>
#include <stdexcept>

class RoboticHand {
private:
    int i2c_fd;
    static constexpr int I2C_ADDR = 0x40;
    static constexpr const char* I2C_DEVICE = "/dev/i2c-1";
    
    // PCA9685 registers
    static constexpr uint8_t MODE1 = 0x00;
    static constexpr uint8_t PRESCALE = 0xFE;
    static constexpr uint8_t LED0_ON_L = 0x06;

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
    RoboticHand() {
        i2c_fd = open(I2C_DEVICE, O_RDWR);
        if (i2c_fd < 0) {
            throw std::runtime_error("Failed to open I2C device");
        }

        if (ioctl(i2c_fd, I2C_SLAVE, I2C_ADDR) < 0) {
            close(i2c_fd);
            throw std::runtime_error("Failed to acquire bus access/talk to slave");
        }

        writeRegister(MODE1, 0x00);
        usleep(5000);
        setFrequency(50);
    }

    void setFrequency(float freq) {
        float prescaleval = 25000000.0;
        prescaleval /= 4096.0;
        prescaleval /= freq;
        prescaleval -= 1.0;

        uint8_t prescale = static_cast<uint8_t>(prescaleval + 0.5);
        uint8_t oldmode = readRegister(MODE1);
        uint8_t newmode = (oldmode & 0x7F) | 0x10;
        
        writeRegister(MODE1, newmode);
        writeRegister(PRESCALE, prescale);
        writeRegister(MODE1, oldmode);
        
        usleep(5000);
        writeRegister(MODE1, oldmode | 0x80);
    }

    void setPWM(uint8_t channel, uint16_t on, uint16_t off) {
        writeRegister(LED0_ON_L + 4 * channel, on & 0xFF);
        writeRegister(LED0_ON_L + 4 * channel + 1, on >> 8);
        writeRegister(LED0_ON_L + 4 * channel + 2, off & 0xFF);
        writeRegister(LED0_ON_L + 4 * channel + 3, off >> 8);
    }

    void setFingerPositions(const std::vector<int>& positions) {
        for (size_t finger = 0; finger < positions.size() && finger < 5; finger++) {
            setPWM(finger, 0, positions[finger]);
            usleep(10000);  // Reduced delay for smoother movement
        }
    }

    ~RoboticHand() {
        if (i2c_fd >= 0) {
            close(i2c_fd);
        }
    }
};

std::vector<int> parseServoValues(const std::string& input) {
    std::vector<int> values;
    std::stringstream ss(input);
    std::string value;
    
    while (std::getline(ss, value, ',')) {
        values.push_back(std::stoi(value));
    }
    
    return values;
}

int main(int argc, char* argv[]) {
    try {
        if (argc != 2) {
            std::cerr << "Usage: " << argv[0] << " servo_value1,servo_value2,servo_value3,servo_value4,servo_value5" << std::endl;
            return 1;
        }

        RoboticHand hand;
        std::vector<int> servo_values = parseServoValues(argv[1]);
        
        if (servo_values.size() != 5) {
            throw std::runtime_error("Expected 5 servo values");
        }

        hand.setFingerPositions(servo_values);
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
}