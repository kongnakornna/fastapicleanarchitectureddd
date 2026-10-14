# 07 — ผลลัพธ์ ddd-domain-interactions (Blind Run)

> ข้อมูลนำเข้า: `01`~`06`
> ไฟล์นี้เป็นผลลัพธ์จากการจำลองการทำงานของ `ddd-domain-interactions` ใน blind run โดย **ไม่ได้อ้างอิง** วัสดุ ground truth ใน `reference/` ใดๆ

## สารบัญ Domain Event

### Event ที่ Booking Context เผยแพร่

| Event | ฟิลด์สำคัญ | ผู้กระตุ้น | ผู้สมัครรับ | คีย์ idempotent |
| :--- | :--- | :--- | :--- | :--- |
| `ShippingRequestSubmitted` | requestId, origin, destination, latestArrival | SubmitShippingRequest | (ภายใน) | requestId |
| `OptionsPresented` | requestId, candidates[] | การค้นหา ACL สำเร็จ | ฝั่ง frontend สำหรับลูกค้า (ผ่าน Tracking หรือเชื่อมต่อโดยตรง) | requestId + queryVersion |
| `ShipmentBooked` | shipmentId, requestId, origin, destination, latestArrival | ConfirmBooking | Tracking, การแจ้งเตือน | shipmentId |
| `RouteAssigned` | shipmentId, routeVersion, legs[] | AssignRoute | Tracking | shipmentId + routeVersion |
| `RouteReassigned` | shipmentId, newRouteVersion, legs[], reason | กระบวนการ Rerouting | Tracking | shipmentId + newRouteVersion |
| `HandlingApplied` | shipmentId, handlingFactId, type, portCode, occurredAt | Booking บริโภคงานที่ได้รับการยอมรับ | Tracking | shipmentId + handlingFactId |
| `CargoMisroutedDetected` | shipmentId, actualPort, expectedPort, detectedAt | อนุมานได้ | Tracking, การแจ้งเตือน, ฝ่ายปฏิบัติการ | shipmentId + handlingFactId |
| `ETARecalculated` | shipmentId, newEta, basedOnRouteVersion | อนุมานได้ | Tracking | shipmentId + (routeVersion, lastHandlingFactId) |
| `CargoDelivered` | shipmentId, deliveredAt | อนุมานได้ (หลังงานรับมอบมาถึง) | Tracking, การแจ้งเตือน | shipmentId |
| `NoFeasibleOptions` | requestId | ภายนอกส่งค่าว่างกลับมา | ฝ่ายปฏิบัติการ | requestId |
| `SelectedOptionExpired` | requestId, candidateId | ลูกค้าเลือกช้า | ลูกค้า | requestId + candidateId |

### Event ที่ Handling Context เผยแพร่

| Event | ฟิลด์สำคัญ | ผู้กระตุ้น | ผู้สมัครรับ | คีย์ idempotent |
| :--- | :--- | :--- | :--- | :--- |
| `AcceptedHandlingEvent` | handlingFactId, shipmentId, type, portCode, occurredAt, voyageLegRef, receivedAt | RegisterHandling ผ่านการตัดซ้ำ+การตรวจสอบ | Booking | handlingFactId |
| `DuplicateHandlingRejected` | inboundPayload, duplicateOfId | RegisterHandling จับคู่ตัดซ้ำ | การตรวจสอบของฝ่ายปฏิบัติการ | inboundPayload.hash |
| `InvalidHandlingQuarantined` | inboundPayload, violations[] | RegisterHandling ตรวจสอบไม่ผ่าน | การตรวจสอบของฝ่ายปฏิบัติการ | inboundPayload.hash |
| `LateHandlingIngested` | handlingFactId, occurredAt, receivedAt, lagSeconds | ตรวจพบความล่าช้าขณะรับ | Booking (กระตุ้นการคำนวณย้อนหลัง) | handlingFactId |

## สัญญา Event สำหรับการเชื่อมต่อ (ภายนอก)

