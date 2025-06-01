async function fetchForecast() {
  try {
    const response = await fetch(`http://${window.location.hostname}:8000/api/forecast`);
    if (!response.ok) throw new Error("HTTP error " + response.status);

    const data = await response.json();
    console.log("Dữ liệu trả về từ API:", data);

    const forecast = data.forecast;

    if (!forecast || !Array.isArray(forecast)) {
      throw new Error("Dữ liệu forecast không hợp lệ hoặc không tồn tại");
    }

    const tableBody = document.getElementById("forecast-table-body");
    if (!tableBody) {
      console.error("Không tìm thấy phần tử #forecast-table-body");
      return;
    }

    tableBody.innerHTML = ""; // Xoá dữ liệu cũ

    forecast.forEach(item => {
      const row = document.createElement("tr");

      const pm10 = item.dust;
      const pm25 = item.dust / 2 ;  // Theo yêu cầu

      row.innerHTML = `
        <td>${item.timestamp}</td>
        <td>${item.temperature.toFixed(2)}</td>
        <td>${item.humidity.toFixed(2)}</td>
        <td>${item.mq.toFixed(2)}</td>
        <td>${pm10.toFixed(2)}</td>
        <td>${pm25.toFixed(2)}</td>
        <td>${item.aqi || 'N/A'}</td>
        <td>${item.chat_luong || 'N/A'}</td>
      `;

      tableBody.appendChild(row);
    });

  } catch (error) {
    console.error("Lấy dữ liệu dự báo lỗi:", error);
  }
}

window.addEventListener("DOMContentLoaded", fetchForecast);
