-- =====================================================================
-- V005__seed_yolo_diseases.sql
-- =====================================================================
BEGIN;

INSERT INTO "public"."yolo_diseases"
    (code, name_th, name_en, pathogen_type, description,
     treatment_json, prevention_json)
VALUES
    ('rice-blast',
     'โรคไหม้ข้าว',
     'Rice Blast',
     'fungal',
     'โรคที่เกิดจากเชื้อรา Pyricularia oryzae',
     '["พ่น tricyclazole 20% WP","ลดปุ๋ยไนโตรเจน"]'::jsonb,
     '["ใช้พันธุ์ต้านทาน","ไม่ปลูกหนาแน่น"]'::jsonb),

    ('tomato-late-blight',
     'โรคใบไหม้มะเขือเทศ',
     'Tomato Late Blight',
     'fungal',
     'โรคที่เกิดจาก Phytophthora infestans',
     '["พ่น chlorothalonil","ตัดใบที่เป็นโรค"]'::jsonb,
     '["ระบายอากาศดี","หลีกเลี่ยงรดน้ำใบ"]'::jsonb),

    ('bacterial-leaf-blight',
     'โรคใบข้าวแห้ง',
     'Bacterial Leaf Blight',
     'bacterial',
     'โรคที่เกิดจาก Xanthomonas oryzae',
     '["ใช้ copper hydroxide","ระบายน้ำ"]'::jsonb,
     '["ไม่ใส่ปุ๋ยไนโตรเจนเกิน","ใช้พันธุ์ต้านทาน"]'::jsonb)
ON CONFLICT (code) DO NOTHING;

COMMIT;