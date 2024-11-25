// handtest1someletters.cpp
#include <iostream>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>
#include <vector>
#include <stdexcept>
#include <string>

class SignLanguageHand {
private:
    int i2c_fd;
    static constexpr int I2C_ADDR = 0x40;
    static constexpr const char* I2C_DEVICE = "/dev/i2c-1";
    
    // PCA9685 registers
    static constexpr uint8_t MODE1 = 0x00;
    static constexpr uint8_t PRESCALE = 0xFE;
    static constexpr uint8_t LED0_ON_L = 0x06;
    
    // Servo position constants
    static constexpr int FINGER_STRAIGHT = 375;
    static constexpr int FINGER_BENT = 150;
    static constexpr int FINGER_SLIGHT_BEND = 340;
    static constexpr int FINGER_HALF_BENT = 263;
    static constexpr int FINGER_MOSTLY_BENT = 190;

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
    SignLanguageHand() {
        std::cout << "Initializing Sign Language Hand..." << std::endl;
        
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
        resetPosition();
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
        for (size_t finger = 0; finger < positions.size(); finger++) {
            setPWM(finger, 0, positions[finger]);
            usleep(100000);  // 100ms delay between finger movements
        }
    }

// Letters A through M
    void letterA() {
        std::cout << "Forming letter A..." << std::endl;
        std::vector<int> positions = {
            FINGER_HALF_BENT,  // Thumb
            FINGER_BENT,       // Index
            FINGER_BENT,       // Middle
            FINGER_BENT,       // Ring
            FINGER_BENT        // Pinky
        };
        setFingerPositions(positions);
    }

    void letterB() {
        std::cout << "Forming letter B..." << std::endl;
        std::vector<int> positions = {
            FINGER_BENT,       // Thumb
            FINGER_STRAIGHT,   // Index
            FINGER_STRAIGHT,   // Middle
            FINGER_STRAIGHT,   // Ring
            FINGER_STRAIGHT    // Pinky
        };
        setFingerPositions(positions);
    }

    void letterC() {
        std::cout << "Forming letter C..." << std::endl;
        std::vector<int> positions = {
            FINGER_HALF_BENT,   // Thumb
            FINGER_HALF_BENT,   // Index
            FINGER_HALF_BENT,   // Middle
            FINGER_HALF_BENT,   // Ring
            FINGER_HALF_BENT    // Pinky
        };
        setFingerPositions(positions);
    }

    void letterD() {
        std::cout << "Forming letter D..." << std::endl;
        std::vector<int> positions = {
            FINGER_HALF_BENT,   // Thumb
            FINGER_STRAIGHT,    // Index
            FINGER_BENT,        // Middle
            FINGER_BENT,        // Ring
            FINGER_BENT         // Pinky
        };
        setFingerPositions(positions);
    }

    void letterE() {
        std::cout << "Forming letter E..." << std::endl;
        std::vector<int> positions = {
            FINGER_BENT,        // Thumb
            FINGER_BENT,        // Index
            FINGER_BENT,        // Middle
            FINGER_BENT,        // Ring
            FINGER_BENT         // Pinky
        };
        setFingerPositions(positions);
    }

    void letterF() {
        std::cout << "Forming letter F..." << std::endl;
        std::vector<int> positions = {
            FINGER_HALF_BENT,    // Thumb
            FINGER_BENT,         // Index
            FINGER_STRAIGHT,     // Middle
            FINGER_STRAIGHT,     // Ring
            FINGER_STRAIGHT      // Pinky
        };
        setFingerPositions(positions);
    }

    void letterG() {
        std::cout << "Forming letter G..." << std::endl;
        std::vector<int> positions = {
            FINGER_STRAIGHT,     // Thumb
            FINGER_STRAIGHT,     // Index
            FINGER_BENT,         // Middle
            FINGER_BENT,         // Ring
            FINGER_BENT          // Pinky
        };
        setFingerPositions(positions);
    }

    void letterH() {
        std::cout << "Forming letter H..." << std::endl;
        std::vector<int> positions = {
            FINGER_STRAIGHT,     // Thumb
            FINGER_STRAIGHT,     // Index
            FINGER_STRAIGHT,     // Middle
            FINGER_BENT,         // Ring
            FINGER_BENT          // Pinky
        };
        setFingerPositions(positions);
    }

