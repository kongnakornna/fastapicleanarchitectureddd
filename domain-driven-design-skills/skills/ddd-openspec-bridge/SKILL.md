---
name: ddd-openspec-bridge
description: "แปลงผลงาน Tactical Modeling ของ DDD เป็นข้อกำหนดเชิงโครงสร้างของ OpenSpec สร้างการเชื่อมต่อที่ราบรื่นจากการ Model Domain ไปสู่การ implement ทางวิศวกรรม"
risk: safe
source: self
tags: "[ddd, implementation, openspec, sdd]"
date_added: "2026-05-11"
---

# DDD OpenSpec Bridge

> 🌐 English version: [English](SKILL.en.md)

## สถานการณ์ที่ควรใช้

- Tactical Modeling (Stage III) เสร็จสมบูรณ์แล้ว โมเดลผ่านการตรวจสอบ (Stage IV) พร้อมเข้าสู่ขั้นตอนการพัฒนา
- ต้องการแปลงโมเดล Domain เป็นข้อกำหนดทางวิศวกรรมเชิงโครงสร้างที่ AI Agent หรือนักพัฒนาสามารถนำไปปฏิบัติได้
- ต้องการสร้าง "แหล่งข้อมูลเดียว" (Source of Truth) ระหว่างโมเดลธุรกิจกับการ implement โค้ด

## ความต้องการ Input

- **จำเป็น**:
  - นิยาม Problem Space (จาก `ddd-scope`)
  - การจำแนก Subdomain และคำประกาศ Domain หลัก (จาก `ddd-subdomains`)
  - สารบัญ Context และ ADR (จาก `ddd-contexts`)
  - แผนที่ Context และรูปแบบการเชื่อมต่อ (จาก `ddd-context-map`)
  - สารบัญ Aggregate และ Invariant (จาก `ddd-aggregates`)
  - นิยาม Domain Interaction: Domain Event, Domain Service, Interface Repository, Factory (จาก `ddd-domain-interactions`)
- **ไม่จำเป็น**:
  - Event Stream และเบาะแสขอบเขตจากขั้นตอน Discovery (จาก `ddd-discover`)
  - รายงานผลการตรวจสอบโมเดล (จาก `ddd-model-review`)
- **เกณฑ์การปฏิบัติ**: ตรรกะการจับคู่ต้องเป็นไปตามนิยามมาตรฐานใน [ddd-openspec-mapping.md](../../docs/ddd-openspec-mapping.md)

## ขั้นตอน

1. **เริ่มต้น OpenSpec Change Set**: สร้าง directory ใน `openspec/changes/<change-id>/` สร้าง `.openspec.yaml` สำหรับการเปลี่ยนแปลงครั้งนี้ หมายเหตุ: นี่ต่างจาก `openspec/config.yaml` แบบ global — อ latter ได้รับการดูแลโดยขั้นตอน `ddd-contexts` ครั้งเดียว ใช้ประกาศ Domain-Bounded Context Mapping และข้อจำกัดทางสถาปัตยกรรม
2. **สร้าง Proposal (`proposal.md`)**:
   - แปลงปัญหาStatements จาก `ddd-scope` เป็น Why
   - เขียน Capabilities ที่ได้รับผลกระทบในการเปลี่ยนแปลงนี้ลงใน What Changes; จัดลำดับความสำคัญตามการจำแนกของ `ddd-subdomains`: **Core Subdomain** ต้อง Scenario ทั้งหมด, **Generic Subdomain** สามารถอ้างอิงข้อกำหนดที่มีอยู่หรือส่วนประกอบภายนอก
   - ใน Impact ระบุ Capabilities ที่ได้รับผลกระทบและรายการการเปลี่ยนแปลง Aggregate; ใน Goals กำหนดเกณฑ์ความสำเร็จ (SLO / ตัวชี้วัดการยอมรับ)
