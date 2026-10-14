---
name: ddd-aggregates
description: "ออกแบบขอบเขต Aggregate จาก Invariant: Aggregate Root, Entity, Value Object, ขอบเขตธุรกรรม และกลยุทธ์ความสอดคล้องข้าม Aggregate"
risk: safe
source: self
tags: "[ddd, tactical, aggregates, invariants]"
date_added: "2026-05-08"
---

# DDD Aggregates

> 🌐 English version: [English](SKILL.en.md)

## สถานการณ์ที่ควรใช้

- Bounded Context และกลยุทธ์การเชื่อมต่อพร้อมแล้ว ต้องการออกแบบส่วนประกอบภายใน Context
- ต้องตอบคำถามว่า "วัตถุใดต้องเปลี่ยนแปลงร่วมกันเพื่อรักษาความสอดคล้อง"
- `ddd-model-review` รายงาน "อัตราการแสดง Invariant < 60%" หรือ `ddd-domain-interactions` รายงาน "Event ต้องพกข้อมูลส่วนตัวของ Aggregate อื่น" ให้ใช้เป็นเป้าหมายการย้อนกลับ

## ความต้องการ Input

- **จำเป็น**: Event Stream และคำสั่งที่เป็นไปได้ (จาก `ddd-discover`), สารบัญ Context และคลังคำศัพท์ (จาก `ddd-contexts`)
- **ไม่จำเป็น**: แผนที่ Context และรูปแบบความล้มเหลว (จาก `ddd-context-map`)

## ขั้นตอน

1. **แยก Invariant**: แยกกฎทางธุรกิจที่ "ต้องเป็นจริงเสมอ" (Invariant) จากคำสั่งและ Event
2. **จัดกลุ่มวัตถุ**: ใช้ Invariant เป็นตัวเชื่อม จัดกลุ่มวัตถุเป็นตัวเลือก Aggregate ระบุ Aggregate Root (จุดเข้าภายนอกเดียว)
3. **ระบุส่วนประกอบ**: แยก Entity (มีตัวตน, มีวงจรชีวิต) และ Value Object (ไม่มีตัวตน, ไม่เปลี่ยนแปลง, เปรียบเทียบตามค่า) ภายใน Aggregate
4. **กำหนดกฎขอบเขต**: ภายนอกถือเฉพาะการอ้างอิงถึง Aggregate Root การอ้างอิงข้าม Aggregate ใช้ ID แต่ละ Aggregate เป็นขอบเขตธุรกรรมเดียว
   - **ตรวจสอบการอ้างอิงภายนอกอีกครั้ง**: สำหรับ "วัตถุอ้างอิงภายนอก" (foreign reference) ทุกรายการในโมเดล ถามอีกครั้ง — เราจำเป็นต้องจัดการวงจรชีวิต (สร้าง, แก้ไข, ยุติ) ของมันเองหรือไม่? ถ้าใช่ มันควรถูกเลื่อนเป็น **Aggregate ภายใน** แทนที่จะเก็บเฉพาะการอ้างอิง ID เครื่องมือกระตุ้น: วัตถุอ้างอิงข้อมูลอ้างอิง (แคตตาล็อกท่าเรือ, ปฏิทิน, แคตตาล็อกเส้นทาง) หากดูแลโดยเรา ต้องจัดเป็น Aggregate
   - **การระบุรูปแบบ Specification**: เมื่อกฎทางธุรกิจบางข้อปรากฏในรูปแบบ predicated "กำหนด X, X 满足 Y หรือไม่" (เช่น `isSatisfiedBy(Itinerary)`) ให้แยกออกมาเป็น Specification อย่างชัดเจน แทนที่จะใส่ใน if ภายใน Factory หรือ Service
5. **ขอบเขตคำสั่ง**: สำหรับแต่ละ Aggregate กำหนดคำสั่งที่รับผิดชอบ, การตรวจสอบก่อน, ผลข้างเคียง
6. **ความสอดคล้องข้าม Aggregate**: ภายใน Aggregate ความสอดคล้องสูง; ระหว่าง Aggregate ความสอดคล้องสุดท้าย — กำหนดกลยุทธ์ Event-Driven / Compensation / Retry
7. **ร่าง Interface Repository**: สร้างนิยามอรรถศาสตร์ของ Interface Repository สำหรับแต่ละ Aggregate (ชื่อ method + อรรถศาสตร์ ไม่รวมโค้ด)

