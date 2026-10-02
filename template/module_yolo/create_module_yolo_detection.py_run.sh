# 1. ลบไฟล์เดิม (ถ้าต้องการ)
rm -rf app/modules/yolo app/modules/ai_ml

# 2. รัน generator
python create_module_yolo_detection.py all yolo 5 yolo --force

# 3. ติดตั้ง dependencies
pip install ultralytics opencv-python albumentations onnx onnxruntime

# 4. Migrate
alembic upgrade head

# 5. Run
uvicorn app.app:app --reload