    void letterI() {
        std::cout << "Forming letter I..." << std::endl;
        std::vector<int> positions = {
            FINGER_BENT,         // Thumb
            FINGER_BENT,         // Index
            FINGER_BENT,         // Middle
            FINGER_BENT,         // Ring
            FINGER_STRAIGHT      // Pinky
        };
        setFingerPositions(positions);
    }

    void letterK() {
        std::cout << "Forming letter K..." << std::endl;
        std::vector<int> positions = {
            FINGER_STRAIGHT,     // Thumb
            FINGER_STRAIGHT,     // Index
            FINGER_STRAIGHT,     // Middle
            FINGER_BENT,         // Ring
            FINGER_BENT          // Pinky
        };
        setFingerPositions(positions);
    }

    void letterL() {
        std::cout << "Forming letter L..." << std::endl;
        std::vector<int> positions = {
            FINGER_STRAIGHT,     // Thumb
            FINGER_STRAIGHT,     // Index
            FINGER_BENT,         // Middle
            FINGER_BENT,         // Ring
            FINGER_BENT          // Pinky
        };
        setFingerPositions(positions);
    }

    void letterM() {
        std::cout << "Forming letter M..." << std::endl;
        std::vector<int> positions = {
            FINGER_BENT,         // Thumb
            FINGER_BENT,         // Index
            FINGER_BENT,         // Middle
            FINGER_BENT,         // Ring
            FINGER_BENT          // Pinky
        };
        setFingerPositions(positions);
    }
    void letterN() {
        std::cout << "Forming letter N..." << std::endl;
        std::vector<int> positions = {
            FINGER_BENT,         // Thumb
            FINGER_BENT,         // Index
            FINGER_BENT,         // Middle
            FINGER_BENT,         // Ring
            FINGER_BENT          // Pinky
        };
        setFingerPositions(positions);
    }

    void letterO() {
        std::cout << "Forming letter O..." << std::endl;
        std::vector<int> positions = {
            FINGER_HALF_BENT,    // Thumb
            FINGER_HALF_BENT,    // Index
            FINGER_HALF_BENT,    // Middle
            FINGER_HALF_BENT,    // Ring
            FINGER_HALF_BENT     // Pinky
        };
        setFingerPositions(positions);
    }

    void letterP() {
        std::cout << "Forming letter P..." << std::endl;
        std::vector<int> positions = {
            FINGER_STRAIGHT,     // Thumb
            FINGER_STRAIGHT,     // Index
            FINGER_STRAIGHT,     // Middle
            FINGER_BENT,         // Ring
            FINGER_BENT          // Pinky
        };
        setFingerPositions(positions);
    }

    void letterQ() {
        std::cout << "Forming letter Q..." << std::endl;
        std::vector<int> positions = {
            FINGER_STRAIGHT,     // Thumb
            FINGER_STRAIGHT,     // Index
            FINGER_BENT,         // Middle
            FINGER_BENT,         // Ring
            FINGER_BENT          // Pinky
        };
        setFingerPositions(positions);
    }

    void letterR() {
        std::cout << "Forming letter R..." << std::endl;
        std::vector<int> positions = {
            FINGER_BENT,         // Thumb
            FINGER_STRAIGHT,     // Index
            FINGER_STRAIGHT,     // Middle
            FINGER_BENT,         // Ring
            FINGER_BENT          // Pinky
        };
        setFingerPositions(positions);
    }

    void letterS() {
        std::cout << "Forming letter S..." << std::endl;
        std::vector<int> positions = {
            FINGER_HALF_BENT,    // Thumb
            FINGER_BENT,         // Index
            FINGER_BENT,         // Middle
            FINGER_BENT,         // Ring
            FINGER_BENT          // Pinky
        };
        setFingerPositions(positions);
    }

    void letterT() {
        std::cout << "Forming letter T..." << std::endl;
        std::vector<int> positions = {
            FINGER_HALF_BENT,    // Thumb
            FINGER_BENT,         // Index
            FINGER_BENT,         // Middle
            FINGER_BENT,         // Ring
            FINGER_BENT          // Pinky
        };
        setFingerPositions(positions);
    }

