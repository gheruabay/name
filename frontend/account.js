document.addEventListener("DOMContentLoaded", async () => {
  const storedEmail = localStorage.getItem("user_email");
  const storedName = localStorage.getItem("user_name");

  if (storedEmail) {
    // @ts-ignore
    document.getElementById("email").value = storedEmail;
  }
  if (storedName) {
    // @ts-ignore
    document.getElementById("name").value = storedName;
  }

  if (!storedEmail) {
    // @ts-ignore
    showNotification("⚠️ Bạn chưa đăng nhập.");
    return;
  }

  try {
    const res = await fetch("/api/user/info", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        email: storedEmail,
      },
    });

    const data = await res.json();

    if (!res.ok) {
      // @ts-ignore
      showNotification("Oh no " + (data.detail || "Kekekekeke."));
      return;
    }

    // @ts-ignore
    document.getElementById("name").value = data.name || storedName || "";
    // @ts-ignore
    document.getElementById("email").value = data.email || storedEmail || "";

    const tbody = document.querySelector("table tbody");
    // @ts-ignore
    tbody.innerHTML = "";

    if (Array.isArray(data.history) && data.history.length > 0) {
      data.history.forEach((row) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${row.created_at}</td>
  <td>${row.temperature}</td>
  <td>${row.humidity}</td>
  <td>${row.dust}</td>
  <td>${row.mq}</td>
  <td>${row.aqi}</td>
  <td>${row.chat_luong}</td>
        `;
        // @ts-ignore
        tbody.appendChild(tr);
      });
    } else {
      // @ts-ignore
      showNotification("📭 Không có lịch sử đo.");
    }
  } catch (err) {
    console.error("Lỗi khi tải dữ liệu:", err);
    // @ts-ignore
    showNotification("🚫 Không thể tải dữ liệu tài khoản.");
  }
});
