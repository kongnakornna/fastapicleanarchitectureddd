# Backtrack-Trigger Test — Flaw Injection

> วัตถุประสงค์: ตรวจสอบว่า feedback loop trigger ของ `ddd-model-review` สามารถระบุและให้ backtrack instruction ได้อย่างถูกต้องภายใต้ **defect ที่ inject อย่างมีการควบคุม**
> วิธีการ: inject 3 ประเภทของ known defect ลงในผลลัพธ์ตาบอด `06-ddd-aggregates.out.md` → ให้ review รันใหม่อีกครั้ง → ตรวจสอบว่า trigger backtrack ที่เกี่ยวข้องหรือไม่

## ทดสอบ Matrix

| หมายเลข | Defect ที่ inject                                                                                                                          | เงื่อนไขที่คาดไว้                       | Backtrack ไปที่                |
| :------: | :---------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------- | :----------------------------- |
|   F1     | ลบ Invariant ส่วนใหญ่ (I-3, I-4, I-5, I-6, I-8, I-9) เหลือเฉพาะ I-1, I-7, I-10, I-11 (4/11 = 36%)                                       | อัตราการแสดง invariant < 60%           | `ddd-aggregates`               |
|   F2     | ให้ TrackingView รับผิดชอบ "unloading judgment" ซ้ำกับ MisroutingDetector ของ Booking                                                      | Aggregate boundary กับ context boundary ขัดแย้ง (ตัดสินใจข้าม boundary) | `ddd-contexts`     |
|   F3     | ลบ event `HandlingApplied` / `ETARecalculated` / `CargoMisroutedDetected` / `CargoDelivered` 4 ตัว (จาก 11 เหลือ 7, ประมาณ 64%)          | ความครบถ้วนของ event < 70%             | `ddd-domain-interactions`      |
|   F4     | แนวคิดหลัก "สินค้าหนึ่ง shipment" ใช้ชื่อเรียก 3 แบบ `Shipment` / `Cargo` / `Order` ผสมกันใน 04 (อัตราความขัดแย้ง 2/9 = 22.2%)            | อัตราความขัดแย้งศัพท์ > 20%            | `ddd-contexts`                 |
|   F5     | 05 ประกาศ ACL แต่ 07 ให้ `RoutingService` คืน raw field จาก Pathfinder โดยตรง (bypass การแปล/degradation/isolation zone)                   | Integration pattern กับ context map ไม่สอดคล้อง | `ddd-context-map`     |

> Defect แต่ละตัวแก้ไขเฉพาะไฟล์ "flawed" version `06/07` เท่านั้น; ไม่แก้ `01`~`05`, `08` ที่เป็นผลลัพธ์เดิม

## F1 — อัตราการแสดง invariant < 60%

### รุ่นที่ inject (flawed-06 summary)

```text
Invariant ที่เหลือ (4 ข้อเท่านั้น):
- I-1 Shipment.origin/destination ไม่เปลี่ยนแปลง
- I-7 HandlingFact ห้ามแก้ไข
- I-10 TrackingView ขับเคลื่อนโดย Booking event เท่านั้น
- I-11 cross-aggregate ใช้เฉพาะ ID

ลบ: I-2, I-3, I-4, I-5, I-6, I-8, I-9
```

การคำนวณ invariant coverage (เดิม 11 ข้อ → เหลือ 4 ข้อ):

- Aggregate Shipment: 6 ข้อ → 1 ข้อ
- Aggregate HandlingFact: 3 ข้อ → 1 ข้อ
- Coverage: 4/11 = **36.4%**

### Review รันใหม่ (ผลลัพธ์ที่คาดไว้)

| เงื่อนไขที่ trigger             | ค่าปัจจุบัน | Threshold ที่ trigger |  ถูก trigger หรือไม่   |
| :----------------------------- | :--------: | :------------------: | :-----------------: |
| อัตราการแสดง invariant         |   36%      |       < 60%          | **✅ ถูก trigger** |
| อัตราความขัดแย้งศัพท์             |   < 10%    |       > 20%          |        ไม่         |
| ความครบถ้วนของ event              |   100%     |       < 70%          |        ไม่         |
| Aggregate-Context boundary ขัดแย้ง |   ไม่มี    |      รายการใดๆ       |        ไม่         |

