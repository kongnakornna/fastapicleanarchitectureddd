# Scorecard — การตรวจสอบ Cargo Skills (Blind Run)

> ให้คะแนน Skill แต่ละตัวจากผลลัพธ์ตาบอด `01`~`08` เทียบกับ ground truth ใน `reference/` ดูกฎการให้คะแนนที่ [rubric.md](./rubric.md)

## ตารางเปรียบเทียบ Terminology Drift (ไม่หักคะแนน บันทึกเพื่อสถิติเท่านั้น)

| ศัพท์ใน Blind Run              | ศัพท์จาก Ground Truth                               | Semantic alignment ตรงกันหรือไม่                                              |
| :----------------------------- | :------------------------------------------------- | :------------------------------------------------------- |
| Shipment / คำสั่งซื้อ           | Cargo                                               | ✓                                                        |
| HandlingFact                   | HandlingEvent                                       | ✓                                                        |
| Route (มี version)             | Itinerary                                           | ✓ (Route versioning ≈ ลำดับของ Itinerary ที่แทนทั้งชุด) |
| RouteCandidate                 | TransitPath (ภายนอก) → Itinerary                   | ✓                                                        |
| PortCode                       | UnLocode                                            | ✓                                                        |
| VoyageRef                      | VoyageNumber                                        | ✓                                                        |
| ShippingRequest                | RouteSpecification                                  | ≈ (ground truth เป็น VO สำหรับ parameters การสั่งซื้อ; blind แยกเป็นแนวคิด阶段性 หลวมกว่าทาง semantic) |
| DeliveryProgress               | Delivery                                            | ✓                                                        |
| TrackingView                   | Delivery + HandlingActivity (projection view)       | ✓                                                        |
| DeduplicationKey (5 ฟิลด์)     | HandlingEvent identity 5 ตัว                        | ✓ (ฟิลด์ใกล้เคียงกัน)                                    |

## Skill 01 — ddd-scope (น้ำหนัก 1.0)

| Anchor                                           | Ground Truth | Blind Hit | หมายเหตุ                     |
| :----------------------------------------------- | :----------- | :-------- | :--------------------------- |
| จุดประสงค์ธุรกิจมุ่งเน้น "lifecycle ของสินค้าหนึ่ง shipment" | ✓            | ✓         | ปัญหา/คุณค่า statement ชัดเจน |
| Non-goal ชัดเจน (ไม่ทำ billing/CRM/carrier dispatch/warehousing) | ✓ | ✓         | reproduce ครบถ้วน            |
| Routing dependency จากภายนอกบันทึกเป็น constraint หลัก | ✓      | ✓         | อยู่ใน constraint table       |
| Terminology seed ≥ 10 พร้อม ambiguity           | ✓            | ✓ (20 ตัว)| เกินเป้า                     |
| ความเสี่ยงครอบคลุม 4 ประเภท                      | ✓            | ✓         | 10 ข้อ สมดุล                 |

**คะแนน: 4 / 4** (ดีเลิศ; ระบุเพิ่ม "operational scale calculation" และ "customer notification")

## Skill 02 — ddd-discover (น้ำหนัก 1.5)

| Anchor                                     | Ground Truth                          | Blind Hit     | หมายเหตุ                                                                      |
| :----------------------------------------- | :------------------------------------ | :------------ | :---------------------------------------------------------------------------- |
| เส้นทางหลัก: สั่งซื้อ → มอบหมาย → โหลด/ขนถ่าย → รับสินค้า | ✓ (16 ขั้นตอน)                 | ✓ (14 ขั้นตอน) | จำนวนขั้นตอนใกล้เคียง; semantic ตรงกัน                                        |
| Unloading ผิด → Replanning 闭环           | ✓                                     | ✓ (กลุ่ม E-C) | ครบถ้วน                                                                        |
| การลงทะเบียนงานผิดปกติ (ซ้ำ, ผิดกฎหมาย, สาย) | Ground truth มีเพียง "InvalidHandlingEventRejected" | ✓ (3 类型 E-B) | **เกิน ground truth**: เพิ่ม late arrival replay ซึ่งเป็นสิ่งที่ README ของ ground truth ยอมรับว่าเป็น real-world extension |
| ชื่อ event เป็น past tense               | ✓                                     | ✓             | ถูกต้อง                                                                       |
| ระบุ idempotency ของ command              | ✓                                     | ✓             | ทุกข้อมี idempotency key                                                       |
| รายการ hotspot/ambiguity                  | ✓                                     | ✓             | โครงสร้างสมบูรณ์                                                               |

