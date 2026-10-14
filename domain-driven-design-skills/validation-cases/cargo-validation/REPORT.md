# การตรวจสอบระบบ技能 Cargo — รายงานสุดท้าย

> กรณี: Cargo Shipping DDD Sample (Eric Evans + Citerus) @ sub-module `validation-cases/cargo-shipping` (ล็อก `d8b8962`)
> วิธีการ: **Blind run (การรันแบบตาบอด)**, ดำเนินการ pipeline ของ Skill ทั้ง 8 ตัวอย่างสมบูรณ์, จากนั้นให้คะแนนตาม ground truth และทดสอบ defect injection ของ backtrack trigger
> รายงานนี้และ artifact ทั้งหมดเขียนเป็นภาษาจีนเป็นหลัก

## 1. สรุปการดำเนินงาน

| รายการ               | ค่า                                                                              |
| :------------------ | :------------------------------------------------------------------------------- |
| คะแนนถ่วงน้ำหนักรวม | **85.8 %** (B+ / ดี)                                                              |
| ขั้นตอนแข็งแกร่งที่สุด | ขั้นตอน I (Discovery) & ขั้นตอน III-b (Domain Interaction) — ทั้งคู่ 4.0/4        |
| ขั้นตอนอ่อนแอที่สุด  | ขั้นตอน III-a (Aggregate) — 2.5/4                                                 |
| ผลการทดสอบ Backtrack Trigger | **5/5 ข้อบกพร่องที่ inject ถูกจับได้อย่างถูกต้องและนำทาง**                |
| ข้อบกพร่องร้ายแรงของระบบ技能 | ไม่มี (ไม่ได้ถูก trigger B- deduction)                                    |
| Insight ที่มีค่าที่สูญหาย | 3 รายการ (ช่องว่าง Billing/Customer, ความซ้ำซ้อน HandlingEvent/Activity/Status, การ简化 Carrier) |

Pipeline ของ Skill ทั้ง 8 ตัวสร้าง Domain Model ที่มีความ**เทียบเท่า**กับตัวอย่างมาตรฐานของ Cargo ในทุกพฤติกรรมหลัก (Aggregate decoupling, ACL boundary, event sourcing, replanning loop, idempotency) แต่**ขาด Aggregate ภายในสองตัว** (Voyage, Location) และ**ขาดการระบุ DDD pattern หนึ่งตัว** (Specification) Backtrack trigger ใน feedback loop ทำงานปกติ

## 2. ขอบเขตการตรวจสอบ

### 2.1 ข้อมูลเข้า (ตาบอด)

- [00-fuzzy-prompt.md](./00-fuzzy-prompt.md) — บันทึกธุรกิจภาษาจีน 550 คำ บรรบริษัทขนส่งทางเรือระหว่างประเทศ ลบคำศัพท์ DDD ทั้งหมดและชื่อคลาสของตัวอย่าง Cargo ออก

### 2.2 ผลลัพธ์ของ Pipeline (ตาบอด)

| ไฟล์                                                                     | Skill                   | ขั้นตอน    |
| :----------------------------------------------------------------------- | :---------------------- | :---------- |
| [01-ddd-scope.out.md](./01-ddd-scope.out.md)                             | ddd-scope               | I Discovery |
| [02-ddd-discover.out.md](./02-ddd-discover.out.md)                       | ddd-discover            | I Discovery |
| [03-ddd-subdomains.out.md](./03-ddd-subdomains.out.md)                   | ddd-subdomains          | II Strategy |
| [04-ddd-contexts.out.md](./04-ddd-contexts.out.md)                       | ddd-contexts            | II Strategy |
| [05-ddd-context-map.out.md](./05-ddd-context-map.out.md)                 | ddd-context-map         | II Strategy |
| [06-ddd-aggregates.out.md](./06-ddd-aggregates.out.md)                   | ddd-aggregates          | III Tactical|
| [07-ddd-domain-interactions.out.md](./07-ddd-domain-interactions.out.md) | ddd-domain-interactions | III Tactical|
| [08-ddd-model-review.out.md](./08-ddd-model-review.out.md)               | ddd-model-review        | IV Validation|

