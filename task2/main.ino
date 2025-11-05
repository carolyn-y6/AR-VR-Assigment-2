#include "MPU9250.h"

MPU9250 mpu;

void setup() {
  Serial.begin(115200);
  Wire.begin();
  delay(2000);

  if (!mpu.setup(0x68)) {  // change to your own address
    while (1) {
      Serial.println("MPU connection failed. Please check your connection with `connection_check` example.");
      delay(5000);
    }
  }
}

void loop() {
  if (mpu.update()) {
    static uint32_t prev_ms = millis();
    if (millis() > prev_ms + 25) {
      get_angles();
      prev_ms = millis();
    }
  }
}

void get_angles() {
  // you need to implement this function to get the angles
  // Hints: you must read the functions in MPU9250.h to find out how to get the angles
  
  delay(1000);
}
