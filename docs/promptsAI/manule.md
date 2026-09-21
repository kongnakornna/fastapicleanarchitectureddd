REM สร้างพื้นฐาน (health + example)
scaffold.bat

REM สร้าง + venv + migrate
scaffold.bat --setup

REM สร้าง + setup + run
scaffold.bat --run

REM สร้างเฉพาะ module เดียว
scaffold.bat --module forecast

REM สร้างทั้ง Layer 5 (Intelligence)
scaffold.bat --layer 5

REM สร้างทั้งหมด 65 modules
scaffold.bat --all

REM patch เฉพาะ settings/templates (แบบเดิม)
scaffold.bat --fix

REM ลบไฟล์ที่สร้างไว้ทั้งหมด
scaffold.bat --clean