3. **สร้างสารบัญ Bounded Context**: ตามสารบัญ Context ของ `ddd-contexts` สร้างไฟล์ข้อกำหนดสำหรับแต่ละ Capability ใน `specs/<bounded-context>/<capability>/spec.md` **ห้ามใช้ directory แบบ flat `specs/domain-model/`** — มันจะทำลายการจัดวางเชิงกลยุทธ์ระหว่าง Bounded Context และสารบัญ Domain
4. **เขียน Requirement และ Scenario** (เป็นไปตามทิศทางการจับคู่ใน [ddd-openspec-mapping.md §2.1](../../docs/ddd-openspec-mapping.md) อย่างเคร่งครัด):
   - **Requirement** ← คำสั่งและ Domain Service ใน `ddd-domain-interactions`; 1 Requirement ตรงกับ **1 ความสามารถทางธุรกิจที่ตรวจสอบได้อิสระ** จำนวน Scenario ≤ 5 และไม่ข้าม Aggregate Root
   - **Scenario** ← พฤติกรรม Aggregate และ Invariant ใน `ddd-aggregates` อธิบายแบบ Given/When/Then; Invariant ระดับ P0 ต้องมี Scenario ที่ตรงกัน
   - **Domain Event** เขียนเป็นผลข้างเคียงใน Clause Then/And ของ Scenario (เช่น "And เผยแพร่ Event OrderPlaced")
   - **กฎทางธุรกิจมาก่อน**: Scenario อธิบายเฉพาะกฎทางธุรกิจและ Invariant ห้ามแทรก的技术细节 (Database, HTTP, ORM, Cache ฯลฯ)
5. **ตรวจสอบภาษากลาง**: เทียบกับคลังคำศัพท์ของ `ddd-contexts` ให้แน่ใจว่าศัพท์ใน `proposal.md` และ `spec.md` ทั้งหมดอยู่ในคลังคำศัพท์; ศัพท์ที่ยังไม่ได้收录ต้องเขียนกลับคลังคำศัพท์ก่อนหรือใช้คำพ้องความหมาย
6. **ออกแบบเทคนิค (`design.md`)**: รวมรูปแบบการเชื่อมต่อจาก `ddd-context-map` และกลไกการทำงานร่วมกันจาก `ddd-domain-interactions`; อธิบายการจับคู่สถาปัตยกรรมแบบชั้น, การแปลข้าม Context (ACL), รูปแบบการเผยแพร่/บริโภค Event (Outbox Pattern, Idempotency Key, 1 ธุรกรรมแก้ไข 1 Aggregate — ดู [ภาคผนวก A ของ ddd-openspec-mapping.md](../../docs/ddd-openspec-mapping.md))
7. **แยกงานพัฒนา (`tasks.md`)**: ตามลำดับการพึ่งพาของ Spec (Domain Model → Repository → Application Service → API/Integration) แยกงาน แต่ละงานเชื่อมโยง Requirement หรือ Scenario ที่เกี่ยวข้องเป็นเกณฑ์การยอมรับ

## ผลลัพธ์

| ผลงาน           | ข้อกำหนดโครงสร้าง                                                           |
| :--------------- | :---------------------------------------------------------------------------- |
| `proposal.md`    | มี Why, What Changes, Impact (Capabilities / การเปลี่ยนแปลง Aggregate), Goals  |
| `design.md`      | มีการออกแบบสถาปัตยกรรม, การจับคู่โมเดลข้อมูล, ข้อมูลหลัก, การนิยาม Interface Protocol |
| สารบัญ `specs/`  | โฟลเดอร์ย่อยจัดตาม Capability มี `spec.md` (รูปแบบ Requirement + Scenario)    |
| `tasks.md`       | มีชื่องาน, คำอธิบายงาน, เส้นทาง Spec ที่เชื่อมโยง, เกณฑ์การยอมรับ          |

## รายการตรวจสอบ

