
![image](https://github.com/user-attachments/assets/27d45ef1-de40-4820-93a6-e6b9b8544f66)


# 프로젝트 소개
## 목표
- IoT 기술을 활용하여 반려동물의 건강과 생활을 관리할 수 있는 스마트 펫 관리 시스템 개발

## 주제 선정 배경
- 반려동물 시장의 성장
- 반려동물의 건강 문제 예방
- 보호자 돌봄 부담 완화
- 기술 융합의 가능성

## User Requirements

|  | **기능**                 | **설명**                                                                 |
|-------|--------------------------|-----------------------------------------------------------------------|
| **1**     | **배식 기능(Feeder)**            | - 사용자가 설정한 시간에 자동으로 배식<br>- 물 그릇에 자동 급수 및 단수                                   |
| **2**     | **반려동물과 상호작용 기능(Communicator)** | - 반려동물의 모습을 웹캠으로 원격 관찰<br>- 보호자의 목소리를 출력해 반려동물과 소통<br>- 공 던지고 받는 놀이 기능 |
| **3**     | **반려동물 상태 확인 기능(PetChecker)** | - 착용한 목걸이를 통해 반려동물의 실시간 상태 확인                     |


## 팀원 소개

| **이름**   | **역할**                                      |
|:------------:|----------------------------------------------|
| **임주원<br>(팀장)** | -프로젝트 총괄<br>-Feeder 제작 및 개발       |
| **함동균** | -Communicator 제작 및 개발<br>-Server 개발<br>-Server GUI 개발 |
| **김소영** | -Feeder 제작<br>-Client 개발<br>-Client GUI 개발   |
| **김재현** | -Feeder 기구 설계 및 제작<br>-PetChecker 제작 및 개발 |

## 활용 기술
|구분|상세|
|:---:|---|
|**개발환경 및 도구**|<img src="https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white"/> <img src="https://img.shields.io/badge/AMAZON RDS-527fff?style=for-the-badge&logo=visualstudiocode&logoColor=white"/> <img src="https://img.shields.io/badge/VSCode-007ACC?style=for-the-badge&logo=visualstudiocode&logoColor=white"/> <img src="https://img.shields.io/badge/Arduino-00878F?style=for-the-badge&logo=arduino&logoColor=white"/>|
|**언어**|<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/> <img src="https://img.shields.io/badge/C++-00599C?style=for-the-badge&logo=cplusplus&logoColor=white"/>|
|**UI**|<img src="https://img.shields.io/badge/PyQt5-28c745?style=for-the-badge&logo=PyQt5&logoColor=white"/>|
|**기구 설계**|<img src="https://img.shields.io/badge/CATIA-2b388f?style=for-the-badge&logo=PyQt5&logoColor=white"/>|
|**DBMS**| <img src="https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white"/>|
|**협업**|<img src="https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white"/> <img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white"/> <img src="https://img.shields.io/badge/SLACK-4A154B?style=for-the-badge&logo=slack&logoColor=white"/> <img src="https://img.shields.io/badge/Confluence-172B4D?style=for-the-badge&logo=confluence&logoColor=white"/> <img src="https://img.shields.io/badge/JIRA-0052CC?style=for-the-badge&logo=jira&logoColor=white"/> |


# 설계


## System Architecture  
<img src="https://github.com/user-attachments/assets/804583a4-f028-4b06-9abf-e99acf2a9b64" width="900"/><br/>

## ERD
<img src="https://github.com/user-attachments/assets/d6c8adcb-cc91-459e-95d5-46a56e80b1ef" width="900"/><br/>

## Scenario
<img src="https://github.com/user-attachments/assets/d54b7165-086f-4926-9d2f-93b9de292dad" width="900"/><br/>

## 배식기 기구설계
<img src="https://github.com/user-attachments/assets/5d164e08-ed92-412d-b44e-b0ef7f76d67c" width="900"/><br/>

## 구성도
<img src="https://github.com/user-attachments/assets/fdc1d0e5-7a03-42bf-aa5c-00e99c8fccdb" width="900"/><br/>

# 기능 설명

## Client

| **기능**                   | **설명**                                                                 |
|----------------------------|-------------------------------------------------------------------------|
| **반려동물 상태 확인**      | 반려동물의 체온, 심박수, 활동 상태, 소모 칼로리 등 실시간 상태를 확인 가능                     |
| **배식기 잔량 상태 확인**   | 배식기의 사료 및 물 잔량을 확인                    |
| **등록정보 수정 / 배식 시간 설정** | 반려동물의 프로필 정보 수정 및 배식 시간을 사용자 지정                       |
| **카메라 모니터링 / 조작** | 웹캠을 통해 반려동물을 모니터링하며, 카메라를 상하좌우로 조작 가능                   |
| **일주일 기록 확인**     | 반려동물의 일주일간 활동 및 식사 정보를 GUI를 통해 확인 가능                      |<br/>

<img src="https://github.com/user-attachments/assets/48e06be6-9d5d-4722-b83d-9e5d123878c7" width="900"/>


## Server

| **기능**                   | **설명**                                                                 |
|----------------------------|-------------------------------------------------------------------------|
| **반려동물 정보 확인**      | 반려동물의 이름, 나이, 종 등 기본 정보를 확인 가능                        |
| **통신 상태 확인**          | Server, Client, Controller의 연결 상태를 실시간으로 확인 |
| **PetChecker 정보**         | 반려동물의 체온, 심박수, 활동 상태, 소모 칼로리 등 실시간 상태를 확인 가능             |
| **Feeder 설정/정보**        | 배식 시간 설정 및 사료와 물 잔량 정보를 확인 가능              |
| **Communicator 카메라 화면**| 웹캠을 통해 반려동물을 모니터링하며, 카메라를 상하좌우로 조작 가능              |<br/>


<img src="https://github.com/user-attachments/assets/37ea97c3-9b04-4ca4-bf43-b9187954ac99" width="900"/><br/>


## Controller


| **Product**           | **Component**    | **Description**                          |
|------------------------|------------------|------------------------------------------|
| **Smart Pet Feeder**   | **1. Feeder**       | 자동 배식 및 급수가 가능한 배식기    |
|                        | **2. Communicator** | 반려동물 관찰 웹캠                   |
| **Smart Collar**       | **3. PetChecker**   | 반려동물 상태 확인 목걸이             |

<img src="https://github.com/user-attachments/assets/017877b4-f1b7-4d36-b57e-9a70fb4020d6" width="900"/><br/>

  
### 1. Feeder

| **기능**                     | **설명**                                                                                     |
|-------------------------------|---------------------------------------------------------------------------------------------|
| **자동 배식 기능**            | Client가 설정한 시간에 맞춰 자동으로 사료 배식                                               |
| **자동 급수 기능**            | 물의 수위가 임계값 이하로 낮아지면 자동으로 급수                                              |
| **자동 단수 기능**            | 물의 수위가 임계값 이상으로 높아지면 자동으로 단수                                            |
| **환경 온습도 실시간 정보 확인** | 실시간으로 환경의 온도와 습도 정보를 확인                                                   |
| **배식기 잔량 확인**          | 그릇의 잔량을 측정해서 하루 동안 섭취한 양을 GUI에서 표시                                     |


   
   
 </br>
<img src="https://github.com/user-attachments/assets/46fd905b-281a-4c56-8629-dcac5422f5b9" width="900"/><br/>

**[Feeding Schedule Setting]**
<br/>


</div>
<img src="https://github.com/user-attachments/assets/19b1c437-598f-4166-94a8-4f3e40871ada" width="900"/><br/>

**[Server-Feeding Schedule changed]** 
<br/>


<img src="https://github.com/user-attachments/assets/c4ac2420-75b6-4a62-b598-ad5f5cc3dcff" width="600"/>
<br/>

**[Feeding]** 


<img src="https://github.com/user-attachments/assets/e0478d91-161b-4b3e-aaf1-1a22baea2841" width="900"/>
<br/>

**[Water Sensor - Servo]** 



<img src="https://github.com/user-attachments/assets/53a21fb5-d51d-4702-bcd0-61145f579ec8" width="700"/>
<br/>

**[Water Sensor - Graph]** 
<br/>

### 2. Communicator

| **기능**           | **설명**                                                                 |
|---------------------|-------------------------------------------------------------------------|
| **관찰 기능**       | 웹캠을 통해 원격으로 반려견 모니터링                                      |
| **카메라 조작 기능** | 버튼을 통해 상하좌우로 카메라 각도를 조절 가능                            |
| **즐겨찾기 기능**   | 반려견이 자주 머무는 장소를 저장<br>저장된 장소를 누르면 해당 위치로 카메라가 회전 |


   
<img src="https://github.com/user-attachments/assets/cc9b84fe-1c34-487e-9a67-1e86525efa65" width="900"/> <br/>

<img src="https://github.com/user-attachments/assets/bdf0cc14-bd56-4ff6-ae03-0f64024034cc" width="900"/><br/>
**[Client Camera Control]**



<img src="https://github.com/user-attachments/assets/cf55bac2-c427-4b7e-8af2-0c8c9187a6a4" width="900"/> <br/>
**[Camera Position Control to Saved Place]**

### 3. PetChecker  <br/>


| **기능**            | **설명**                                                                 |
|----------------------|-------------------------------------------------------------------------|
| **반려동물 현재 상태 실시간 모니터링** | 체온, 심박수, 활동 상태, 칼로리 소모량을 실시간으로 모니터링                                     |
| **상태 기록 조회**    | 일주일 동안의 활동과 식사 정보를 확인 가능                                  |

 

<img src="https://github.com/user-attachments/assets/f3678384-e3d9-4070-9a8f-52ca35d3b6ca" width="900"/><br/>
**[Activity Status]**  <br/>




<img src = "https://github.com/user-attachments/assets/737438e0-13f5-49b0-9fa0-31e98ff59e85" width = "900"/> <br/>
**[Weekly Report]**  <br/>


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

### Feeder - 사료그릇 잔량 표시
* 기존의 계획했던 압력 센서 미도착
* 초음파 센서를 대체 사용했으나, 센서값이 정확하지 않음
* 개선 방안 : 향후 센서 도착 시, 기존 센서와 통합하여 데이터 정확도를 비교 및 보완

### Communicator - 놀이 및 스피커 기능
* 협업 도구(Jira, Confluence)를 활용해 일정을 관리했으나 우선순위 조정으로 미구현 
* 개선 방안 : 우선순위 설정과 작업 분배 방식을 조금 더 개선하여 이후 프로젝트에서는 더 완성도 높은 결과를 이끌어낼 계획이다.

### 운동량 기반 섭취량 조절 기능
* 개선 방안 : 수집된 데이터를 분석해 머신러닝을 통해 섭취량 조절 모델 구현


## 결과 및 기대 효과
- 데이터 기반 관리 시스템을 구축해 사용자 맞춤형 반려동물 건강 관리 서비스를 제공할 수 있었다.  
- 실시간 상태 모니터링과 자동화 기능을 통해 반려동물을 효율적으로 관리하며, 건강 문제를 예방하고 사용자의 편의성을 향상시키는 효과가 기대된다.

# 발표 자료
https://docs.google.com/presentation/d/1pv5TJea4zawtUooIV6gafMzH5ZcCtFoCPv8cDFzU4AY/edit?usp=sharing
