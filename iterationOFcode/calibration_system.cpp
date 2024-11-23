// # Create a Makefile
// g++ -o sign_language_system main.cpp sign_language_hand.cpp calibration_system.cpp -I.

// Calibrate a specific letter
// ./sign_language_system calibrate A

// # Run the calibration wizard for all letters
// ./sign_language_system wizard

// # Display a calibrated letter
// ./sign_language_system display A

// --------------------------------------------------------------------------

// // Example of calibrating letter 'A'
// ./sign_language_system calibrate A

// > Calibrating letter A
// > Current finger: Thumb (0)
// > Position: 263
// > Controls:
// >   w/s - Small adjust up/down
// >   a/d - Large adjust up/down
// >   n - Next finger
// >   p - Previous finger
// >   q - Save and quit

// The calibration file (calibration.conf) looks like:

// (Format: {thumb, index, middle, ring, pinky})
// A,263,150,150,150,150
// B,150,375,375,375,375
// C,263,263,263,263,263


// --------------------------------------------------------------------------

// calibration_tool.cpp
#include <iostream>
#include <fstream>
#include <vector>
#include <map>
#include <string>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>

class CalibrationTool {
private:
    int i2c_fd;
    static constexpr int I2C_ADDR = 0x40;
    static constexpr const char* I2C_DEVICE = "/dev/i2c-1";
    static constexpr const char* CALIBRATION_FILE = "calibration.conf";
    
    // Servo position limits
    static constexpr int FINGER_STRAIGHT = 375;
    static constexpr int FINGER_BENT = 150;
    
    std::map<char, std::vector<int>> letterCalibrations;

    void writeRegister(uint8_t reg, uint8_t value) {
        uint8_t buffer[2] = {reg, value};
        write(i2c_fd, buffer, 2);
    }

    void setPWM(uint8_t channel, uint16_t off) {
        writeRegister(0x06 + 4 * channel, 0);
        writeRegister(0x07 + 4 * channel, 0);
        writeRegister(0x08 + 4 * channel, off & 0xFF);
        writeRegister(0x09 + 4 * channel, off >> 8);
    }

    void loadExistingCalibration() {
        std::ifstream file(CALIBRATION_FILE);
        if (!file.is_open()) {
            std::cout << "No existing calibration file found. Starting fresh.\n";
            return;
        }

        std::string line;
        while (std::getline(file, line)) {
            if (line.empty()) continue;
            
            std::vector<int> positions;
            char letter = line[0];
            size_t pos = 2;  // Skip letter and first comma
            
            for (int i = 0; i < 5; i++) {
                size_t next = line.find(',', pos);
                if (next == std::string::npos) next = line.length();
                positions.push_back(std::stoi(line.substr(pos, next - pos)));
                pos = next + 1;
            }
            
            letterCalibrations[letter] = positions;
        }
        std::cout << "Loaded existing calibrations for " << letterCalibrations.size() << " letters\n";
    }

    void saveCalibration() {
        std::ofstream file(CALIBRATION_FILE);
        if (!file.is_open()) {
            throw std::runtime_error("Unable to save calibration file");
        }

        for (const auto& [letter, positions] : letterCalibrations) {
            file << letter;
            for (int pos : positions) {
                file << "," << pos;
            }
            file << "\n";
        }
        std::cout << "Calibration saved to " << CALIBRATION_FILE << "\n";
    }

    void displayMenu() {
        std::cout << "\nControls:"
                  << "\nw/s - Increase/decrease position by 5"
                  << "\na/d - Increase/decrease position by 25"
                  << "\nn - Next finger"
                  << "\np - Previous finger"
                  << "\nr - Reset to straight position"
                  << "\nv - View current letter"
                  << "\nq - Save and quit\n" << std::endl;
    }

    void resetHand() {
        for (int i = 0; i < 5; i++) {
            setPWM(i, FINGER_STRAIGHT);
            usleep(100000);
        }
    }

public:
    CalibrationTool() {
        // Initialize I2C
        i2c_fd = open(I2C_DEVICE, O_RDWR);
        if (i2c_fd < 0) throw std::runtime_error("Failed to open I2C device");
        
        if (ioctl(i2c_fd, I2C_SLAVE, I2C_ADDR) < 0) {
            close(i2c_fd);
            throw std::runtime_error("Failed to acquire bus access");
        }

        // Initialize PCA9685
        writeRegister(0x00, 0x00);  // Mode 1 register
        usleep(5000);
        
        // Set frequency to 50Hz
        writeRegister(0xFE, 121);  // Prescale for 50Hz
        usleep(5000);

        loadExistingCalibration();
        resetHand();
    }

    void calibrateLetter(char letter) {
        letter = toupper(letter);
        std::vector<int>& positions = letterCalibrations[letter];
        
        // Initialize positions if not exist
        if (positions.empty()) {
            positions = std::vector<int>(5, FINGER_STRAIGHT);
        }

        int currentFinger = 0;
        displayMenu();

        while (true) {
            std::cout << "\nCalibrating letter " << letter 
                      << " - Finger " << currentFinger 
                      << " (Position: " << positions[currentFinger] << ")\n";
            
            char cmd;
            std::cout << "Command: ";
            std::cin >> cmd;

            switch (cmd) {
                case 'w':
                    positions[currentFinger] = std::min(positions[currentFinger] + 5, FINGER_STRAIGHT);
                    break;
                case 's':
                    positions[currentFinger] = std::max(positions[currentFinger] - 5, FINGER_BENT);
                    break;
                case 'a':
                    positions[currentFinger] = std::min(positions[currentFinger] + 25, FINGER_STRAIGHT);
                    break;
                case 'd':
                    positions[currentFinger] = std::max(positions[currentFinger] - 25, FINGER_BENT);
                    break;
                case 'n':
                    if (currentFinger < 4) currentFinger++;
                    break;
                case 'p':
                    if (currentFinger > 0) currentFinger--;
                    break;
                case 'r':
                    positions[currentFinger] = FINGER_STRAIGHT;
                    break;
                case 'v':
                    // Show full letter position
                    for (int i = 0; i < 5; i++) {
                        setPWM(i, positions[i]);
                        usleep(100000);
                    }
                    continue;
                case 'q':
                    saveCalibration();
                    return;
            }
            
            // Update servo position
            setPWM(currentFinger, positions[currentFinger]);
        }
    }

    ~CalibrationTool() {
        resetHand();
        if (i2c_fd >= 0) close(i2c_fd);
    }
};

int main(int argc, char* argv[]) {
    try {
        CalibrationTool calibrator;
        
        if (argc != 2) {
            std::cout << "Usage: " << argv[0] << " <letter>\n";
            return 1;
        }

        calibrator.calibrateLetter(argv[1][0]);
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
}