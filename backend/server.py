"""
간단한 날씨 백엔드 서버 (Python 표준 라이브러리만 사용)

- GET /api/weather?city=도시이름  -> 현재 날씨 JSON 반환
- 그 외 경로                      -> frontend 폴더의 정적 파일 제공

날씨 데이터: Open-Meteo (https://open-meteo.com) - API Key 불필요
"""

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

HOST = "127.0.0.1"
PORT = 8000

# frontend 폴더 경로 (backend 폴더와 같은 위치에 있는 frontend)
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# Open-Meteo 날씨 코드(WMO) -> 한국어 설명
WEATHER_CODES = {
    0: "맑음",
    1: "대체로 맑음",
    2: "부분적으로 흐림",
    3: "흐림",
    45: "안개",
    48: "서리 안개",
    51: "약한 이슬비",
    53: "이슬비",
    55: "강한 이슬비",
    56: "약한 어는 이슬비",
    57: "강한 어는 이슬비",
    61: "약한 비",
    63: "비",
    65: "강한 비",
    66: "약한 어는 비",
    67: "강한 어는 비",
    71: "약한 눈",
    73: "눈",
    75: "강한 눈",
    77: "싸락눈",
    80: "약한 소나기",
    81: "소나기",
    82: "강한 소나기",
    85: "약한 눈 소나기",
    86: "강한 눈 소나기",
    95: "뇌우",
    96: "약한 우박을 동반한 뇌우",
    99: "강한 우박을 동반한 뇌우",
}


# Open-Meteo 지오코딩은 한글 검색이 약해서("서울" 검색 결과 없음 등)
# 자주 쓰는 국내 도시는 영어 이름으로 바꿔서 검색한다.
KOREAN_CITY_ALIASES = {
    "서울": "Seoul",
    "부산": "Busan",
    "인천": "Incheon",
    "대구": "Daegu",
    "대전": "Daejeon",
    "광주": "Gwangju",
    "울산": "Ulsan",
    "세종": "Sejong",
    "수원": "Suwon",
    "제주": "Jeju City",
    "전주": "Jeonju",
    "창원": "Changwon",
    "포항": "Pohang",
    "강릉": "Gangneung",
    "춘천": "Chuncheon",
    "청주": "Cheongju",
    "천안": "Cheonan",
    "도쿄": "Tokyo",
    "오사카": "Osaka",
    "베이징": "Beijing",
    "상하이": "Shanghai",
    "뉴욕": "New York",
    "런던": "London",
    "파리": "Paris",
}


def fetch_json(url, params):
    """URL에 GET 요청을 보내고 JSON 결과를 돌려준다."""
    full_url = url + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(full_url, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def get_weather(city):
    """도시 이름으로 좌표를 찾은 뒤, 해당 좌표의 현재 날씨를 가져온다."""
    # 1) 도시 이름 -> 위도/경도
    # "서울시", "부산광역시"처럼 입력해도 별칭을 찾을 수 있게 접미사를 떼고 비교
    short_name = city.removesuffix("특별시").removesuffix("광역시").removesuffix("시")
    search_name = KOREAN_CITY_ALIASES.get(city) or KOREAN_CITY_ALIASES.get(short_name, city)
    geo = fetch_json(GEOCODING_URL, {"name": search_name, "count": 1, "language": "ko"})
    results = geo.get("results")
    if not results:
        return None

    place = results[0]

    # 2) 위도/경도 -> 현재 날씨
    forecast = fetch_json(FORECAST_URL, {
        "latitude": place["latitude"],
        "longitude": place["longitude"],
        "current": "temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,wind_speed_10m",
        "timezone": "auto",
    })
    current = forecast["current"]
    code = current["weather_code"]

    return {
        "city": place.get("name", city),
        "country": place.get("country", ""),
        "time": current["time"],
        "temperature": current["temperature_2m"],
        "feels_like": current["apparent_temperature"],
        "humidity": current["relative_humidity_2m"],
        "wind_speed": current["wind_speed_10m"],
        "weather_code": code,
        "description": WEATHER_CODES.get(code, "알 수 없음"),
    }


class WeatherHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # 정적 파일은 frontend 폴더에서 제공
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/weather":
            self.handle_weather(parsed.query)
        else:
            super().do_GET()

    def handle_weather(self, query):
        city = urllib.parse.parse_qs(query).get("city", [""])[0].strip()
        if not city:
            self.send_json(400, {"error": "도시 이름을 입력해 주세요."})
            return

        try:
            data = get_weather(city)
        except (urllib.error.URLError, TimeoutError, KeyError, ValueError) as e:
            print("날씨 API 오류:", e)
            self.send_json(502, {"error": "날씨 정보를 가져오지 못했습니다. 잠시 후 다시 시도해 주세요."})
            return

        if data is None:
            self.send_json(404, {"error": f"'{city}' 도시를 찾을 수 없습니다."})
            return

        self.send_json(200, data)

    def send_json(self, status, body):
        payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        # index.html을 파일로 직접 연 경우(file://)에도 요청을 허용 (CORS)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(payload)


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), WeatherHandler)
    print(f"서버 실행 중: http://{HOST}:{PORT}  (종료: Ctrl+C)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n서버를 종료합니다.")
        server.server_close()
