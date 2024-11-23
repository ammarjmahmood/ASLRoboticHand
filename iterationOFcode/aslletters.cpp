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
    static constexpr int FINGER_STRAIGHT = 375;  // Fully extended (0 degrees)
    static constexpr int FINGER_BENT = 150;      // Fully bent (90 degrees)
    // Additional positions for more natural letter formations
    static constexpr int FINGER_SLIGHT_BEND = 340;  // Just slightly bent
    static constexpr int FINGER_HALF_BENT = 263;    // Half way bent
    static constexpr int FINGER_MOSTLY_BENT = 190;  // Most of the way bent

    struct FingerPosition {
        std::vector<int> positions;
        std::string description;
        FingerPosition(std::vector<int> pos, std::string desc) 
            : positions(pos), description(desc) {}
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
    // Format: {thumb, index, middle, ring, pinky}
    
    letterConfigs['A'] = FingerPosition(
        {FINGER_HALF_BENT, FINGER_BENT, FINGER_BENT, FINGER_BENT, FINGER_BENT},
        "Fist with thumb resting on side"
    );
    
    letterConfigs['B'] = FingerPosition(
        {FINGER_BENT, FINGER_STRAIGHT, FINGER_STRAIGHT, FINGER_STRAIGHT, FINGER_STRAIGHT},
        "All fingers straight up, thumb tucked"
    );
    
    letterConfigs['C'] = FingerPosition(
        {FINGER_HALF_BENT, FINGER_HALF_BENT, FINGER_HALF_BENT, FINGER_HALF_BENT, FINGER_HALF_BENT},
        "Curved hand shape like letter C"
    );
    
    letterConfigs['D'] = FingerPosition(
        {FINGER_HALF_BENT, FINGER_STRAIGHT, FINGER_BENT, FINGER_BENT, FINGER_BENT},
        "Index up, others curved"
    );
    
    letterConfigs['E'] = FingerPosition(
        {FINGER_HALF_BENT, FINGER_MOSTLY_BENT, FINGER_MOSTLY_BENT, FINGER_MOSTLY_BENT, FINGER_MOSTLY_BENT},
        "Fingers curved into palm"
    );
    
    letterConfigs['F'] = FingerPosition(
        {FINGER_STRAIGHT, FINGER_BENT, FINGER_STRAIGHT, FINGER_STRAIGHT, FINGER_STRAIGHT},
        "Index finger touching thumb, others straight"
    );
    
    letterConfigs['G'] = FingerPosition(
        {FINGER_STRAIGHT, FINGER_STRAIGHT, FINGER_BENT, FINGER_BENT, FINGER_BENT},
        "Index pointing sideways, thumb straight"
    );
    
    letterConfigs['H'] = FingerPosition(
        {FINGER_STRAIGHT, FINGER_STRAIGHT, FINGER_STRAIGHT, FINGER_BENT, FINGER_BENT},
        "Index and middle fingers straight"
    );
    
    letterConfigs['I'] = FingerPosition(
        {FINGER_HALF_BENT, FINGER_BENT, FINGER_BENT, FINGER_BENT, FINGER_STRAIGHT},
        "Pinky straight up"
    );
    
    letterConfigs['K'] = FingerPosition(
        {FINGER_STRAIGHT, FINGER_STRAIGHT, FINGER_STRAIGHT, FINGER_BENT, FINGER_BENT},
        "Index and middle finger up in V shape"
    );
    
    letterConfigs['L'] = FingerPosition(
        {FINGER_STRAIGHT, FINGER_STRAIGHT, FINGER_BENT, FINGER_BENT, FINGER_BENT},
        "L-shape with thumb and index"
    );
    
    letterConfigs['M'] = FingerPosition(
        {FINGER_BENT, FINGER_BENT, FINGER_BENT, FINGER_BENT, FINGER_BENT},
        "Three fingers over thumb"
    );
    
    letterConfigs['N'] = FingerPosition(
        {FINGER_BENT, FINGER_BENT, FINGER_BENT, FINGER_BENT, FINGER_BENT},
        "Two fingers over thumb"
    );
    
    letterConfigs['O'] = FingerPosition(
        {FINGER_HALF_BENT, FINGER_MOSTLY_BENT, FINGER_MOSTLY_BENT, FINGER_MOSTLY_BENT, FINGER_MOSTLY_BENT},
        "Fingertips touching thumb in O shape"
    );
    
    letterConfigs['P'] = FingerPosition(
        {FINGER_STRAIGHT, FINGER_STRAIGHT, FINGER_BENT, FINGER_BENT, FINGER_BENT},
        "Index pointing down"
    );
    
    letterConfigs['Q'] = FingerPosition(
        {FINGER_STRAIGHT, FINGER_STRAIGHT, FINGER_BENT, FINGER_BENT, FINGER_BENT},
        "Index and thumb down"
    );
    
    letterConfigs['R'] = FingerPosition(
        {FINGER_HALF_BENT, FINGER_STRAIGHT, FINGER_STRAIGHT, FINGER_BENT, FINGER_BENT},
        "Crossed index and middle fingers"
    );
    
    letterConfigs['S'] = FingerPosition(
        {FINGER_HALF_BENT, FINGER_BENT, FINGER_BENT, FINGER_BENT, FINGER_BENT},
        "Fist with thumb wrapped over fingers"
    );
    
    letterConfigs['T'] = FingerPosition(
        {FINGER_BENT, FINGER_BENT, FINGER_BENT, FINGER_BENT, FINGER_BENT},
        "Thumb between index and middle"
    );
    
    letterConfigs['U'] = FingerPosition(
        {FINGER_HALF_BENT, FINGER_STRAIGHT, FINGER_STRAIGHT, FINGER_BENT, FINGER_BENT},
        "Index and middle straight up"
    );
    
    letterConfigs['V'] = FingerPosition(
        {FINGER_BENT, FINGER_STRAIGHT, FINGER_STRAIGHT, FINGER_BENT, FINGER_BENT},
        "Index and middle in V shape"
    );
    
    letterConfigs['W'] = FingerPosition(
        {FINGER_BENT, FINGER_STRAIGHT, FINGER_STRAIGHT, FINGER_STRAIGHT, FINGER_BENT},
        "Index, middle, and ring fingers up"
    );
    
    letterConfigs['X'] = FingerPosition(
        {FINGER_HALF_BENT, FINGER_HALF_BENT, FINGER_BENT, FINGER_BENT, FINGER_BENT},
        "Index finger hooked"
    );
    
    letterConfigs['Y'] = FingerPosition(
        {FINGER_STRAIGHT, FINGER_BENT, FINGER_BENT, FINGER_BENT, FINGER_STRAIGHT},
        "Thumb and pinky out"
    );
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

    void displayLetter(char letter) {
        letter = toupper(letter);
        
        if (letterConfigs.find(letter) == letterConfigs.end()) {
            throw std::runtime_error("Letter configuration not found: " + std::string(1, letter));
        }

        const auto& config = letterConfigs[letter];
        std::cout << "Displaying letter " << letter << ": " << config.description << std::endl;
        
        for (int finger = 0; finger < 5; finger++) {
            setPWM(finger, 0, config.positions[finger]);
            usleep(100000);  // Small delay between finger movements for more natural motion
        }
    }

    void resetPosition() {
        std::cout << "Resetting to rest position..." << std::endl;
        for (int finger = 0; finger < 5; finger++) {
            setPWM(finger, 0, FINGER_STRAIGHT);
            usleep(100000);
        }
    }

    // Test sequence to verify servo operation
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