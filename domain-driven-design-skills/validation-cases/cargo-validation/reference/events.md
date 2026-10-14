# Ground Truth — อ้างอิง Event Flow และ Domain Interaction

> แหล่งที่มา: `src/test/java/se/citerus/dddsample/scenario/CargoLifecycleScenarioTest.java` (lifecycle แบบ end-to-end), `src/main/java/se/citerus/dddsample/application/ApplicationEvents.java` (application event), `src/main/java/se/citerus/dddsample/domain/service/RoutingService.java` (domain service)

## ตาราง Event Flow (ที่คาดไว้, อิงจากเส้นทางหลัก + เส้นทางผิดปกติของ CargoLifecycleScenarioTest)

> หมายเหตุ **M** = เส้นทางหลัก (HK→NYC→CHI→STO), **R** = เส้นทาง replanning (HK→TOKYO unload ผิด → TOKYO→HAMBURG→STO)

| ลำดับ | ชื่อ Event (past tense)         | Command ที่ trigger                       | ผู้เข้าร่วม            | ข้อมูลเข้า/ออกหลัก                              | สาขา     |
| :---- | :----------------------------- | :---------------------------------------- | :------------------- | :---------------------------------------------- | :------- |
| 1     | CargoBooked                    | bookNewCargo                              | พนักงานจองห้อง        | (origin, destination, arrivalDeadline) → TrackingId | M        |
| 2     | RouteCandidatesRequested       | requestPossibleRoutesForCargo             | พนักงานจองห้อง        | TrackingId → List<Itinerary>                    | M        |
| 3     | RouteAssigned                  | assignCargoToRoute                        | พนักงานจองห้อง        | (TrackingId, Itinerary)                         | M        |
| 4     | CargoReceived                  | registerHandlingEvent (type=RECEIVE)      | พนักงานท่าเรือ         | (trackingId, HONGKONG, 2009-03-01)              | M        |
| 5     | CargoLoaded                    | registerHandlingEvent (type=LOAD)         | พนักงานท่าเรือ         | (trackingId, HONGKONG, voyage=v100)             | M        |
| 6     | InvalidHandlingEventRejected   | registerHandlingEvent (voyage+UnLocode ผิด) | ระบบภายนอก           | → CannotCreateHandlingEventException            | ผิดปกติ  |
| 7     | CargoUnloaded                  | registerHandlingEvent (type=UNLOAD)       | พนักงานท่าเรือ         | (trackingId, TOKYO, v100) — **unload ผิด**      | R        |
| 8     | CargoWasMisdirected            | CargoInspectionService.inspectCargo       | ระบบ (application event) | Cargo.isMisdirected() == true                   | R        |
| 9     | DestinationChanged / RouteRespecified | specifyNewRoute                  | พนักงานจัดส่ง/ลูกค้าสัมพันธ์ | (trackingId, RouteSpecification ใหม่ TOKYO→STOCKHOLM) | R |
| 10    | RouteReAssigned                | assignCargoToRoute                        | พนักงานจัดส่ง           | (trackingId, Itinerary ใหม่)                    | R        |
| 11    | CargoLoaded (2)                | registerHandlingEvent(LOAD)               | พนักงานท่าเรือ         | (TOKYO, v300)                                   | R        |
| 12    | CargoUnloaded (2)              | registerHandlingEvent(UNLOAD)             | พนักงานท่าเรือ         | (HAMBURG, v300)                                 | R        |
| 13    | CargoLoaded (3)                | registerHandlingEvent(LOAD)               | พนักงานท่าเรือ         | (HAMBURG, v400)                                 | R        |
| 14    | CargoUnloaded (3)              | registerHandlingEvent(UNLOAD)             | พนักงานท่าเรือ         | (STOCKHOLM, v400)                               | R        |
| 15    | CargoHasArrived                | CargoInspectionService.inspectCargo       | ระบบ (application event) | trigger การแจ้งเตือนการถึง                      | R        |
| 16    | CargoClaimed                   | registerHandlingEvent(CLAIM)              | ลูกค้า                  | (STOCKHOLM) — lifecycle สิ้นสุด                  | R        |

## รายการ Command Candidate

| Command                       | ผู้ริเริ่ม               | ผลลัพธ์ที่คาด                                          | Idempotency requirement                                                               |
| :---------------------------- | :--------------------- | :------------------------------------------------------- | :----------------------------------------------------------------------------------- |
| bookNewCargo                  | พนักงานจองห้อง         | คืน TrackingId; Aggregate Cargo เก็บลง database            | **ไม่ idempotent** (ทุกครั้งสร้าง Cargo ใหม่); แต่ client สามารถใช้ idempotency key จากภายนอก |
| specifyNewRoute               | พนักงานจัดส่ง           | routeSpecification ของ Cargo ถูกแทนที่; Delivery คำนวณใหม่ synchronous | **Idempotent**: RouteSpecification เดิมเรียกซ้ำไม่มี side effect (VO equality)     |
| assignCargoToRoute            | พนักงานจองห้อง/จัดส่ง  | itinerary ของ Cargo ถูกแทนที่; Delivery คำนวณใหม่ synchronous | **Idempotent** (เหมือนข้างต้น)                                                     |
| changeDestination             | ลูกค้าสัมพันธ์           | destination ของ RouteSpecification ถูกแทนที่               | Idempotent                                                                          |
| registerHandlingEvent         | พนักงานท่าเรือ/ระบบภายนอก | HandlingEvent เก็บลง database; trigger asynchronous ให้ Cargo คำนวณ Delivery ใหม่ | **Idempotency key**: identity ของ HandlingEvent = composite (cargo, voyage, completionTime, location, type), การลงทะเบียนซ้ำควร deduplicate |
| inspectCargo                  | ระบบ (subscribe CargoWasHandled) | ตัดสินใจ misdirected/arrived แล้ว emit application event | Idempotent: การตัดสินใจอิงจาก snapshot ปัจจุบัน                                      |

