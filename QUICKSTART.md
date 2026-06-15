# 🚀 Hướng dẫn Deploy Nhanh

## 📌 Tóm tắt

Có 3 cách deploy ứng dụng Steganography:

| Nền tảng | Dễ | Cách | Chi phí |
|----------|-----|------|--------|
| **Hugging Face Spaces** | ⭐⭐⭐⭐⭐ | Git push | **Miễn phí** |
| **GitHub Pages** (static) | ⭐⭐⭐ | Git push | **Miễn phí** |
| **AWS/GCP/Azure** | ⭐⭐⭐ | Docker | **Tính phí** |

---

## 🤗 **Cách 1: Hugging Face Spaces (Recommended - Dễ nhất)**

### Bước 1: Tạo tài khoản & Space

1. Truy cập [huggingface.co/spaces](https://huggingface.co/spaces)
2. Nhấp **"Create new Space"**
3. Điền:
   - **Space name**: `web-stegano`
   - **License**: Chọn `MIT`
   - **Space SDK**: Chọn **`Gradio`** ← Quan trọng!
   - Nhấp **"Create Space"**

### Bước 2: Upload code

**Cách A: Qua Git (Khuyến nghị)**

```bash
# Clone Space repo
git clone https://huggingface.co/spaces/YOUR_USERNAME/web-stegano
cd web-stegano

# Copy files
cp ../steganography.py .
cp ../app_gradio_simple.py app.py
cp ../requirements.txt .

# Đẩy lên
git add .
git commit -m "Add steganography demo"
git push
```

**Cách B: Upload trực tiếp trong Web UI**

1. Mở Space vừa tạo
2. Kích **"Files"** → **"Upload file"**
3. Upload: `steganography.py`, `app.py`, `requirements.txt`

### Bước 3: Chỉnh sửa `app.py` (nếu cần)

Hugging Face Spaces sẽ tự động phát hiện `app.py` với Gradio. Nếu không chạy:

1. Mở file `app.py` trong Space
2. Sửa dòng cuối:

```python
if __name__ == "__main__":
    demo.launch()  # Xóa server_name, server_port
```

3. Nhấp **"Commit changes"**

### ✅ Xong! Space sẽ tự động chạy

URL của bạn: `https://huggingface.co/spaces/YOUR_USERNAME/web-stegano`

---

## 💻 **Cách 2: GitHub + Render/Railway (Miễn phí)**

### Bước 1: Push lên GitHub

```bash
git init
git add .
git commit -m "Initial: Steganography web demo"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/web-stegano.git
git push -u origin main
```

### Bước 2: Deploy lên Render

1. Truy cập [render.com](https://render.com)
2. Nhấp **"New +"** → **"Web Service"**
3. Chọn repo GitHub
4. Điền:
   - **Name**: `web-stegano`
   - **Runtime**: `Python 3`
   - **Build command**: `pip install -r requirements.txt`
   - **Start command**: `python app_gradio_simple.py`
   - Nhấp **"Create Web Service"**

### ✅ Xong! URL sẽ được cấp tự động

---

## 🐳 **Cách 3: Docker (VPS/Cloud)**

### Bước 1: SSH vào máy chủ

```bash
ssh root@YOUR_SERVER_IP
```

### Bước 2: Clone repo

```bash
cd /opt
git clone https://github.com/YOUR_USERNAME/web-stegano.git
cd web-stegano
```

### Bước 3: Build & chạy Docker

```bash
# Build image
docker build -t steganography-app .

# Chạy container
docker run -d -p 80:7860 --name stegano steganography-app
```

### ✅ Xong! Truy cập: `http://YOUR_SERVER_IP`

---

## 🏠 **Cách 4: Chạy cục bộ (Development)**

```bash
# Setup
python -m venv .venv
.\.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Mac/Linux

# Install
python -m pip install -r requirements.txt

# Run
python app_gradio_simple.py
```

Truy cập: `http://localhost:7860`

---

## 📝 File quan trọng cho mỗi cách deploy

| File | Hugging Face | GitHub | Docker | Local |
|------|--------------|--------|--------|-------|
| `app_gradio_simple.py` | ✅ | ✅ | ✅ | ✅ |
| `steganography.py` | ✅ | ✅ | ✅ | ✅ |
| `requirements.txt` | ✅ | ✅ | ✅ | ✅ |
| `Dockerfile` | ❌ | ❌ | ✅ | ❌ |

---

## 🔗 So sánh nhanh

### Hugging Face Spaces

**✅ Ưu điểm:**
- Không cần server riêng
- Miễn phí unlimited
- Tự động HTTPS
- Dễ share link

**❌ Nhược điểm:**
- Chậm nếu Space "sleep"
- Hạn chế tài nguyên

### Docker + VPS

**✅ Ưu điểm:**
- Điều khiển toàn bộ
- Tốc độ nhanh
- Có thể tùy chỉnh

**❌ Nhược điểm:**
- Cần trả tiền VPS ($5-20/tháng)
- Phải quản lý server

### GitHub + Render

**✅ Ưu điểm:**
- Miễn phí
- Tự động deploy (push GitHub = auto update)
- HTTPS tự động

**❌ Nhược điểm:**
- Render "sleep" sau 15 phút không dùng
- Cần GitHub account

---

## 🆘 Troubleshooting

### "pip.exe blocked" trên Windows

```bash
python -m pip install -r requirements.txt
```

### Port 7860 bị chiếm

```bash
python app_gradio_simple.py --server_port=8000
```

### Lỗi "gradio not installed"

```bash
python -m pip install gradio
```

### Hugging Face Space không chạy

1. Kiểm tra logs: **"Settings"** → **"Logs"**
2. Đảm bảo `app.py` tồn tại ở root
3. Kiểm tra `requirements.txt` không lỗi

---

## 📞 Hỗ trợ

- Hugging Face: [huggingface.co/docs/hub/spaces](https://huggingface.co/docs/hub/spaces)
- Render: [render.com/docs](https://render.com/docs)
- Docker: [docker.com/docs](https://docker.com/docs)
- Gradio: [gradio.app/docs](https://gradio.app/docs)
