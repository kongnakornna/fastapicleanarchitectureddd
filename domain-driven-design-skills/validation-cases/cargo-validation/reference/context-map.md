# Ground Truth — อ้างอิง Context Relationship และ Integration Pattern

> แหล่งที่มา: `src/main/java/com/pathfinder/` (external routing service), `src/main/java/se/citerus/dddsample/infrastructure/routing/ExternalRoutingService.java` (ACL implementation), `src/main/java/se/citerus/dddsample/interfaces/handling/` (inbound HandlingReport API), `src/site/apt/patterns-reference.apt`

## ตาราง Context Relationship (ที่คาดไว้)

| Upstream             | Downstream           | Pattern                      | ข้อมูล / Event                                     | ความเสี่ยง / Failure Mode                                    |
| :------------------- | :------------------- | :--------------------------- | :------------------------------------------------- | :----------------------------------------------------------- |
| Booking              | Routing (Pathfinder) | **ACL + Customer-Supplier**  | คำขอ: RouteSpecification; คำตอบ: List<TransitPath> → แปลเป็น List<Itinerary> | ระบบภายนอกไม่พร้อมใช้งาน → degradation: ไม่สามารถ route ได้แต่สั่งซื้อได้; timeout ต้อง circuit breaker |
| Handling             | Cargo (ผ่าน Aggregate ใน Booking BC) | **Published Language (HandlingEvent)** | Async event CargoWasHandled; Cargo อ้างอิงผ่าน TrackingId | Event หาย → สถานะ Delivery ล่าช้า; ส่งซ้ำต้อง idempotent    |
| Handling             | Tracking             | **Published Language**        | เหมือนข้างต้น CargoWasHandled + derived event CargoWasMisdirected / CargoHasArrived | ความต่างของ consistency window (reader เห็นสถานะเก่า)         |
| ระบบงานภายนอก (คลังสินค้า/ท่าเรือ) | Handling             | **Conformist + ACL at edge**  | HandlingReport (JSON/CSV) → HandlingEventRegistrationAttempt | ข้อมูลสกปรก, ส่งซ้ำ, clock skew                               |
| Tracking             | Booking              | **Conformist** (read-only Cargo projection) | อ่าน Aggregate Cargo                         | อ่าน eventual consistency snapshot                            |

> **จุดสำคัญสำหรับการให้คะแนน**:
> 1. Routing ต้องถูกระบุว่าเป็น **external context** และใช้ **ACL** ป้องกัน Booking; ถ้า skill ใส่ Routing ในBooking หรือไม่มี ACL ให้หักคะแนน
> 2. HandlingEvent ต้องถูกระบุว่าเป็น **cross-context Published Language**; ถ้า skill ถือว่าเป็น event ภายใน Booking ให้หักคะแนน
> 3. ไม่ควรมี circular dependency (Booking → Handling → Booking)

## ตาราง Contract Ownership (ที่คาดไว้)

| สัญญา (Contract)                                         | Owner              | ผู้ใช้งาน (Consumer)       | ขั้นตอนการเปลี่ยนแปลง                                              | กลยุทธ์เผยแพร่                              |
| :------------------------------------------------------- | :----------------- | :----------------------- | :------------------------------------------------------------------- | :----------------------------------------- |
| HandlingReport REST API (POST /dddsample/handlingReport) | ทีม Handling        | ระบบงานภายนอก             | backward compatible; เพิ่มฟิลด์ก่อน; breaking change ต้องแจ้ง deprecation | path version v1; ช่วง compatible 6 เดือน  |
| CargoWasHandled integration event schema                 | ทีม Handling        | Tracking, Cargo Inspection | backward compatible; เพิ่มฟิลด์ก่อน                                   | schema registry + contract tests           |
| RoutingService Domain interface                          | ทีม Booking         | Booking (ผู้เดียว)         | การเปลี่ยน interface ต้องเจรจากับทีม Pathfinder                      | ไม่มี version ภายนอก; internal evolution   |
| TransitPath/TransitEdge (Pathfinder external API)        | ทีมภายนอก Pathfinder | Booking (ผ่าน ACL)        | Booking ไม่สามารถ drive การเปลี่ยนแปลง; เป็น Pathfinder เป็นผู้เผยแพร่ | ภายนอกควบคุม; ACL ดูดซับความแตกต่าง        |

## การแปลและ ACL Decision (ที่คาดไว้)

| Object / Event                     | กฎการแปล                                                                                      | คำอธิบาย semantic difference                                                     | ตำแหน่ง Implementation                                                  |
| :--------------------------------- | :--------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------- | :----------------------------------------------------------------------- |
| TransitPath → Itinerary            | ทุก TransitEdge → Leg; extract voyage/location; กรองเส้นทางที่ไม่ผ่าน RouteSpec                 | Pathfinder ไม่รู้ว่ามี Cargo; รู้เพียง origin/destination/deadline             | `infrastructure/routing/ExternalRoutingService`                           |
| HandlingReport JSON → HandlingEventRegistrationAttempt | เปลี่ยนชื่อฟิลด์, normalize timezone, ตรวจสอบ UnLocode | ภายนอกอาจใช้ชื่อฟิลด์, timezone ต่างกัน; ต้อง parse อย่างยืดหยุ่น | `interfaces/handling/ws/HandlingReportServiceImpl` (ACL)                 |

