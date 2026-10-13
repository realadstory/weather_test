# 날씨 확인 웹앱

도시 이름을 입력하고 **날씨 확인** 버튼을 누르면 그 도시의 현재 날씨를 보여주는 간단한 웹앱입니다.

- 프론트엔드: HTML, CSS, JavaScript
- 백엔드: Python 표준 라이브러리만 사용 (별도 설치 필요 없음)
- 날씨 데이터: [Open-Meteo](https://open-meteo.com) 무료 API (API Key 필요 없음)

## 표시 정보

- 현재 기온, 체감 온도
- 날씨 상태 (맑음, 흐림, 비 등)
- 습도, 풍속
- 기준 시각 (해당 도시의 현지 시각)

## 파일 구조

```
weather_test/
├── backend/
│   └── server.py      # 백엔드 서버: 날씨 API 호출 + 화면 파일 제공
└── frontend/
    ├── index.html     # 화면 구조
    ├── style.css      # 디자인
    └── script.js      # 버튼 클릭 → 백엔드에 요청 → 결과 표시
```

## 실행 방법

1. **Python 3.9 이상이 설치되어 있는지 확인합니다.**
   ```
   python --version
   ```

2. **저장소를 내려받고 폴더로 이동합니다.**
   ```
   git clone https://github.com/realadstory/weather_test.git
   cd weather_test
   ```

3. **백엔드 서버를 실행합니다.**
   ```
   python backend/server.py
   ```
   `서버 실행 중: http://127.0.0.1:8000` 메시지가 나오면 성공입니다.

4. **브라우저에서 http://127.0.0.1:8000 에 접속합니다.**
   `frontend/index.html` 파일을 더블클릭해서 열어도 됩니다. 어느 쪽이든 3번의 서버는 켜져 있어야 합니다.

5. **도시 이름을 입력하고 "날씨 확인"을 누릅니다.**
   예: 서울, 부산, 제주, Tokyo, London

6. **종료할 때는 터미널에서 `Ctrl + C`를 누릅니다.**

## 동작 방식

1. 화면(`script.js`)이 백엔드의 `/api/weather?city=도시이름` 주소로 요청합니다.
2. 백엔드(`server.py`)가 Open-Meteo를 두 번 호출합니다.
   - 도시 이름으로 위도와 경도를 찾습니다.
   - 그 좌표의 현재 날씨를 가져옵니다.
3. 백엔드가 결과를 정리해서 화면에 돌려주고, 화면이 이를 표시합니다.

## 한글 도시 이름 검색 참고

Open-Meteo는 한글 검색이 약합니다. 예를 들어 "서울"로는 결과가 나오지 않습니다. 그래서 `server.py`의 `KOREAN_CITY_ALIASES` 목록에서 주요 도시의 한글 이름을 영어 이름으로 바꿔 검색합니다.

이 목록에 없는 도시는 영어로 입력하거나, 목록에 한 줄을 추가하면 됩니다.

```python
KOREAN_CITY_ALIASES = {
    "서울": "Seoul",
    "목포": "Mokpo",   # 이렇게 추가
    ...
}
```
