# Ground Truth — อ้างอิง Aggregate, Entity, Value Object และ Invariant

> แหล่งที่มา: `src/main/java/se/citerus/dddsample/domain/model/{cargo,handling,location,voyage}/` และ `src/site/apt/characterization.apt`

## สารบัญ Aggregate (ที่คาดไว้ 4 Aggregate Root)

| ชื่อ Aggregate     | Aggregate Root  | Entity ที่มี       | Value Object ที่มี                                                                              | Invariant หลัก                                                                                                   | Command หลัก                                                                   |
| :---------------- | :------------- | :--------------- | :--------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------- |
| **Cargo**         | Cargo          | —                | TrackingId, RouteSpecification, Itinerary, Leg, Delivery, TransportStatus, RoutingStatus       | I1 จุดเริ่มต้นไม่เปลี่ยนตลอดเวลา; I2 Delivery คำนวณได้จาก RouteSpec+Itinerary+HandlingHistory เท่านั้น; I3 RouteSpec.origin ≠ destination | bookNewCargo, specifyNewRoute, assignToRoute, deriveDeliveryProgress           |
| **HandlingEvent** | HandlingEvent  | —                | HandlingEvent.Type (LOAD/UNLOAD/RECEIVE/CLAIM/CUSTOMS)                                        | I4 LOAD/UNLOAD ต้องเชื่อมกับ Voyage; I5 RECEIVE/CLAIM/CUSTOMS ห้ามเชื่อม Voyage                                | registerHandlingEvent (สร้างผ่าน HandlingEventFactory)                        |
| **Voyage**        | Voyage         | —                | VoyageNumber, Schedule, CarrierMovement                                                       | I6 CarrierMovement ของ Schedule เรียงตามเวลา; I7 VoyageNumber ไม่ซ้ำกัน                                          | — (ในตัวอย่างโหลดจาก master data; ในระบบจริงควรมี createVoyage)              |
| **Location**      | Location       | —                | UnLocode                                                                                       | I8 UnLocode ตรงตามรหัส UN/LOCODE 5 ตัวอักษร                                                                     | — (master data)                                                                |

> **ข้อสังเกตสำคัญ**: Itinerary, RouteSpecification, Delivery, HandlingActivity, Leg, TrackingId, UnLocode, VoyageNumber ทั้งหมดเป็น **Value Object ที่ไม่เปลี่ยนแปลง** ตัวอย่างให้ความสำคัญกับ VO > Entity > Event อย่างชัดเจน

## ตาราง Invariant (ครบถ้วน)

| หมายเลข | Invariant                                                                                     | Command ที่ trigger                   | ตำแหน่งตรวจสอบ                        | พฤติกรรมเมื่อละเมิด                                                |
| :------ | :-------------------------------------------------------------------------------------------- | :------------------------------------ | :-------------------------------------- | :------------------------------------------------------------ |
| I1      | จุดเริ่มต้นของ Cargo ไม่เปลี่ยนหลังสร้าง (แม้ RouteSpec จะเปลี่ยน)                            | bookNewCargo, specifyNewRoute         | Constructor ของ Cargo                   | ข้อจำกัดฝังอยู่ใน constructor ไม่สามารถละเมิดได้               |
| I2      | Delivery คำนวณจาก (RouteSpec, Itinerary, HandlingHistory) เท่านั้น ห้าม assign จากภายนอกโดยตรง | specifyNewRoute, assignToRoute, deriveDeliveryProgress | Aggregate Root ของ Cargo | ห้ามเปิดเผย setter ในโมเดล; ในระบบจริงการละเมิด = สถานะถูก forge ได้ |
| I3      | RouteSpecification.origin ≠ destination                                                       | new RouteSpecification                | Constructor ของ RouteSpecification      | โยน IllegalArgumentException                                    |
| I4      | HandlingEvent.Type ∈ {LOAD, UNLOAD} ⇒ voyage ต้องไม่เป็น null                                 | HandlingEventFactory.createHandlingEvent | Constructor ของ HandlingEvent (double construction) | โยน IllegalArgumentException                                    |
| I5      | HandlingEvent.Type ∈ {RECEIVE, CLAIM, CUSTOMS} ⇒ voyage ต้องเป็น null                          | เหมือนข้างต้น                           | เหมือนข้างต้น                             | โยน IllegalArgumentException                                    |
| I6      | RouteSpecification.isSatisfiedBy(Itinerary): จุดเริ่มต้นเหมือนกัน, จุดปลายเหมือนกัน, deadline หลังวันถึงอย่างเข้มงวด | assignToRoute                         | RouteSpecification                      | คืน false → RoutingStatus=MISROUTED                              |
| I7      | VoyageNumber / TrackingId / UnLocode ไม่ซ้ำกันในระบบ                                          | การสร้างแต่ละ Aggregate               | Constructor ของ VO แต่ละตัว + Repository | ละเมิดไม่ซ้ำกัน → Repository ปฏิเสธ                              |
| I8      | Aggregate Cargo และ Aggregate HandlingEvent cross-aggregate reference ต้องผ่าน ID (TrackingId) เท่านั้น ห้ามถือ object reference ของกันและกัน | การ cross-aggregate interaction ใดๆ | Model convention + Repository interface | ละเมิด → deadlock/performance degradation (อธิบายไว้ใน ADR-1) |

## รายการ Entity และ Value Object

