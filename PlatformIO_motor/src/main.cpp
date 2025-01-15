/*
// 통신 제어 코드
#include <Arduino.h>
#include "packet.h"   // 구조체, 함수 선언

void setup() {
  // Modbus 통신 초기화
  initModbus();
  
  // 초기 속도 한번 세팅 예시 (0~1000 사이 값, 매뉴얼에 따라 다름)
  // 예: 300 (30%), 혹은 1000이면 최대속도 등등
  writeMotorSpeed(300);
}

void loop() {
  static MotorData motorData;

  // 1) 모터 데이터 읽기
  if (readMotorData(motorData)) {
    // 2) 값 출력
    Serial.print("RPM: ");
    Serial.print(motorData.rpm);
    Serial.print(" | Current: ");
    Serial.println(motorData.current);
  }

  // 필요 시, 주기적으로 속도 변경 예시
  // writeMotorSpeed(500);

  delay(1000); // 1초
}
*/

/*
******************************************************
 * Example Arduino code for Motor Driver Control
 * 
 * 핀 매핑:
 * - 모터 제어 (Digital)
 *   PWM_SPEED_PIN   = 10
 *   ENABLE_PIN      = 11
 *   DIRECTION_PIN   = 12
 *   BRAKE_PIN       = 13
 * 
 * - 피드백 (Analog)
 *   HALL_A_PIN      = A5
 *   HALL_B_PIN      = A4
 *   HALL_C_PIN      = A3
 *   ALARM_OUT_PIN   = A2
 *   FG_OUT_PIN      = A1
 *   V33_OUT_PIN     = A0  (3.3V 출력 확인 용도? 실제로는 내부 레퍼런스일 가능성)
 * 
 * - 직렬 통신
 *   MotorDriver TX  -> Arduino RX(1)
 *   MotorDriver RX  -> Arduino TX(0)
 *   MotorDriver GND -> Arduino GND (또는 공통접지)
 * 
 *  본 코드는 기본적인 모터 제어와 센서 피드백 확인에 대한 예시입니다.
 *******************************************************/

#include <Arduino.h>

// 핀 정의
const int PWM_SPEED_PIN   = 10;  // 모터 속도 제어용 PWM 출력
const int ENABLE_PIN      = 11;  
const int DIRECTION_PIN   = 12;
const int BRAKE_PIN       = 13;

// 아날로그 입력 (Hall 센서, Alarm, FG 등)
const int HALL_A_PIN      = A5;
const int HALL_B_PIN      = A4;
const int HALL_C_PIN      = A3;
const int ALARM_OUT_PIN   = A2;
const int FG_OUT_PIN      = A1;
const int V33_OUT_PIN     = A0; // 3.3V 출력(레퍼런스 측정값)

// 직렬 통신: 아두이노의 하드웨어 시리얼(0,1) 사용
//   -> MotorDriver TX = Arduino RX(1)
//   -> MotorDriver RX = Arduino TX(0)
//   주의: USB Serial 모니터 사용 시 동시에 사용할 경우 충돌 가능성 있음

// 모터 속도(0~255, 아날로그Write 8비트 해상도)
int motorSpeed = 100;  

void setup() {
  // 디버그용 시리얼 모니터 초기화
  Serial.begin(115200);

  // 핀 모드 설정
  pinMode(PWM_SPEED_PIN, OUTPUT);
  pinMode(ENABLE_PIN, OUTPUT);
  pinMode(DIRECTION_PIN, OUTPUT);
  pinMode(BRAKE_PIN, OUTPUT);

  // 아날로그 입력 핀은 기본적으로 입력으로 설정되므로 별도 pinMode 불필요
  // pinMode(HALL_A_PIN, INPUT);
  // ...


  // 초기 상태 설정
  digitalWrite(ENABLE_PIN, LOW);     // 모터 정지(ENABLE off)
  digitalWrite(DIRECTION_PIN, LOW);  // 예: 정방향
  digitalWrite(BRAKE_PIN, LOW);      // BRAKE off
}

void loop() {
  // 1) 모터 속도 제어 (PWM 출력)
  analogWrite(PWM_SPEED_PIN, motorSpeed);

  // 2) Hall 센서, Alarm, FG 등 피드백 읽기
  int hallA  = analogRead(HALL_A_PIN);
  int hallB  = analogRead(HALL_B_PIN);
  int hallC  = analogRead(HALL_C_PIN);
  // int alarm  = analogRead(ALARM_OUT_PIN);
  // int fg     = analogRead(FG_OUT_PIN);
  // int v33Val = analogRead(V33_OUT_PIN);

  // 3) 시리얼 모니터로 출력 (디버그/확인)
  // Serial.print("Motor Speed: ");
  // Serial.print(motorSpeed);
  // Serial.print(" | Hall(A,B,C): ");
  Serial.print(hallA); Serial.print(",");
  Serial.print(hallB); Serial.print(",");
  Serial.println(hallC);
  // Serial.print(" | Alarm: ");
  // Serial.print(alarm);
  // Serial.print(" | FG: ");
  // Serial.print(fg);
  // Serial.print(" | 3.3V ref: ");
  // Serial.println(v33Val);

  // 4) 예시: 브레이크/방향/속도 변경 등
  //   필요 시 루프 내에서 조건에 따라 값을 바꿀 수 있습니다.
  //   여기서는 단순 예시로 속도를 증가/감소 시켜볼 수도 있습니다.

  // 간단한 예: motorSpeed를 서서히 변화
  // motorSpeed += 1;
  if (motorSpeed > 255) { // 255가 최댓값이 구나,  아날로그  input 이 0 ~ 255 니까
    motorSpeed = 0;
  }

  delay(10); // 주기(속도 등 확인)
}

/*******************************************************
 * 추가 예시 함수들
 *******************************************************/

// 모터 구동 Enable/Disable
void setMotorEnable(bool enable) {
  if (enable) {
    digitalWrite(ENABLE_PIN, LOW);
  } else {
    digitalWrite(ENABLE_PIN, HIGH);
  }
}

// 모터 방향 설정
void setMotorDirection(bool dir) {
  // dir = false -> LOW  (정방향)
  // dir = true  -> HIGH (역방향)
  digitalWrite(DIRECTION_PIN, !dir ? HIGH : LOW);
}

// 모터 브레이크 설정
void setMotorBrake(bool brakeOn) {
  digitalWrite(BRAKE_PIN, brakeOn ? HIGH : LOW);
}

// 모터 속도 설정 (0~255)
void setMotorSpeed(int speedVal) {
  if (speedVal < 0) speedVal = 0;
  if (speedVal > 255) speedVal = 255;
  analogWrite(PWM_SPEED_PIN, speedVal);
}
