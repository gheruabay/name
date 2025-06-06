// Bắt sự kiện submit form đăng nhập hoặc đăng ký
// @ts-ignore
document.getElementById('auth-form').addEventListener('submit', async function (e) {
  e.preventDefault();

  const errorDiv = document.getElementById('error-message');
  // @ts-ignore
  errorDiv.textContent = ''; // Xóa lỗi cũ nếu có

  // @ts-ignore
  const formType = document.querySelector('.tab.active').dataset.form;
  // @ts-ignore
  const email = document.getElementById('email').value.trim();
  // @ts-ignore
  const password = document.getElementById('password').value.trim();

  if (!email || !password) {
    // @ts-ignore
    errorDiv.textContent = 'Vui lòng nhập đầy đủ thông tin';
    return;
  }

  let payload = { email, password };

  if (formType === 'register') {
    // @ts-ignore
    const name = document.getElementById('name').value.trim();
    // @ts-ignore
    const confirmPassword = document.getElementById('confirm-password').value.trim();
    if (!name || password !== confirmPassword) {
      // @ts-ignore
      errorDiv.textContent = 'Mật khẩu không khớp hoặc thiếu thông tin';
      return;
    }
    payload.name = name;
  }

  const endpoint = formType === 'login' ? '/api/auth/login' : '/api/auth/register';

  try {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    console.log("Response data:", data);

    if (res.ok) {
      // Nếu data.token là object, lấy token, email, name từ trong token object
      let tokenToStore = "";
      let emailToStore = "";
      let nameToStore = "";

      if (typeof data.token === "string") {
        // token là string, email và name lấy ở ngoài data
        tokenToStore = data.token;
        emailToStore = data.email || "";
        nameToStore = data.name || "";
      } else if (typeof data.token === "object" && data.token !== null) {
        // token là object chứa các trường bên trong
        tokenToStore = data.token.token || "";
        emailToStore = data.token.email || "";
        nameToStore = data.token.name || "";
      }

      localStorage.setItem('token', tokenToStore);
      localStorage.setItem('user_email', emailToStore);
      localStorage.setItem('user_name', nameToStore);

      // Lấy lại để kiểm tra
      const storedToken = localStorage.getItem('token');
      const storedEmail = localStorage.getItem('user_email');
      const storedName = localStorage.getItem('user_name');

      console.log("✔️ Token đã lưu:", storedToken);
      console.log("📧 Email đã lưu:", storedEmail);
      console.log("👤 Tên người dùng đã lưu:", storedName);

      // Nếu muốn redirect sau đăng nhập thành công, bỏ comment dòng dưới:
       window.location.href = '/index';
    } else {
      // @ts-ignore
      errorDiv.textContent = data.detail || 'Đã xảy ra lỗi';
    }
  } catch (err) {
    // @ts-ignore
    errorDiv.textContent = 'Lỗi kết nối đến server';
    console.error(err);
  }
});