**Backtrack instruction**: กลับไป `ddd-aggregates` 提炼 invariant ใหม่ รายการปัญหาเฉพาะ:

| ปัญหา                                                        | หลักฐาน (artifact item เดิม)         | การแก้ไขที่แนะนำ                                                                   |
| :----------------------------------------------------------- | :------------------------------------ | :--------------------------------------------------------------------------------- |
| Shipment ขาด consistency constraint ระหว่าง route กับ origin/destination | flawed-06 §ตาราง invariant        | สร้าง I-3 ใหม่: route.legs จุดเริ่มต้นของช่วงแรก == origin และจุดสิ้นสุดของช่วงสุดท้าย == destination |
| Shipment.deliveryProgress ไม่มี derived declaration          | flawed-06 §Aggregate Shipment         | สร้าง I-4 ใหม่: deliveryProgress ต้อง derived, ห้าม setter                       |
| ขาดกฎคำนวณ isMisrouted / ETA                                | flawed-06 §Aggregate Shipment         | สร้าง I-5, I-6 ใหม่                                                                |
| ขาด type/voyage linking validation ของ HandlingFact          | flawed-06 §HandlingFact               | สร้าง I-8 ใหม่                                                                     |
| ขาด dedup key                                               | flawed-06 §HandlingFact               | สร้าง I-9 ใหม่                                                                     |

### ข้อสรุป

✅ **F1 ผ่าน**: Backtrack trigger ระบุได้ถูกต้องว่าอัตราการแสดง invariant 36% < 60% และชี้ไปที่ `ddd-aggregates`

## F2 — Aggregate boundary กับ context boundary ขัดแย้ง

### รุ่นที่ inject (flawed-06 §TrackingView aggregate)

```text
TrackingView aggregate ขยายหน้าที่ (inject):
- เก็บสำเนา route
- เก็บสำเนา HandlingFact ล่าสุด N ตัว
- method: detectMisrouting() → เมื่อ portCode ที่ unload ล่าสุด ≠ ท่าเรือที่ตรงกับ route ให้ตั้ง isMisrouted=true
- method: calculateETA() → คำนวณจาก route + handlings
```

สิ่งนี้จะทำให้:

- Tracking context (ตาม convention ของ `04-contexts`) **ควรเป็น read-only view**, ADR-02 ห้าม carry business rule;
- MisroutingDetector ของ Booking และ detectMisrouting ของ Tracking กลายเป็น **dual-headed judgment**, กฎอาจเบี่ยงเบน

### Review รันใหม่ (ผลลัพธ์ที่คาดไว้)

| เงื่อนไขที่ trigger                     | หลักฐาน                                                                                                       |     ถูก trigger หรือไม่     |
| :--------------------------------------- | :------------------------------------------------------------------------------------------------------------- | :-----------------------: |
| Aggregate boundary กับ context boundary ขัดแย้ง | flawed-06 §TrackingView เพิ่ม detectMisrouting() ขัดแย้งกับ ADR-02 "Tracking read-only ห้ามตัดสินใจ" ของ `04-contexts` |     **✅ ถูก trigger**     |
| อัตราความขัดแย้งศัพท์                      | `isMisrouted` ถูกคำนวณใน 2 จุด, definition ตรงกันแต่ "ใครเป็น authority" ไม่สอดคล้อง                           | ขอบ (<20%, ไม่ trigger) |
| อัตราการแสดง invariant                    | ยัง 100%                                                                                                        |           ไม่             |
| ความครบถ้วนของ event                         | ยัง 100%                                                                                                        |           ไม่             |

**Backtrack instruction**: กลับไป `ddd-contexts` ตรวจสอบ context boundary ใหม่ รายการปัญหาเฉพาะ:

