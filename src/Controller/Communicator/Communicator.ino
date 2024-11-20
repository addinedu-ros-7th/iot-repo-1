#include <Servo.h>

const int UP_DOWN_SERVO_PIN = 9;
const int LEFT_RIGHT_SERVO_PIN = 11;

unsigned long prev_time0;
unsigned long prev_time1;

bool up_flag = false;
bool down_flag = false;
bool left_flag = false;
bool right_flag = false;

int up_down_angle = 90;
int left_right_angle = 90;

Servo up_down_servo;
Servo left_right_servo;

String curr_message;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);

  up_down_servo.attach(UP_DOWN_SERVO_PIN);
  up_down_servo.write(up_down_angle);

  left_right_servo.attach(LEFT_RIGHT_SERVO_PIN);
  left_right_servo.write(left_right_angle);

  // 시리얼 통신 시작 (timeout:100ms, boadrate: 9600)
  Serial.setTimeout(100);
  Serial.begin(9600);

  prev_time0 = millis();
  prev_time1 = millis();
}

void loop() {
  unsigned int curr_time = millis();

  if (curr_time-prev_time0 >= 1000){
    prev_time0 = curr_time;
    digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
  }


  if (curr_time-prev_time1 >= 10){
    prev_time1 = curr_time;

    if (up_flag || down_flag || left_flag || right_flag){

      if (up_flag) up_down_angle++;
      if (down_flag) up_down_angle--;
      if (left_flag) left_right_angle++;
      if (right_flag) left_right_angle--;

      if (up_down_angle > 135) up_down_angle = 135;
      if (up_down_angle < 45) up_down_angle = 45;

      if (left_right_angle > 175) left_right_angle = 175;
      if (left_right_angle < 5) left_right_angle = 5;

      up_down_servo.write(up_down_angle);
      left_right_servo.write(left_right_angle);

      Serial.println(curr_message); // KEY h, t, hic
      Serial.println(up_down_angle);
      Serial.println(left_right_angle);
      Serial.println("end serial");

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
    case 10:
      // up end
      up_flag = false;
      curr_message = message;
      break;
    case 11:
      // up start
      up_flag = true;
      curr_message = message;
      break;

    case 20:
      // down end
      down_flag = false;
      curr_message = message;
      break;
    case 21:
      //down start
      down_flag = true;
      curr_message = message;
      break;

    case 30:
      // left end
      left_flag = false;
      curr_message = message;
      break;
    case 31:
      // left start
      left_flag = true;
      curr_message = message;
      break;

    case 40:
      // right end
      right_flag = false;
      curr_message = message;
      break;
    case 41:
      // right start
      right_flag = true;
      curr_message = message;
      break;

    default:
      // Message Error
      digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
      delay(1000);
      delay(1000);
      delay(1000);
      break;
  }

  // digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
  // Serial.println(intkey + message);
  // delay(100);
}