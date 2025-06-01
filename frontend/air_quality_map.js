// Kết nối WebSocket tới server
const socket = new WebSocket(`ws://${window.location.hostname}:8000/ws/air_quality`);

socket.onopen = () => {
    console.log("✅ WebSocket connected!");
};

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);

    // Nếu server báo lỗi
    if (data.error) {
        // @ts-ignore
        document.getElementById("location").innerText = "❌ Không thể tải dữ liệu chất lượng không khí.";
        return;
    }

    const { latitude, longitude, city, region, country, data_points } = data;

    // Cập nhật vị trí người dùng
    // @ts-ignore
    document.getElementById("location").innerText = `📍 Vị trí của bạn: ${city}, ${region}, ${country}`;

    // Đặt lại tâm bản đồ theo vị trí
    map.setView([latitude, longitude], 13);

    // Cập nhật bản đồ
    updateMap(data_points);
};

socket.onerror = (error) => {
    console.log(`❌ WebSocket error:`, error);
};

socket.onclose = () => {
    console.log("ℹ️ WebSocket connection closed.");
};

// Khởi tạo bản đồ
// @ts-ignore
const map = L.map('map').setView([20.0, 105.0], 5);

// @ts-ignore
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Cập nhật các điểm lên bản đồ
function updateMap(dataPoints) {
    // Xoá marker cũ
    map.eachLayer((layer) => {
        // @ts-ignore
        if (layer instanceof L.Marker) {
            map.removeLayer(layer);
        }
    });

    dataPoints.forEach((point) => {
        const { lat, lon, popup, quality, temperature, humidity, mq, dust, timestamp } = point;

        // @ts-ignore
        const marker = L.marker([lat, lon]).addTo(map);
        marker.bindPopup(popup);

        marker.on('click', () => {
            // @ts-ignore
            document.getElementById("coords").innerText = `${lat.toFixed(5)}, ${lon.toFixed(5)}`;
            // @ts-ignore
            document.getElementById("quality").innerText = quality;
            // @ts-ignore
            document.getElementById("temperature").innerText = `${temperature}°C`;
            // @ts-ignore
            document.getElementById("humidity").innerText = `${humidity}%`;
            // @ts-ignore
            document.getElementById("mq").innerText = mq;
            // @ts-ignore
            document.getElementById("dust").innerText = `${dust} µg/m³`;
            // @ts-ignore
            document.getElementById("timestamp").innerText = timestamp;
        });
    });
}

