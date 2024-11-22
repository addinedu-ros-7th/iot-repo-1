![image](https://github.com/user-attachments/assets/68fb6bbd-9e8b-4313-9bd7-deb40fc886dd)


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

## 활용 기술
|구분|상세|
|:---:|---|
|**개발환경 및 도구**|<img src="https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white"/> <img src="https://img.shields.io/badge/AMAZON RDS-527fff?style=for-the-badge&logo=visualstudiocode&logoColor=white"/> <img src="https://img.shields.io/badge/VSCode-007ACC?style=for-the-badge&logo=visualstudiocode&logoColor=white"/> <img src="https://img.shields.io/badge/Arduino-00878F?style=for-the-badge&logo=arduino&logoColor=white"/>|
|**언어**|<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/> <img src="https://img.shields.io/badge/C++-00599C?style=for-the-badge&logo=cplusplus&logoColor=white"/>|
|**UI**|<img src="https://img.shields.io/badge/PyQt5-28c745?style=for-the-badge&logo=PyQt5&logoColor=white"/>|
|**기구 설계**|<img src="https://img.shields.io/badge/CATIA-2b388f?style=for-the-badge&logo=PyQt5&logoColor=white"/>|
|**DBMS**| <img src="https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white"/>|
|**협업**|<img src="https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white"/> <img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white"/> <img src="https://img.shields.io/badge/SLACK-4A154B?style=for-the-badge&logo=slack&logoColor=white"/> <img src="https://img.shields.io/badge/Confluence-172B4D?style=for-the-badge&logo=confluence&logoColor=white"/> <img src="https://img.shields.io/badge/JIRA-0052CC?style=for-the-badge&logo=jira&logoColor=white"/> |
<br>

# 설계 <br/>


## System Architecture  
<img src="https://github.com/user-attachments/assets/804583a4-f028-4b06-9abf-e99acf2a9b64" width="900"/><br/>

## ERA  <br/>
<img src="https://github.com/user-attachments/assets/ee79098a-f8e9-4636-9cf0-1847e1115216" width="900"/><br/>
<br/>

## Scenario  <br/>
<img src="https://github.com/user-attachments/assets/d54b7165-086f-4926-9d2f-93b9de292dad" width="900"/><br/>
<br/>

## 배식기 기구설계  <br/>
<img src="https://github.com/user-attachments/assets/5d164e08-ed92-412d-b44e-b0ef7f76d67c" width="900"/><br/>
<br/>

## 구성도 <br/>
<img src="https://github.com/user-attachments/assets/fdc1d0e5-7a03-42bf-aa5c-00e99c8fccdb" width="900"/><br/>

# 기능 설명  <br/>

## Client GUI  <br/>

<img src="https://github.com/user-attachments/assets/48e06be6-9d5d-4722-b83d-9e5d123878c7" width="900"/><br/>
* 반려동물 상태 확인
* 배식기 잔량 상태 확인
* 등록정보 수정 / 배식 시간 설정 창
* 카메라 모니터링 / 조작 창
* 일주일 기록 확인 창
<br/>

## Server GUI <br/>

<img src="https://github.com/user-attachments/assets/37ea97c3-9b04-4ca4-bf43-b9187954ac99" width="900"/><br/>
* 반려동물 정보 확인
* 통신 상태 확인
* PetChecker 정보
* Feeder 설정/ 정보
* Communicator 카메라 화면 
<br/>

## Controller
* **Feeder**
 	자동배식 및 급수가 가능한 배식기
* **Communicator**
 	반려동물 관찰 웹캠
* **PetChecker**
 	반려동물 상태 확인 목걸이
  
### Feeder<br/>
* 자동 배식 기능
  * Client가 설정한 시간에 맞춰 자동으로 사료 배식
* 자동 급수 기능
  * 물의 수위가 임계값 이하로 낮아지면 자동으로 급수
  * 물의 수위가 임계값 이상으로 높아지면 자동으로 단수

* 환경 온습도 실시간 정보 확인

* 배식기 잔량 확인
  * 그릇의 잔량을 측정해서 하루동안 섭취한 양을 GUI에서 표시
   
 </br>
<img src="https://github.com/user-attachments/assets/46fd905b-281a-4c56-8629-dcac5422f5b9" width="450"/>
<img src="https://github.com/user-attachments/assets/19b1c437-598f-4166-94a8-4f3e40871ada" width="450"/>
<br/>  
**[Feeding Schedule Setting]** 　　　　　　　　　　　　　　　   **[Server-Feeding Schedule changed]** 

<br/>
<br/>

[![water sensor](https://img.youtube.com/vi/dZg-E-FREUM/0.jpg)](https://youtu.be/dZg-E-FREUM "water sensor") 
<br/>
**[Water Sensor - Servo]** 

<br/>
<br/>
<br/>

[![water sensor graph](https://img.youtube.com/vi/N9_jNXCYSfQ/0.jpg)](https://youtu.be/N9_jNXCYSfQ "water sensor graph") 
<br/>
**[Water Sensor - Graph]** 
<br/>
<br/>
<br/>

### Communicator  <br/>
* 관찰 기능
  * 웹캠을 통해 원격으로 반려견 모니터링

* 카메라 조작 기능
	 * 버튼을 통해 상하좌우로 카메라 각도를 조절 가능


* 즐겨찾기 기능
 	* 반려견이 자주 머무는 장소를 저장
	 * 장소를 누르면 해당 위치로 카메라가 회전

   
<img src="https://github.com/user-attachments/assets/cc9b84fe-1c34-487e-9a67-1e86525efa65" width="900"/> <br/>

[![Client camera control](https://img.youtube.com/vi/h4qdG65eTXY/0.jpg)](https://youtu.be/h4qdG65eTXY "Client camera control") 
<br/>

**[Client Camera Control]**

<br/>

[![move to saved place](https://img.youtube.com/vi/KkiUwIEK9dQ/0.jpg)](https://youtu.be/KkiUwIEK9dQ "move to saved place") 
<br/>

**[Camera Position Control to Saved Place]**

<br/>

## PetChecker  <br/>
</br>
* 반려동물 현재 상태 실시간 모니터링
	 * 체온, 심박수, 홛동 상태, 칼로리 소모량

* 상태 기록 조회
 	* 일주일 동안의 활동과 식사 정보 확인

[![Activity Status](https://img.youtube.com/vi/87SXgsLanEE/0.jpg)](https://youtu.be/87SXgsLanEE "Activity status") 
<br/>
**[Activity Status]**  <br/>

<br/>


<img src = "https://github.com/user-attachments/assets/737438e0-13f5-49b0-9fa0-31e98ff59e85" width = "900"/> <br/>
<br/>


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