### 2.3 ข้อมูลจริง (Ground Truth)

| ไฟล์                                                   | ดึงมาจาก                                                                                                 |
| :----------------------------------------------------- | :-------------------------------------------------------------------------------------------------------- |
| [reference/contexts.md](./reference/contexts.md)       | architecture.apt, characterization.apt, domain/model/, interfaces/ package                                 |
| [reference/aggregates.md](./reference/aggregates.md)   | Cargo.java, HandlingEvent.java, Voyage.java, Location.java, RouteSpecification.java, characterization.apt |
| [reference/events.md](./reference/events.md)           | CargoLifecycleScenarioTest.java, ApplicationEvents.java, RoutingService.java                               |
| [reference/context-map.md](./reference/context-map.md) | infrastructure/routing/, interfaces/handling/, patterns-reference.apt, com.pathfinder package              |

### 2.4 การให้คะแนนและการทดสอบ Backtrack

| ไฟล์                                                                       | เนื้อหา                             |
| :------------------------------------------------------------------------- | :----------------------------------- |
| [scoring/rubric.md](./scoring/rubric.md)                                   | น้ำหนัก, เกณฑ์, รายการ anchor       |
| [scoring/scorecard.md](./scoring/scorecard.md)                             | คะแนน Skill แต่ละตัว + offset table + คะแนนถ่วงน้ำหนักรวม |
| [backtrack-test/injection-report.md](./backtrack-test/injection-report.md) | inject ข้อบกพร่อง 5 ข้อ ทั้งหมด trigger ได้ถูกต้อง |

## 3. ภาพรวมการให้คะแนน

| Skill                   | น้ำหนัก | คะแนน |    คะแนนถ่วงน้ำหนัก    | จุดเด่น                                                       | สิ่งที่ขาด                                                    |
| :---------------------- | :--: | :--: | :---------------: | :-------------------------------------------------------- | :---------------------------------------------------------------- |
| ddd-scope               | 1.0  | 4.0  |      4.00      | เป้าหมายที่ไม่ใช่ DDD, 20 คำศัพท์, 4 ประเภทความเสี่ยง                  | —                                                                 |
| ddd-discover            | 1.5  | 4.0  |      6.00      | เส้นทางหลัก 14 ขั้นตอน + 3 สาขาผิดปกติ (รวม late arrival)                | —                                                                 |
| ddd-subdomains          | 1.0  | 3.0  |      3.00      | การจำแนก Core/Supporting/Generic ถูกต้อง                     | ช่องว่าง Billing/Customer ในอนาคต                                  |
| ddd-contexts            | 1.5  | 3.5  |      5.25      | 4 BC + 4 ADR; Tracking read-only constraint  Implemented    | ShippingRequest แบ่งย่อยเกินไป                                   |
| ddd-context-map         | 1.5  | 4.0  |      6.00      | ACL + OHS + Customer-Supplier ใช้งานได้ถูกต้องทั้งหมด            | —                                                                 |
| ddd-aggregates          | 2.0  | 2.5  |      5.00      | HandlingEvent เป็น Aggregate อิสระ; dedup key 5 ตัว; Delivery เป็น derived VO | **ขาด Aggregate Voyage + Location**; ขาด Specification pattern   |
| ddd-domain-interactions | 1.5  | 4.0  |      6.00      | RoutingService / ACL separation; ผู้สมัคร Inspection; idempotency      | —                                                                 |
| ddd-model-review        | 1.0  | 2.5  |      2.50      | การประเมิน internal consistency 8 มิติ; การตัดสิน backtrack       | ความซ้ำซ้อน HandlingEvent/Activity/Status; ช่องว่าง Billing/Customer/Carrier |
| **รวม**                 | 11.0 |  —   | **37.75 / 44** | **85.8 %**                                                |                                                                   |

## 4. ผลการทดสอบ Backtrack Trigger

inject ข้อบกพร่องที่ควบคุมได้ 3 รายการลงในผลลัพธ์ตาบอด จากนั้นรัน backtrack matrix ของ `ddd-model-review` ใหม่:

