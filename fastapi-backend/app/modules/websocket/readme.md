# ติดตั้ง (ถ้ายังไม่มี)
winget install websocat

# Login ก่อน (บันทึก cookie ลงไฟล์)
curl -X POST http://localhost:8000/api/v1/authentication/login/ `
  -H "Content-Type: application/x-www-form-urlencoded" `
  -d "username=johndoe@example.com&password=MyP@ssword123" `
  -c cookies.txt

# ดู cookie
Get-Content cookies.txt

# เชื่อมต่อ (แทน <SESSION_ID> ด้วยค่าจริง)
websocat -H="Cookie: hub_session_id=<SESSION_ID>" `
  ws://localhost:8000/api/v1/websocket/connect/
