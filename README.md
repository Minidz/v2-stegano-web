# Web Steganography Demo API

Một demo web API đơn giản để ẩn và giải mã tin nhắn trong ảnh bằng phương pháp LSB (Least Significant Bit).

## Tệp chính

- `app.py`: ứng dụng FastAPI với 2 endpoint `/encode` và `/decode`
- `steganography.py`: hàm encode/decode hình ảnh
- `requirements.txt`: các thư viện cần cài

## Cài đặt

1. Tạo môi trường Python và cài gói:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

2. Chạy server:

```bash
python app.py
```

Server sẽ chạy ở `http://127.0.0.1:7860`.

## Giao diện web

Sau khi chạy, mở `http://127.0.0.1:7860` để vào giao diện Gradio.

- Tab `Encode`: upload ảnh và nhập tin nhắn
- Tab `Decode`: upload ảnh stego và đọc tin nhắn

## API

### POST /encode

- `cover_image`: file ảnh PNG hoặc JPEG
- `message`: nội dung văn bản muốn ẩn

Trả về ảnh PNG chứa tin nhắn ẩn.

Ví dụ dùng `curl`:

```bash
curl -X POST "http://localhost:7860/encode" \
  -F "cover_image=@cover.png" \
  -F "message=Hello from steganography" \
  --output stego.png
```

### POST /decode

- `stego_image`: file ảnh PNG hoặc JPEG đã chứa tin nhắn

Trả về JSON chứa tin nhắn giải mã.

Ví dụ dùng `curl`:

```bash
curl -X POST "http://localhost:7860/decode" \
  -F "stego_image=@stego.png"
```

## Triển khai lên GitHub

1. Khởi tạo repo Git trong thư mục này:

```bash
git init
git add .
git commit -m "Add steganography API demo"
```

2. Đẩy lên GitHub bằng remote của bạn.

## Triển khai lên Hugging Face

Hugging Face Spaces có thể chạy ứng dụng Python nếu bạn sử dụng một Space Docker hoặc Spaces hỗ trợ FastAPI. Cách nhanh nhất:

1. Tạo repository Space mới.
2. Đặt `app.py` và `requirements.txt` vào root của Space.
3. Thiết lập Space để khởi chạy `python app.py`.

> Nếu Space không hỗ trợ FastAPI trực tiếp, bạn có thể dùng Docker tùy chỉnh hoặc triển khai API trên một máy chủ khác và phơi ra từ Hugging Face Inference Endpoint.

## Ghi chú

- Đây là demo đơn giản; thuật toán sử dụng LSB để viết tin nhắn vào bit thấp nhất của mỗi kênh màu.
- Dữ liệu được lưu trữ trong các pixel đầu tiên của ảnh.