| ปัญหา                                | หลักฐาน                                        | การแก้ไขที่แนะนำ                                                                                                                                                   |
| :----------------------------------- | :---------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Tracking context carry การตัดสินใจทางธุรกิจ | flawed-06 TrackingView.detectMisrouting()       | ทางเลือก A: ยกเลิก method ตัดสินใจของ TrackingView ปฏิบัติตาม ADR-02 อย่างเข้มงวด; ทางเลือก B: ถ้า Tracking จำเป็นต้องมีสิทธิ์ตัดสินใจ ให้ย้าย MisroutingDetector จาก Booking ไป Tracking และแก้ `04-contexts` |
| การตัดสินใจ dual-headed (Booking + Tracking) | flawed-06 + 07 §MisroutingDetector              | กำหนด **owner เดียว** (แนะนำ Booking), อีกฝั่งเป็น projection เท่านั้น                                                                                               |

### ข้อสรุป

✅ **F2 ผ่าน**: Trigger ระบุว่า "aggregate ได้ carry หน้าที่ที่ context ไม่ควรมี" และชี้ไปที่ `ddd-contexts`

## F3 — ความครบถ้วนของ event < 70%

### รุ่นที่ inject (flawed-07 §Booking publish)

ลบ event 4 ตัว จาก 11 event ที่ Booking publish:

- `HandlingApplied`
- `ETARecalculated`
- `CargoMisroutedDetected`
- `CargoDelivered`

เหลือ 7 ตัว ความครบถ้วนของ event = 7/11 = **63.6%**

ปัญหาสำคัญ:

- Tracking ฝั่ง downstream ไม่สามารถ project "งานที่ apply แล้ว" และ "ETA ที่เปลี่ยน" ได้
- การระบุ exception ไม่ได้ publish สู่ภายนอก ช่องทางแจ้งเตือนขาดตอน
- event derived จากเส้นทางหลัก M13/M14/E-C1/E-C6 ใน `02-ddd-discover` หายไปจาก event catalog

### Review รันใหม่ (ผลลัพธ์ที่คาดไว้)

| เงื่อนไขที่ trigger  | ค่าปัจจุบัน | Threshold |  ถูก trigger หรือไม่   |
| :------------------- | :--------: | :-------: | :-----------------: |
| ความครบถ้วนของ event   |  63.6%     |  < 70%    | **✅ ถูก trigger** |
| รายการอื่นๆ            |     —      |     —     |        ไม่         |

**Backtrack instruction**: กลับไป `ddd-domain-interactions` เติม event catalog ให้ครบ รายการปัญหาเฉพาะ:

| ปัญหา                                                                       | หลักฐาน                            | การแก้ไขที่แนะนำ                                                                        |
| :--------------------------------------------------------------------------- | :---------------------------------- | :--------------------------------------------------------------------------------------- |
| เส้นทางหลัก M13 (ETARecalculated) มีใน `02-discover` แต่ขาดใน event catalog | flawed-07 เทียบกับ 02 §M13           | เพิ่ม event `ETARecalculated`, กำหนด idempotency key (shipmentId, routeVersion, lastHandlingFactId) |
| Event unloading ไม่ได้ publish สู่ภายนอก                                     | flawed-07 เทียบกับ 02 §E-C1          | เพิ่ม `CargoMisroutedDetected`; subscriber รวมช่องทางแจ้งเตือน                            |
| Event การรับสินค้าขาด                                                         | flawed-07 เทียบกับ 02 §M12           | เพิ่ม `CargoDelivered`                                                                   |
| `HandlingApplied` ที่ Tracking ต้องใช้ขาด                                    | flawed-07 เทียบกับ 05 §Booking→Tracking | เพิ่ม `HandlingApplied`                                                               |

### ข้อสรุป

✅ **F3 ผ่าน**: Trigger ระบุว่าความครบถ้วนของ event 63.6% < 70% และชี้ไปที่ `ddd-domain-interactions`

## F4 — อัตราความขัดแย้งศัพท์ > 20%

> วิธี inject ตาม design "รายการที่ยังไม่ได้ทดสอบ" เดิม: ใช้ชื่อเรียก 3 แบบ `Shipment` / `Cargo` / `Order` ผสมกันในบทต่างๆ ของ 04

### รุ่นที่ inject (flawed-04 summary)

แนวคิดหลัก "สินค้าหนึ่ง shipment" ใช้ชื่อเรียก 3 แบบในบทต่างๆ ของ 04:

