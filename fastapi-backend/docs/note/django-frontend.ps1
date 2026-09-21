cd C:\github\fastapi-clean-architecture-ddd-erp-iot\django-frontend

# ดูว่ามี venv กี่ตัว
Get-ChildItem -Directory -Force | Where-Object { $_.Name -match '^\.?venv$' }
# ผลลัพธ์อาจเป็น: venv  และ  .venv  (เลือกใช้ตัวเดียว)

# แนะนำ: ลบทั้ง 2 แล้วสร้างใหม่
Remove-Item -Recurse -Force .\venv, .\.venv -ErrorAction SilentlyContinue

# ลบ user site-packages ที่ pip หลงติดตั้ง (สะอาดกว่า)
Remove-Item -Recurse -Force "$env:APPDATA\Python\Python314\site-packages\Django*"     -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$env:APPDATA\Python\Python314\site-packages\httpx*"      -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$env:APPDATA\Python\Python314\site-packages\dotenv*"     -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$env:APPDATA\Python\Python314\site-packages\asgiref*"    -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$env:APPDATA\Python\Python314\site-packages\sqlparse*"   -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$env:APPDATA\Python\Python314\site-packages\httpcore*"   -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$env:APPDATA\Python\Python314\site-packages\h11*"        -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$env:APPDATA\Python\Python314\site-packages\anyio*"      -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$env:APPDATA\Python\Python314\site-packages\idna*"       -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$env:APPDATA\Python\Python314\site-packages\certifi*"    -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$env:APPDATA\Python\Python314\site-packages\sniffio*"    -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$env:APPDATA\Python\Python314\site-packages\typing_ext*" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$env:APPDATA\Python\Python314\site-packages\tzdata*"     -ErrorAction SilentlyContinue