**คะแนน: 4 / 4** (ดีเลิศ; เส้นทาง late arrival E-B เป็นการเพิ่มเติมที่ ground truth ไม่มี)

## Skill 03 — ddd-subdomains (น้ำหนัก 1.0)

| Anchor                                           | Ground Truth | Blind Hit                                          | หมายเหตุ            |
| :----------------------------------------------- | :----------- | :------------------------------------------------- | :------------------ |
| Core domain = Shipping & Tracking                | ✓            | ✓                                                  |                     |
| Handling = Supporting (รับข้อมูลงานจากภายนอก)      | ✓            | ✓                                                  |                     |
| Customer Tracking View = Supporting               | ✓            | ✓                                                  |                     |
| Routing = Generic (ภายนอก)                        | ✓            | ✓                                                  |                     |
| Non-goal (Billing/CRM/Carrier) ไม่ถูกนำเข้ามาผิด | ✓            | ✓                                                  | ชัดเจน              |
| ระบุช่องว่าง Billing/Customer (bonus item)       | —            | ✗ (มีเฉพาะ non-goal ไม่ได้ระบุว่า "อนาคตควรสร้าง Billing BC") | ได้ bonus แต่ไม่ได้รับ |

**คะแนน: 3 / 4** (ผ่านเกณฑ์; ไม่ได้เสนอ bonus point "ในอนาคต Billing/Customer ควร model อิสระ")

## Skill 04 — ddd-contexts (น้ำหนัก 1.5)

| Anchor                                           | Ground Truth                                          | Blind Hit                     | หมายเหตุ                                                                                                                |
| :----------------------------------------------- | :---------------------------------------------------- | :---------------------------- | :---------------------------------------------------------------------------------------------------------------------- |
| 4 BC: Booking / Handling / Tracking / Routing    | ✓                                                     | ✓                             | ครบถ้วน                                                                                                                  |
| Tracking read-only, ห้ามตัดสิน                     | ✓                                                     | ✓ (ADR-02)                    | ชัดเจน                                                                                                                  |
| Booking เป็นเจ้าของสิทธิ์การตัดสินใจหลัก          | ✓                                                     | ✓ (ADR-01)                    | ชัดเจน                                                                                                                  |
| ใช้ ACL กับ Pathfinder                            | ✓                                                     | ✓ (ADR-03)                    | ชัดเจน                                                                                                                  |
| ShippingRequest vs Shipment แยกกัน                | Ground truth ใช้ RouteSpecification + Cargo ไม่มี ShippingRequest อิสระ | ✓ (ADR-04, blind แยกชั้นเพิ่ม) | **semantic drift เล็กน้อย**: ground truth มี Cargo ตั้งแต่ก่อนเลือกแผน; blind แยก "ก่อนเลือกแผน" เป็น ShippingRequest ละเอียดกว่าแต่เบี่ยงเบนจากโมเดล ground truth |
| Customer notification context                     | —                                                     | ✗                             | ground truth ก็ไม่ได้แยก                                                                                               |
| Glossary per-BC                                  | ✓                                                     | ✓                             |                                                                                                                         |
| รายการคำตรงข้าม (antonym list)                    | ✓                                                     | ✓ (5 ประเภท)                  |                                                                                                                         |

**คะแนน: 3.5 / 4** (ใกล้ดีเลิศ; การ引入 ShippingRequest อิสระเป็นการปรับปรุงที่สมเหตุสมผลแต่ไม่ตรงกับ ground truth ทั้งหมด หัก 0.5)

## Skill 05 — ddd-context-map (น้ำหนัก 1.5)

