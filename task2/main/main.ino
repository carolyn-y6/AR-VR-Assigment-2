#include "lib/GY85.h"

GY_85 mpu;

void setup()
{
  Serial.begin(115200);

  delay(2000);
  mpu.init();
  
}

void loop()
{
  mpu.updateQuaternion();

  static uint32_t prev_ms = 0;
  uint32_t current_ms = millis();
  if (current_ms - prev_ms >= 10)
  {
    get_angles();
    prev_ms = current_ms;
  }
  //delay(2000);
}

inline void get_angles()
{
  float yaw = mpu.getYaw();
  float pitch = mpu.getPitch();
  float roll = mpu.getRoll();
  
  Serial.print("Y:");
  Serial.print(yaw,1);
  Serial.print(",P:");
  Serial.print(pitch,1);
  Serial.print(",R:");
  Serial.println(roll,1);
}