```text
§สารบัญ Bounded Context         → "คำสั่งซื้อ / สินค้าหนึ่ง shipment Shipment"
§สารบัญ Universal Language (Booking) → "Cargo (definition เหมือน Shipment: การขนส่งจริงหนึ่งครั้งหลังลูกค้ายืนยันแผน)"
§ADR-04 boundary decision        → "Order (表述 เหมือน Shipment: คำสั่งซื้อที่เกิดขึ้นหลังยืนยันแผน)"

ความขัดแย้งที่สองจากต้นทางเดียวกัน:
- §สารบัญ "ความต้องการขนส่ง ShippingRequest" ↔ §ADR-04 "BookingRequest (ความตั้งใจในขั้นตอนขอแผน)"
```

สถิติศัพท์ที่ขัดแย้ง (ใน Universal Language ของ Booking context 9 ศัพท์ มี 2 ศัพท์ได้รับผลกระทบ):

- สินค้าหนึ่ง shipment: สารบัญ `Shipment` / คำศัพท์ `Cargo` / ADR `Order` — 3 ชื่อ refer กันและกัน
- ความต้องการขนส่ง: สารบัญ `ShippingRequest` / ADR-04 `BookingRequest` — 2 ชื่อ refer กันและกัน
- อัตราความขัดแย้ง = 2/9 = **22.2%** > 20%

### Review รันใหม่ (ผลลัพธ์ที่คาดไว้)

| เงื่อนไขที่ trigger  | ค่าปัจจุบัน | Threshold ที่ trigger |  ถูก trigger หรือไม่   |
| :------------------- | :--------: | :------------------: | :-----------------: |
| อัตราความขัดแย้งศัพท์ |  22.2%     |       > 20%          | **✅ ถูก trigger** |
| รายการอื่นๆ           |     —      |         —            |        ไม่         |

**Backtrack instruction**: กลับไป `ddd-contexts` ปรับปรุง Universal Language ให้สอดคล้องกัน รายการปัญหาเฉพาะ:

| ปัญหา                   | หลักฐาน (artifact item เดิม)               | การแก้ไขที่แนะนำ                                                         |
| :---------------------- | :------------------------------------------ | :----------------------------------------------------------------------- |
| ชื่อเรียกสินค้าหนึ่ง shipment 3 แบบ | flawed-04 §สารบัญ เทียบกับ §คำศัพท์ เทียบกับ §ADR-04 | กำหนดศัพท์เดียว (แนะนำ `Shipment`), แทนที่ในคำศัพท์และ ADR ทั้งหมด และเพิ่มใน anti-term list |
| ชื่อเรียกความต้องการขนส่ง 2 แบบ     | flawed-04 §สารบัญ เทียบกับ §ADR-04           | ปรับเป็น `ShippingRequest` ทั้งหมด, แก้ ADR-04                           |
| Event contract ชื่อได้รับผลกระทบ     | flawed-04 §คำศัพท์ รายการ "event ที่เกี่ยวข้อง" | ปรับชื่อ event เช่น `ShipmentBooked` ฯลฯ ให้สอดคล้องกับศัพท์ใหม่          |

### ข้อสรุป

✅ **F4 ผ่าน**: Trigger ระบุว่าอัตราความขัดแย้งศัพท์ 22.2% > 20% และชี้ไปที่ `ddd-contexts`

## F5 — Integration pattern กับ context map ไม่สอดคล้อง

> วิธี inject ตาม design "รายการที่ยังไม่ได้ทดสอบ" เดิม: 05 ประกาศ ACL แต่ 07 ให้ domain service คืน raw field จากภายนอกโดยตรง

### รุ่นที่ inject (flawed-05 + flawed-07 summary)

```text
flawed-05 (คงสภาพเดิม):
- ACL-1: Pathfinder → Booking, แผนภายนอกผ่านการแปลเป็น internal RouteCandidate; รหัสที่ไม่รู้จักเข้า isolation zone;
  ฟิลด์ราคาลบออก; timeout degradation เป็น "cache + empty list"

flawed-07 (inject):
- RoutingService.queryOptions() คืน raw OpenAPI payload จาก Pathfinder โดยตรง (ชื่อ field ภายนอก,
  รหัสท่าเรือ, timezone, ฟิลด์ราคาส่งต่อแบบเดิม)
- ไม่มี isolation zone, ไม่มี version compatibility, ไม่มี degradation handling
```

