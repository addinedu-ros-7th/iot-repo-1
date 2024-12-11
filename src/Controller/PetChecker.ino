#include <WiFi.h>
#include <Wire.h>
#include <MPU6050.h>

// Wi-Fi 설정
const char* ssid = "addinedu_class_1(2.4G)";
const char* password = "addinedu1";
const char* server_ip = "192.168.2.29";
const uint16_t server_port = 8080;

// LM35 센서 핀
const int sensorPin = 33;

// MPU6050 객체 생성 (I2C 주소 0x68)
MPU6050 mpu(0x68);

WiFiClient client;

unsigned long lastUpdateTime = 0;
unsigned long previousMillis = 0;
const long interval = 500;

// 활동 시간 변수
unsigned long restTime = 0;
unsigned long walkingTime = 0;
unsigned long runningTime = 0;

// 칼로리 계산용
float weightKg = 70.0; // 사용자의 몸무게 (kg)
float caloriesBurned = 0.0;

// 현재 활동 상태
String currentState = "쉬는 중";

void setup() {
  Serial.begin(115200);

  // Wi-Fi 연결 설정
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }
  Serial.println("\nConnected to WiFi");

  // 서버 연결 시도
  if (client.connect(server_ip, server_port)) {
    Serial.println("Connected to server");
  } else {
    Serial.println("Connection to server failed");
  }

  // LM35 핀 설정
  pinMode(sensorPin, INPUT);

  // MPU6050 초기화
  Wire.begin();
  mpu.initialize();
  if (mpu.testConnection()) {
    Serial.println("MPU6050 연결 성공");
  } else {
    Serial.println("MPU6050 연결 실패");
  }

  lastUpdateTime = millis();
}

void loop() {
  // LM35 온도 데이터 읽기
  int sensorValue = analogRead(sensorPin);
  float voltage = sensorValue * (3.3 / 4095.0);
  float temperatureC = voltage * 100.0;

  // 체온 보정: 15.7도에서 38도로 보정
  float correctedTemperatureC = temperatureC + 26.8;

  // MPU6050 가속도 데이터 읽기
  int16_t ax, ay, az;
  mpu.getAcceleration(&ax, &ay, &az);
  float ax_g = (ax / 16384.0);
  float ay_g = (ay / 16384.0);
  float az_g = (az / 16384.0);
  float totalAcceleration = sqrt(ax_g * ax_g + ay_g * ay_g + az_g * az_g);
  Serial.println(totalAcceleration);

  // 히스테리시스 기반 상태 전환
  String newState = currentState;

  if (currentState == "쉬는 중") {
    if (totalAcceleration > 0.9) {
      newState = "걷는 중";
    }
  } else if (currentState == "걷는 중") {
    if (totalAcceleration > 1.1) {
      newState = "달리는 중";
    } else if (totalAcceleration < 0.87) {
      newState = "쉬는 중";
    }
  } else if (currentState == "달리는 중") {
    if (totalAcceleration < 1.0) {
      newState = "걷는 중";
    }
  }

  // 1초마다 누적 시간 및 칼로리 계산 업데이트
  unsigned long currentTime = millis();
  if (currentTime - lastUpdateTime >= 1000) {
    if (currentState == "걷는 중") {
      walkingTime++;
      caloriesBurned += calculateCalories(3.5, 1); // MET: 3.5
    } else if (currentState == "달리는 중") {
      runningTime++;
      caloriesBurned += calculateCalories(7.0, 1); // MET: 7.0
    }

    // 쉬는 중일 때는 시간을 누적하되, 칼로리는 계산하지 않음
    if (currentState == "쉬는 중") {
      restTime++;
    }

    lastUpdateTime = currentTime;
  }

  if (newState != currentState) {
    currentState = newState;
  }

  // 랜덤 심박수 생성 (80~120)
  int heartRate = random(80, 121);

  // 서버에 데이터 전송
  if (!client.connected()) {
    Serial.println("Disconnected from server, reconnecting...");
    if (client.connect(server_ip, server_port)) {
      Serial.println("Reconnected to server");
    } else {
      return;
    }
  }

  // 데이터 합치기
  String key = "PetChecker Sync Data";
  String split_data = "&&";

  // 데이터1: 보정된 온도, 데이터2: 심박수, 데이터3: 칼로리, 데이터4: 현재 상태, 데이터5: 쉬는 중 누적 시간, 데이터6: 걷는 중 누적 시간, 데이터7: 달리는 중 누적 시간
  String data1 = String(correctedTemperatureC);   // 보정된 온도
  String data2 = String(heartRate);               // 심박수
  String data3 = String(caloriesBurned, 2);       // 칼로리
  String data4 = currentState;                    // 현재 상태
  String data5 = String(restTime);                // 쉬는 중 누적 시간
  String data6 = String(walkingTime);             // 걷는 중 누적 시간
  String data7 = String(runningTime);             // 달리는 중 누적 시간

  String data = key + split_data + data1 + split_data + data2 + split_data + data3 + split_data + data4 + split_data + data5 + split_data + data6 + split_data + data7;

  // 일정 간격마다 데이터 전송
  if (currentTime - previousMillis >= interval) {
    previousMillis = currentTime;

    client.print(data);

    Serial.println("Sent to server: " + data);
  }

  // 서버 응답 처리
  while (client.available()) {
    String response = client.readStringUntil('\n');
    Serial.println("Received from server: " + response);
  }

  delay(200);
}

// 칼로리 계산 함수
float calculateCalories(float met, int seconds) {
  return (met * weightKg * 3.5 / 200.0) * (seconds / 60.0);
}
