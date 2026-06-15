FROM python:3.11-slim

WORKDIR /app

# Cài đặt dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy mã nguồn
COPY app.py .
COPY steganography.py .
COPY steganography_gan.py .
COPY models ./models

# Expose port
EXPOSE 7860

# Chạy ứng dụng
CMD ["python", "app.py"]
