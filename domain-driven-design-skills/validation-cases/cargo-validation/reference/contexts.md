# Ground Truth — อ้างอิง Bounded Context

> แหล่งที่มา: [validation-cases/cargo-shipping](../../cargo-shipping/) (ตัวอย่าง DDD อย่างเป็นทางการของ Eric Evans + Citerus) ใช้สำหรับขั้นตอนการให้คะแนนเทียบ 1:1 กับผลลัพธ์ของ Skill **ห้ามเปิดเผยให้ Skill ระหว่าง blind run**

## แหล่งอ้างอิงหลักฐาน

- `src/site/apt/architecture.apt` (layered architecture และ Domain layer responsibilities)
- `src/site/apt/characterization.apt` (ยืนยัน Aggregate Root 4 ตัว)
- `src/site/apt/patterns-reference.apt` (mapping จาก pattern ไปยัง code path)
- `src/main/java/se/citerus/dddsample/interfaces/{booking,handling,tracking}/` (UI/API entry point 3 จุด)
- `src/main/java/com/pathfinder/` (external routing service, package อิสระ)

## สารบัญ Context (ที่คาดไว้)

> ตัวอย่าง Cargo อย่างเป็นทางการใส่ Aggregate ทั้งหมดใน package เดียว `se.citerus.dddsample` แต่ interface layer แยกทางกายภาพตาม 3 use case คือ **booking / handling / tracking**; นอกจากนี้ `com.pathfinder` เป็น external context อิสระ O&B 2014 ชี้ชัดว่า "ตัวอย่างอย่างเป็นทางการมีเพียง 1 BC ซึ่งเป็นข้อจำกัด ในทางปฏิบัติควรแยกอย่างน้อย 3~4 BC" ดังนั้นในการให้คะแนน "แยก 3 + 1 ภายนอก" เป็น baseline ของคะแนนเต็ม "单一 BC" ถือว่าไม่ผ่านเกณฑ์

| ชื่อ Context            | หน้าที่                                             | ศัพท์หลัก                                                                     | Event หลัก                                                           | Data Ownership                       | ทีมรับผิดชอบ (ที่คาดไว้)   |
| :---------------------- | :------------------------------------------------- | :---------------------------------------------------------------------------- | :------------------------------------------------------------------ | :----------------------------------- | :------------------- |
| **Booking**             | สั่งซื้อสินค้า, เปลี่ยนปลายทาง, ขอและมอบหมายเส้นทาง | Cargo, TrackingId, RouteSpecification, Itinerary, Leg, UnLocode              | CargoBooked (implicit), RouteAssigned (implicit), DestinationChanged | Aggregate Cargo, Value Object Itinerary/RouteSpec | ทีมจองห้อง/ลูกค้าสัมพันธ์ |
| **Handling**            | ลงทะเบียนเหตุการณ์งานท่าเรือ (RECEIVE/LOAD/UNLOAD/CLAIM/CUSTOMS) | HandlingEvent, HandlingEventType, HandlingHistory, HandlingEventRegistrationAttempt | HandlingEventRegistered, CargoWasHandled                             | Aggregate HandlingEvent              | ทีมงานท่าเรือ/คลังสินค้า |
| **Tracking**            | แสดงสถานะสินค้าปัจจุบันและขั้นตอนถัดไปให้ลูกค้า    | Delivery, TransportStatus, RoutingStatus, NextExpectedActivity               | CargoWasMisdirected, CargoHasArrived (subscriber side)              | Read-only: subscribe Handling event แล้ว project เป็น Cargo | ทีมฝั่งลูกค้า/frontend |
| **Routing (Pathfinder)** | ค้นหาเส้นทางที่เป็นไปได้ตาม RouteSpecification      | TransitPath, TransitEdge, GraphTraversalService                               | — (request/response, ไม่มี event)                                   | External routing graph data          | ทีมภายนอก (ไม่ได้อยู่ภายใต้การควบคุม) |

## สารบัญ Universal Language (ตัวอย่าง, ที่คาดไว้)