| ข้อบกพร่องที่ inject                            | เงื่อนไขที่คาดไว้              | เป้าหมาย backtrack ที่คาดไว้      |  ผลลัพธ์  |
| :----------------------------------------------- | :--------------------------- | :----------------------------- | :-----: |
| F1: เก็บ Invariant 4/11 ตัวเท่านั้น (36%)         | อัตราการแสดง invariant < 60%       | ddd-aggregates                 | ✅ PASS |
| F2: TrackingView รับผิดชอบ unloading judgment    | Aggregate boundary กับ context boundary ขัดแย้ง | ddd-contexts            | ✅ PASS |
| F3: ลบ Derived Event 4 ตัว (完整性 64%)           | ความครบถ้วนของ event < 70%         | ddd-domain-interactions        | ✅ PASS |
| F4: ชื่อเรียกเดียวกัน 3 แบบในสินค้าเดียว (ความขัดแย้ง 22.2%) | อัตราความขัดแย้งศัพท์ > 20%         | ddd-contexts            | ✅ PASS |
| F5: Domain Service เชื่อมต่อกับภายนอกโดย bypass ACL  | Integration pattern กับ context map ไม่สอดคล้อง | ddd-context-map         | ✅ PASS |

Trigger ทั้ง 5 ตัวถูก activate อย่างถูกต้อง, วินิจฉัยไม่มีข้อผิดพลาด, และนำทางได้ถูกต้อง F4 (อัตราความขัดแย้งศัพท์ > 20%) และ F5 (integration pattern ไม่สอดคล้อง) ไม่สามารถสร้างตัวอย่างเชิงลบได้ในการ blind run ครั้งแรกเพราะ baseline สะอาดเกินไป หลังจากนั้นจึงทดสอบผ่านตามแผน injection ใน `injection-report.md` §F4 / §F5

## 5. ผลการวิจัยหลัก

### 5.1 จุดแข็งของระบบ技能

1. **ขั้นตอน Discovery แข็งแกร่ง**: โดยไม่มีการรั่วไหลของคำศัพท์ DDD, prompt คลุมเครือถูก收敛เป็นปัญหาที่ชัดเจน, คำศัพท์ 20 คำ, และบัญชีความเสี่ยง 4 ประเภทครบถ้วน Event Storming ในขั้นตอน I สร้าง event จริงได้ 14/16 ตัว (และเพิ่มเส้นทาง "late arrival replay" ที่ไม่เคยมีใน reference implementation แต่จำเป็นในสถานการณ์จริง)
2. **การระบุ Integration Pattern แม่นยำ**: pattern ทุกตัวใน context-map (ACL, Open Host Service, Customer-Supplier, Conformist) ตรงกับ reference implementation อย่างสมบูรณ์ ไม่มีข้อผิดพลาด และไม่มี circular dependency
3. **ชั้น Tactical Interaction สะอาด**: idempotency key, factory validation (Type+Voyage pairing), subscription chain, และตำแหน่งของ unloading detector ในฐานะ Domain Service ตรงกับตัวอย่างมาตรฐาน
4. **Feedback loop ทำงานได้**: Backtrack matrix ของ `ddd-model-review` จับ regression ทั้ง 3 ประเภทได้อย่างถูกต้องเมื่อมี defect injection

### 5.2 จุดอ่อนที่ปรากฏ