## Failure Mode และการ缓解 (ที่คาดไว้)

| Failure Mode                       | ผลกระทบ                           | วิธีตรวจจับ                       | การ缓解                                                                | กลยุทธ์ชดเชย                                            |
| :--------------------------------- | :------------------------------- | :------------------------------- | :--------------------------------------------------------------------- | :----------------------------------------------------- |
| Pathfinder timeout                 | ลูกค้าไม่เห็นเส้นทางที่เลือกได้   | request timeout + metric routing_timeout | Circuit breaker; คืนค่าว่าง + user prompt "ลองใหม่ภายหลัง"                | ไม่มีการชดเชย; ลูกค้าลองใหม่ได้                        |
| Pathfinder คืนเส้นทางผิดปกติ       | ลูกค้าเลือก Itinerary ที่เป็นไปไม่ได้ | RouteSpecification.isSatisfiedBy | Booking ตรวจสอบซ้ำ; ไม่ผ่านให้ปฏิเสธ assignCargoToRoute                 | ปฏิเสธและขอให้เลือกใหม่                                |
| HandlingEvent หาย                   | สถานะ Delivery ล่าช้า              | เปรียบเทียบ event stream กับระบบภายนอก | Reconciliation task; replay window                                  | ดึงกลับจากระบบภายนอกและลงทะเบียนใหม่ (idempotency guarantee ไม่ซ้ำ) |
| HandlingEvent ซ้ำ                   | อาจ misjudge misdirected          | identity 5 ตัวมี idempotency ตามธรรมชาติ | Factory deduplicate                                                 | —                                                      |
| ระบบงานภายนอก clock skew           | completionTime ผิดพลาด             | ลงทะเบียนแล้ว print ค่าต่างของ registrationTime กับ completionTime | Alarm ผิดปกติ; ช่วง tolerance ±2 ชั่วโมง                            | แก้ไขด้วยตนเอง                                          |
| Cargo คำนวณใหม่ล้มเหลว (inspectCargo exception) | สถานะ Delivery ไม่สอดคล้องกัน   | monitor inspect_failure_rate    | Retry (idempotent); dead letter queue                                  | 介入ด้วยตนเอง                                            |

## กลยุทธ์ Version (ที่คาดไว้)

- **HandlingReport API**: path version v1; breaking change ต้องมีช่วง deprecation 6 เดือน; เพิ่มฟิลด์ต้อง backward compatible
- **CargoWasHandled event schema**: จดทะเบียนใน schema registry; ผู้ใช้งานให้ contract tests
- **RoutingService internal interface**: ไม่มี requirement ด้าน versioning, วิวัฒนาการตาม codebase

## Design Trade-off ที่รู้จัก (ใช้เป็น bonus ในการให้คะแนน)

- **HandlingEvent เป็น Aggregate อิสระ** (ไม่ใช่ sub-resource ของ Cargo): O(n) write แทน O(cargo_size × events) loading, ดู `characterization.apt` "The main reason for not making HandlingEvent part of the cargo aggregate is performance"
- **Delivery เป็น derived Value Object**: ป้องกัน inconsistent state โดยธรรมชาติ
- **RouteSpecification ในฐานะ Specification pattern**: `isSatisfiedBy(Itinerary)` ใช้ซ้ำได้สำหรับการค้นหาและการตรวจสอบ

## Bonus ในการให้คะแนน (ข้อจำกัดที่รู้จักของตัวอย่าง Cargo อย่างเป็นทางการ)

นี่คือข้อจำกัดของตัวอย่าง Cargo ที่ O&B และชุมชนยอมรับโดยทั่วไป ถ้า skill สามารถระบุและเสนอได้เอง ให้ bonus:

1. **Context Billing ขาด**: ตัวอย่างอย่างเป็นทางการไม่มี Billing; ถ้า skill เสนอ "เมื่อลูกค้า CLAIM สำเร็จ ควรมี billing trigger" ให้ bonus
2. **Context Customer ขาด**: ไม่มีการจัดการลูกค้าอิสระ; ถ้า skill เสนอ Customer เป็น Generic subdomain ให้ bonus
3. **ความสัมพันธ์ระหว่าง Carrier (carrier) กับ Voyage ไม่ได้ model**: Voyage มี VoyageNumber แต่บริษัท carrier ไม่อยู่ในโมเดล; ถ้า skill ระบุว่านี่คือ external modeling simplification ให้ bonus
4. **Semantic overlap ของ HandlingEvent / HandlingActivity / TransportStatus**: O&B ระบุชัดว่าควรรวมเป็น HandlingActivity; ถ้า skill ระบุความซ้ำซ้อนนี้ใน `ddd-model-review` **bonus สำคัญ**