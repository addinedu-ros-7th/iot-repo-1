# ARUINO - 반려동물과 보호자를 위한 스마트 펫 케어 시스템


# 프로젝트 소개
## 목표
- IoT 기술을 활용하여 반려동물의 건강과 생활을 관리할 수 있는 스마트 펫 관리 시스템 개발

## 주제 선정 배경
- 반려동물 시장의 성장
- 반려동물의 건강 문제 예방
- 보호자 돌봄 부담 완화
- 기술 융합의 가능성

## User Requirements

| **기능**                 | **설명**                                                                 |
|--------------------------|-----------------------------------------------------------------------|
| **1. 배식 기능(Feeder)**            | - 사용자가 설정한 시간에 자동으로 배식<br>- 물 그릇에 자동 급수 및 단수                                   |
| **2. 반려동물과 상호작용 기능(Communicator)** | - 반려동물의 모습을 웹캠으로 원격 관찰<br>- 보호자의 목소리를 출력해 반려동물과 소통<br>- 공 던지고 받는 놀이 기능 |
| **3. 반려동물 상태 확인 기능(PetChecker)** | - 착용한 목걸이를 통해 반려동물의 실시간 상태 확인                                           |

## 팀원 소개

| **이름**   | **역할**                                      |
|:------------:|----------------------------------------------|
| **임주원<br>(팀장)** | -프로젝트 총괄<br>-Feeder 제작 및 개발       |
| **함동균** | -Communicator 제작 및 개발<br>-Server 개발<br>-Server GUI 개발 |
| **김소영** | -Feeder 제작<br>-Client 개발<br>-Client GUI 개발   |
| **김재현** | -Feeder 기구 설계 및 제작<br>-PetChecker 제작 및 개발 |

# 설계
## System Architecture  
<img src="https://github.com/user-attachments/assets/804583a4-f028-4b06-9abf-e99acf2a9b64" width="550"/><br/>

## ERD
<img src="https://github.com/user-attachments/assets/ee79098a-f8e9-4636-9cf0-1847e1115216" width="550"/><br/>

## Scenario  
<img src="https://github.com/user-attachments/assets/d54b7165-086f-4926-9d2f-93b9de292dad" width="550"/><br/>

## 배식기 기구 설계  
<img src="https://github.com/user-attachments/assets/5d164e08-ed92-412d-b44e-b0ef7f76d67c" width="550"/><br/>

# 기능 설명  

## Client GUI  
<img src="https://github.com/user-attachments/assets/48e06be6-9d5d-4722-b83d-9e5d123878c7" width="550"/><br/>

## Server GUI  
<img src="https://github.com/user-attachments/assets/37ea97c3-9b04-4ca4-bf43-b9187954ac99" width="550"/><br/>

## Feeder  
**[Feeding Schedule Setting]**  
<img src="https://github.com/user-attachments/assets/46fd905b-281a-4c56-8629-dcac5422f5b9" width="550"/><br/>  

**[Server-Feeding Schedule changed]**  
<img src="https://github.com/user-attachments/assets/19b1c437-598f-4166-94a8-4f3e40871ada" width="550"/><br/>  

## Communicator  
<img src="https://github.com/user-attachments/assets/cc9b84fe-1c34-487e-9a67-1e86525efa65" width="550"/><br/>

## PetChecker  



# 결론
## 통합테스트 결과
| **Function**                          | **Description**                                                                                       | **Result** |
|---------------------------------------|-------------------------------------------------------------------------------------------------------|:------------:|
| **1. 물의 수위 제어**                 | - 물의 수위가 임계값 이하로 낮아지면 자동으로 급수<br>- 물의 수위가 임계값 이상으로 높아지면 자동으로 단수                      | Pass       |
| **2. 사료 배식**                      | - Client가 설정한 시간에 맞춰 사료 배식을 자동으로 진행                                                                  | Pass       |
| **3. 카메라 회전 제어**               | - Client GUI 클릭 시 카메라 좌우/상하 회전 기능<br>- 특정 위치를 저장한 뒤, 클릭 시 카메라가 해당 위치로 회전                     | Pass       |
| **4. Server GUI에서 정보 확인**       | - Server GUI에서 반려동물과 배식기, 그리고 온습도를 실시간 모니터링                                                       | Pass       |
| **5. Controller와 Server GUI의 정보 연동** | - Controller에서 수집한 정보를 Server GUI에서 실시간 모니터링                                                            | Pass       |
| **6. 물그릇 잔량 표시**               | - Feeder 물그릇에서 물의 양 변화에 따라 Client GUI에서 실시간 잔량 표시                                                   | Pass       |
| **7. 사료그릇 잔량 표시**             | - Feeder 사료그릇에서 사료 양 변화에 따라 Client GUI에서 실시간 잔량 표시                                                 | Fail       |
| **8. 운동량 및 칼로리 변화 표시**     | - 반려동물의 움직임에 따라 Client GUI에서 운동량과 소모 칼로리를 실시간으로 확인                                          | Pass       |
| **9. 놀이 기능**                      | - Controller에서 공을 던지고 강아지가 공을 물어오면 간식 제공                                                            | Fail       |
| **10. 음성 출력 기능**                | - Client에서 버튼을 클릭 시 저장된 음성이 출력                                                                          | Fail       |

## 문제점 및 개선 방안
## 결과 및 기대 효과