    void letterU() {
        std::cout << "Forming letter U..." << std::endl;
        std::vector<int> positions = {
            FINGER_BENT,         // Thumb
            FINGER_STRAIGHT,     // Index
            FINGER_STRAIGHT,     // Middle
            FINGER_BENT,         // Ring
            FINGER_BENT          // Pinky
        };
        setFingerPositions(positions);
    }

    void letterV() {
        std::cout << "Forming letter V..." << std::endl;
        std::vector<int> positions = {
            FINGER_BENT,         // Thumb
            FINGER_STRAIGHT,     // Index
            FINGER_STRAIGHT,     // Middle
            FINGER_BENT,         // Ring
            FINGER_BENT          // Pinky
        };
        setFingerPositions(positions);
    }

    void letterW() {
        std::cout << "Forming letter W..." << std::endl;
        std::vector<int> positions = {
            FINGER_BENT,         // Thumb
            FINGER_STRAIGHT,     // Index
            FINGER_STRAIGHT,     // Middle
            FINGER_STRAIGHT,     // Ring
            FINGER_BENT          // Pinky
        };
        setFingerPositions(positions);
    }

    void letterX() {
        std::cout << "Forming letter X..." << std::endl;
        std::vector<int> positions = {
            FINGER_BENT,         // Thumb
            FINGER_HALF_BENT,    // Index
            FINGER_BENT,         // Middle
            FINGER_BENT,         // Ring
            FINGER_BENT          // Pinky
        };
        setFingerPositions(positions);
    }

    void letterY() {
        std::cout << "Forming letter Y..." << std::endl;
        std::vector<int> positions = {
            FINGER_STRAIGHT,     // Thumb
            FINGER_BENT,         // Index
            FINGER_BENT,         // Middle
            FINGER_BENT,         // Ring
            FINGER_STRAIGHT      // Pinky
        };
        setFingerPositions(positions);
    }

    void displayLetter(char letter) {
        letter = toupper(letter);
        switch(letter) {
            case 'A': letterA(); break;
            case 'B': letterB(); break;
            case 'C': letterC(); break;
            case 'D': letterD(); break;
            case 'E': letterE(); break;
            case 'F': letterF(); break;
            case 'G': letterG(); break;
            case 'H': letterH(); break;
            case 'I': letterI(); break;
            case 'K': letterK(); break;
            case 'L': letterL(); break;
            case 'M': letterM(); break;
            case 'N': letterN(); break;
            case 'O': letterO(); break;
            case 'P': letterP(); break;
            case 'Q': letterQ(); break;
            case 'R': letterR(); break;
            case 'S': letterS(); break;
            case 'T': letterT(); break;
            case 'U': letterU(); break;
            case 'V': letterV(); break;
            case 'W': letterW(); break;
            case 'X': letterX(); break;
            case 'Y': letterY(); break;
            default:
                if (letter == 'J' || letter == 'Z') {
                    throw std::runtime_error("Letter " + std::string(1, letter) + " requires motion and is not supported");
                }
                throw std::runtime_error("Unsupported letter: " + std::string(1, letter));
        }
    }

    void resetPosition() {
        std::cout << "Resetting to rest position..." << std::endl;
        std::vector<int> positions(5, FINGER_STRAIGHT);
        setFingerPositions(positions);
    }

    void demonstrateAlphabet() {
        std::cout << "Demonstrating implemented letters..." << std::endl;
        const std::string letters = "ABCDEFGHIKLMNOPQRSTUVWXY"; // Excluding J and Z
        for(char letter : letters) {
            std::cout << "\nShowing letter " << letter << std::endl;
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
            hand.demonstrateAlphabet();
        } else if (argc == 2) {
            hand.displayLetter(argv[1][0]);
            sleep(2);
            hand.resetPosition();
        } else {
            std::cout << "Usage: " << argv[0] << " [letter]" << std::endl;
            std::cout << "Supported letters: A-I, K-Y (J and Z require motion and are not supported)" << std::endl;
            return 1;
        }
        
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
}