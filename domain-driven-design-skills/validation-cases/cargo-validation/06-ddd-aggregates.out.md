# 06 — ผลลัพธ์ ddd-aggregates (Blind Run)

> ข้อมูลนำเข้า: `01`~`05`
> ไฟล์นี้เป็นผลลัพธ์จากการจำลองการทำงานของ `ddd-aggregates` ใน blind run โดย **ไม่ได้อ้างอิง** วัสดุ ground truth ใน `reference/` ใดๆ

## สารบัญ Aggregate

| Aggregate | Context ที่สังกัด | Aggregate Root | Root ID | คำอธิบายขอบเขตธุรกรรม |
| :--- | :--- | :--- | :--- | :--- |
| **Shipment การขนส่งหนึ่งรายการ** | Booking | Shipment | ShipmentId | รวม: จุดเริ่มต้น/จุดหมาย เวลาถึงล่าสุด เส้นทางปัจจุบัน (มีเวอร์ชัน) ความคืบหน้าการจัดส่งที่คำนวณได้ (ตำแหน่ง/ขั้นตอนถัดไป/ETA/การขนถ่ายผิดหรือไม่) ธุรกรรมเดียวกันรับประกันความสอดคล้องระหว่าง "การกำหนดเส้นทาง" และ "การคำนวณความคืบหน้า" |
| **RouteCandidate ร่างเส้นทาง** | Booking | RouteCandidate | CandidateId (อายุสั้นภายใน ACL) | ค่าครั้งเดียวที่ ACL แปลงมาจากตัวเลือกภายนอก; ไม่บันทึกถาวร; ใช้โดย Shipment แล้ว freeze เป็น Shipment.route |
| **HandlingFact ข้อเท็จจริงการปฏิบัติงาน** | Handling | HandlingFact | HandlingFactId | ข้อเท็จจริงการปฏิบัติงานหนึ่งรายการเมื่อเขียนแล้วจะเปลี่ยนแปลงไม่ได้; คีย์ตัดซ้ำตรงจะใช้ Id ที่มีอยู่แล้ว; ธุรกรรมเดียวเขียนหนึ่งรายการ |
| **TrackingView มุม-view การติดตาม** | Tracking | TrackingView | ShipmentId (1:1) | มุม-view การอ่านล้วน; project จาก Event ที่ Booking เผยแพร่; ไม่แบกรับกฎธุรกิจ |
| **PortDirectory คลังข้อมูลท่าเรือ** (สันนิษฐาน) | Supporting | PortDirectoryEntry | PortCode | ข้อมูลอ้างอิง; อ่านอย่างเดียวสำหรับทุก Context |

> หมายเหตุ: `RouteCandidate` เหมาะจะเป็น Value Object มากกว่า Aggregate Root ที่บันทึกถาวร การรวมไว้ที่นี่เป็นเพื่อให้ ACL มีผลลัพธ์ที่ชัดเจน; เมื่อใช้งานจริงแนะนำให้กำหนดเป็น VO ภายในของ Booking

## การจัดหมวดหมู่ Entity / Value Object

### Aggregate Shipment

| ประเภท | ชื่อ | บทบาท | ฟิลด์สำคัญ / Invariant |
| :--- | :--- | :--- | :--- |
| Entity (Root) | Shipment | Aggregate Root ของคำสั่งซื้อ | id, origin, destination, latestArrival, route, deliveryProgress |
| VO | Origin / Destination | จุดเริ่มต้น/จุดหมาย | PortCode คงที่ |
| VO | LatestArrival | เวลาถึงล่าสุด | เปลี่ยนแปลงไม่ได้; หลังสร้างแล้วจะเปลี่ยนได้เฉพาะใน "กระบวนการเปลี่ยนแปลงของลูกค้า" โดยแทนค่าทั้งหมด |
| Entity (ภายใน) | Route | เส้นทาง (มีเวอร์ชัน) | version, legs[], เวลาถึงที่วางแผนไว้; เวอร์ชันเพิ่มขึ้นเรื่อยๆ |
| VO | Leg | ช่วงเรือ | from, to, loadTime, unloadTime, voyageRef |
| VO | VoyageRef | การอ้างอิงตารางเดินเรือภายนอก | เก็บเฉพาะรหัสอ้างอิง ไม่เก็บ Entity ภายนอก |
| VO | DeliveryProgress | ความคืบหน้าที่คำนวณได้ | currentLocation, nextExpectedAction, eta, isMisrouted, isDelivered |

### Aggregate HandlingFact