| Anchor                                            | Ground Truth | Blind Hit                     | หมายเหตุ                                |
| :------------------------------------------------ | :----------- | :---------------------------- | :-------------------------------------- |
| Booking ↔ Pathfinder: ACL + Customer-Supplier     | ✓            | ✓                             | hit                                     |
| Handling → Booking/Tracking: Published Language   | ✓            | ✓ (OHS + PL)                  | hit                                     |
| ฝ่ายงานภายนอก → Handling: Conformist + edge ACL  | ✓            | ≈ (blind เรียก "channel adaptation layer") | semantic เทียบเท่า ชื่อไม่เป็นมาตรฐาน |
| Failure mode และ degradation                      | ✓            | ✓                             | ครบถ้วน                                  |
| Ownership ของสัญญา (contract ownership)           | ✓            | ✓                             | ครบถ้วน                                  |
| กลยุทธ์เวอร์ชัน (version strategy)               | ✓            | ✓                             | 2 มิติ (event + RouteVersion) ชัดเจนกว่า |
| ไม่มี circular dependency                         | ✓            | ✓                             | แผนภาพชัดเจน                            |

**คะแนน: 4 / 4** (ดีเลิศ)

## Skill 06 — ddd-aggregates (น้ำหนัก 2.0, น้ำหนักสูงสุด)

| Anchor                                                   | Ground Truth | Blind Hit                      | หมายเหตุ                                                                                                                                                             |
| :------------------------------------------------------- | :----------- | :----------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Aggregate Root 4 ตัว: Cargo / HandlingEvent / Voyage / Location | ✓            | ✗ บางส่วน                     | **Blind ให้ Shipment + HandlingFact + TrackingView + RouteCandidate + PortDirectory; ขาด Voyage; Location อยู่ในรูปแบบ PortDirectory แต่ระบุเพียง "assume"**        |
| HandlingEvent เป็น Aggregate อิสระ (ADR-1 performance)   | ✓            | ✓ (HandlingFact อิสระ)        | ✓ เหตุผลสมเหตุสมผลแต่ไม่ได้ระบุว่า "performance"                                                                                                                   |
| Delivery เป็น derived VO ห้าม setter                      | ✓            | ✓ (I-4 ชัดเจน)                | hit                                                                                                                                                                   |
| I4/I5 (voyage/type linking)                               | ✓            | ✓ (I-8 แสดงในตัว)             | hit                                                                                                                                                                   |
| HandlingEvent identity 5 ตัว                              | ✓            | ✓ (DeduplicationKey 5 ฟิลด์)  | hit                                                                                                                                                                   |
| RouteSpec.isSatisfiedBy(Itinerary) Specification pattern  | ✓            | ✗                              | ไม่ได้ระบุ Specification pattern; factory validation ทำหน้าที่แทน                                                                                                    |
| Repository: HandlingEventRepository ไม่มี generic CRUD    | ✓            | ≈                              | appendIfAbsent + findById + history ผ่านเกณฑ์ แต่เปิด暴露 "findByShipment" query ที่กว้างเกินไป (เบี่ยงเบนเล็กน้อย)                                                  |
| Aggregate Cargo ห้าม reference object HandlingEvent เก็บเฉพาะ ID | ✓         | ✓ (I-11 ชัดเจน)               | hit                                                                                                                                                                   |
| RouteCandidate ถูกระบุเป็น Aggregate อย่างผิดพลาด       | —            | ✗                              | self-review (08) ระบุเป็น P1 แล้ว แนะนำลดเป็น VO; หัก 0.25                                                                                                          |

**สิ่งที่ขาด**:

- **ขาด Aggregate Voyage**: `VoyageRef` ทำหน้าที่ reference เท่านั้น แต่ใน ground truth Voyage เป็น Aggregate อิสระ (Schedule, CarrierMovement) Blind สมมติว่า "จัดการโดยภายนอก" แต่ตัวอย่างจริง Voyage เป็น Aggregate ภายใน นี่คือ semantic gap ไม่ใช่ terminology difference
- **ขาด Aggregate Location อิสระ**: `PortDirectory` "assume ว่ามีอยู่" เท่านั้น ไม่ได้ระบุ Aggregate root/invariant อย่างชัดเจน
- ไม่ได้ระบุ Specification pattern

**คะแนน: 2.5 / 4** (ใช้ได้ในระดับสูง; ขาดการประกาศชัดเจนของ Aggregate Voyage/Location สองตัว)

## Skill 07 — ddd-domain-interactions (น้ำหนัก 1.5)

