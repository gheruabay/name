const socket = new WebSocket(`ws://${window.location.host}/ws/data`);



function getAQIClass(aqi) {
    if (aqi <= 50) return 'aqi-good';
    if (aqi <= 100) return 'aqi-moderate';
    if (aqi <= 150) return 'aqi-unhealthy1';
    if (aqi <= 200) return 'aqi-unhealthy2';
    if (aqi <= 300) return 'aqi-verybad';
    return 'aqi-hazardous';
}

function updateUI(data) {
    const circle = document.getElementById("aqiCircle");
    const value = document.getElementById("aqiValue");
    const status = document.getElementById("aqiStatus");
    const quality = document.getElementById("qualityText");

    // Reset class
    // @ts-ignore
    circle.className = 'aqi-circle';

    // Update AQI
    // @ts-ignore
    value.textContent = data.aqi;
    const aqiClass = getAQIClass(data.aqi);
    // @ts-ignore
    circle.classList.add(aqiClass);

    // Status & text
    // @ts-ignore
    status.textContent = data.quality;
    // @ts-ignore
    

    // Others
    // @ts-ignore
    document.getElementById("pm10").textContent = data.dust;
    // @ts-ignore
    document.getElementById("pm25").textContent = (data.dust / 2 ).toFixed(1); // giả định
    // @ts-ignore
    document.getElementById("mq").textContent = data.mq;
    // @ts-ignore
    document.getElementById("temperature").textContent = data.temperature;
    // @ts-ignore
    document.getElementById("humidity").textContent = data.humidity;
    // @ts-ignore
    
}

socket.onmessage = function (event) {
    const data = JSON.parse(event.data);
    console.log("📡 Dữ liệu nhận được từ WebSocket:", data);  // ← ở đây
    updateUI(data);
};


socket.onerror = function (error) {
    console.error("WebSocket Error:", error);
};

socket.onclose = function () {
    console.log("WebSocket disconnected.");
};