| สัญญา | ทิศทาง | ตัวกลาง | เวอร์ชัน | หมายเหตุ |
| :--- | :--- | :--- | :--- | :--- |
| AcceptedHandlingEvent | Handling → Booking | Event bus | v1 | Published Language |
| กลุ่ม Event ที่คำนวณของ Booking | Booking → Tracking | Event bus | v1 | Open Host Service |
| การค้นหา RouteCandidate | Booking ↔ Pathfinder | HTTP ซิงโครนัส | — (เวอร์ชันภายนอก) | ผ่าน ACL |
| Event การแจ้งเตือนลูกค้า | Tracking/Booking → ช่องทางการแจ้งเตือน | ไม่พร้อมกัน | v1 | แนะนำแยกเป็นบริการย่อยอิสระ |

## กลยุทธ์ Idempotency

| ฝั่งผู้บริโภค | คีย์ idempotent | หน้าต่างตัดซ้ำ |
| :--- | :--- | :--- |
| Booking บริโภค AcceptedHandlingEvent | handlingFactId | ไม่จำกัด (บันทึกถาวร applied-set) |
| Tracking บริโภค Event ของ Booking | shipmentId + eventVersion | บันทึกหมายเลขเวอร์ชันล่าสุดถาวร |
| การเรียกใช้ Pathfinder ตอบกลับ | requestId | 5 นาที (เก็บแคชได้) |
| การแจ้งเตือนลูกค้า | shipmentId + reason + routeVersion | บันทึกถาวร |

## Domain Service

| Service | Context ที่อยู่ | หน้าที่ | เหตุผลที่ไม่ใส่ใน Aggregate |
| :--- | :--- | :--- | :--- |
| `RoutingService` | Booking | เรียก ACL กรองตัวเลือกที่ยอมรับได้จากตัวเลือกที่เป็นไปได้; เตรียมพารามิเตอร์ค้นหา "จากตำแหน่งปัจจุบัน" สำหรับการวางแผนใหม่ | เกี่ยวข้องกับการเรียกใช้ภายนอกและอัลกอริทึมกลยุทธ์ ไม่ใช่ Invariant ภายใน Shipment |
| `MisroutingDetector` | Booking | ตัดสิน isMisrouted จากงานที่ได้รับการยอมรับ + เวอร์ชันเส้นทางปัจจุบัน | ชุดกฎการคำนวณที่ไม่เกี่ยวกับ Aggregate เดียว แต่ผลลัพธ์เขียนลงใน Shipment |
| `ETACalculator` | Booking | คำนวณ ETA จากงานที่ได้รับการยอมรับ + เวอร์ชันเส้นทางปัจจุบัน | เช่นเดียวกัน อัลกอริทึมพัฒนาได้ง่าย |
| `HandlingValidator` | Handling | ตรวจสอบฟิลด์และกฎ (type, voyageLegRef) | ชุดกฎพัฒนาอิสระ |
| `DeduplicationService` | Handling | การเขียน idempotent ด้วย DeduplicationKey | บทบาทการจัดระเบียบร่วมกับ Repository |

## อินเทอร์เฟซ Repository (ต่อยอดจาก 06)

```text
interface ShipmentRepository {
    find(id): Shipment
    save(shipment)
    findByStatus(predicate): Shipment[]
}

interface HandlingFactRepository {
    appendIfAbsent(fact): HandlingFactId
    findById(id): HandlingFact
    findByShipment(id, orderBy=occurredAt): HandlingFact[]
}

interface TrackingViewRepository {
    upsertProjection(view)
    findByShipment(id)
}
```

## โรงงาน (Factory)

| โรงงาน | ผลลัพธ์ | กฎสำคัญ |
| :--- | :--- | :--- |
| `ShipmentFactory.fromRequestAndOption(request, selectedCandidate)` | Shipment ใหม่, route v1 | ตรวจสอบเข้มงวด: origin/destination/latestArrival เข้ากันได้กับ route (I-3) |
| `RouteFactory.fromCandidate(candidate)` | Route v1 | ผลลัพธ์แปลง ACL → legs ภายใน |
| `RouteFactory.reroute(currentShipment, newCandidate)` | Route v(n+1) | ตรวจสอบว่าจุดเริ่มต้นช่วงแรกของเส้นทางใหม่ == ตำแหน่งปัจจุบัน จุดหมายช่วงสุดท้าย == destination |
| `HandlingFactFactory.fromRegistration(payload)` | HandlingFact | ผ่าน HandlingValidator; เติม DeduplicationKey |