| Anchor                                                                | Ground Truth | Blind Hit                                                 | หมายเหตุ                          |
| :-------------------------------------------------------------------- | :----------- | :-------------------------------------------------------- | :-------------------------------- |
| RoutingService เป็น Domain Service interface + Infrastructure ACL implementation แยกกัน | ✓            | ✓ (RoutingService อยู่ใน Domain layer ของ Booking; ACL อยู่ใน Infrastructure) | hit                                |
| CargoInspectionService subscribe CargoWasHandled → emit misdirected/arrived | ✓          | ✓ (MisroutingDetector + CargoDelivered event)             | hit, ความรับผิดชอบต่างกันเล็กน้อยแต่เทียบเท่า |
| CargoWasHandled เป็น Published Language ข้าม BC                       | ✓            | ✓ (AcceptedHandlingEvent)                                 | hit (terminology difference)       |
| Idempotency key = HandlingEvent identity 5 ตัว                         | ✓            | ✓ (HandlingFactId + DeduplicationKey)                     | hit                                |
| HandlingEventFactory: Type+Voyage linking validation                    | ✓            | ✓ (HandlingFactFactory)                                   | hit                                |
| เส้นทางหลัก + unloading ผิด + สาย 3 สถานการณ์                          | ✓ (2 แรก)    | ✓ ทั้ง 3 สถานการณ์                                        | สถานการณ์สายเกิน ground truth      |
| Subscriber และ side effect                                              | ✓            | ✓                                                         |                                    |

**คะแนน: 4 / 4** (ดีเลิศ)

## Skill 08 — ddd-model-review (น้ำหนัก 1.0)

| Anchor                                                              | Ground Truth ที่คาดไว้ | Blind Hit | หมายเหตุ                                                                                                               |
| :------------------------------------------------------------------ | :--------------------- | :-------- | :--------------------------------------------------------------------------------------------------------------------- |
| Self-review 8 มิติ                                                  | —                      | ✓         | โครงสร้างสมบูรณ์                                                                                                       |
| การตัดสิน backtrack trigger                                          | —                      | ✓         | 5 ข้อตัดสินทั้งหมด                                                                                                     |
| ระบุความซ้ำซ้อน semantic ของ HandlingEvent/Activity/TransportStatus (bonus สำคัญ) | ✓                | ✗         | **ขาด**: ไม่ได้ระบุความซ้ำซ้อนนี้ (TrackingView ใน blind ผสาน HandlingActivity กับ TransportStatus เข้าด้วยกัน จึงรู้สึกว่าไม่ซ้ำซ้อน) |
| ระบุช่องว่าง Billing/Customer (bonus)                               | ✓                      | ≈         | non-goal ได้บันทึกไว้แล้วแต่ไม่ได้เสนอเป็น "known gap สำหรับ model evolution ในอนาคต" อย่างอิสระ                        |
| ระบุช่องว่าง Carrier (bonus)                                        | ✓                      | ✗         | VoyageRef "จัดการโดยภายนอก" เป็นการหลบเลี่ยง Carrier modeling โดยไม่ได้ระบุอย่างชัดเจน                                   |

**คะแนน: 2.5 / 4** (ใช้ได้; bonus item 3 ตัวสำคัญไม่ได้รับ แต่ internal consistency review ผ่านเกณฑ์)

## คะแนนถ่วงน้ำหนักรวม

| Skill                   | คะแนน | น้ำหนัก |   ถ่วงน้ำหนัก   |
| :---------------------- | :--: | :--: | :---------: |
| ddd-scope               | 4.0  | 1.0  |    4.0    |
| ddd-discover            | 4.0  | 1.5  |    6.0    |
| ddd-subdomains          | 3.0  | 1.0  |    3.0    |
| ddd-contexts            | 3.5  | 1.5  |   5.25    |
| ddd-context-map         | 4.0  | 1.5  |    6.0    |
| ddd-aggregates          | 2.5  | 2.0  |    5.0    |
| ddd-domain-interactions | 4.0  | 1.5  |    6.0    |
| ddd-model-review        | 2.5  | 1.0  |    2.5    |
| **รวม**                 |  —   | 11.0 | **37.75** |

**คะแนนถ่วงน้ำหนักรวม**: 37.75 / 44 = **85.8%** (B+ / ดี)

## Bonus และ Deduction