| ประเภท | ชื่อ | ฟิลด์สำคัญ / Invariant |
| :--- | :--- | :--- |
| Entity (Root) | HandlingFact | id, shipmentId, type, portCode, occurredAt, voyageLegRef, receivedAt |
| VO | HandlingType | enum (Receive/Load/Unload/Arrive/Transit/Claim); มีความเชื่อมโยงกับความจำเป็นของ voyageLegRef |
| VO | DeduplicationKey | (shipmentId, type, portCode, occurredAt, voyageLegRef) |

### Aggregate TrackingView

| ประเภท | ชื่อ | ฟิลด์สำคัญ |
| :--- | :--- | :--- |
| Entity (Root) | TrackingView | shipmentId (=1:1), currentLocation, nextExpectedAction, eta, isMisrouted, lastUpdated |

## ตาราง Invariant

| รหัส | Invariant | Aggregate ที่อยู่ | ตำแหน่งที่กระตุ้น | ระดับ |
| :--- | :--- | :--- | :--- | :--- |
| I-1 | origin/destination ของ Shipment เมื่อสร้างแล้วจะเปลี่ยนแปลงเงียบๆ ไม่ได้; การเปลี่ยนแปลงต้องผ่านกระบวนการ "วางแผนใหม่ / เปลี่ยนแปลงของลูกค้า" อย่างเปิดเผย | Shipment | การสร้าง การวางแผนใหม่ | เข้มงวด |
| I-2 | latestArrival ของ Shipment เปลี่ยนได้เฉพาะในกระบวนการวางแผนใหม่โดยได้รับอนุญาตจากฝ่ายธุรกิจเท่านั้น | Shipment | การวางแผนใหม่ | เข้มงวด |
| I-3 | Shipment.route ต้องเข้ากันได้กับ Shipment.origin/destination (จุดเริ่มต้นของช่วงแรก == origin จุดหมายของช่วงสุดท้าย == destination); ถ้าวางแผนใหม่จุดเริ่มต้นของช่วงแรก == ตำแหน่งจริงปัจจุบัน | Shipment | การกำหนดเส้นทาง | เข้มงวด |
| I-4 | Shipment.deliveryProgress ต้องเป็นค่าที่ **คำนวณได้** (จาก route + งานที่ได้รับการยอมรับ) ห้ามถูกตั้งค่าจากภายนอกโดยตรง | Shipment | ทุกครั้งหลังได้รับ Event งานที่ได้รับการยอมรับ | เข้มงวด |
| I-5 | isMisrouted เป็นจริงก็ต่อเมื่อท่าเรือของงาน "ขนถ่าย/ถึงท่า" ล่าสุด ≠ ท่าเรือที่วางแผนไว้ตามเวอร์ชันเส้นทางปัจจุบัน | Shipment | การคำนวณได้ | เข้มงวด |
| I-6 | ETA ต้องคำนวณใหม่จาก "เวอร์ชันเส้นทางปัจจุบัน + งานที่ได้รับการยอมรับ" ห้ามใช้เส้นทางในอดีต | Shipment | การคำนวณได้ | เข้มงวด |
| I-7 | HandlingFact เมื่อเขียนแล้วเปลี่ยนแปลงไม่ได้; การแก้ไขต้องทำโดย "เขียนทับด้วยข้อเท็จจริงใหม่ + เก็บประวัติ" | HandlingFact | การเขียน | เข้มงวด |
| I-8 | (type, voyageLegRef) ของ HandlingFact ต้องสมเหตุสมผล: Load/Unload/Transit ต้องมี voyageLegRef; Receive/Arrive/Claim ต้องไม่มี | HandlingFact | การเขียน | เข้มงวด |
| I-9 | DeduplicationKey เดียวกันมีได้สูงสุด 1 รายการใน HandlingFact | HandlingFact | การเขียน | เข้มงวด |
| I-10 | TrackingView ขับเคลื่อนโดย Event ที่คำนวณได้จาก Booking เท่านั้น; ห้ามถูกเขียนจากแหล่งอื่น | TrackingView | Project | เข้มงวด |
| I-11 | Shipment อ้างอิงเฉพาะสำเนาของ route; การอ้างอิงข้าม Aggregate ไปยัง HoldingFact เก็บเฉพาะ HandlingFactId | Shipment / HandlingFact | กฎการออกแบบ | ปานกลาง |

**การตรวจสอบความครอบคลุมของ Invariant**: 11 Invariant แบ่งเป็นconstraint เข้มงวด 10 รายการ ปานกลาง 1 รายการ

## ความสอดคล้องข้าม Aggregate

