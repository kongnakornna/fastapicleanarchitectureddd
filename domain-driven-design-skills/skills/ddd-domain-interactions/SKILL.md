---
name: ddd-domain-interactions
description: "ออกแบบกลไกการทำงานร่วมกันระหว่างส่วนประกอบ: Domain Event, Domain Service, Interface Repository และ Factory"
risk: safe
source: self
tags: "[ddd, tactical, events, services, repositories]"
date_added: "2026-05-08"
---

# DDD Domain Interactions

> 🌐 English version: [English](SKILL.en.md)

## สถานการณ์ที่ควรใช้

- ขอบเขต Aggregate ออกแบบเสร็จแล้ว ต้องกำหนดกลไกการทำงานร่วมกันระหว่าง Aggregate และระหว่าง Aggregate กับภายนอก
- ต้องตอบคำถามว่า "Aggregate สื่อสารกันอย่างไร ใครเป็นผู้ประสานงานข้าม Aggregate สัญญาการ持久化คืออะไร"
- เป็นขั้นตอนสุดท้ายของ Tactical Modeling เติมเต็ม "เนื้อเยื่อเชื่อมต่อ" ทั้งหมด

## ความต้องการ Input

- **จำเป็น**: สารบัญ Aggregate และตาราง Invariant (จาก `ddd-aggregates`), รายการ Event ที่เป็นไปได้ (จาก `ddd-discover`)
- **ไม่จำเป็น**: แผนที่ Context และข้อมูลสัญญา (จาก `ddd-context-map`), สารบัญ Context และคลังคำศัพท์ (จาก `ddd-contexts` ใช้เพื่อแยกแยะ Domain Event กับ Integration Event)

## ขั้นตอน

1. **ปรับมาตรฐาน Event**: ปรับรูปแบบการตั้งชื่อ Event ให้เป็นมาตรฐาน (อดีตกาล, ฝ่ายธุรกิจเข้าใจได้, ไม่มีคำเทคนิค) สำหรับแต่ละ Event กำหนดเงื่อนไขการกระตุ้น, Aggregate ต้นทาง, ช่องข้อมูลสำคัญ, ความต้องการเรียงลำดับ
2. **แยกแยะขอบเขต**: แยก Domain Event (ภายใน Context) และ Integration Event (ข้าม Context/เผยแพร่ภายนอก)
3. **กลยุทธ์ความน่าเชื่อถือ**: สำหรับแต่ละ Event กำหนด Idempotency Key, กลยุทธ์ Replay, หน้าต่าง Deduplication, การจัดการ Dead Letter
4. **Domain Service**: ระบุ operation ที่ไม่สังกัด Aggregate เดียวแต่รับผิดชอบ logic ทางธุรกิจ กำหนดเป็น Domain Service — ระบุ Input, Output, Aggregate และ Event ที่ใช้
5. **Interface Repository**: สำหรับแต่ละ Aggregate กำหนด Interface Repository ทางอรรถศาสตร์ (โหลด, 持久化, Query) — กำหนดเฉพาะสัญญา ไม่เกี่ยวกับการ implement
6. **Factory**: ระบุ logic ที่ซับซ้อนในการสร้าง Aggregate กำหนด Factory Method — ระบุเงื่อนไขการสร้าง, กฎการตรวจสอบ และสถานะเริ่มต้น
7. **Subscriber และผลข้างเคียง**: ระบุผู้บริโภค, การกระทำที่กระตุ้น, กลยุทธ์ชดเชย, ตัวชี้วัดการตรวจสอบ สำหรับแต่ละ Event

## ผลลัพธ์

| ผลงาน                       | ข้อกำหนดโครงสร้าง                                                             |
| :--------------------------- | :------------------------------------------------------------------------------ |
| สารบัญ Domain Event          | ตาราง: ชื่อ Event, Aggregate ต้นทาง, เงื่อนไขการกระตุ้น, ช่องข้อมูลสำคัญ, ขอบเขต (Domain/Integration) |
| สัญญา Integration Event      | ตาราง: ชื่อ Event, ผู้เผยแพร่, ผู้บริโภค, Owner สัญญา, กลยุทธ์เวอร์ชัน, กรอบเวลาความเข้ากันได้ |
| กลยุทธ์ Idempotency และ Replay | ตาราง: Event, Idempotency Key, หน้าต่าง Deduplication, กฎ Replay, การจัดการข้อผิดพลาด |
| นิยาม Domain Service         | ตาราง: ชื่อบริการ, หน้าที่, Input, Output, Aggregate/Event ที่พึ่งพา, logic ที่ไม่ควรมี |
| รายการ Interface Repository  | ตาราง: Aggregate, ลายเซ็น method (อรรถศาสตร์), คำอธิบายอรรถศาสตร์, ขอบเขต Query |
| รายการ Factory               | ตาราง: ชื่อ Factory/method, เป้าหมายการสร้าง, เงื่อนไขการสร้าง, กฎการตรวจสอบ, สถานะเริ่มต้น |
| Subscriber และผลข้างเคียง   | ตาราง: Event, Subscriber, การกระทำที่กระตุ้น, กลยุทธ์ชดเชย, ตัวชี้วัดการตรวจสอบ     |

## รายการตรวจสอบ

- [ ] ทุก Event ตั้งชื่อเป็นอดีตกาล ไม่มีการปนเปื้อนคำเทคนิค
- [ ] Event ที่เผยแพร่ข้าม Context มีกลยุทธ์เวอร์ชันและกรอบเวลาความเข้ากันได้
- [ ] Event สำคัญมี Idempotency Key และกลยุทธ์ Replay
- [ ] Domain Service ไม่มี logic ทางธุรกิจที่ควรอยู่ใน Aggregate (หลีกเลี่ยง Anemic Model)
- [ ] Interface Repository กำหนดเฉพาะสัญญาอรรถศาสตร์ ไม่มีรายละเอียดการ implement (SQL, ORM)
- [ ] ทุก logic การสร้างที่ซับซ้อนมี Factory ที่สอดคล้อง (ไม่ new ตรงๆ ใน Application Layer)

## การย้อนกลับ

- Event ต้องพกข้อมูลส่วนตัวของ Aggregate อื่น (ไม่สามารถออกแบบ Event Schema ที่สะอาดได้) → ย้อนกลับไป `ddd-aggregates` (ขอบเขต Aggregate ต้องปรับเพื่อให้ Event เป็น self-contained)

## ตัวอย่าง

```text
@ddd-domain-interactions
จากการออกแบบ Aggregate ต่อไปนี้ ช่วยออกแบบชั้น Domain Interaction:
- Aggregate: Booking (Root: Booking, VO: TimeSlot, BookingStatus)
- Aggregate: RoomSchedule (Root: RoomSchedule, VO: TimeSlotOccupancy)
- Event ที่เป็นไปได้: BookingConfirmed, BookingCancelled, CheckInRecorded
สร้าง สารบัญ Domain Event, Domain Service, Interface Repository และรายการ Subscriber
```
