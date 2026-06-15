# 🔐 Web Steganography Demo

Ứng dụng web đơn giản để ẩn và giải mã tin nhắn trong ảnh bằng phương pháp **LSB (Least Significant Bit)**.

Giao diện Gradio + API FastAPI, dễ triển khai lên **GitHub**, **Hugging Face Spaces**, hoặc **máy chủ riêng**.

## 📁 Cấu trúc dự án

```
.
├── app.py                  # Ứng dụng Gradio + FastAPI
├── steganography.py        # Thư viện encode/decode LSB
├── requirements.txt        # Thư viện Python cần cài
├── Dockerfile              # Triển khai với Docker
├── docker-compose.yml      # Docker Compose config
├── README.md               # Tài liệu này
└── .gitignore              # Loại trừ file tạm
```

## 🚀 Chạy cục bộ

### 1. Chuẩn bị môi trường

```bash
# Tạo virtual environment
python -m venv .venv

# Kích hoạt (Windows)
.venv\Scripts\activate

# Kích hoạt (Mac/Linux)
source .venv/bin/activate
```

### 2. Cài đặt dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Chạy ứng dụng

```bash
python app.py
```

Mở trình duyệt: **http://localhost:7860**

## 🐳 Chạy với Docker

```bash
# Xây dựng image
docker build -t steganography-app .

# Chạy container
docker run -p 7860:7860 steganography-app
```

Hoặc dùng Docker Compose:

```bash
docker-compose up
```

## 📤 Triển khai lên GitHub

### 1. Tạo repository trên GitHub

```bash
git init
git add .
git commit -m "Initial commit: Steganography web demo"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/web-stegano.git
git push -u origin main
```

## 🤗 Triển khai lên Hugging Face Spaces

### Cách 1: Dùng Gradio Spaces (Dễ nhất)

1. Truy cập [Hugging Face Spaces](https://huggingface.co/spaces)
2. Nhấp **"Create new Space"**
3. Chọn **"Gradio"** làm SDK
4. Tạo Space
5. Đẩy code:

```bash
git clone https://huggingface.co/spaces/YOUR_USERNAME/web-stegano
cd web-stegano
git add .
git commit -m "Add steganography demo"
git push
```

6. Hugging Face sẽ tự động phát hiện `app.py` và chạy nó

### Cách 2: Dùng Docker Spaces

1. Tạo Space mới chọn **"Docker"**
2. Đẩy `Dockerfile`, `requirements.txt`, `app.py`, `steganography.py`
3. Hugging Face tự động build và deploy

## 💻 API Endpoints (nếu dùng FastAPI)

### POST /encode

Ẩn tin nhắn vào ảnh.

**Tham số:**
- `cover_image`: file ảnh (PNG/JPEG)
- `message`: văn bản cần ẩn

**Ví dụ:**

```bash
curl -X POST "http://localhost:7860/encode" \
  -F "cover_image=@cover.png" \
  -F "message=Hello World" \
  --output stego.png
```

### POST /decode

Giải mã tin nhắn từ ảnh.

**Tham số:**
- `stego_image`: file ảnh có chứa tin nhắn

**Ví dụ:**

```bash
curl -X POST "http://localhost:7860/decode" \
  -F "stego_image=@stego.png"
```

## 🌐 Triển khai lên máy chủ (VPS/Cloud)

### AWS EC2 / DigitalOcean / Linode

1. SSH vào máy chủ
2. Clone repo:

```bash
git clone https://github.com/YOUR_USERNAME/web-stegano.git
cd web-stegano
```

3. Cài đặt Docker (nếu chưa có):

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

4. Build và chạy:

```bash
docker build -t stegano .
docker run -d -p 80:7860 stegano
```

5. Truy cập qua IP hoặc tên miền: `http://your-server-ip`

## 📝 Cách sử dụng giao diện Gradio

### Tab "Encode" (Ẩn tin nhắn)

1. Chọn **"Ảnh gốc (Cover)"**
2. Nhập **"Tin nhắn cần ẩn"**
3. Nhấp **"🔒 Ẩn tin nhắn"**
4. Tải về **ảnh có chứa tin nhắn (Stego)**

### Tab "Decode" (Giải mã)

1. Chọn **"Ảnh có chứa tin nhắn (Stego)"**
2. Nhấp **"🔓 Giải mã"**
3. Xem **kết quả giải mã**

## ⚙️ Tùy chỉnh

### Đổi cổng mặc định

Sửa trong `app.py`:

```python
demo.launch(server_name="0.0.0.0", server_port=5000)  # Thay 7860 bằng 5000
```

### Đổi tên ứng dụng

Sửa tiêu đề Gradio:

```python
with gr.Blocks(title="Tên ứng dụng của tôi"):
```

## 🔒 Bảo mật

- Hiện tại là **demo đơn giản**, không có xác thực
- Để production, thêm:
  - Authentication (JWT tokens)
  - Rate limiting
  - HTTPS/TLS
  - File size validation

## 📊 Giới hạn

- **Kích thước ảnh tối thiểu**: 256×256 pixels (để chứa ~8KB tin nhắn)
- **Định dạng hỗ trợ**: PNG, JPEG
- **Tốc độ**: Thường < 1 giây/ảnh

## 🐛 Troubleshooting

### Lỗi "python-multipart" not installed

```bash
python -m pip install python-multipart
```

### Lỗi "0.0.0.0 is not a valid URL"

Dùng `localhost` hoặc `127.0.0.1` trong trình duyệt:
```
http://localhost:7860
```

### Port 7860 đã bị chiếm

```bash
python app.py --port 8000
```

## 📚 Tham khảo

- [Gradio Docs](https://gradio.app)
- [Hugging Face Spaces](https://huggingface.co/spaces)
- [Docker Docs](https://docs.docker.com)
- [LSB Steganography](https://en.wikipedia.org/wiki/Steganography)

## 📄 License

MIT License - Tự do sử dụng, sửa đổi, phân phối

## 👨‍💻 Tác giả

Tạo bởi: Web Steganography Demo Project