| สถานการณ์ | รูปแบบความสอดคล้อง | คำอธิบาย |
| :--- | :--- | :--- |
| Handling ยอมรับงานหนึ่งรายการ → Booking อัปเดต Shipment.deliveryProgress | สอดคล้องกันในที่สุด (ขับเคลื่อนด้วย Event) | Handling ส่ง + เผยแพร่ Event + Booking สมัครรับ; ฝั่ง Booking idempotent (ด้วย HandlingFactId) |
| Booking กำหนดเส้นทางใหม่ → Tracking อัปเดตมุม-view | สอดคล้องกันในที่สุด | ผ่าน Event RouteReassigned ไป project |
| งานมาถึงสาย → Booking คำนวณย้อนหลัง → Tracking project ใหม่ | สอดคล้องกันในที่สุด + การย้อนเวลา | รันสายพานคำนวณใหม่ตาม occurredAt |
| ลูกค้าเปลี่ยน origin/destination/latestArrival | สอดคล้องกันทันที (ธุรกรรมภายใน Aggregate) | เปลี่ยนได้เฉพาะผ่าน "คำสั่งเปลี่ยนแปลงของลูกค้า" โดย atomic พร้อมคำนวณ deliveryProgress ใหม่ |

## ร่างอินเทอร์เฟซ Repository

```text
interface ShipmentRepository {
    find(id: ShipmentId): Shipment
    save(shipment: Shipment): void   // เขียนทั้ง Aggregate, ล็อกแบบ optimistic บน route.version หรือ Aggregate version
    findOverdue(asOf: Timestamp): Shipment[]   // สำหรับฝ่ายปฏิบัติการ
}

interface HandlingFactRepository {
    appendIfAbsent(fact: HandlingFact): HandlingFactId   // เขียนแบบ idempotent; ตัดซ้ำด้วย DeduplicationKey
    findById(id: HandlingFactId): HandlingFact
    history(shipmentId: ShipmentId, orderBy: "occurredAt"): HandlingFact[]
}

interface TrackingViewRepository {
    upsertProjection(view: TrackingView): void
    findByShipment(id: ShipmentId): TrackingView
}
```

## ขอบเขตและกลยุทธ์ธุรกรรม

- **ขอบเขตการเขียน**: Shipment ธุรกรรมเดียวรวม "การกำหนด route + การคำนวณ deliveryProgress"; HandlingFact ธุรกรรมเดียวเขียนหนึ่งรายการ
- **ห้าม**: ธุรกรรมข้าม Aggregate ขนาดใหญ่ เมื่อ Booking อัปเดต Shipment อ้างอิง HandlingFact ผ่าน ID + สำเนา Event load เท่านั้น
- **คีย์ idempotent**: DeduplicationKey ของ HandlingFact; ฝั่ง Booking บริโภค AcceptedHandlingEvent ด้วย HandlingFactId แบบ idempotent

## การตรวจสอบตนเอง

- [x] ทุก Aggregate มีการระบุขอบเขตธุรกรรมที่ชัดเจน
- [x] แยกแยะ Aggregate Root, Entity, VO ได้ชัดเจน
- [x] Invariant ≥ 10 รายการ และสัดส่วนconstraint เข้มงวดสูง (10/11)
- [x] ปฏิสัมพันธ์ข้าม Aggregate ทั้งหมดผ่านความสอดคล้องกันในที่สุด ไม่พบธุรกรรมขนาดใหญ่แฝง
- [x] อินเทอร์เฟซ Repository เปิดเผยเฉพาะระดับ Aggregate Root เท่านั้น
- [x] สอดคล้องกับสัญญาของ `ddd-context-map` (HandlingFactId เป็นคีย์ idempotent)

## จุดอ่อนที่อาจเกิดขึ้น (บันทึกด้วยความจริงใจ)

- ตำแหน่งของ `RouteCandidate` ค่อนข้างน่าอึดอัด: ควรอยู่ใน VO ของ Booking จะเรียบร้อยกว่า การแยกออกมาที่นี่ทำเพื่อความสะดวกในการอธิบาย ACL เมื่อใช้งานจริงแนะนำให้ตัด Aggregate ออก
- `VoyageRef` ปัจจุบันเป็นเพียงรหัสอ้างอิง; ถ้าในอนาคตต้องจัดการวงจรชีวิต "ตารางเดินเรือ" ภายใน (ขยายจากเป้าหมายที่ไม่ใช่) จะต้องอัปเกรดเป็น Aggregate อิสระ ตอนนี้สันนิษฐานว่าจัดการโดยภายนอก