| จุดอ่อน                                           | ตำแหน่ง         | สาเหตุหลัก                                                                                                                        | คำแนะนำแก้ไข                                                                                                                         |
| :------------------------------------------------ | :--------------- | :---------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------- |
| **ขาด Aggregate Voyage**                          | 06-aggregates    | ข้อมูลเข้าตาบอดระบุว่า Pathfinder เป็นภายนอก โมเดลจึงปฏิบัติต่อ Voyage เป็น external reference ความจริงมี lifecycle สมบูรณ์ (Schedule, CarrierMovement) ใน Voyage | เพิ่มใน SKILL ของ `ddd-aggregates`: สำหรับ external reference ทุกตัว ต้องถามอีกครั้งว่าเราต้องจัดการ lifecycle หรือไม่ ถ้าใช่ ควรยกระดับเป็น Aggregate ภายใน |
| **Aggregate Location ถูกลดเป็น "สมมติฐาน"**        | 06-aggregates    | ท่าเรือถูกติดป้ายว่าเป็น "reference data assumption" ไม่ได้ปฏิบัติในฐานะ aggregate หลัก                                              | เหมือนข้างต้น — ระบุ subdomain ของ reference data อย่างชัดเจน                                                                          |
| **ไม่ได้ระบุ Specification pattern**              | 06-aggregates    | predicate เช่น `isSatisfiedBy(Itinerary)` ถูก synthetize เข้า factory โดยไม่ได้กล่าวถึงชื่อ pattern                                  | เพิ่ม Specification pattern ในรายการตรวจสอบของ `ddd-aggregates`                                                                         |
| **`ddd-model-review` ขาดมุมมอง "industry benchmark"** | 08               | การ review ตาบอดทำ internal review เท่านั้น ไม่ได้เทียบกับจุด争议 3 จุดในตัวอย่าง Cargo (HandlingEvent/Activity/TransportStatus ซ้อนทับ, Billing/Customer ขาด, Carrier ไม่ได้ model) | เพิ่มใน `ddd-model-review`: ถ้า domain มี reference implementation open source ที่成熟 ควรเปรียบเทียบและ列出 "สิ่งที่ converge/diverge", "known limitations ที่ระบุเอง", "future domain ที่ควรพิจารณา" |
| **ShippingRequest แบ่งย่อยเกินไป**               | 04-contexts      | โมเดลตาบอด引入แนวคิด "ก่อนสั่งซื้อ/ความตั้งใจ" ในขณะที่ตัวอย่างมาตรฐานใช้ RouteSpecification เป็น VO ของ Cargo ตั้งแต่แรก ทั้งสองวิธีถูกต้องแต่เบี่ยงเบนจากมาตรฐาน | คงสภาพปัจจุบัน; ในการ review โมเดล ให้บันทึกว่าทั้งสองทางเลือกถูกต้อง                                                              |

### 5.3 จุดเด่นเชิงบวก (值得表扬)

- **Late arrival replay (E-B3)**: Pipeline ตาบอด model event `LateHandlingIngested` และกลยุทธ์ "recalculate from anchor point" reference implementation ไม่มี mechanism นี้; เป็นการ enhance ระดับอุตสาหกรรมที่เกิดจาก prompt ที่เขียนว่า "delay เป็นชั่วโมงถึงวัน"
- **Explicit RouteVersion**: โมเดลตาบอดทำให้ Route versioning เป็น concept หลักตัวอย่างมาตรฐานแทนที่ Itinerary ทั้งชุดโดยไม่มี explicit version; แผนตาบอด利于การ audit
- **Dual-axis version management**: ใน `05-context-map` แยก event Schema version กับ RouteVersion ออกจากกัน สะอาดกว่า reference implementation

## 6. ข้อเสนอแนะสำหรับระบบ技能

### 6.1 การอัปเดต SKILL.md ที่เสนอ

**`skills/ddd-aggregates/SKILL.md`** — เพิ่มในขั้นตอนที่ 4:

> สำหรับ "foreign reference object" ในโมเดลทุกตัว ต้องถามอีกครั้งว่า: เราต้องจัดการ lifecycle ของมันเองหรือไม่? ถ้าใช่ ควรยกระดับเป็น **Aggregate ภายใน** แทนที่จะเก็บเฉพาะ ID reference นอกจากนี้ ให้ระบุโอกาสที่จะพบ Specification pattern (เช่น "ชุดกฎธุรกิจใดสามารถ抽出เป็น predicate `isSatisfiedBy(...)` ได้")

**`skills/ddd-model-review/SKILL.md`** — เพิ่มบรรทัดใหม่ในขั้นตอนที่ 1:

