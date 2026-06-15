# 🔐 Web Steganography Demo

**Ứng dụng web để ẩn và giải mã tin nhắn bên trong ảnh bằng phương pháp LSB.**

[![Deploy to Hugging Face](https://img.shields.io/badge/Deploy%20to-Hugging%20Face-FFD21E?style=flat&logo=huggingface)](https://huggingface.co/spaces)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat&logo=python)](https://www.python.org/)
[![License MIT](https://img.shields.io/badge/License-MIT-green?style=flat)](LICENSE)

## 🚀 Bắt đầu nhanh (30 giây)

### Chạy cục bộ

```bash
# 1. Cài đặt dependencies
pip install -r requirements.txt

# 2. Chạy ứng dụng
python app_gradio_simple.py

# 3. Mở trình duyệt
# http://localhost:7860
```

### Deploy lên Hugging Face Spaces

Xem **[QUICKSTART.md](QUICKSTART.md)** để deploy miễn phí lên **Hugging Face Spaces** trong 5 phút!

## 📁 Dự án có

```
web-stegano/
├── app_gradio_simple.py    # Gradio UI (dùng cho Hugging Face)
├── app.py                   # FastAPI + Gradio (full API)
├── steganography.py         # LSB encode/decode
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker deployment
├── docker-compose.yml       # Docker Compose
├── QUICKSTART.md            # Deploy guide (⭐ Start here!)
├── DEPLOY.md                # Chi tiết deploy
└── README.md                # File này
```

## 💡 Cách sử dụng

### 🔒 Ẩn tin nhắn trong ảnh

1. **Upload ảnh gốc** (PNG hoặc JPEG)
2. **Nhập tin nhắn** cần ẩn
3. **Tải ảnh kết quả** chứa tin nhắn ẩn

### 🔓 Giải mã tin nhắn từ ảnh

1. **Upload ảnh** chứa tin nhắn
2. **Xem kết quả** tin nhắn giải mã

## 🌐 Deploy (Chọn 1 cách)

| Nền tảng | Chi phí | Dễ | Link |
|----------|--------|-----|------|
| **Hugging Face Spaces** | Miễn phí | ⭐⭐⭐⭐⭐ | [Hướng dẫn](QUICKSTART.md#-cách-1-hugging-face-spaces-recommended---dễ-nhất) |
| **Docker + VPS** | $5-20/tháng | ⭐⭐⭐ | [Hướng dẫn](QUICKSTART.md#-cách-3-docker-vpcloud) |
| **GitHub + Render** | Miễn phí | ⭐⭐⭐⭐ | [Hướng dẫn](QUICKSTART.md#-cách-2-github--renderrailway-miễn-phí) |

👉 **Khuyên dùng: Hugging Face Spaces** (miễn phí, dễ, tự động HTTPS)

## 🔧 Cài đặt cục bộ (Chi tiết)

### 1️⃣ Clone hoặc download dự án

```bash
git clone https://github.com/YOUR_USERNAME/web-stegano.git
cd web-stegano
```

### 2️⃣ Tạo virtual environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3️⃣ Cài đặt gói

```bash
pip install -r requirements.txt
```

### 4️⃣ Chạy ứng dụng

```bash
# Chỉ Gradio UI (nhẹ nhàng)
python app_gradio_simple.py

# Hoặc FastAPI + Gradio + API
python app.py
```

### 5️⃣ Mở trình duyệt

```
http://localhost:7860
```

## 📋 Yêu cầu hệ thống

- **Python**: 3.8 hoặc cao hơn
- **RAM**: 512MB tối thiểu
- **Disk**: 200MB (bao gồm venv)

## 🐳 Docker (1 dòng lệnh)

```bash
docker build -t stegano . && docker run -p 7860:7860 stegano
```

## 📚 Tài liệu chi tiết

- **[QUICKSTART.md](QUICKSTART.md)** - Deploy guide (3 cách)
- **[DEPLOY.md](DEPLOY.md)** - Hướng dẫn deploy chi tiết + API

## 🔐 Bảo mật & Hạn chế

⚠️ **Đây là demo giáo dục:**
- Sử dụng LSB cơ bản (không bảo vệ theo tiêu chuẩn)
- Không có mã hóa tích hợp
- Phù hợp để học tập, không dùng cho dữ liệu nhạy cảm

📊 **Giới hạn kỹ thuật:**
- Ảnh phải ≥ 256×256 pixels
- Tin nhắn tối đa ~8KB trên ảnh 1024×1024
- Hỗ trợ PNG, JPEG

## 🛠️ Tùy chỉnh

### Đổi cổng
```python
# Trong app_gradio_simple.py, dòng cuối
demo.launch(server_port=8000)  # Thay 7860 → 8000
```

### Đổi tên app
```python
# Trong app_gradio_simple.py
with gr.Blocks(title="Tên ứng dụng của bạn"):
```

## 🆘 Gặp lỗi?

| Lỗi | Giải pháp |
|-----|----------|
| `ModuleNotFoundError: gradio` | `pip install gradio` |
| `ModuleNotFoundError: PIL` | `pip install pillow` |
| `Port 7860 đã chiếm` | `python app_gradio_simple.py --server_port=8000` |
| `0.0.0.0 not valid URL` | Dùng `localhost:7860` hoặc `127.0.0.1:7860` |

## 📖 API Endpoints (nếu dùng `app.py`)

### POST `/encode`
```bash
curl -X POST "http://localhost:7860/encode" \
  -F "cover_image=@cover.png" \
  -F "message=Hello" \
  --output stego.png
```

### POST `/decode`
```bash
curl -X POST "http://localhost:7860/decode" \
  -F "stego_image=@stego.png"
```

## 📄 License

MIT License - Tự do sử dụng, sửa đổi, phân phối

## 👋 Hỗ trợ

- GitHub Issues: Report bugs
- Discussions: Hỏi đáp
- [Gradio Docs](https://gradio.app)
- [Hugging Face Docs](https://huggingface.co/docs)

---

**⭐ Nếu thích dự án, hãy Star trên GitHub!**

**👉 [Deploy ngay lên Hugging Face](QUICKSTART.md)**