- [ ] โครงสร้าง Directory ของ OpenSpec เป็นไปตามข้อกำหนด (config, specs, changes); `specs/` จัดเป็นโฟลเดอร์ตาม Bounded Context ไม่มี `domain-model/` แบบ flat
- [ ] **ขนาด Requirement เหมาะสม**: แต่ละ Requirement ตรงกับ 1 ความสามารถทางธุรกิจที่ตรวจสอบได้อิสระ จำนวน Scenario ≤ 5 และไม่ข้าม Aggregate Root
- [ ] **Scenario ยึดหลักกฎทางธุรกิจ**: ไม่มีรายละเอียดทางเทคนิค (Database, HTTP, ORM, Cache); Invariant P0 ของ `ddd-aggregates` ทั้งหมดได้รับการแปลงเป็น Scenario แล้ว
- [ ] **ความสอดคล้องศัพท์**: ศัพท์ใน `proposal.md` และ `spec.md` ทั้งหมดค้นหาได้ในคลังคำศัพท์ของ `ddd-contexts`; Capabilities ใน `proposal.md` สอดคล้องกับ `ddd-contexts`
- [ ] **รูปแบบ Event-Driven ได้รับการ **: สถานการณ์ข้าม Aggregate ใน `design.md` ระบุอย่างชัดเจนว่าเป็นไปตาม Outbox Pattern, Idempotency Key และ "1 ธุรกรรมแก้ไข 1 Aggregate"
- [ ] **จังหวะการทำซпотенциcontrolled (ก้าวเล็กๆ เร็วๆ)**: ขนาด Change Set นี้สามารถทำให้เสร็จในขั้นตอน Apply เดียวได้ ไม่ลื่นไปเป็น Waterfall จิ๋ว
- [ ] งานใน `tasks.md` สามารถปฏิบัติได้ และแต่ละงานมีการอ้างอิง Requirement / Scenario ที่ชัดเจนเป็นเกณฑ์การยอมรับ
- [ ] การจัดรูปแบบภาษาจีน-อังกฤษเป็นไปตามข้อกำหนดโครงการ (มีช่องว่างระหว่างจีนกับอังกฤษ ชื่อเฉพาะใส่ backtick)

## การย้อนกลับ

- เขียน Scenario แล้วพบว่า Domain Logic มีจุดคลุมเครือหรือข้อขัดแย้ง → ย้อนกลับไป `ddd-aggregates` หรือ `ddd-domain-interactions`
- ไม่สามารถแสดงรูปแบบการเชื่อมต่อได้ชัดเจนในโครงสร้าง OpenSpec → ย้อนกลับไป `ddd-context-map`
- ไม่สามารถลบรายละเอียดทางเทคนิค (Database / HTTP / ORM ฯลฯ) ออกจาก Scenario ได้ → ละเมิดหลักกฎทางธุรกิจมาก่อน; เขียนใหม่ใน Skill นี้ก่อน หากยังไม่สามารถทำให้บริสุทธิ์ได้ให้ย้อนกลับไป `ddd-aggregates` นิยามพฤติกรรม Aggregate ใหม่
- Requirement เดียวมี Scenario มากกว่า 5 หรือข้าม Aggregate Root หลายตัว → ละเมิดข้อตกลงขนาด ย้อนกลับไป `ddd-domain-interactions` แยกคำสั่งและ Domain Service
- ศัพท์ไม่ได้อยู่ในคลังคำศัพท์ของ `ddd-contexts` → ย้อนกลับไป `ddd-contexts` เติมหรือปรับมาตรฐานศัพท์

## ตัวอย่าง

> ตัวอย่างการเขียน Requirement / Scenario ที่สมบูรณ์ดูที่ [ddd-openspec-mapping.md §5](../../docs/ddd-openspec-mapping.md) (ตัวอย่างที่ทำได้จริงขั้นต่ำตั้งแต่ต้นจนจบโดยใช้ "การลงทะเบียนผู้ใช้" เป็นตัวอย่าง)