## รายการ Event Candidate

| Event                       | ฟิลด์สำคัญ                                                             | ขอบเขต           | ข้าม context หรือไม่ | เผยแพร่สู่ภายนอกหรือไม่ |
| :-------------------------- | :-------------------------------------------------------------------- | :--------------- | :-------------------- | :--------------------- |
| CargoWasHandled             | HandlingEvent (มี cargo, voyage, location, type, completionTime)       | Domain Event     | ใช่ (Handling→Cargo→Tracking) | ใช่ (Published Language) |
| CargoWasMisdirected         | Cargo (read-only projection)                                          | Application      | ไม่ (การแจ้งเตือนภายใน)     | แจ้งเตือนลูกค้า: ใช่    |
| CargoHasArrived             | Cargo                                                                  | Application      | ไม่                   | แจ้งเตือนลูกค้า: ใช่    |
| HandlingEventRegistrationAttempt | raw request fields                                                | Interfaces       | ไม่                   | ไม่ (ข้อมูล inbound)    |

## Domain Service (ที่คาดไว้)

| ชื่อ Service                 | หน้าที่                                                                | ข้อมูลเข้า                | ข้อมูลออก               | Aggregate/Event ที่ depend | สิ่งที่ไม่ควรมี                               |
| :--------------------------- | :-------------------------------------------------------------------- | :---------------------- | :--------------------- | :----------------------- | :------------------------------------------- |
| **RoutingService** (Domain interface) | ค้นหา Itinerary ที่เป็นไปได้ตาม RouteSpecification               | RouteSpecification      | List<Itinerary>        | — (External context Pathfinder) | ไม่รับผิดชอบการมอบหมายเส้นทาง, ไม่แตะสถานะ Cargo |
| **CargoInspectionService** (Application service แต่ carrying domain logic) | คำนวณ Delivery ใหม่จาก HandlingHistory ล่าสุด แล้ว emit notification misdirected/arrived | TrackingId | side effect: อัปเดต Cargo + emit event | Aggregate Cargo, Repository HandlingEvent | ไม่เขียน HandlingEvent ใหม่                     |

> **จุดสำคัญสำหรับการให้คะแนน**: RoutingService เป็น Domain Service interface (Domain layer), **implementation** `ExternalRoutingService` อยู่ใน Infrastructure layer ทำหน้าที่เป็น ACL ถ้า skill ใส่ implementation ของ RoutingService ใน Domain layer ให้หักคะแนน

## Factory (ที่คาดไว้)

| ชื่อ Factory/Method                              | เป้าหมายที่สร้าง | เงื่อนไขที่สร้าง                                                                                      | กฎตรวจสอบ                                                                          | สถานะเริ่มต้น                        |
| :---------------------------------------------- | :--------------- | :----------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------- | :---------------------------------- |
| CargoFactory.newCargo                           | Cargo            | (origin UnLocode, destination UnLocode, arrivalDeadline)                                              | จุดเริ่มต้น/จุดปลายทางต้องมีอยู่; จุดเริ่มต้น ≠ จุดปลายทาง; TrackingId ไม่ซ้ำกัน      | Delivery=NOT_RECEIVED, NOT_ROUTED   |
| HandlingEventFactory.createHandlingEvent         | HandlingEvent    | (completionTime, trackingId, voyageNumber?, unLocode, type)                                          | Cargo/Location/Voyage (ถ้าจำเป็น) ต้องมีอยู่; Type และ Voyage คู่กันได้ถูกกฎหมาย    | เก็บลง database ได้ทันที              |

## Subscriber และ Side Effect

| Event               | Subscriber                     | การกระทำที่ trigger                                   | กลยุทธ์ชดเชย                              | Monitoring metric                         |
| :------------------ | :----------------------------- | :----------------------------------------------------- | :---------------------------------------- | :---------------------------------------- |
| CargoWasHandled     | CargoInspectionService         | คำนวณ Delivery ใหม่; ถ้า misdirected แจ้งเตือน; ถ้า arrived แจ้งเตือน | retry (idempotent); dead letter → manual intervention | handled_event_lag, inspect_failure_rate |
| CargoWasMisdirected | (ภายนอก) ช่องทางแจ้งเตือนลูกค้า | push ให้ลูกค้า                                           | retry; degradation เป็น email              | misdirected_count                        |
| CargoHasArrived     | (ภายนอก) ช่องทางแจ้งเตือนลูกค้า | push ให้ลูกค้า                                           | เหมือนข้างต้น                               | arrived_count                            |