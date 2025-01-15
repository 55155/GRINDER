#ifndef PACKET_H
#define PACKET_H

#include <Arduino.h>
#include <SoftwareSerial.h>
#include <ModbusMaster.h>

/***************************************************
 * 1) RS-485 & Modbus 기본 설정
 ***************************************************/
// 모터 드라이버의 슬레이브 ID
static const uint8_t SLAVE_ID = 0x64; // ID = 100 Default

// RS-485 제어핀 (DE/RE) : HIGH=송신, LOW=수신
static const int RS485_CTRL_PIN = 2;  

// SoftwareSerial 핀 (예: 10=RX, 11=TX)
static const uint8_t MODBUS_RX_PIN = 10;
static const uint8_t MODBUS_TX_PIN = 11;

// SoftwareSerial 객체 (RS485 통신용)
static SoftwareSerial modbusSerial(MODBUS_RX_PIN, MODBUS_TX_PIN); // Serial 통신선

// ModbusMaster 객체
static ModbusMaster node;

/***************************************************
 * 2) 송수신 제어 콜백 함수
 ***************************************************/
inline void preTransmission()
{
  digitalWrite(RS485_CTRL_PIN, HIGH); // 송신 모드
}

inline void postTransmission()
{
  digitalWrite(RS485_CTRL_PIN, LOW);  // 수신 모드
}

/***************************************************
 * 3) 레지스터 주소/데이터 구조체 정의
 ***************************************************/
// (1) 모터 레지스터 주소 모음
//     - 예: 프로젝트에서 자주 쓰는 주소들을 모아둠
struct MotorRegisters {
  uint16_t regRpm;          // MOTOR_RPM (0x0015)
  uint16_t regCurrent;      // MOTOR_CURRENT (0x0016)
  uint16_t regSetSpeed;     // SET_SPEED_REMOTE (0x0001 등)
};

// (2) 실제 모터 상태값
struct MotorData {
  uint16_t rpm;            // 현재 모터 RPM
  uint16_t current;        // 현재 모터 전류
};

// 사용할 레지스터 주소 (실제 주소는 매뉴얼에 따라 수정)
static const MotorRegisters g_motorReg = { // 구조체 주소 정의
  0x0015,  // MOTOR_RPM
  0x0016,  // MOTOR_CURRENT
  0x0001   // SET_SPEED_REMOTE
};

/***************************************************
 * 4) 초기화 함수
 ***************************************************/
// RS-485 & Modbus 통신 초기화
inline void initModbus()
{
  // 디버그용 시리얼(USB) 시작
  Serial.begin(115200);
  while (!Serial) { }

  // RS-485 제어 핀 초기화
  pinMode(RS485_CTRL_PIN, OUTPUT);
  digitalWrite(RS485_CTRL_PIN, LOW); // 수신 모드로 초기화

  // SoftwareSerial (modbusSerial) 시작
  // 모터 드라이버 설정(9600 8N1 등)에 맞춰 설정
  modbusSerial.begin(115200);

  // ModbusMaster 초기화
  node.begin(SLAVE_ID, modbusSerial);
  node.preTransmission(preTransmission);
  node.postTransmission(postTransmission);

  Serial.println("[INIT] Modbus & RS-485 ready.");
}

/***************************************************
 * 5) READ: 모터 데이터 읽기 (Function Code 3)
 ***************************************************/
inline bool readMotorData(MotorData &data)
{
  // MOTOR_RPM(0x0015)부터 2개 레지스터(0x0015, 0x0016) 연속 읽기
  uint8_t result = node.readHoldingRegisters(g_motorReg.regRpm, 2);
  if (result == node.ku8MBSuccess) {
    // 인덱스 0 → RPM, 인덱스 1 → Current
    data.rpm     = node.getResponseBuffer(0);
    data.current = node.getResponseBuffer(1);
    return true;
  } else {
    Serial.print("[Modbus] Read Error. Code = ");
    Serial.println(result);
    return false;
  }
}

/***************************************************
 * 6) WRITE: 단일 레지스터 쓰기 (Function Code 6)
 ***************************************************/
// 예: SET_SPEED_REMOTE(0x0001) 주소에 원하는 속도(0~1000 등)를 써서 모터 속도 설정
inline bool writeMotorSpeed(uint16_t speedValue)
{
  // writeSingleRegister( address, value )
  uint8_t result = node.writeSingleRegister(g_motorReg.regSetSpeed, speedValue);
  if (result == node.ku8MBSuccess) {
    // 성공
    return true;
  } else {
    Serial.print("[Modbus] Write Error. Code = ");
    Serial.println(result);
    return false;
  }
}

#endif // PACKET_H
