#include <Servo.h>
#include <DHT.h>
///////////////////////////////////////////////
// 사료
#define TRIG_PIN 5
#define ECHO_PIN 6
long duration;
int distance;
int lastValidDistance = 15;
Servo servo_Water;
Servo servo_Food;
///////////////////////////////////////////////
// 물
const int waterLevelPin = A0;
const int servo_WaterPin = 10;
int waterLimit = 540;
int waterLimit_L = waterLimit-30;
int waterLimit_H = waterLimit + 20; 
int lastValidWaterLevel = waterLimit+50;
int servo_WaterAngle = 150;
int waterServoCloseAngle = servo_WaterAngle;
int waterServoOpenAngle = 100;
bool isWaterClosed = true;
///////////////////////////////////////////////
// 배식
const int servo_FoodPin = 9;
int servo_FoodAngle = 150;
int close_Angle = servo_FoodAngle;
int open_Angle = close_Angle - 15;
///////////////////////////////////////////////
// 온습도
#define DHTPIN A5
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);
float temperature = 0.0;
float humidity = 0.0;
///////////////////////////////////////////////
// 자동 모드 설정
bool isUnifiedAutoModeActive = false;
bool isFoodClosed = true;
int feedTimeLimit = 2; 
bool first_init_flag = false;
unsigned long curr_time = millis();
void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  servo_Water.attach(servo_WaterPin);
  servo_Food.attach(servo_FoodPin);
  servo_Food.write(servo_FoodAngle);
  servo_Water.write(servo_WaterAngle);
  dht.begin();
  Serial.begin(9600);

  delay(200);
  for (int servo_WaterAngle = servo_WaterAngle ; servo_WaterAngle <= 160; servo_WaterAngle += 10) {
    servo_Water.write(servo_WaterAngle);
    delay(20);
  }  
}
void loop() {
  static unsigned long prev_time = millis();
  curr_time = millis();
  // 1초에 한 번
  // 센싱
  // 물 수위 센싱값 기준으로 open / close
  // Serial Sync Data
  if(curr_time - prev_time >= 1000 && first_init_flag == true){
    measureAndPrintAllSensorData(); // 모든 센서 데이터 측정 및 출력
    manageWaterServo();
  
    Serial.println("Feeder Sencing Data");
    Serial.println(humidity);
    Serial.println(temperature);
    Serial.println(0);  // 체감온도 (측정x)
    Serial.println(lastValidWaterLevel);
    Serial.println(0);  // 초음파 센서 거리 (측정x)
    Serial.println("end serial");
    
    prev_time = millis();
  }
  
}

void hdk(){
  static bool open_flag = false;
  if (isFoodClosed) {
    moveServoSmoothly(servo_Food, servo_FoodAngle, open_Angle);
    moveServoSmoothly(servo_Water, 175, waterServoOpenAngle);
    isWaterClosed = false;
    open_flag = true;
  }
  if (open_flag == true)
    delay(feedTimeLimit * 1000); // 설정된 시간만큼 배식
    moveServoSmoothly(servo_Food, servo_FoodAngle, close_Angle);
    open_flag = false;
}
// 사료 서보 제어 (시간 기반)
void manageFoodServoByTime() {
  static bool open_flag = false;
  if (isFoodClosed) {
    moveServoSmoothly(servo_Food, servo_FoodAngle, open_Angle);
    isFoodClosed = false;
    open_flag = true;
  }
  // delay(feedTimeLimit * 1000);
  if (open_flag == true)
    delay(feedTimeLimit * 1000); // 설정된 시간만큼 배식
    moveServoSmoothly(servo_Food, servo_FoodAngle, close_Angle);
    isFoodClosed = true;
    open_flag = false;
}
// 물 서보 제어
void manageWaterServo() {
  // 닫는 코드
     if (lastValidWaterLevel >= waterLimit_H && isWaterClosed == false) {
      moveServoSmoothly(servo_Water, 100, 185);
      isWaterClosed = true;
      servo_WaterAngle = waterServoCloseAngle;
    }
    // 여는 코드
    else if (lastValidWaterLevel <= waterLimit_L && isWaterClosed == true) {
      moveServoSmoothly(servo_Water, 160, waterServoOpenAngle);
      isWaterClosed = false;
      servo_WaterAngle = waterServoOpenAngle;
    }
}
// 모든 센서 데이터 측정 및 출력
void measureAndPrintAllSensorData() {
  measureDistance();
  measureWaterLevel();
  measureTemperatureAndHumidity();
}
// 초음파 거리 측정
void measureDistance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  duration = pulseIn(ECHO_PIN, HIGH, 30000); // 최대 30ms 대기
  if (duration == 0) {
    distance = lastValidDistance;
  } else {
    distance = duration * 0.034 / 2;
    if (distance > 0) {
      lastValidDistance = distance;
    }
  }
}

// 수위 측정
void measureWaterLevel() {
  int waterLevel = analogRead(waterLevelPin);
  if (waterLevel > 0) {
    lastValidWaterLevel = waterLevel;
  }
}

// 온도 및 습도 측정
void measureTemperatureAndHumidity() {
  temperature = dht.readTemperature();
  humidity = dht.readHumidity();
  if (isnan(temperature) || isnan(humidity)) {
    //Serial.println("Failed to read from DHT sensor!");
    temperature = 38.2;
    humidity = 52.8;
    return;
  }
}

// 서보 모터 부드럽게 이동
void moveServoSmoothly(Servo &servo, int currentAngle, int targetAngle) {
  if (currentAngle < targetAngle) {
    for (int angle = currentAngle; angle <= targetAngle; angle++) {
      servo.write(angle);
      delay(30); // 30ms 지연
    }
  } else {
    for (int angle = currentAngle; angle >= targetAngle; angle--) {
      servo.write(angle);
      delay(30); // 30ms 지연
    }
  }
}

// serial 입력이 있을 때 동작하는 Event 함수
void serialEvent(){
  int intkey = 0;
  String str_test = Serial.readString();
  str_test.trim();
  String key = str_test.substring(0, 2);
  String message = str_test.substring(2, str_test.length());
  intkey = key.toInt();

  switch (intkey){
    case 1: //시스템 시작 (수위 측정)
      first_init_flag = true;
      digitalWrite(LED_BUILTIN, HIGH);
      break;

    case 53: //사료 배식
      manageFoodServoByTime();
      break;
      
    case 54: //사료 + 물 배식
      hdk();
      break;

    default:
      delay(1000);
      delay(1000);
      delay(1000);
      break;
  }
}