| ศัพท์                 | นิยาม                                                                      | ตัวอย่าง                                                    | Context ที่อยู่       | คำพ้องความหมาย (ที่ใช้ในธุรกิจ) | Anti-term / การจัดการความขัดแย้ง                              |
| :------------------- | :------------------------------------------------------------------------ | :------------------------------------------------------- | :----------------- | :----------------- | :--------------------------------------------------------- |
| Cargo                | สินค้าที่ลูกค้าส่งครั้งเดียว ระบุด้วย TrackingId                         | สินค้าหนึ่ง shipment จาก HONGKONG→STOCKHOLM              | Booking            | คำสั่งซื้อ, ใบนำส่ง  | ห้ามใช้ "Order" (ไม่เทียบเท่าทางธุรกิจ)                    |
| RouteSpecification   | ข้อกำหนดของลูกค้า: จุดเริ่มต้น, จุดปลายทาง, เวลาถึงกำหนด               | HONGKONG→STOCKHOLM, กำหนดถึง 2009-03-18                   | Booking            | ข้อเรียกร้องการสั่งซื้อ | ห้ามใช้ "Request" (ไม่มีความหมายทางธุรกิจ)                |
| Itinerary            | เส้นทางที่วางแผน ประกอบด้วย Leg หลายตัว; **Value Object**, แทนทั้งชุดไม่ได้แก้ไข | [HK→NYC via v100, NYC→CHI via v200, CHI→STO via v200]    | Booking            | แผนเส้นทาง         | แยกจาก Route: Route หมายถึงผลลัพธ์ของ graph algorithm, Itinerary เป็น commitment ทางธุรกิจ |
| HandlingEvent        | ข้อเท็จจริงของงานที่เกิดขึ้นจริงที่ท่าเรือ (LOAD/UNLOAD/RECEIVE/CLAIM/CUSTOMS) | "2009-03-03 โหลดขึ้น v100 ที่ HK"                        | Handling           | บันทึกงาน          | ห้ามใช้ "Operation" (กว้างเกินไป); แยกจาก HandlingActivity |
| HandlingActivity     | ขั้นตอนถัดไปที่ Cargo คาดหวัง (Value Object)                             | (UNLOAD, NEWYORK, v100)                                  | Tracking           | ขั้นตอนถัดไป       | **มี semantic overlap ที่รู้จัก**: HandlingEvent / HandlingActivity / TransportStatus มีความซ้ำซ้อน เป็น health item ของโมเดล |
| Delivery             | สถานะการส่งมอบ snapshot, **derive** จาก RouteSpec+Itinerary+HandlingHistory | มี transportStatus, lastKnownLocation, isMisdirected     | Tracking           | สถานะ               | **Invariant**: ห้าม set โดยตรงตลอดเวลา                      |
| Voyage               | การเดินทางครั้งหนึ่ง (vessel + schedule) ระบุด้วย VoyageNumber          | v100: HK→NYC→...                                         | Booking            | เที่ยวบิน           | แยกจาก Vessel: Voyage คือ "การเดินทางหนึ่งครั้ง" ไม่ใช่ตัวเรือเอง |
| Misdirected          | สถานะที่งานจริงเบี่ยงเบนจาก Itinerary                                   | ควร unload ที่ NYC แต่ unload ที่ TOKYO จริง             | Tracking           | ไปผิดทาง, ขนส่งผิด | —                                                          |

## Anti-term (ที่คาดไว้)

| คำห้ามใช้  | เหตุผลที่ห้าม                                     | คำแนะนำทดแทน                           |
| :------- | :--------------------------------------------- | :--------------------------------- |
| Manager  | คำเทคนิคปนเปื้อน ไม่มีความหมายทางธุรกิจ           | BookingService / (Domain Service)   |
| Handler  | คำเทคนิคปนเปื้อน                                  | — (ใช้คำกริยาทางธุรกิจแทน)            |
| Order    | ไม่เทียบเท่าทางธุรกิจ (logistics ไม่ใช่ e-commerce) | Cargo                              |
| Status   | กว้างเกินไป                                       | TransportStatus/RoutingStatus ฯลฯ จำเพาะเจาะจง |

## ADR สำคัญ (ที่คาดไว้)

- **ADR-1**: HandlingEvent แยกเป็น Aggregate อิสระ ไม่ฝังใน Cargo เหตุผล: event มาจากระบบภายนอก, throughput สูง, ต้อง async; การใส่ HandlingEvent ใน Aggregate Cargo จะเกิด synchronous loading overhead และ deadlock risk การแลกเปลี่ยน: สถานะ Cargo ต้องคำนวณใหม่ผ่าน `deriveDeliveryProgress(HandlingHistory)` ซึ่งเป็น eventual consistency
- **ADR-2**: Delivery ออกแบบเป็น **derived Value Object** ไม่ใช่ mutable entity เหตุผล: รักษา invariant "สถานะมาจากข้อเท็จจริง (RouteSpec+Itinerary+HandlingHistory)" ป้องกัน anti-pattern ของการใช้ setter
- **ADR-3**: Routing capability (Pathfinder) เป็น external context อิสระเชื่อมต่อผ่าน Domain interface `RoutingService` + Infrastructure layer ACL (`ExternalRoutingService`)