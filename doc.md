# 1. สร้าง folder
New-Item -ItemType Directory -Force -Path postman

# 2. Save 2 JSON files ตามด้านบน

# 3. เปิด Postman
# Import → drop folder → ทั้ง 2 ไฟล์จะถูก import
# เลือก environment "Local (FastAPI Clean Arch)"
# รัน Sign Up → Login → Get Me



# 1. สร้าง app/core/swagger.py (ตาม 3.1)

# 2. แก้ app/app.py เพิ่ม configure_openapi(app)

# 3. Restart server
make dev

# 4. เปิด http://localhost:8000/docs
#    - ควรเห็น tags 3 กลุ่ม: Health, Authentication, User
#    - ปุ่ม Authorize มี CookieAuth, BearerAuth, ApiKeyAuth
#    - Contact info ปรากฏที่หัว
