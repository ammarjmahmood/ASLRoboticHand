#include <iostream>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>
#include <cstring>
#include <stdexcept>
#include <map>
#include <vector>
#include <string>
#include <fstream>
#include <sstream>
#include <filesystem>

class SignLanguageHand {
private:
    int i2c_fd;
    static constexpr int I2C_ADDR = 0x40;
    static constexpr const char* I2C_DEVICE = "/dev/i2c-1";
    static constexpr const char* CALIBRATION_FILE = "calibration.conf";
    
    // PCA9685 registers
    static constexpr uint8_t MODE1 = 0x00;
    static constexpr uint8_t PRESCALE = 0xFE;
    static constexpr uint8_t LED0_ON_L = 0x06;
    
    // Servo position constants
    static constexpr int FINGER_STRAIGHT = 375;  // Fully extended (0 degrees)
    static constexpr int FINGER_BENT = 150;      // Fully bent (90 degrees)
    static constexpr int FINGER_SLIGHT_BEND = 340;  // Just slightly bent
    static constexpr int FINGER_HALF_BENT = 263;    // Half way bent
    static constexpr int FINGER_MOSTLY_BENT = 190;  // Most of the way bent

    struct FingerPosition {
        std::vector<int> positions;
        std::string description;
        FingerPosition(std::vector<int> pos, std::string desc) 
            : positions(pos), description(desc) {}
        FingerPosition() {} // Default constructor
    };
    
    std::map<char, FingerPosition> letterConfigs;

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

    void initializeLetterConfigs() {
        // Your existing initializeLetterConfigs code stays exactly the same
        // ... (keep all the letterConfigs['A'] through letterConfigs['Y'] exactly as they are)
    }

    void loadCalibrationFile() {
        std::ifstream file(CALIBRATION_FILE);
        if (!file.is_open()) {
            std::cout << "No calibration file found, using default positions\n";
            return;
        }

        int calibratedCount = 0;
        std::string line;
        while (std::getline(file, line)) {
            if (line.empty()) continue;
            
            std::vector<int> positions;
            char letter = toupper(line[0]);
            size_t pos = 2;  // Skip letter and first comma
            
            bool validPositions = true;
            // Parse positions
            for (int i = 0; i < 5; i++) {
                size_t next = line.find(',', pos);
                if (next == std::string::npos) next = line.length();
                
                try {
                    int position = std::stoi(line.substr(pos, next - pos));
                    
                    // Validate position is within bounds
                    if (position >= FINGER_BENT && position <= FINGER_STRAIGHT) {
                        positions.push_back(position);
                    } else {
                        std::cout << "Warning: Invalid position value for letter " << letter 
                                 << " finger " << i << ": " << position 
                                 << " (must be between " << FINGER_BENT 
                                 << " and " << FINGER_STRAIGHT << ")\n";
                        validPositions = false;
                        break;
                    }
                } catch (...) {
                    std::cout << "Warning: Invalid calibration data format for letter " 
                             << letter << ", using default position\n";
                    validPositions = false;
                    break;
                }
                
                pos = next + 1;
            }
            
            // Only update if we got all 5 valid positions
            if (validPositions && positions.size() == 5) {
                auto it = letterConfigs.find(letter);
                if (it != letterConfigs.end()) {
                    // Keep the description but update positions
                    std::string desc = it->second.description;
                    letterConfigs[letter] = FingerPosition(positions, desc);
                    calibratedCount++;
                    std::cout << "Loaded calibrated positions for letter " << letter << std::endl;
                }
            }
        }
        
        std::cout << "Loaded " << calibratedCount << " calibrated letter positions\n";
    }

public:
    SignLanguageHand() {
        std::cout << "Initializing Sign Language Hand..." << std::endl;
        
        // Open I2C device
        i2c_fd = open(I2C_DEVICE, O_RDWR);
        if (i2c_fd < 0) {
            throw std::runtime_error("Failed to open I2C device");
        }

        // Set I2C slave address
        if (ioctl(i2c_fd, I2C_SLAVE, I2C_ADDR) < 0) {
            close(i2c_fd);
            throw std::runtime_error("Failed to acquire bus access/talk to slave");
        }

        // Initialize PCA9685
        writeRegister(MODE1, 0x00);
        usleep(5000);
        setFrequency(50);  // 50Hz for servos
        
        // Initialize letter configurations
        initializeLetterConfigs();
        
        // Load calibration file if it exists
        loadCalibrationFile();
        
        // Move to rest position
        resetPosition();
    }

    void setFrequency(float freq) {
        float prescaleval = 25000000.0;    // 25MHz
        prescaleval /= 4096.0;             // 12-bit
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

    bool isLetterCalibrated(char letter) {
        std::ifstream file(CALIBRATION_FILE);
        if (!file.is_open()) return false;

        std::string line;
        while (std::getline(file, line)) {
            if (!line.empty() && toupper(line[0]) == toupper(letter)) {
                return true;
            }
        }
        return false;
    }

    void displayLetter(char letter) {
        letter = toupper(letter);
        
        if (letterConfigs.find(letter) == letterConfigs.end()) {
            throw std::runtime_error("Letter configuration not found: " + std::string(1, letter));
        }

        const auto& config = letterConfigs[letter];
        std::cout << "Displaying letter " << letter << ": " << config.description;
        
        if (isLetterCalibrated(letter)) {
            std::cout << " (Using calibrated position)";
        } else {
            std::cout << " (Using default position)";
        }
        std::cout << std::endl;
        
        // Print the actual positions being used
        std::cout << "Finger positions: ";
        for (int i = 0; i < 5; i++) {
            std::cout << config.positions[i];
            if (i < 4) std::cout << ", ";
        }
        std::cout << std::endl;
        
        for (int finger = 0; finger < 5; finger++) {
            setPWM(finger, 0, config.positions[finger]);
            usleep(100000);  // Small delay between finger movements
        }
    }

    void resetPosition() {
        std::cout << "Resetting to rest position..." << std::endl;
        for (int finger = 0; finger < 5; finger++) {
            setPWM(finger, 0, FINGER_STRAIGHT);
            usleep(100000);
        }
    }

    void testSequence() {
        std::cout << "Running test sequence..." << std::endl;
        
        // Test each finger individually
        for (int finger = 0; finger < 5; finger++) {
            std::cout << "Testing finger " << finger << std::endl;
            setPWM(finger, 0, FINGER_BENT);
            sleep(1);
            setPWM(finger, 0, FINGER_STRAIGHT);
            sleep(1);
        }
        
        // Test a few letters
        const std::vector<char> testLetters = {'A', 'B', 'C'};
        for (char letter : testLetters) {
            std::cout << "Testing letter: " << letter << std::endl;
            displayLetter(letter);
            sleep(2);
        }
        
        resetPosition();
    }

    ~SignLanguageHand() {
        resetPosition();
        if (i2c_fd >= 0) {
            close(i2c_fd);
        }
    }
};

int main(int argc, char* argv[]) {
    try {
        SignLanguageHand hand;
        
        if (argc == 1) {
            // No arguments - run test sequence
            hand.testSequence();
        } else if (argc == 2) {
            // Single letter argument
            hand.displayLetter(argv[1][0]);
        } else {
            std::cerr << "Usage: " << argv[0] << " [letter]" << std::endl;
            return 1;
        }
        
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
}