## ความสัมพันธ์การสมัครรับ

| ฝั่งเผยแพร่ | Event | ฝั่งสมัครรับ | การจัดการ |
| :--- | :--- | :--- | :--- |
| Handling | AcceptedHandlingEvent | Booking | Shipment.apply(handling) → คำนวณ deliveryProgress ใหม่ → เผยแพร่ HandlingApplied + อาจมี ETARecalculated / CargoMisroutedDetected / CargoDelivered |
| Handling | LateHandlingIngested | Booking | กระตุ้นให้ Shipment เล่นซ้ำตามลำดับ occurredAt เผยแพร่กลุ่ม Event ที่เกี่ยวกับ StateRecomputed |
| Booking | กลุ่ม Event ที่คำนวณได้ | Tracking | upsertProjection(TrackingView) |
| Booking | CargoMisroutedDetected | ช่องทางการแจ้งเตือน | ส่งการแจ้งเตือนถึงลูกค้าและฝ่ายปฏิบัติการ |
| Booking | CargoDelivered | ช่องทางการแจ้งเตือน | การแจ้งเตือนยืนยันการจัดส่ง |

## กระแสข้อมูล (สถานการณ์สำคัญ)

### Happy Path

1. ลูกค้า `SubmitShippingRequest` → Booking เรียก `RoutingService` → `OptionsPresented`
2. ลูกค้า `SelectOption` + `ConfirmBooking` → Booking `ShipmentFactory.fromRequestAndOption` → บันทึกถาวร + เผยแพร่ `ShipmentBooked` + `RouteAssigned(v1)`
3. ท่าเรือต่างๆ `RegisterHandling` (ฝั่ง Handling) → ทุกครั้งเผยแพร่ `AcceptedHandlingEvent`
4. Booking บริโภค → ใช้กับ Shipment → คำนวณความคืบหน้า → เผยแพร่ `HandlingApplied` + `ETARecalculated`
5. ถึงขั้นรับมอบ → `CargoDelivered`

### การขนถ่ายผิดและการวางแผนใหม่

1. การขนถ่ายหนึ่งครั้ง portCode ≠ ท่าเรือที่วางแผนไว้ → Booking คำนวณ `CargoMisroutedDetected`
2. เจ้าหน้าที่บริการลูกค้า/ระบบ `RequestReroute` → `RoutingService` ค้นหาจากตำแหน่งปัจจุบัน → `RouteFactory.reroute` → เผยแพร่ `RouteReassigned(v(n+1))` + `ETARecalculated`

### ความล่าช้าในการมาถึง

1. Handling รับข้อเท็จจริงที่ occurredAt เร็วกว่าปัจจุบันมาก → เขียน idempotent + เผยแพร่ `LateHandlingIngested`
2. Booking สมัครรับ → เล่นซ้ำจากจุดยึดในอดีตตาม occurredAt → แก้ไขความคืบหน้าที่คำนวณได้ → เผยแพร่ Event ที่คำนวณได้ที่เกี่ยวข้อง (คีย์ idempotent ทำให้ปลายน้ำรับรู้เฉพาะค่าล่าสุด)

## การตรวจสอบตนเอง

- [x] Event ทั้งหมดตั้งชื่อด้วยกาลในอดีต
- [x] ทุก Event ข้าม Context มีการกำหนดคีย์ idempotent
- [x] Domain Service กับหน้าที่ของ Aggregate ไม่ทับซ้อนกัน และไม่ได้แบกรับ Invariant ที่ควรอยู่ใน Aggregate
- [x] อินเทอร์เฟซ Repository มีระดับเท่ากับ Aggregate Root
- [x] โรงงานรับผิดชอบการตรวจสอบ Invariant I-3 / I-8 / I-9 ที่ทางเข้า
- [x] สถานการณ์ข้อผิดพลาดทั้งหมด (ซ้ำซ้อน ผิดกฎหมาย ล่าช้า ขนถ่ายผิด ลดระดับ) มีความสัมพันธ์การสมัครรับที่ชัดเจน