|                                    รายการ                               |  +/-   | คำอธิบาย                                                       |
| :------------------------------------------------------------: | :----: | :----------------------------------------------------------- |
|              B-bonus 1 ระบุ Billing/Customer                     | ไม่ได้รับ | มีเฉพาะ non-goal statement                                  |
| B-bonus 2 ระบุความซ้ำซ้อน HandlingEvent/Activity/TransportStatus | ไม่ได้รับ | โมเดลตาบอดผสานแนวคิดเหล่านี้เข้าด้วยกัน กลับ "ไม่รู้สึกว่าซ้ำซ้อน" ควรเป็นบทเรียน |
|              B-bonus 3 การ简化 modeling ของ Carrier ภายนอก       | ไม่ได้รับ | คำว่า "จัดการโดยภายนอก" ของ VoyageRef คลุมเครือ              |
|        B-deduction 1 HandlingEventRepository generic CRUD         |   ไม่มี   | blind ไม่ได้ทำผิดข้อนี้                                      |
|           B-deduction 2 RoutingService implementation ใน Domain layer |   ไม่มี   | blind แยกแยะชัดเจน                                            |
|              B-deduction 3 Routing ใส่ใน Booking                   |   ไม่มี   | blind externalize ชัดเจน                                      |
|               B-deduction 4 Delivery มี setter                     |   ไม่มี   | blind I-4 ห้ามไว้ชัดเจน                                       |

**คะแนนถ่วงน้ำหนักสุดท้าย**: ไม่มี deduction, bonus ไม่ได้รับ → **85.8%** คงเดิม

## ผลสังเกตสำคัญ

### สิ่งที่ทำได้ดี

1. **Stage I / III (discover / interactions) แข็งแกร่งที่สุด (4.0)**: Event storming coverage, idempotency strategy, ACL layering แม่นยำทั้งหมด
2. **การเพิ่มเติมที่เกิน ground truth**: Late arrival replay (E-B3) และ RouteVersion versioning เป็น industrial-grade enhancement ที่ ground truth ไม่ได้กล่าวถึงอย่างชัดเจน
3. **วินัย non-goal**: Billing/CRM/Carrier/Warehousing ถูกตัดออกอย่างเคร่งครัด ไม่มี scope creep

### สิ่งที่ต้องปรับปรุง

1. **การระบุ Aggregate ค่อนข้างอนุรักษ์นิยม (ร้ายแรงที่สุด)**: Voyage และ Location ไม่ได้ถูกยกเป็น Aggregate อิสระ ลดเป็น "external reference / assume dictionary" นี่คือจุดอ่อนจริงของ blind run — เมื่อไม่เห็น source code ของ Cargo เป็นการยากที่จะอนุมานว่า "Voyage เป็น internal management voyage"
2. **ขาด Specification pattern**: Pattern คลาสสิกของ DDD คือ RouteSpec.isSatisfiedBy ไม่ได้ถูกระบุ
3. **bonus item ของ model-review ขาดทั้งหมด**: ความซ้ำซ้อน HandlingEvent/Activity/TransportStatus, Billing/Customer evolution, Carrier modeling ไม่ได้ถูกระบุเอง แสดงว่า review ปัจจุบันเน้น "internal consistency" เป็นหลัก ขาดมุมมอง "เปรียบเทียบกับ industry standard implementation"

### ข้อเสนอแนะสำหรับระบบ Skill

1. **SKILL.md ของ ddd-aggregates ควรเพิ่ม**: "นอกจากการเริ่มจาก invariant ของธุรกิจแล้ว ควรมองจากมุม 'external reference object ต้องจัดการ lifecycle ภายในหรือไม่' เพื่อหลีกเลี่ยงการพลาด Aggregate ที่ดูเหมือนภายนอกแต่จริงๆ ต้องสร้างภายใน (เช่น Voyage)"
2. **SKILL.md ของ ddd-model-review ควรเพิ่ม**: "ถ้าอุตสาหกรรมมี mature open source reference implementation review ควรเปรียบเทียบและ列出 semantic overlap/convergence point ในโมเดลของตัวเอง (เช่น Activity vs Status vs Event)"
3. **ShippingRequest vs Cargo ใน ddd-contexts**: การแยกย่อยของ blind ละเอียดกว่า ควรคงไว้; ground truth ไม่แยกเพราะ Spring + Hibernate implementation constraint ไม่ใช่เพราะโมเดลเองต้องการ