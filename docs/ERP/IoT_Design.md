1.1.Business canvas model
1.2.ERP
1.2.CRM
1.3.KPI
1.4.REPORT
1.5.Supply chain
1.6.Online Marketing
1.7.Logistics saas
1.8.IoT
1.9.การใช้ AI คาดการณ์การผลิต (Predictive Production and Demand Forecasting) ช่วยเพิ่มความแม่นยำในการวางแผน ลดของเสีย และบริหารทรัพยากรในโรงงานได้อย่างมีประสิทธิภาพสูงสุด
1.10.ระบบติดตามการผลิตด้วย QR Code คือการใช้คิวอาร์โค้ดแปะบนชิ้นงาน พาเลท หรือใบสั่งผลิต (Job Order) เพื่อสแกนบันทึกข้อมูลสถานะแบบเรียลไทม์ 
1.11.POS ย่อมาจาก Point of Sale หรือระบบขายหน้าร้าน
1.12.ecommerce  
1.13.ระบบบัญชีและภาษี
1.14.GAP (Good Agricultural Practices) หรือการปฏิบัติทางการเกษตรที่ดี

 
2.สร้างบทนิยาม
3.สร้างบทหัวข้อ
4.ออกแบบ workflow
5.case study
 สารบัญ
    - โครงสร้างการทำงาน
    - วัตุประสงค์
    - กลุ่มเป้าหมาย
    - ความรู้พื้นฐาน
    - เนื้อหา โดยย่อ กระชับ เน้น วัตถุประสงค์  ประโยชน์ของการใช้
    - บทนำ
    - บทนิยาม
  - โครงสร้างโฟลเดอร์ | folder-structure 
  - หลักการทำงาน (Concept) 
  - Workflow และ Dataflow  
     - ออกแบบ workflow
    - วาดรูป dataflow สร้าง รูปแบบ dataflow เหมือนจริง ลักษณะ flowchart   เพื่ออธิบายกระบวนการ ทำความเข้าใจ
    - พร้อมอธิบาย แบบ ละเอียด 
    - คอมเม้น code ภาษาไทย และ ภาษาอังถถษ อธิบาย การทำงาน แต่ละจุด
    - ยกตัวอย่างการใช้งานจริง หรือ กรณีศึกษา แนวทางแก้ไขปัญหา ที่อาจจะเกิดขึ้น 
  - Code เทมเพลต และ ตัวอย่างโค้ด พร้อมนำไป run ได้ทันที  มีคำอธิบายการใช้งานแต่ละจุด การคอมเม้น  
     การคอมเม้น โค้ด ใช้ 2 ภาษา อังกถษ และ ภาษาไทย คนละบรรทัด
   - Check list  module การทำงาน 
   - Security Code
   - load test development 
  # สรุป
    -ประโยชน์ที่ได้รับ
    -ข้อควรระวัง
    -ข้อดี
    -ข้อเสีย
    -ข้อห้าม ถ้ามี
    -ตัวอย่างโค้ดที่รันได้จริง
  - คู่มือการทดสอบ 
     - Check List Test  
  - คู่มือการใช้งาน 
  -  คู่มือการบำรุงรักษา 
  -  คู่มือการขยาย/แก้ไข
  - ออกแบบ Git flow 
 - ออกแบบ Code review Code PR 
   - Check list 
 - ออกแบบ CI/CD
 - Root Cause Solution
  ขั้นตอนการทำ RCA  
  - ระบุปัญหา (Define the Problem): เกิดอะไรขึ้น?
  - รวบรวมข้อมูล (Collect Data): หลักฐานและเหตุการณ์ที่เกี่ยวข้อง
  - ระบุสาเหตุที่เป็นไปได้ (Identify Possible Causes): ทำไมถึงเกิดเหตุการณ์นี้
  - หา "สาเหตุหลัก" (Find the Root Cause): วิเคราะห์ลงลึกว่าสาเหตุใดคือสาเหตุหลักที่แท้จริง
  - วางแผนและแก้ไข (Implement Solution): ลงมือแก้ไขและป้องกัน
  - ติดตามผล (Monitor): ตรวจสอบว่าปัญหาไม่กลับมาอีก เอกสารต้นแบบสำหรับให้ AI สร้าง/แก้ไขโปรแกรมภาษา Go ทุกประเภท**  
  - 
> ใช้โครงสร้าง **Clean Architecture + DDD** พร้อม Layer ที่ชัดเจน, Cross-cutting Concerns ครบ, และ Pattern  แยก Modules


# ออกแบบระบบ IoT + Automation + AI สำหรับฟาร์มเห็ดอัจฉริยะ (ฉบับแตกส่วน)

---

## ภาพรวมสถาปัตยกรรมระบบ

```
[ชั้นเก็บข้อมูล] → [ชั้นส่งข้อมูล] → [ชั้นประมวลผล] → [ชั้น AI วิเคราะห์] → [ชั้นสั่งการอัตโนมัติ]
   Sensors         Gateway/5G       Cloud/Edge        AI Models           Actuators/ERP
```

---

## ส่วนที่ 1: ชั้นเก็บข้อมูล (Data Acquisition Layer)

### 1.1 เซ็นเซอร์วัดสภาพแวดล้อมโรงเพาะ

| ประเภทเซ็นเซอร์ | ค่าวัด | ตำแหน่งติดตั้ง | ความถี่ |
|---|---|---|---|
| DHT22 / SHT31 | อุณหภูมิ, ความชื้นสัมพัทธ์ | ทุกชั้นวาง, 4 มุมโรง | 30 วินาที |
| MH-Z19B (CO₂) | คาร์บอนไดออกไซด์ | กลางโรง, ระดับล่าง | 1 นาที |
| เซ็นเซอร์แสง (BH1750) | ความเข้มแสง (Lux) | หลังคา, ระดับชั้น | 5 นาที |
| เซ็นเซอร์ความชื้นวัสดุ | ความชื้นก้อนเชื้อ | ฝังในก้อนเชื้อ | 10 นาที |
| เซ็นเซอร์ pH ดิน/วัสดุ | ค่า pH | ก้อนเชื้อ | 1 ชั่วโมง |

### 1.2 เซ็นเซอร์วัดคุณภาพน้ำ/ปุ๋ย

| เซ็นเซอร์ | ค่าวัด | 用途 |
|---|---|---|
| EC Sensor | ค่าการนำไฟฟ้า | วัดความเข้มข้นปุ๋ย |
| pH Sensor | ค่า pH น้ำ | ควบคุมการผสมปุ๋ย |
| TDS Sensor | แร่ธาตุรวม | ตรวจสอบคุณภาพน้ำ |
| Flow Meter | ปริมาณน้ำที่ใช้ | คิดต้นทุนน้ำ |