## ผลลัพธ์

| ผลงาน                      | ข้อกำหนดโครงสร้าง                                                          |
| :-------------------------- | :--------------------------------------------------------------------------- |
| สารบัญ Aggregate            | ตาราง: ชื่อ Aggregate, Aggregate Root, Entity ที่มี, Value Object ที่มี, Invariant หลัก, คำสั่งหลัก |
| ตาราง Invariant             | ตาราง: Invariant, คำสั่งที่กระตุ้น, ตำแหน่งตรวจสอบ, พฤติกรรมเมื่อล่วงละเมิด |
| รายการ Entity และ Value Object | ตาราง: ชื่อ, ประเภท (Entity/VO), Aggregate ที่สังกัด, กลยุทธ์ตัวตน/คำจำกัดความความเท่าเทียม |
| คำอธิบายขอบเขตธุรกรรม     | รายการ: กฎเริ่มต้น, เงื่อนไขยกเว้น, กลยุทธ์ concurrency/lock              |
| กลยุทธ์ความสอดคล้องข้าม Aggregate | ตาราง: สถานการณ์, Event ที่กระตุ้น, วิธีชดเชย, การรับประกัน Idempotency, กลยุทธ์ Retry |
| ร่าง Interface Repository   | ตาราง: Aggregate, method, คำอธิบายอรรถศาสตร์, ขอบเขต Query               |

## รายการตรวจสอบ

- [ ] ทุก Aggregate มีอย่างน้อย 1 Invariant ที่ชัดเจน
- [ ] ขอบเขต Aggregate อธิบายขอบเขตธุรกรรม; เริ่มต้น "1 ธุรกรรมแก้ไข 1 Aggregate"
- [ ] ความสอดคล้องข้าม Aggregate มี Event และกลยุทธ์ชดเชย
- [ ] ไม่มีรูปแบบต้องห้าม "ใช้ Foreign Key แบ่ง Aggregate" (Aggregate ไม่ใช่ ORM Relationship Mapping)
- [ ] การแยก Entity และ Value Object มีเหตุผลชัดเจน (ตัวตน vs. ค่า)
- [ ] ขนาด Aggregate เหมาะสม: Aggregate เดียวไม่ควรมี > 5 Entity (ถ้าเกินต้องให้เหตุผล)
- [ ] ทุกการอ้างอิงภายนอกได้รับการตอบคำถาม "วงจรชีวิตจัดการโดยเราหรือไม่" แล้ว; ผู้ที่ตอบใช่ได้รับการเลื่อนเป็น Aggregate ภายในแล้ว
- [ ] สแกน "กฎทางธุรกิจแบบ predicated" และประเมินรูปแบบ Specification แล้ว; ผู้ที่เลือกได้รับการจัดเป็นส่วนประกอบหลักแล้ว

## การย้อนกลับ

- Invariant ข้ามหลาย Context → ย้อนกลับไป `ddd-contexts` (ความต้องการความสอดคล้องถูกตัดขาดโดยขอบเขต)
- ถูก trigger ย้อนกลับโดย `ddd-domain-interactions`: Event ต้องพกข้อมูลส่วนตัวของ Aggregate อื่น แสดงว่าขอบเขต Aggregate ต้องปรับ
- ถูก trigger ย้อนกลับโดย `ddd-model-review`: อัตราการแสดง Invariant < 60% (Aggregate อาจเป็น Data Container แทนที่จะเป็นขอบเขตพฤติกรรม)

## ตัวอย่าง

```text
@ddd-aggregates
จากนิยาม Context และ Event Stream ต่อไปนี้ ช่วยออกแบบ Aggregate ภายใน Context Booking:
- Context: Booking (วงจรชีวิตการจองทั้งหมด)
- ศัพท์หลัก: Booking, TimeSlot, BookingPolicy, CheckIn
- Event หลัก: BookingRequested, BookingConfirmed, BookingCancelled, CheckInRecorded
สร้าง สารบัญ Aggregate, ตาราง Invariant, รายการ Entity/Value Object และคำอธิบายขอบเขตธุรกรรม
```