| ชื่อ                | ประเภท    | Aggregate ที่อยู่  | Identity Strategy / Equality                                                          |
| :------------------ | :------- | :--------------- | :----------------------------------------------------------------------------------- |
| Cargo               | Entity   | Cargo            | Identity = trackingId; sameIdentityAs                                                |
| HandlingEvent       | DomainEvent (identity + ไม่เปลี่ยนแปลง) | HandlingEvent | Identity = (cargo, voyage, completionTime, location, type) composite; sameEventAs |
| Voyage              | Entity   | Voyage           | Identity = VoyageNumber                                                              |
| Location            | Entity   | Location         | Identity = UnLocode                                                                  |
| TrackingId          | VO       | Cargo            | เทียบตาม value                                                                       |
| RouteSpecification  | VO       | Cargo            | เทียบตาม triple (origin, destination, arrivalDeadline)                               |
| Itinerary           | VO       | Cargo            | เทียบตาม legs list                                                                   |
| Leg                 | VO       | Cargo            | เทียบตาม (voyage, loadLoc, unloadLoc, loadTime, unloadTime)                          |
| Delivery            | VO       | Cargo            | แทนทั้งชุดไม่ได้แก้ไข                                                                |
| TransportStatus     | VO(enum) | Cargo            | NOT_RECEIVED / IN_PORT / ONBOARD_CARRIER / CLAIMED / UNKNOWN                         |
| RoutingStatus       | VO(enum) | Cargo            | NOT_ROUTED / ROUTED / MISROUTED                                                      |
| HandlingActivity    | VO       | Cargo            | Triple (Type, Location, Voyage?)                                                     |
| HandlingEvent.Type  | VO(enum) | HandlingEvent    | LOAD / UNLOAD / RECEIVE / CLAIM / CUSTOMS                                            |
| VoyageNumber        | VO       | Voyage           | เทียบตาม string                                                                      |
| Schedule            | VO       | Voyage           | เทียบตาม CarrierMovement list                                                        |
| CarrierMovement     | VO       | Voyage           | เทียบตาม (from, to, depart, arrive)                                                  |
| UnLocode            | VO       | Location         | เทียบตามรหัส 5 ตัวอักษร                                                              |

## คำอธิบาย Transaction Boundary

- **กฎเริ่มต้น**: transaction หนึ่งตัวแก้ไข Aggregate หนึ่งตัวเท่านั้น
- **การอัปเดตแบบ synchronous ของ Cargo** (assignToRoute/specifyNewRoute) และ **การอัปเดตแบบ asynchronous** (deriveDeliveryProgress จาก HandlingHistory) อยู่ร่วมกัน: 前者ทำภายใน transaction ของ Cargo, 后者ถูก trigger โดย application layer event (`cargoWasHandled`) หลัง HandlingEvent ลงทะเบียนสำเร็จ cross-aggregate eventual consistency
- การควบคุม concurrency: ตัวอย่างใช้ Hibernate + optimistic locking (implicit, ไม่ได้ระบุใน code อย่างชัดเจน)

## กลยุทธ์ Cross-Aggregate Consistency

| สถานการณ์                                   | Event ที่ trigger                   | การชดเชย / retry                                           | Idempotency guarantee                                                |
| :------------------------------------------- | :--------------------------------- | :---------------------------------------------------------- | :------------------------------------------------------------------- |
| HandlingEvent ลงทะเบียน → Cargo คำนวณ Delivery ใหม่ | CargoWasHandled                     | Application layer event mechanism (ตัวอย่างใช้ JMS; ทดสอบใช้ SynchronousStub) | HandlingEvent identity 5 ตัวมี idempotency ตามธรรมชาติ; เมื่อ replay Delivery คำนวณผลเหมือนเดิม |
| Cargo เบี่ยงเบนจาก Itinerary                 | CargoWasMisdirected                 | แจ้งบุคลากรที่เกี่ยวข้อง → trigger replanning              | CargoInspectionService ตัดสินใจครั้งเดียวใน inspectCargo               |
| Cargo ถึงจุดหมายปลายทาง                     | CargoHasArrived                     | แจ้งลูกค้า → รอ CLAIM event                                 | เหมือนข้างต้น                                                          |

## ร่าง Repository Interface (ที่คาดไว้)

| Aggregate     | วิธีใช้งาน                                                                               | ความหมาย                              | ขอบเขต query            |
| :------------ | :--------------------------------------------------------------------------------------- | :------------------------------------ | :----------------------- |
| Cargo         | `find(TrackingId): Cargo`, `store(Cargo)`, `findAll(): List<Cargo>`, `nextTrackingId()` | ค้นหา/จัดเก็บตาม identity              | คืนเฉพาะ Aggregate Root |
| HandlingEvent | `store(HandlingEvent)`, `lookupHandlingHistoryOfCargo(TrackingId): HandlingHistory`     | มีเฉพาะ store และค้นหาประวัติตาม TrackingId | **ไม่มี generic CRUD interface** |
| Voyage        | `find(VoyageNumber): Voyage`                                                             | ค้นหาตาม identity                     | —                        |
| Location      | `find(UnLocode): Location`, `findAll(): List<Location>`                                  | ค้นหาตาม identity; master data        | —                        |

> **จุดสำคัญสำหรับการให้คะแนน**: HandlingEventRepository **ไม่ควรมี** generic CRUD; ถ้า skill output มี method `delete`/`update` ให้หักคะแนน