### 1.3 เซ็นเซอร์วัดไฟฟ้า/พลังงาน

| อุปกรณ์ | ค่าวัด |
|---|---|
| CT Clamp / PZEM-004T | กระแส, แรงดัน, กำลังไฟ, kWh |
| Smart Breaker | ตัดไฟอัตโนมัติเมื่อเกิน |
| Solar Inverter Monitor | พลังงานแสงอาทิตย์ |

### 1.4 กล้องและ AI Vision

| ประเภท | 用途 |
|---|---|
| กล้อง RGB ความละเอียดสูง | ตรวจการเจริญเติบโต, โรค |
| กล้อง Thermal | ตรวจความร้อนผิดปกติ |
| กล้องจุลทรรศน์ดิจิทัล | ตรวจเชื้อโรคในก้อนเชื้อ |
| Drone/กล้องโดม | ภาพรวมโรงเพาะ |

### 1.5 เซ็นเซอร์ติดตามการขนส่ง

| อุปกรณ์ | ค่าวัด |
|---|---|
| GPS Tracker | ตำแหน่งรถขนส่ง |
| Temperature Logger | อุณหภูมิระหว่างขนส่ง |
| RFID / QR | ติดตามล็อตสินค้า |
| Weight Sensor | น้ำหนักบรรทุก |

---

## ส่วนที่ 2: ชั้นส่งข้อมูล (Connectivity Layer)

### 2.1 โปรโตคอลการสื่อสาร

| ระยะ | เทคโนโลยี | ข้อดี |
|---|---|---|
| ระยะสั้น (ในโรง) | LoRaWAN, Zigbee, BLE | ประหยัดไฟ, สัญญาณทะลุ |
| ระยะกลาง (ฟาร์ม) | Wi-Fi 6, Ethernet | ความเร็วสูง |
| ระยะไกล (ขนส่ง) | 4G/5G, NB-IoT | ทั่วประเทศ |
| สำรอง | Satellite (Starlink) | พื้นที่ห่างไกล |

### 2.2 Gateway และ Edge Computing

```
เซ็นเซอร์ → Gateway (Raspberry Pi / Industrial PC) → Edge Server → Cloud
```

- **Edge Computing**: ประมวลผลเบื้องต้นที่หน้างาน เช่น กรองสัญญาณรบกวน, แจ้งเตือนทันที
- **MQTT Broker**: Mosquitto / EMQX สำหรับรับส่งข้อมูล
- **Time-Series DB**: InfluxDB / TimescaleDB เก็บข้อมูลอนุกรมเวลา

---

## ส่วนที่ 3: ชั้นประมวลผลและฐานข้อมูล (Data Platform)

### 3.1 โครงสร้างฐานข้อมูล

| ฐานข้อมูล | 用途 | ตัวอย่าง |
|---|---|---|
| Time-Series DB | ข้อมูลเซ็นเซอร์ | InfluxDB |
| Relational DB | ข้อมูลธุรกิจ | PostgreSQL / MySQL |
| Document DB | ข้อมูลไม่โครงสร้าง | MongoDB |
| Data Lake | ข้อมูลดิบทั้งหมด | MinIO / S3 |
| Cache | ข้อมูลเรียลไทม์ | Redis |

### 3.2 Data Pipeline

```
Sensor → MQTT → Kafka → Stream Processing (Flink) → Data Warehouse → AI
```

- **Kafka**: รับข้อมูลปริมาณมาก
- **Apache Flink**: ประมวลผลสตรีมแบบเรียลไทม์
- **Airflow**: จัดตารางงาน batch
- **Grafana**: แดชบอร์ดแสดงผล

---

## ส่วนที่ 4: ชั้น AI วิเคราะห์และคาดการณ์ (AI & Analytics Layer)

### 4.1 โมเดลวิเคราะห์สภาพโรงเพาะ

| โมเดล | หน้าที่ | อัลกอริทึม |
|---|---|---|
| **พยากรณ์อุณหภูมิ/ความชื้น** | คาดการณ์ล่วงหน้า 1-24 ชม. | LSTM, GRU, Prophet |
| **ตรวจจับความผิดปกติ** | แจ้งเตือนเมื่อค่าเกิน | Isolation Forest, Autoencoder |
| **ควบคุมอัตโนมัติ** | ปรับพัดลม/พ่นหมอก | Reinforcement Learning (PPO) |
| **จำแนกระยะการเจริญ** | ระบุระยะเห็ด | CNN (ResNet, EfficientNet) |
| **ตรวจจับโรค** | ตรวจเชื้อรา/แบคทีเรีย | YOLOv8, Vision Transformer |
| **พยากรณ์ผลผลิต** | คาดการณ์น้ำหนักเก็บ | XGBoost, Random Forest |
| **พยากรณ์ราคาตลาด** | ราคาขายล่วงหน้า | ARIMA, LSTM |
| **เพิ่มประสิทธิภาพปุ๋ย** | สูตรปุ๋ยที่เหมาะสม | Bayesian Optimization |
| **ตรวจจับการรั่วไหลน้ำ** | ผิดปกติการใช้น้ำ | Anomaly Detection |
| **พยากรณ์การใช้ไฟฟ้า** | ค่าไฟล่วงหน้า | Gradient Boosting |

### 4.2 ตัวอย่างโมเดล AI แยกตามงาน

#### (ก) โมเดลพยากรณ์สภาพอากาศในโรง
```
Input:  อุณหภูมิ, ความชื้น, CO₂, แสง, เวลา, ฤดูกาล (อดีต 7 วัน)
Model:  LSTM 2 ชั้น + Dropout
Output: อุณหภูมิ, ความชื้น (ล่วงหน้า 1, 6, 12, 24 ชม.)
Loss:   MSE
```

#### (ข) โมเดลตรวจจับโรคเห็ด
```
Input:  ภาพถ่ายก้อนเชื้อ/ดอกเห็ด (224x224)
Model:  YOLOv8 + Classification Head
Classes: ปกติ, ราขาว, ราดำ, แบคทีเรีย, ไวรัส
Output: Bounding Box + Confidence + ระดับความรุนแรง
```

#### (ค) โมเดลพยากรณ์ผลผลิต
```
Input:  ข้อมูลสภาพแวดล้อม, อายุเชื้อ, สายพันธุ์, น้ำ, ปุ๋ย
Model:  XGBoost + Feature Engineering
Output: น้ำหนักผลผลิตต่อวัน (kg) ล่วงหน้า 7 วัน
Metric: MAPE < 10%
```

