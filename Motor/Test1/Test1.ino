const int enablePin = 13;  // 사용할 핀 설정

void setup() {
  pinMode(enablePin, OUTPUT);    // 핀을 출력 모드로 설정
  digitalWrite(enablePin, HIGH); // 핀에 HIGH 신호 출력
  
  pinMode(enablePin, INPUT);     // 핀 상태 확인을 위해 INPUT 모드로 전환
  Serial.begin(9600);            // 시리얼 모니터 시작
}

void loop() {
  int pinState = digitalRead(enablePin);  // 핀 상태 읽기
  
  if (pinState == HIGH) {
    Serial.println("Signal Sent: HIGH");
  } else {
    Serial.println("Signal Sent: LOW");
  }
  delay(1000);  // 1초마다 상태 확인
}
