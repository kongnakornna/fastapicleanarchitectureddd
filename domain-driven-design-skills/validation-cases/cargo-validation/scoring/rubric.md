# หลักเกณฑ์การให้คะแนน — การตรวจสอบ Cargo Skills

> วัตถุประสงค์: เปรียบเทียบ 1:1 ระหว่างผลลัพธ์ตาบอดของ `validation-cases/cargo-validation/01`~`08` กับ ground truth ใน `reference/`
> วิธีการ: ให้คะแนน Skill แต่ละตัวตามมิติที่กำหนดไว้; บันทึก hit, สิ่งที่ขาด, misjudgment, bonus item ที่เพิ่มเอง

## ขนาดมาตราส่วนการให้คะแนน (ทุกมิติ)

- **4 = ดีเลิศ**: ตรงกับ ground truth ทั้งหมด + มี insight เพิ่มเติมที่สมเหตุสมผล
- **3 = ผ่านเกณฑ์**: ตรง ≥ 80% ของประเด็นหลัก สิ่งที่ขาดเป็นเรื่องรองทั้งหมด
- **2 = ใช้ได้**: ตรง 60%–80% มีสิ่งที่ขาดชัดเจนหรือ misjudgment 1 จุด
- **1 = อ่อนแอ**: ตรง < 60% มีข้อบกพร่องที่กระทบขั้นตอนถัดไป
- **0 = ไม่มี**: ไม่ได้ออกผลิตภัณฑ์หรือเบี่ยงเบนทั้งหมด

## การถ่วงน้ำหนัก

| ขั้นตอน  | Skill                   |   น้ำหนัก   |
| :------- | :---------------------- | :------: |
| I        | ddd-scope               |   1.0    |
| I        | ddd-discover            |   1.5    |
| II       | ddd-subdomains          |   1.0    |
| II       | ddd-contexts            |   1.5    |
| II       | ddd-context-map         |   1.5    |
| III      | ddd-aggregates          |   2.0    |
| III      | ddd-domain-interactions |   1.5    |
| IV       | ddd-model-review        |   1.0    |
| **รวม**  | —                       | **11.0** |

คะแนนถ่วงน้ำหนักรวม = Σ(คะแนน Skill × น้ำหนัก) / (4 × Σน้ำหนัก) × 100%

## Anchor สำคัญสำหรับการเปรียบเทียบ (摘自 ground truth)

| Anchor | ข้อกำหนดจาก ground truth                                                                | จุดตรวจสอบ          |
| :----- | :------------------------------------------------------------------------------------- | :--------------- |
| A1     | Aggregate Root 4 ตัว: Cargo, HandlingEvent, Voyage, Location                           | 06 ครอบคลุมทั้งหมดหรือไม่ |
| A2     | HandlingEvent เป็น Aggregate อิสระ (เหตุผลด้านประสิทธิภาพ ADR-1)                       | 06 + 05 อธิบายหรือไม่   |
| A3     | Delivery เป็น derived VO ห้าม setter                                                   | 06 I-4/5          |
| A4     | I4/I5: LOAD/UNLOAD ต้องมี voyage; RECEIVE/CLAIM/CUSTOMS ห้าม voyage                    | 06 ครอบคลุมหรือไม่     |
| A5     | ตัวตน HandlingEvent = 5 ตัว (cargo, voyage, completionTime, location, type)             | 06 dedup key      |
| A6     | RoutingService เป็น **Domain Service interface**, ExternalRoutingService เป็น **Infrastructure ACL** | 07 กับ 05     |
| A7     | Routing เป็น BC ภายนอก, Booking→Routing ใช้ ACL + Customer-Supplier                    | 04/05            |
| A8     | HandlingEvent เป็น Published Language ข้าม context                                     | 05               |
| A9     | RouteSpec.isSatisfiedBy(Itinerary) ในฐานะ Specification pattern                       | 06               |
| A10    | CargoInspectionService subscribe CargoWasHandled → derive misdirected/arrived           | 07               |
| A11    | เส้นทางหลัก + เส้นทาง replanning กรณี unloading ผิด 16 ขั้นตอน event flow            | 02               |
| A12    | BC 4+ ตัว: Booking / Handling / Tracking / Routing                                     | 04               |
| B-โบนัส | ระบุช่องว่าง Billing/Customer/Carrier                                                  | 05/08            |
| B-โบนัส | ระบุความซ้ำซ้อนทาง semantic ของ HandlingEvent/HandlingActivity/TransportStatus         | 08               |
| B-หักคะแนน | HandlingEventRepository มี generic CRUD                                               | 06/07            |
| B-หักคะแนน | RoutingService implementation ใส่ใน Domain layer                                       | 07               |
| B-หักคะแนน | Routing ใส่ใน Booking โดยไม่มี ACL                                                    | 04/05            |
| B-หักคะแนน | Delivery มี setter / ไม่ใช่ derived                                                    | 06               |

## กฎการให้คะแนน

- Anchor ประเภท **A** ต้อง hit ทั้งหมดถึงจะได้ 3 คะแนน; hit ≥ 80% แต่ชื่อต่างกันยังนับเป็น hit
- Hit `B-โบนัส`: คะแนนรวม +2% (สูงสุด)
- Hit `B-หักคะแนน`: คะแนนรวม -5% ต่อรายการ
- ความแตกต่างของศัพท์ (เช่น Shipment vs Cargo, HandlingFact vs HandlingEvent, Route vs Itinerary, PortCode vs UnLocode) **ไม่หักคะแนน**; semantic alignment ตรงกันก็พอ บันทึกเป็น "ศัพท์เบี่ยงเบน" (terminology drift) เพื่อสถิติ

## ผลลัพธ์

ดูการให้คะแนนแบบละเอียดตามแต่ละ Skill ได้ที่ [scorecard.md](./scorecard.md)