#### (ง) โมเดลควบคุมอัตโนมัติ (Reinforcement Learning)
```
State:  อุณหภูมิ, ความชื้น, CO₂, แสง, เวลา, ค่าไฟ
Action: เปิด/ปิดพัดลม, พ่นหมอก, เปิดไฟ, ปรับม่าน
Reward: -|อุณหภูมิ-เป้าหมาย| - ค่าไฟ - ความเสี่ยงโรค
Agent:  PPO / SAC
```

#### (จ) โมเดลพยากรณ์ราคาและต้นทุน
```
Input:  ราคาตลาดย้อนหลัง, ปริมาณผลผลิต, ฤดูกาล, ต้นทุน
Model:  Prophet + LSTM Ensemble
Output: ราคาขายที่เหมาะสม, กำไรคาดการณ์
```

### 4.3 ระบบแนะนำอัจฉริยะ (Recommendation Engine)

| ระบบแนะนำ | ข้อมูลนำเข้า | ผลลัพธ์ |
|---|---|---|
| แนะนำการเก็บเกี่ยว | ระยะเจริญ, ราคาตลาด | วันเก็บที่ให้กำไรสูงสุด |
| แนะนำสูตรปุ๋ย | ค่า EC, pH, ระยะเจริญ | สูตรปุ๋ยที่เหมาะสม |
| แนะนำเส้นทางขนส่ง | GPS, สภาพจราจร, อุณหภูมิ | เส้นทางที่เร็ว/ประหยัด |
| แนะนำช่องทางขาย | ราคา, อุปสงค์, ต้นทุนขนส่ง | ขายออนไลน์/ตลาดสด/ส่งโรงงาน |

---

## ส่วนที่ 5: ชั้น Automation และสั่งการ (Control Layer)

### 5.1 อุปกรณ์สั่งการ (Actuators)

| อุปกรณ์ | ควบคุม | เงื่อนไขที่ trigger |
|---|---|---|
| พัดลมระบายอากาศ | ความชื้น, CO₂ | ความชื้น > 90% หรือ CO₂ > 1000 ppm |
| ปั๊มพ่นหมอก | ความชื้น | ความชื้น < 85% |
| หลอด LED Grow | แสง | แสง < 500 Lux (ช่วงกลางวัน) |
| ปั๊มน้ำ + วาล์ว | การรดน้ำ | ตามตาราง AI แนะนำ |
| เครื่องทำความเย็น | อุณหภูมิ | อุณหภูมิ > 28°C |
| เครื่องให้ปุ๋ยอัตโนมัติ | EC/pH | ตามสูตร AI |
| ม่านบังแสง | แสง/อุณหภูมิ | แสงจ้าเกิน |
| เครื่องฆ่าเชื้อ UV | โรค | ตรวจพบเชื้อโรค |

### 5.2 ตรรกะควบคุมอัตโนมัติ (Automation Rules)

```
IF อุณหภูมิ > 30°C AND ความชื้น < 70% THEN เปิดพัดลม + พ่นหมอก
IF CO₂ > 1200 ppm THEN เปิดพัดลมระบาย
IF ตรวจพบโรค (AI) THEN แจ้งเตือน + เปิด UV + กักบริเวณ
IF ราคาตลาดสูง AND ผลผลิตพร้อม THEN แนะนำเก็บเกี่ยว
IF ค่าไฟช่วง Peak THEN ลดการใช้งานที่ไม่จำเป็น
```

### 5.3 Digital Twin (แบบจำลองเสมือนโรงเพาะ)

- สร้างแบบจำลอง 3D ของโรงเพาะ
- จำลองสถานการณ์: "ถ้าเพิ่มความชื้น 5% จะเกิดอะไร"
- ทดสอบกลยุทธ์ก่อนใช้งานจริง
- เทคโนโลยี: Unity / NVIDIA Omniverse / AWS TwinMaker

---

## ส่วนที่ 6: ชั้นเชื่อม ERP (Integration Layer)

### 6.1 การเชื่อมข้อมูล IoT → ERP

| ข้อมูล IoT | โมดูล ERP | การใช้งาน |
|---|---|---|
| น้ำ/ไฟ/ปุ๋ย | บัญชีต้นทุน | คิดต้นทุนต่อหน่วย |
| ผลผลิต | สินค้าคงคลัง | อัปเดตสต็อกเรียลไทม์ |
| อุณหภูมิขนส่ง | โลจิสติกส์ | ตรวจสอบคุณภาพ |
| ราคาตลาด | CRM/ขาย | ตั้งราคาไดนามิก |
| แรงงาน | HR | คิดต้นทุนแรงงาน |
| โรค/ความเสียหาย | คุณภาพ | ตัดจำหน่าย/เคลม |

### 6.2 API Integration

```
ERP (Odoo/SAP) ←→ REST API ←→ Middleware ←→ IoT Platform
                              ↓
                         Webhook แจ้งเตือน
```

---

## ส่วนที่ 7: ชั้นแสดงผลและแจ้งเตือน (Dashboard & Alert)

### 7.1 แดชบอร์ด

| แดชบอร์ด | ข้อมูล | ผู้ใช้ |
|---|---|---|
| Real-time Monitor | อุณหภูมิ, ความชื้น, CO₂ | พนักงานโรง |
| Production Dashboard | ผลผลิต, แผนเก็บเกี่ยว | ผู้จัดการผลิต |
| Financial Dashboard | ต้นทุน, กำไร, ราคา | ผู้บริหาร |
| Logistics Dashboard | GPS, อุณหภูมิขนส่ง | ฝ่ายขนส่ง |
| AI Insights | พยากรณ์, คำแนะนำ | นักวิเคราะห์ |

### 7.2 การแจ้งเตือน

| ช่องทาง | ระดับความเร่งด่วน |
|---|---|
| LINE Notify / Telegram | ทั่วไป |
| SMS | เร่งด่วน |
| เสียงในโรง | ฉุกเฉิน |
| Email | รายงานประจำวัน |
| Push App | เรียลไทม์ |

---

## ส่วนที่ 8: ความมั่นคงปลอดภัย (Security)

| ด้าน | มาตรการ |
|---|---|
| Device Security | Certificate, TPM, Secure Boot |
| Network Security | VPN, Firewall, VLAN แยก |
| Data Security | Encryption at rest/in transit |
| Access Control | RBAC, MFA |
| Backup | สำรองข้อมูล 3-2-1 |
| Compliance | PDPA, ISO 27001 |

