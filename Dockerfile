# Sử dụng image Python chính thức
FROM python:3.11-slim

# Đặt thư mục làm việc
WORKDIR /app

# Copy toàn bộ file dự án vào container
COPY . .

# Cài đặt các thư viện cần thiết
RUN pip install --no-cache-dir -r requirements.txt

# Mở cổng 10000 (Render mặc định sẽ map port này)
EXPOSE 10000

# Chạy ứng dụng bằng Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
