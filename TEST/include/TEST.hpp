#include <Arduino.h>
// 궁금증,  port를 어떻게 알고 있는건가?

// 구조체 정의
struct MotorData {
  uint16_t motor_rpm;     // Reg 0x0015
  uint16_t motor_current; // Reg 0x0016
  // ... add more if needed
};

MotorData g_motorData; // 전역 또는 적절한 범위에 선언


// motor control input 부분
uint16_t SPEED_IN_PWM = 10;
uint16_t Enable = 11;
uint16_t Direction = 12;        // 0 -> CCW   // 1 -> CW
uint16_t Brake = 13;            // 0 -> Brake // 1 -> Brake OFF 

// motor control output 부분
uint16_t Hall_A_out = A5;
uint16_t Hall_B_out = A4;
uint16_t Hall_C_out = A3;
uint16_t Alarm_out = A2;
uint16_t FG_out = A1;
uint16_t _33V_out = A0;

// Communication 부분 
uint16_t Tx = 0;
uint16_t Rx = 1;
  

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  // Write
  pinMode(SPEED_IN_PWM, OUTPUT); 
  pinMode(Enable, OUTPUT);  digitalWrite(Enable, LOW); // 항상 HIGH
  pinMode(Direction, OUTPUT);
  pinMode(Brake, OUTPUT);   digitalWrite(Brake, LOW);
  pinMode(Tx, OUTPUT);

  // Read
  pinMode(Hall_A_out, INPUT);
  pinMode(Hall_B_out, INPUT);
  pinMode(Hall_C_out, INPUT);
  pinMode(Alarm_out, INPUT);
  pinMode(FG_out, INPUT);
  pinMode(_33V_out, INPUT);
  pinMode(Rx, INPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  
}
