# Sử dụng Python 3.11
FROM python:3.11-slim

# Đặt thư mục làm việc
WORKDIR /app

# Copy file requirements và cài thư viện
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ project vào container
COPY . .

# Mở port 10000 (Render thường dùng)
EXPOSE 10000

# Chạy server FastAPI bằng uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