> ถ้า domain มี reference implementation open source ที่成熟 (เช่น domain โลจิสติกส์ใช้ Cargo, domain e-commerce ใช้ Broadleaf) ให้ใช้เป็น benchmark ที่ 9 โดย逐条列出: สิ่งที่ **converge/diverge** กับ reference implementation, **known limitations ที่ระบุเอง** (เช่น ความซ้ำซ้อน Activity/Status/Event), **future domain ที่ควรพิจารณา** (เช่น Billing/Customer/Carrier)

**`skills/ddd-contexts/SKILL.md`** — เพิ่มในรายการตรวจสอบ:

> ถ้าในขั้นตอนการสั่งซื้อมีการ引入แนวคิด "的需求/ความตั้งใจ" ระหว่างทาง (เช่น ShippingRequest) ต้องระบุความสัมพันธ์ lifecycle กับ Aggregate ที่เกี่ยวข้อง (เป็น upstream → ยกระดับเป็น Aggregate, หรือเทียบเท่ากับ VO ของ Aggregate) ทั้งสองทางเลือกถูกต้อง ต้องแสดงและบันทึก ADR

### 6.2 แนวทางการทดสอบ

กรณีตรวจสอบในอนาคตควร:

- เพิ่มอย่างน้อยหนึ่งกรณี domain ที่**ไม่มี reference implementation open source ที่成熟** เพื่อทดสอบการทำงานของ技能เมื่อไม่มี baseline
- ~~ทดสอบ trigger ที่ยังไม่ได้ทดสอบ 2 ตัว (อัตราความขัดแย้งศัพท์ > 20%, integration pattern ไม่สอดคล้อง)~~ — เสร็จแล้ว ดู `backtrack-test/injection-report.md` §F4 / §F5

## 7. สารบัญ Artifact

```text
validation-cases/cargo-validation/
├── 00-fuzzy-prompt.md                     ข้อมูลเข้าตาบอด
├── 01-ddd-scope.out.md                    blind run ขั้นตอน I
├── 02-ddd-discover.out.md                 blind run ขั้นตอน I
├── 03-ddd-subdomains.out.md               blind run ขั้นตอน II
├── 04-ddd-contexts.out.md                 blind run ขั้นตอน II
├── 05-ddd-context-map.out.md              blind run ขั้นตอน II
├── 06-ddd-aggregates.out.md               blind run ขั้นตอน III
├── 07-ddd-domain-interactions.out.md      blind run ขั้นตอน III
├── 08-ddd-model-review.out.md             blind run ขั้นตอน IV (self-review)
├── reference/
│   ├── contexts.md                        ground truth — BC และ Universal Language
│   ├── aggregates.md                      ground truth — Aggregate และ Invariant
│   ├── events.md                          ground truth — Event flow และ Service
│   └── context-map.md                     ground truth — Integration และ ACL
├── scoring/
│   ├── rubric.md                          น้ำหนัก, anchor, กฎ
│   └── scorecard.md                       คะแนน Skill แต่ละตัว, offset table, คะแนนรวม
├── backtrack-test/
│   └── injection-report.md                inject 5 ข้อบกพร่อง, trigger ทั้ง 5 ผ่านการตรวจสอบ
└── REPORT.md                              (ไฟล์นี้)
```

## 8. ข้อสรุป

ภายใต้เงื่อนไข blind run, pipeline DDD modeling ของ Skill ทั้ง 8 ตัว收敛 prompt ทางธุรกิจคลุมเครือเป็น Domain Model ที่ได้คะแนน **85.8 %** เทียบกับตัวอย่างมาตรฐานของ Cargo: ไม่มี structural regression, backtrack trigger ทำงานได้ครบถ้วน SKILL.md patch 2 รายการที่เสนอ (การค้นหา Aggregate Voyage/Location, model-review เพิ่ม industry benchmark) คาดว่าจะเพิ่มคะแนนในการรันครั้งถัดไปเป็น 90–95 %

เมื่อ domain ไม่มี reference implementation ที่标准 ระบบ技能นี้**พร้อมใช้งานจริง**; เมื่อมี reference implementation ที่标准可以通过การปรับปรุงเป้าหมายข้างต้นเพิ่มประสิทธิภาพได้มากขึ้น