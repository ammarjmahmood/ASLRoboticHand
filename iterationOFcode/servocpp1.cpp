/*
Installation needed:
```bash
sudo apt-get install libgpiod-dev
```
What the code does/uses:
Instead of using GPIO libraries (WiringPi, pigpio) (not compatible with Pi 5) we used
* libgpiod - modern Linux GPIO interface: https://github.com/brgl/libgpiod
Differences from Arduino:
1. Arduino has built-in Servo library with simple `servo.write(angle)` commands
2. This code manually generates PWM signals using GPIO
3. Arduino handles timing in hardware this uses software timing
4. Arduino uses simplified C++ (i swear its the same but whtv)
5. Requires manual GPIO setup and pin configuration which is diff than Arduino
The code works by generating PWM signals: rapidly switching the GPIO pin between high and low states to create pulses that control the servo position. Width of these pulses (500-2500μs) determines the servo angle.
To run code: 
* raspi@Family-PC:~ $ g++ -o servo servocpp.cpp -lgpiod -std=c++17 -pthread
* raspi@Family-PC:~ $ sudo ./servo
 */
#include <cstdio>
#include <memory>
#include <stdexcept>
#include <thread>
#include <chrono>
#include <gpiod.h>

class Servo {
private:
    struct ChipDeleter {
        void operator()(gpiod_chip* chip) { gpiod_chip_close(chip); }
    };
    
    struct LineDeleter {
        void operator()(gpiod_line* line) { gpiod_line_release(line); }
    }; 

    std::unique_ptr<gpiod_chip, ChipDeleter> chip;
    std::unique_ptr<gpiod_line, LineDeleter> line;
    static constexpr int PIN = 18;

public:
    Servo() {
        chip.reset(gpiod_chip_open_by_name("gpiochip4"));
        if (!chip) {
            throw std::runtime_error("Failed to open GPIO chip");
        }

        line.reset(gpiod_chip_get_line(chip.get(), PIN));
        if (!line) {
            throw std::runtime_error("Failed to get GPIO line");
        }

        if (gpiod_line_request_output(line.get(), "servo-control", 0) < 0) {
            throw std::runtime_error("Failed to request GPIO line");
        }
    }

    void setAngle(int angle) {
        using namespace std::chrono;
        
        const auto cycleTime = 20000us;  // 20ms cycle (50Hz)
        const auto pulseWidth = microseconds(500 + (angle * 2000 / 180));
        for(int i = 0; i < 50; i++) {
            gpiod_line_set_value(line.get(), 1);
            std::this_thread::sleep_for(pulseWidth);
            gpiod_line_set_value(line.get(), 0);
            std::this_thread::sleep_for(cycleTime - pulseWidth);
        }
    }
};

int main() {
    try {
        Servo servo;
        
        for (int angle = 0; angle <= 180; angle += 45) {
            std::printf("Moving to %d degrees\n", angle);
            servo.setAngle(angle);
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }
    } catch (const std::exception& e) {
        std::fprintf(stderr, "Error: %s\n", e.getMessage());
        return 1;
    }
    return 0;
}