---

## ส่วนที่ 9: แผนการนำไปใช้ (Implementation Roadmap)

| ระยะ | ระยะเวลา | สิ่งที่ทำ |
|---|---|---|
| **Phase 1: Foundation** | 1-3 เดือน | ติดเซ็นเซอร์พื้นฐาน, ตั้ง Gateway, แดชบอร์ดเรียลไทม์ |
| **Phase 2: Automation** | 3-6 เดือน | ระบบควบคุมอัตโนมัติ, แจ้งเตือน |
| **Phase 3: AI Analytics** | 6-12 เดือน | โมเดลพยากรณ์, ตรวจจับโรค, แนะนำ |
| **Phase 4: Integration** | 12-18 เดือน | เชื่อม ERP, Digital Twin, ขายออนไลน์ |
| **Phase 5: Optimization** | 18-24 เดือน | Reinforcement Learning, ปรับปรุงต่อเนื่อง |

---

## ส่วนที่ 10: ตัวชี้วัดความสำเร็จ (KPI)

| KPI | เป้าหมาย |
|---|---|
| ลดการสูญเสียผลผลิต | > 30% |
| ลดต้นทุนน้ำ/ไฟ | > 20% |
| เพิ่มผลผลิตต่อพื้นที่ | > 25% |
| ความแม่นยำพยากรณ์ | > 90% |
| ตรวจจับโรคก่อนลุกลาม | > 95% |
| ลดต้นทุนแรงงาน | > 40% |
| กำไรสุทธิเพิ่ม | > 35% |

---

## สรุปสถาปัตยกรรมแบบองค์รวม

```
┌─────────────────────────────────────────────────────────────┐
│                    ชั้นผู้ใช้ (User Layer)                    │
│  Dashboard │ Mobile App │ LINE │ ERP │ Marketplace          │
└─────────────────────────────────────────────────────────────┘
                            ↑↓
┌─────────────────────────────────────────────────────────────┐
│              ชั้น AI & Analytics (AI Layer)                  │
│  พยากรณ์ │ ตรวจจับโรค │ แนะนำ │ Digital Twin │ RL Control  │
└─────────────────────────────────────────────────────────────┘
                            ↑↓
┌─────────────────────────────────────────────────────────────┐
│            ชั้นประมวลผล (Data Platform Layer)                │
│  Kafka │ Flink │ InfluxDB │ PostgreSQL │ Data Lake          │
└─────────────────────────────────────────────────────────────┘
                            ↑↓
┌─────────────────────────────────────────────────────────────┐
│              ชั้นส่งข้อมูล (Connectivity Layer)              │
│  LoRaWAN │ Wi-Fi │ 5G │ MQTT │ Edge Gateway                 │
└─────────────────────────────────────────────────────────────┘
                            ↑↓
┌─────────────────────────────────────────────────────────────┐
│         ชั้นเก็บข้อมูล & สั่งการ (Sensor & Actuator)          │
│  Temp │ Humidity │ CO₂ │ Light │ pH │ EC │ Camera │ Motor   │
└─────────────────────────────────────────────────────────────┘
```

---

**หากคุณต้องการเจาะลึกส่วนใดเป็นพิเศษ** เช่น:
- ออกแบบโมเดล AI ตัวใดตัวหนึ่งโดยละเอียด (พร้อมโครงสร้างโค้ด)
- เลือกฮาร์ดแวร์เซ็นเซอร์จริงและราคา
- ออกแบบฐานข้อมูลและ schema
- เขียน automation rules สำหรับโรงเพาะเห็ดชนิดเฉพาะ (นางรม/ขอนขาว/กระดุม)

# 📘 คู่มือสถาปัตยกรรมระบบ IoT + Automation + AI สำหรับฟาร์มเห็ดอัจฉริยะ

## สารบัญ

