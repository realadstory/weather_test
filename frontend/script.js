// 백엔드 주소
// - http://127.0.0.1:8000 으로 접속한 경우: 같은 서버이므로 "" (상대 경로)
// - index.html 파일을 더블클릭해서 연 경우(file://): 백엔드 주소를 직접 지정
const API_BASE = location.protocol === "file:" ? "http://127.0.0.1:8000" : "";

const form = document.getElementById("weather-form");
const cityInput = document.getElementById("city-input");
const searchButton = document.getElementById("search-button");
const message = document.getElementById("message");
const result = document.getElementById("result");

form.addEventListener("submit", async (event) => {
  event.preventDefault(); // 페이지 새로고침 방지

  const city = cityInput.value.trim();
  if (!city) {
    showMessage("도시 이름을 입력해 주세요.");
    return;
  }

  showMessage("날씨 정보를 불러오는 중...", true);
  result.classList.add("hidden");
  searchButton.disabled = true;

  try {
    // 우리 백엔드에 요청 (백엔드가 외부 날씨 API를 호출함)
    const response = await fetch(`${API_BASE}/api/weather?city=${encodeURIComponent(city)}`);
    const data = await response.json();

    if (!response.ok) {
      showMessage(data.error || "오류가 발생했습니다.");
      return;
    }

    showWeather(data);
    showMessage("");
  } catch (error) {
    showMessage("서버에 연결할 수 없습니다. 백엔드가 실행 중인지 확인해 주세요.");
  } finally {
    searchButton.disabled = false;
  }
});

function showWeather(data) {
  document.getElementById("city-name").textContent =
    data.country ? `${data.city}, ${data.country}` : data.city;
  document.getElementById("description").textContent = data.description;
  document.getElementById("temperature").textContent = `${Math.round(data.temperature)}°C`;
  document.getElementById("feels-like").textContent = `${Math.round(data.feels_like)}°C`;
  document.getElementById("humidity").textContent = `${data.humidity}%`;
  document.getElementById("wind-speed").textContent = `${data.wind_speed} km/h`;
  document.getElementById("updated-time").textContent =
    `기준 시각 (현지): ${data.time.replace("T", " ")}`;
  result.classList.remove("hidden");
}

function showMessage(text, isLoading = false) {
  message.textContent = text;
  message.classList.toggle("loading", isLoading);
}
