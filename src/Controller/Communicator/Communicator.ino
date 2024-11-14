unsigned long prev_time0;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);

  // 시리얼 통신 시작 (timeout:100ms, boadrate: 9600)
  Serial.setTimeout(100);
  Serial.begin(9600);

  prev_time0 = millis();
}

void loop() {
  unsigned int curr_time = millis();

  if (curr_time-prev_time0 >= 1000){
    prev_time0 = curr_time;
    Serial.println(1); // KEY 1sec Auto Serial
    Serial.println("1 Sec Auto Serial");
    Serial.println("end serial");
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
    case 1:
      // 배식 시간 설정
      break;

    case 2:
      // 놀이 설정
      break;

    case 3:
      // 웹캠 조작
      break;

    case 4:
      //break;

    default:
      // Message Error
      digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
      break;
  }

  // digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
  // Serial.println(intkey + message);
  // delay(100);
}