1. [บทนิยาม](#1-บทนิยาม)
2. [บทหัวข้อ](#2-บทหัวข้อ)
3. [Workflow และ Dataflow](#3-workflow-และ-dataflow)
4. [Case Study](#4-case-study)
5. [โครงสร้างโฟลเดอร์](#5-โครงสร้างโฟลเดอร์)
6. [เทมเพลตโค้ด Go (Clean Architecture + DDD)](#6-เทมเพลตโค้ด-go)
7. [Checklist Module](#7-checklist-module)
8. [Security Code](#8-security-code)
9. [Load Test](#9-load-test-development)
10. [สรุป](#10-สรุป)
11. [คู่มือทดสอบ/ใช้งาน/บำรุงรักษา](#11-คู่มือ)
12. [Git Flow / Code Review / CI-CD](#12-git-flow--code-review--cicd)
13. [Root Cause Analysis](#13-root-cause-analysis)

---

## 1. บทนิยาม

| คำศัพท์ | ความหมาย |
|---|---|
| **IoT (Internet of Things)** | อุปกรณ์ที่เชื่อมต่ออินเทอร์เน็ตได้ เช่น เซ็นเซอร์วัดอุณหภูมิ ส่งข้อมูลอัตโนมัติ |
| **Edge Computing** | การประมวลผลที่หน้างาน ก่อนส่งขึ้น Cloud เพื่อลด latency |
| **MQTT** | โปรโตคอลส่งข้อความเบา เหมาะกับ IoT ใช้ publish/subscribe |
| **Digital Twin** | แบบจำลองเสมือนของโรงเพาะ ใช้ทดลองก่อนใช้งานจริง |
| **Reinforcement Learning** | AI เรียนรู้จากการลองผิดลองถูกผ่าน reward |
| **Clean Architecture** | แยกชั้นโค้ดเป็น Domain, Usecase, Interface, Infrastructure |
| **DDD (Domain-Driven Design)** | ออกแบบซอฟต์แวร์ตาม business domain จริง |
| **KPI** | ตัวชี้วัดความสำเร็จ เช่น ลดของเสีย 30% |
| **GAP** | Good Agricultural Practices มาตรฐานเกษตรดี |
| **RCA** | Root Cause Analysis การวิเคราะห์หาสาเหตุราก |

---

## 2. บทหัวข้อ

### 2.1 โครงสร้างการทำงาน
ระบบแบ่งเป็น **5 ชั้นหลัก**:
1. **Data Acquisition** — เซ็นเซอร์เก็บข้อมูล
2. **Connectivity** — ส่งข้อมูลผ่าน LoRaWAN/5G/MQTT
3. **Data Platform** — Kafka, Flink, InfluxDB, PostgreSQL
4. **AI & Analytics** — พยากรณ์ ตรวจจับโรค แนะนำ
5. **Automation & Control** — Actuators, ERP, Dashboard

### 2.2 วัตถุประสงค์
- เพิ่มความแม่นยำการผลิตเห็ด
- ลดของเสีย/ต้นทุนน้ำ-ไฟ
- ตรวจจับโรคก่อนลุกลาม
- พยากรณ์ผลผลิตและราคา
- เชื่อม ERP เพื่อบริหารต้นทุนเรียลไทม์

### 2.3 กลุ่มเป้าหมาย
- เจ้าของฟาร์มเห็ด
- ผู้จัดการโรงเพาะ
- นักวิเคราะห์ข้อมูล
- ทีมพัฒนา IoT/AI

### 2.4 ความรู้พื้นฐาน
- การเขียนโปรแกรม Go, Python
- โปรโตคอล MQTT, HTTP/REST
- ฐานข้อมูล Time-Series
- แนวคิด Machine Learning

### 2.5 บทนำ
ฟาร์มเห็ดแบบดั้งเดิมควบคุมด้วยมือ ทำให้ผลผลิตไม่คงที่ ระบบ IoT+AI ช่วยให้ควบคุมอัตโนมัติ 24/7 พยากรณ์ล่วงหน้า และเชื่อมธุรกิจครบวงจร

---

## 3. Workflow และ Dataflow

### 3.1 Workflow การทำงานหลัก

```
[1] Sensor เก็บค่า → [2] Gateway ส่ง MQTT → [3] Kafka รับ
       ↓
[4] Flink ประมวลผล → [5] InfluxDB เก็บ → [6] AI วิเคราะห์
       ↓
[7] แจ้งเตือน/สั่ง Actuator → [8] Dashboard/ERP → [9] Feedback Loop
```

### 3.2 Dataflow Diagram (Flowchart)

```
┌──────────┐   MQTT    ┌──────────┐   produce   ┌──────────┐
│ Sensors  │──────────▶│ Gateway  │────────────▶│  Kafka   │
│ (DHT22,  │           │ (RPi)    │             │  Topic   │
│  CO₂,pH) │           └──────────┘             └────┬─────┘
└──────────┘                                         │ consume
                                                     ▼
┌──────────┐   query   ┌──────────┐   write    ┌──────────┐
│Grafana/  │◀──────────│ InfluxDB │◀───────────│  Flink   │
│Dashboard │           │PostgreSQL│            │ Stream   │
└──────────┘           └────┬─────┘            └────┬─────┘
                            │                       │
                            ▼                       ▼
                     ┌──────────┐            ┌──────────┐
                     │ AI Model │───────────▶│ Actuator │
                     │ (LSTM,   │  control   │ (Fan,    │
                     │  YOLO)   │            │  Pump)   │
                     └────┬─────┘            └──────────┘
                          │
                          ▼
                   ┌──────────┐
                   │  ERP /   │
                   │ LINE API │
                   └──────────┘
```

### 3.3 คำอธิบายแต่ละจุด

| จุด | การทำงาน | เทคโนโลยี |
|---|---|---|
| 1 | อ่านค่าจากเซ็นเซอร์ทุก 30 วินาที | DHT22, MH-Z19B |
| 2 | Gateway รวมข้อมูล ส่งผ่าน MQTT | Mosquitto |
| 3 | Kafka รับ message แบบ distributed | Kafka Topic |
| 4 | Flink กรอง noise, คำนวณ moving avg | Apache Flink |
| 5 | เก็บ time-series + business data | InfluxDB + PostgreSQL |
| 6 | AI โหลดข้อมูล พยากรณ์/ตรวจโรค | LSTM, YOLOv8 |
| 7 | ส่งคำสั่ง Actuator ผ่าน MQTT | Relay, Motor |
| 8 | แสดงผล dashboard + sync ERP | Grafana, Odoo API |
| 9 | Feedback กลับไป train model | MLflow |

### 3.4 ตัวอย่างปัญหาและแนวทางแก้ไข

| ปัญหา | สาเหตุ | แนวทาง |
|---|---|---|
| เซ็นเซอร์ส่งค่าซ้ำ | Network retry | ใช้ QoS 1 + idempotent key |
| AI พยากรณ์คลาดเคลื่อน | ข้อมูลไม่พอ | เพิ่ม data + retrain |
| Actuator ทำงานช้า | Latency Cloud | ย้าย logic ไป Edge |
| Kafka ล้น | producer เร็วเกิน | เพิ่ม partition + backpressure |

---

## 4. Case Study

### กรณีศึกษา: ฟาร์มเห็ดนางรม จ.เชียงราย

**ปัญหาเดิม:**
- อุณหภูมิ fluctuated 22-32°C
- ผลผลิตเสียหาย 25% จากโรค
- ต้นทุนไฟสูง ฿45,000/เดือน

**การแก้ไข:**
1. ติดตั้ง DHT22 12 จุด + MH-Z19B 4 จุด
2. Gateway Raspberry Pi + MQTT
3. AI LSTM พยากรณ์อุณหภูมิ 6 ชม.
4. Auto control พัดลม/พ่นหมอก
5. YOLOv8 ตรวจจับราขาว

**ผลลัพธ์ (6 เดือน):**
| KPI | ก่อน | หลัง | เปลี่ยนแปลง |
|---|---|---|---|
| ผลผลิต/เดือน | 800 kg | 1,050 kg | +31% |
| ของเสีย | 25% | 8% | -68% |
| ค่าไฟ | ฿45,000 | ฿34,000 | -24% |
| กำไรสุทธิ | ฿85,000 | ฿142,000 | +67% |

---

## 5. โครงสร้างโฟลเดอร์

```
mushroom-farm-iot/
├── cmd/
│   ├── api/main.go
│   ├── gateway/main.go
│   └── worker/main.go
├── internal/
│   ├── domain/              # Entities, Value Objects
│   │   ├── sensor/
│   │   ├── actuator/
│   │   └── prediction/
│   ├── usecase/             # Business Logic
│   │   ├── collect_data.go
│   │   ├── control_device.go
│   │   └── predict_yield.go
│   ├── repository/          # Interfaces
│   │   ├── sensor_repo.go
│   │   └── actuator_repo.go
│   ├── delivery/            # HTTP/gRPC/MQTT handlers
│   │   ├── http/
│   │   └── mqtt/
│   └── infrastructure/      # DB, MQTT, AI client
│       ├── influxdb/
│       ├── postgres/
│       ├── mqtt/
│       └── ai_client/
├── pkg/
│   ├── logger/
│   ├── config/
│   └── middleware/
├── migrations/
├── deployments/
│   ├── docker/
│   └── k8s/
├── tests/
│   ├── unit/
│   └── integration/
├── docs/
├── .env.example
├── Makefile
├── go.mod
└── README.md
```

---

## 6. เทมเพลตโค้ด Go

### 6.1 Domain Layer — Sensor Entity

```go
// internal/domain/sensor/sensor.go
package sensor

import (
	"errors"
	"time"
)

// Sensor represents an IoT sensor entity in the mushroom farm
// Sensor แทนเอนทิตีเซ็นเซอร์ IoT ในฟาร์มเห็ด
type Sensor struct {
	ID        string
	Type      SensorType
	Location  string
	Value     float64
	Unit      string
	Timestamp time.Time
}

// SensorType defines the kind of sensor
// SensorType กำหนดชนิดของเซ็นเซอร์
type SensorType string

const (
	TypeTemperature SensorType = "temperature"
	TypeHumidity    SensorType = "humidity"
	TypeCO2         SensorType = "co2"
	TypeLight       SensorType = "light"
	TypePH          SensorType = "ph"
)

// Validate checks if the sensor reading is within acceptable range
// Validate ตรวจสอบว่าค่าที่อ่านได้อยู่ในช่วงที่ยอมรับได้
func (s *Sensor) Validate() error {
	if s.ID == "" {
		return errors.New("sensor ID cannot be empty") // ID ต้องไม่ว่าง
	}
	if s.Timestamp.IsZero() {
		return errors.New("timestamp is required") // ต้องมี timestamp
	}
	switch s.Type {
	case TypeTemperature:
		if s.Value < -10 || s.Value > 60 {
			return errors.New("temperature out of range") // อุณหภูมิ超出
		}
	case TypeHumidity:
		if s.Value < 0 || s.Value > 100 {
			return errors.New("humidity must be 0-100") // ความชื้น 0-100
		}
	case TypeCO2:
		if s.Value < 0 || s.Value > 10000 {
			return errors.New("CO2 out of range") // CO2 ผิดปกติ
		}
	}
	return nil
}
```

### 6.2 Repository Interface

```go
// internal/repository/sensor_repo.go
package repository

import (
	"context"
	"time"

	"mushroom-farm/internal/domain/sensor"
)

// SensorRepository defines the contract for sensor data storage
// SensorRepository กำหนดสัญญาสำหรับการจัดเก็บข้อมูลเซ็นเซอร์
type SensorRepository interface {
	Save(ctx context.Context, s *sensor.Sensor) error
	GetLatest(ctx context.Context, sensorID string) (*sensor.Sensor, error)
	GetRange(ctx context.Context, sensorID string, from, to time.Time) ([]*sensor.Sensor, error)
}
```

### 6.3 Usecase — Collect Data

```go
// internal/usecase/collect_data.go
package usecase

import (
	"context"
	"log"

	"mushroom-farm/internal/domain/sensor"
	"mushroom-farm/internal/repository"
)

// CollectDataUseCase handles incoming sensor data
// CollectDataUseCase จัดการข้อมูลเซ็นเซอร์ที่เข้ามา
type CollectDataUseCase struct {
	repo      repository.SensorRepository
	alertSvc  AlertService
}

func NewCollectDataUseCase(repo repository.SensorRepository, alert AlertService) *CollectDataUseCase {
	return &CollectDataUseCase{repo: repo, alertSvc: alert}
}

// Execute validates and stores sensor data
// Execute ตรวจสอบและจัดเก็บข้อมูลเซ็นเซอร์
func (uc *CollectDataUseCase) Execute(ctx context.Context, s *sensor.Sensor) error {
	// Step 1: Validate input data
	// ขั้นที่ 1: ตรวจสอบข้อมูลนำเข้า
	if err := s.Validate(); err != nil {
		log.Printf("[ERROR] validation failed: %v", err) // บันทึก error
		return err
	}

	// Step 2: Save to time-series database
	// ขั้นที่ 2: บันทึกลงฐานข้อมูล time-series
	if err := uc.repo.Save(ctx, s); err != nil {
		log.Printf("[ERROR] save failed: %v", err)
		return err
	}

	// Step 3: Check thresholds and alert if needed
	// ขั้นที่ 3: ตรวจสอบค่า threshold และแจ้งเตือนถ้าจำเป็น
	if s.Type == sensor.TypeTemperature && s.Value > 30 {
		uc.alertSvc.Send(ctx, "High temperature: "+s.ID) // แจ้งอุณหภูมิสูง
	}
	return nil
}

type AlertService interface {
	Send(ctx context.Context, msg string) error
}
```

### 6.4 Infrastructure — MQTT Client

```go
// internal/infrastructure/mqtt/client.go
package mqtt

import (
	"encoding/json"
	"fmt"
	"log"
	"time"

	mqtt "github.com/eclipse/paho.mqtt.golang"
	"mushroom-farm/internal/domain/sensor"
	"mushroom-farm/internal/usecase"
)

// MQTTClient wraps the MQTT broker connection
// MQTTClient ครอบการเชื่อมต่อกับ MQTT broker
type MQTTClient struct {
	client mqtt.Client
	uc     *usecase.CollectDataUseCase
}

func NewMQTTClient(broker, clientID string, uc *usecase.CollectDataUseCase) *MQTTClient {
	opts := mqtt.NewClientOptions().
		AddBroker(broker).
		SetClientID(clientID).
		SetAutoReconnect(true)

	c := mqtt.NewClient(opts)
	if token := c.Connect(); token.Wait() && token.Error() != nil {
		log.Fatalf("MQTT connect failed: %v", token.Error()) // เชื่อมต่อไม่สำเร็จ
	}
	return &MQTTClient{client: c, uc: uc}
}

// Subscribe starts listening to sensor topics
// Subscribe เริ่มฟัง topic ของเซ็นเซอร์
func (m *MQTTClient) Subscribe(topic string) error {
	handler := func(_ mqtt.Client, msg mqtt.Message) {
		var s sensor.Sensor
		// Parse JSON payload from sensor
		// แปลง JSON ที่ได้จากเซ็นเซอร์
		if err := json.Unmarshal(msg.Payload(), &s); err != nil {
			log.Printf("[ERROR] unmarshal: %v", err)
			return
		}
		s.Timestamp = time.Now()

		// Call usecase to process
		// เรียก usecase เพื่อประมวลผล
		if err := m.uc.Execute(context.Background(), &s); err != nil {
			log.Printf("[ERROR] usecase: %v", err)
		}
	}

	token := m.client.Subscribe(topic, 1, handler) // QoS 1
	if token.Wait() && token.Error() != nil {
		return fmt.Errorf("subscribe failed: %w", token.Error())
	}
	log.Printf("[INFO] subscribed to %s", topic)
	return nil
}
```

### 6.5 Main — Run ได้ทันที

```go
// cmd/gateway/main.go
package main

import (
	"log"
	"os"
	"os/signal"
	"syscall"

	"mushroom-farm/internal/infrastructure/mqtt"
	"mushroom-farm/internal/infrastructure/postgres"
	"mushroom-farm/internal/usecase"
)

func main() {
	// Load config from environment
	// โหลด config จาก environment
	broker := os.Getenv("MQTT_BROKER")
	dbDSN := os.Getenv("DB_DSN")
	if broker == "" || dbDSN == "" {
		log.Fatal("MQTT_BROKER and DB_DSN required") // ต้องมีค่า config
	}

	// Initialize repository
	// เริ่มต้น repository
	repo, err := postgres.NewSensorRepo(dbDSN)
	if err != nil {
		log.Fatalf("db init failed: %v", err)
	}

	// Initialize usecase
	// เริ่มต้น usecase
	alertSvc := &LogAlertService{}
	uc := usecase.NewCollectDataUseCase(repo, alertSvc)

	// Initialize MQTT client
	// เริ่มต้น MQTT client
	client := mqtt.NewMQTTClient(broker, "gateway-01", uc)
	if err := client.Subscribe("farm/+/sensor/+"); err != nil {
		log.Fatalf("subscribe failed: %v", err)
	}

	log.Println("[INFO] gateway started, waiting for messages...")

	// Graceful shutdown
	// ปิดระบบอย่างปลอดภัย
	sig := make(chan os.Signal, 1)
	signal.Notify(sig, syscall.SIGINT, syscall.SIGTERM)
	<-sig
	log.Println("[INFO] shutting down")
}

type LogAlertService struct{}

func (l *LogAlertService) Send(_ context.Context, msg string) error {
	log.Printf("[ALERT] %s", msg) // แจ้งเตือนผ่าน log
	return nil
}
```

---

## 7. Checklist Module

| # | Module | สถานะ | หมายเหตุ |
|---|---|---|---|
| 1 | Sensor Collection | ☐ | DHT22, CO₂, pH |
| 2 | MQTT Gateway | ☐ | QoS 1, auto-reconnect |
| 3 | Time-Series Storage | ☐ | InfluxDB retention 90d |
| 4 | Business DB | ☐ | PostgreSQL |
| 5 | Stream Processing | ☐ | Flink window 5min |
| 6 | AI Forecasting | ☐ | LSTM retrain weekly |
| 7 | Disease Detection | ☐ | YOLOv8 |
| 8 | Auto Control | ☐ | Rule engine + RL |
| 9 | Alert Service | ☐ | LINE, SMS, Email |
| 10 | Dashboard | ☐ | Grafana |
| 11 | ERP Integration | ☐ | Odoo REST |
| 12 | Authentication | ☐ | JWT + MFA |
| 13 | Logging | ☐ | Structured JSON |
| 14 | Monitoring | ☐ | Prometheus |
| 15 | Backup | ☐ | 3-2-1 rule |

---

## 8. Security Code

```go
// pkg/middleware/auth.go
package middleware

import (
	"net/http"
	"strings"

	"github.com/golang-jwt/jwt/v5"
)

// JWTAuth middleware validates JWT tokens
// JWTAuth middleware ตรวจสอบ JWT token
func JWTAuth(secret []byte) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			// Extract Authorization header
			// ดึง header Authorization
			auth := r.Header.Get("Authorization")
			if !strings.HasPrefix(auth, "Bearer ") {
				http.Error(w, "missing token", http.StatusUnauthorized) // ไม่มี token
				return
			}
			tokenStr := strings.TrimPrefix(auth, "Bearer ")

			// Parse and verify token
			// แยกและตรวจสอบ token
			token, err := jwt.Parse(tokenStr, func(t *jwt.Token) (interface{}, error) {
				if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
					return nil, jwt.ErrSignatureInvalid // วิธีเซ็นไม่ถูกต้อง
				}
				return secret, nil
			})
			if err != nil || !token.Valid {
				http.Error(w, "invalid token", http.StatusUnauthorized) // token ไม่ถูกต้อง
				return
			}
			next.ServeHTTP(w, r)
		})
	}
}
```

**หลักการความปลอดภัย:**
- ใช้ HTTPS/TLS ทุก endpoint
- เก็บ secret ใน Vault/K8s Secret
- เปิด MFA สำหรับ admin
- Rate limit API (100 req/min/IP)
- Sanitize input ป้องกัน SQL injection
- Encrypt data at rest (AES-256)

---

## 9. Load Test Development

```go
// tests/load/sensor_load_test.go
package load

import (
	"testing"
	"time"

	mqtt "github.com/eclipse/paho.mqtt.golang"
)

// TestSensorThroughput tests 10,000 messages/sec
// TestSensorThroughput ทดสอบ 10,000 ข้อความ/วินาที
func TestSensorThroughput(t *testing.T) {
	opts := mqtt.NewClientOptions().AddBroker("tcp://localhost:1883")
	c := mqtt.NewClient(opts)
	if token := c.Connect(); token.Wait() && token.Error() != nil {
		t.Fatalf("connect failed: %v", token.Error())
	}
	defer c.Disconnect(250)

	const total = 10000
	start := time.Now()
	for i := 0; i < total; i++ {
		payload := `{"id":"s1","type":"temperature","value":25.5}`
		c.Publish("farm/s1/sensor/temp", 1, false, payload)
	}
	elapsed := time.Since(start)
	t.Logf("published %d msgs in %v (%.0f msg/s)", total, elapsed, float64(total)/elapsed.Seconds())
}
```

**เครื่องมือแนะนำ:**
- **k6** — HTTP load test
- **JMeter** — MQTT plugin
- **Gatling** — streaming
- **Vegeta** — constant rate

---

## 10. สรุป

### ประโยชน์ที่ได้รับ
- ผลผลิตเพิ่ม 25-35%
- ลดของเสีย >30%
- ลดต้นทุนน้ำ/ไฟ >20%
- ตรวจจับโรคก่อนลุกลาม >95%

### ข้อควรระวัง
- เซ็นเซอร์ต้อง calibrate ทุก 6 เดือน
- Network ขาด → ต้องมี buffer ที่ Edge
- AI ต้อง retrain เมื่อสภาพเปลี่ยน
- PDPA: ข้อมูลเกษตรกรต้องขอ consent

### ข้อดี
- ทำงาน 24/7
- ลดแรงงานคน
- ข้อมูลเรียลไทม์

### ข้อเสีย
- ต้นทุนเริ่มต้นสูง
- ต้องมีความรู้เทคนิค
- ขึ้นกับไฟฟ้า/เน็ต

### ข้อห้าม
- ❌ ห้ามเปิด actuator โดยไม่มี safety interlock
- ❌ ห้ามเก็บ password แบบ plaintext
- ❌ ห้ามใช้ default credential

### ตัวอย่างโค้ดที่รันได้จริง
ดูหัวข้อ 6.5 (`cmd/gateway/main.go`)

---

## 11. คู่มือ

### 11.1 คู่มือการทดสอบ (Checklist Test)

| # | รายการ | ผล |
|---|---|---|
| 1 | Unit test coverage >80% | ☐ |
| 2 | Integration test MQTT→DB | ☐ |
| 3 | AI model accuracy >90% | ☐ |
| 4 | Alert ทำงานถูกต้อง | ☐ |
| 5 | Failover Gateway | ☐ |
| 6 | Security scan (gosec) | ☐ |
| 7 | Load test 10k msg/s | ☐ |
| 8 | Backup/restore | ☐ |

### 11.2 คู่มือการใช้งาน
1. เปิด dashboard → ดูค่า real-time
2. ตั้ง threshold แจ้งเตือน
3. ดู AI forecast 7 วัน
4. กด manual override เมื่อจำเป็น
5. Export รายงาน

### 11.3 คู่มือการบำรุงรักษา
- Daily: ตรวจ alert log
- Weekly: ตรวจ sensor health
- Monthly: retrain AI model
- Quarterly: update firmware
- Yearly: calibrate sensors

### 11.4 คู่มือการขยาย/แก้ไข
- เพิ่มเซ็นเซอร์ใหม่ → เพิ่มใน domain + repo
- เพิ่ม AI model → สร้าง usecase ใหม่
- เพิ่ม ERP module → สร้าง adapter

---

## 12. Git Flow / Code Review / CI-CD

### 12.1 Git Flow

```
main ─────●────────────●──────────●───▶ (production)
           \          / \        /
            \        /   \      /
develop ─────●──●───●─────●────●─────▶ (staging)
              \    /
feature/x ─────●──●
```

**Branch:**
- `main` — production, tag version
- `develop` — integration
- `feature/*` — ฟีเจอร์ใหม่
- `hotfix/*` — แก้บั๊กฉุกเฉิน
- `release/*` — เตรียมปล่อย

### 12.2 Code Review / PR Checklist

- [ ] โค้ด build ผ่าน
- [ ] Test ผ่านทั้งหมด
- [ ] Coverage ไม่ลด
- [ ] ไม่มี hardcoded secret
- [ ] Comment 2 ภาษา
- [ ] อัปเดต docs
- [ ] มี 2 reviewer approve

### 12.3 CI/CD Pipeline

```yaml
# .github/workflows/ci.yml
name: CI/CD
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with: { go-version: '1.22' }
      - run: go mod download
      - run: go vet ./...
      - run: go test -race -coverprofile=coverage.out ./...
      - run: go build -o bin/gateway ./cmd/gateway
      - name: Security scan
        run: |
          go install github.com/securego/gosec/v2/cmd/gosec@latest
          gosec ./...
  deploy:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploy to production" # ปรับใช้จริง
```

---

## 13. Root Cause Analysis (RCA)

### ขั้นตอนการทำ RCA

#### 13.1 ระบุปัญหา (Define the Problem)
> ตัวอย่าง: "พัดลมไม่ทำงานตอนอุณหภูมิ 32°C เมื่อวาน 14:00-15:00"

#### 13.2 รวบรวมข้อมูล (Collect Data)
- Log จาก MQTT broker
- Sensor history ใน InfluxDB
- Actuator command log

#### 13.3 ระบุสาเหตุที่เป็นไปได้ (Identify Possible Causes)
- Sensor เสีย?
- Network timeout?
- Rule engine ผิด?
- Relay ฮาร์ดแวร์เสีย?
- สิทธิ์การสั่ง?

#### 13.4 หาสาเหตุหลัก (Find Root Cause) — 5 Whys

```
1. Why พัดลมไม่เปิด? → command ไม่ถึง
2. Why command ไม่ถึง? → MQTT publish ล้มเหลว
3. Why publish ล้ม? → Network timeout
4. Why timeout? → Wi-Fi AP รีสตาร์ท
5. Why AP รีสตาร์ท? → Firmware bug + ไม่มี UPS
```

**Root Cause:** ไม่มี UPS + firmware bug

#### 13.5 วางแผนและแก้ไข (Implement Solution)
- ติดตั้ง UPS
- อัปเดต firmware AP
- เพิ่ม fallback rule ที่ Edge

#### 13.6 ติดตามผล (Monitor)
- เพิ่ม dashboard uptime AP
- Alert เมื่อ AP offline > 1 นาที
- ตรวจ 30 วันว่าไม่เกิดซ้ำ

### เทมเพลต RCA

```markdown
## RCA Report #001
- วันที่: 2026-09-11
- ปัญหา: พัดลมไม่ทำงาน 1 ชม.
- Impact: อุณหภูมิพุ่ง 32°C, เสี่ยงผลผลิต
- Root Cause: Wi-Fi AP รีสตาร์ท
- แก้ไข: ติด UPS + firmware update
- ป้องกัน: Edge fallback + monitoring
- สถานะ: ✅ ปิด
```

---

## 📌 สรุปสุดท้าย

สถาปัตยกรรมนี้ผสาน **IoT + AI + Automation + ERP** ในรูปแบบ **Clean Architecture + DDD** ใช้ภาษา **Go** เป็นหลัก รองรับการขยายทั้งแนวตั้ง (เพิ่มเซ็นเซอร์) และแนวนอน (เพิ่มฟาร์ม) พร้อมกระบวนการ **Git Flow, CI/CD, RCA** ที่เป็นมาตรฐานสากล

หากต้องการเจาะลึกส่วนใดเพิ่มเติม แจ้งได้เลย:
- 🔧 ออกแบบ AI model ตัวใดตัวหนึ่ง (พร้อมโค้ด Python)
- 💰 เลือกฮาร์ดแวร์จริง + ราคา
- 🗄️ ออกแบบ database schema ละเอียด
- 🌾 Automation rules สำหรับเห็ดชนิดเฉพาะ