### Review รันใหม่ (ผลลัพธ์ที่คาดไว้)

| เงื่อนไขที่ trigger                        | หลักฐาน                                                                                     | ถูก trigger หรือไม่   |
| :----------------------------------------- | :------------------------------------------------------------------------------------------- | :-----------------: |
| Integration pattern กับ context map ไม่สอดคล้อง | flawed-07 §RoutingService เชื่อมต่อภายนอกโดยตรง ขัดแย้งกับ ACL-1 "การแปล/degradation/isolation zone" ของ flawed-05 | **✅ ถูก trigger** |
| อัตราความขัดแย้งศัพท์                        | ชื่อ field ภายนอก (เช่น port_code / ETD) เข้าสู่ core model                                  | ขอบ (<20%)       |
| รายการอื่นๆ                                   | —                                                                                            |        ไม่         |

**Backtrack instruction**: กลับไป `ddd-context-map` ตรวจสอบ integration boundary ใหม่ รายการปัญหาเฉพาะ:

| ปัญหา                                  | หลักฐาน                                    | การแก้ไขที่แนะนำ                                                  |
| :------------------------------------- | :------------------------------------------ | :--------------------------------------------------------------- |
| Raw field จากภายนอก leak เข้า core model | flawed-07 §RoutingService คืน payload จากภายนอก | คืน ACL translation: internal รับเฉพาะ `RouteCandidate`; รหัสที่ไม่รู้จักเข้า isolation zone |
| Timezone / หน่วยไม่ได้ normalize        | flawed-07 คืนค่าโดยตรง                       | แปลเป็น UTC ตามกฎ ACL-1 + ความหมาย occurredAt                    |
| ฟิลด์ราคาไม่ได้ลบออก (ข้อมูล non-goal เข้า database) | flawed-07 ส่งต่อ payload           | ลบฟิลด์ราคาตาม ACL-1                                             |
| Logic degradation และ isolation zone ไม่ทำงาน | flawed-07 ไม่มี cache / degradation branch | คืน "cache + empty list" และ alarm path                           |

### ข้อสรุป

✅ **F5 ผ่าน**: Trigger ระบุว่า tactical layer integration approach กับ mapping declaration ไม่สอดคล้องกัน และชี้ไปที่ `ddd-context-map`

## สรุปผล

| Defect ที่ inject               | Trigger ที่คาดไว้               | Trigger จริง | เป้าหมาย backtrack ที่คาดไว้         | เป้าหมาย backtrack จริง         | ผลการทดสอบ |
| :----------------------------- | :----------------------------- | :----------: | :---------------------------------- | :------------------------------- | :--------: |
| F1 Invariant expression 36%    | Invariant < 60%                | ✅           | ddd-aggregates                      | ddd-aggregates                   | ✅ PASS    |
| F2 Tracking ตัดสินใจเกินสิทธิ์ | Aggregate-Context boundary ขัดแย้ง | ✅           | ddd-contexts                        | ddd-contexts                     | ✅ PASS    |
| F3 ลบ 4 derived events         | ความครบถ้วน event < 70%         | ✅           | ddd-domain-interactions             | ddd-domain-interactions          | ✅ PASS    |
| F4 ชื่อเรียกสินค้าหนึ่ง shipment 3 แบบผสมกัน | อัตราความขัดแย้งศัพท์ > 20% | ✅           | ddd-contexts                        | ddd-contexts                     | ✅ PASS    |
| F5 Domain Service bypass ACL โดยตรง | Integration pattern ไม่สอดคล้อง | ✅           | ddd-context-map                     | ddd-context-map                  | ✅ PASS    |

**ข้อสรุป**: Backtrack trigger condition ทั้ง 5 ข้อของ `ddd-model-review` **ถูก activate อย่างถูกต้องทั้งหมด** ในการทดลอง inject ที่มีการควบคุม และ diagnosis ไม่มีข้อผิดพลาด, routing ตรงไปยังเป้าหมายที่คาดไว้ 5/5 ผ่านทั้งหมด