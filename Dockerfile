# از تصویر رسمی پایتون ۳.۱۰ استفاده کن
FROM python:3.10-slim

# تنظیمات اولیه
WORKDIR /app
COPY . /app

# نصب کتابخانه‌ها
RUN pip install --no-cache-dir -r requirements.txt

# اجرای فایل اصلی
CMD ["python", "main.py"]
