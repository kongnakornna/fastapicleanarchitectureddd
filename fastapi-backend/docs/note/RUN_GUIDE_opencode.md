# คู่มือการรัน opencode  
เทคนิคสำคัญในการทำให้ OpenCode (หรือ AI Coding Agent ทุกตัว) ทำงานได้เร็วที่สุด และ ประหยัด Token ได้มากถึง 50-80% คือการลดสิ่งที่เรียกว่า "AI Hallucination" และ "Chat Overheads" (การพูดคุยทักทายที่ยืดยาว) โดยการจ่าย Context ที่กระชับ โครงสร้างสถาปัตยกรรมที่ชัดเจน และจำกัดขอบเขต (Scope) ด้วยโค้ดตัวอย่าง เหมือนที่คุณทำในเทมเพลตด้านบนครับ
------------------------------
## 💡 เทคนิคการใช้ Skill และสั่ง OpenCode ให้ประหยัด Token + ทำงานเร็ว
## 1. การส่งบริบทแบบ "ขอบเขตจำกัด" (Micro-Context Isolation)

* ปัญหา: การสาดโค้ดทั้งโปรเจกต์เข้าไปในแชทเดียว จะทำให้ Token บวมอย่างรวดเร็ว และ AI จะประมวลผลช้าลงเรื่อย ๆ
* วิธีแก้: แยกการสั่งงานเป็น 1 Module ต่อ 1 Prompt (ตามเทมเพลตที่คุณออกแบบไว้ดีมาก) และใช้คำสั่งเจาะจงให้ AI ตอบเฉพาะไฟล์ที่เกี่ยวข้อง โดยไม่ต้องอธิบายหลักการซ้ำ

## 2. ใช้ System Constraints เพื่อบังคับให้ตอบกระชับ
คุณสามารถเติมคำสั่งเปิดหัวโปรเจกต์ (System Prompt) เพื่อล็อกพฤติกรรมของ OpenCode ให้เน้นความเร็วและประหยัด Token เช่น:

[Constraints]- ไม่ต้องกล่าวทักทาย ไม่ต้องสรุปสิ่งที่ฉันสั่ง
- เขียนโค้ดตัวเต็ม (Production-ready) ห้ามใช้คอมเมนต์ละไว้แบบ `// ... code here ...`- ตอบกลับเฉพาะโค้ดของไฟล์ที่ระบุในข้อกำหนดเท่านั้น

------------------------------
## 📄 เทมเพลตตัวอย่าง (Template) สำหรับการสร้าง Module ถัดไป
คุณสามารถใช้เทมเพลตโครงสร้างนี้ก๊อปปี้ไปปรับใช้กับ Module อื่น ๆ เช่น billing, inventory, หรือ auth ได้ทันที โดยมันจะถูกออกแบบให้ AI เข้าใจสถาปัตยกรรมภายใน 1 วินาที และเริ่มเขียนโค้ดได้ทันทีโดยไม่เปลือง Token นอกเรื่องครับ

## 📄 Module [X.X]: `[ชื่อ Module]`
### Metadata
| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `[ชื่อ Module เช่น inventory]` |
| **Layer** | `[เลข Layer เช่น 1 (Core) / 2 (Application)]` |
| **Priority** | 🔴 (High) / 🟡 (Medium) / 🟢 (Low) |
| **Phase** | [เลข Phase เช่น 1] |
| **มิติธุรกิจ** | [เช่น Core / Support / Generic] |
| **Dependencies** | `[Module ที่ต้องใช้ก่อนหน้า เช่น tenant_context]` |
| **Domain Concepts** | `[ชื่อ Entity / Enum / VO เช่น StockItem, StockAction]` |
| **Prefix** | `[ตัวย่อ 3 หลัก เช่น inv]` |
| **Tables** | `tenant_{tid}.[ชื่อตาราง]` |
### 🎯 Prompt (Copy ทั้งหมด)```markdown
# สร้าง Module `[ชื่อ Module]`

## บริบท
- ERP + CRM + IoT สำหรับ SME (Multi-company)
- Clean Architecture + DDD (4 layers)
- [ระบุกฎเกณฑ์สำคัญของธุรกิจ 3-4 ข้อ ตรงนี้]
- 

## ข้อกำหนด

### 1. Domain Layer (`domain/`)

**`domain/entities.py`**
```python
# [ใส่โครงสร้างคลาส Entity หลัก และ Logic สำคัญ]```

**`domain/value_objects.py`**
```python
# [ใส่ Value Objects ที่ต้องใช้เพื่อความสมบูรณ์ของโดเมน]```

**`domain/enums.py`**
```python
# [ใส่ Enum ทั้งหมดที่เกี่ยวข้องกับ Module นี้]```

### 2. Application Layer (`application/`)

**`application/interfaces.py`**
```python
# [กำหนด Protocol/Interface สำหรับ Repository, Cache หรือ Gateway/Publisher]```

**`application/use_cases.py`**
```python
# [ระบุ Use Case หลักที่ต้องการให้เขียน Logic สั่งการ]```

**`application/mappers.py`** — `[ชื่อ]Mapper`
**`application/exceptions.py`** — `[ชื่อ]Exception`
**`application/utils.py`** 

### 3. Infrastructure Layer (`infrastructure/`)

**`infrastructure/models.py`**
```python
# [กำหนด Database Schema / ORM Model โดยใช้คีย์ฟิลด์ที่สอดคล้องกับ Domain]```

**`infrastructure/repositories.py`** — `Postgres[ชื่อ]Repository`
**`infrastructure/caches.py`** — `Redis[ชื่อ]Cache`
**`infrastructure/services.py`** — 

### 4. Presentation Layer (`presentation/`)

**`presentation/routers.py`**
```python
# [ระบุโครงสร้าง API RouterEndpoints และ HTTP Methods]```

**`presentation/schemas.py`** — Pydantic Schemas สำหรับ Input/Output
**`presentation/docs.py`** — Documentation metadata
**`presentation/dependencies.py`** — DI สำหรับ Use Cases

### 5. Error Handling
- Use cases: **3-branch** (Success, Expected Error, Unexpected Error)
- Repositories: **2-branch**
- Caches: **never-raise** (ห้ามพังแอปหากแคชล่ม)

### 6. Invariants (กฎที่ห้ามละเมิด)
- [ระบุกฎเหล็ก 2-3 ข้อที่ระบบต้องเช็กทุกครั้ง]

### 7. Domain Events
- [ระบุชื่อ Event ที่จะถูกสร้างขึ้นเมื่อเกิด Action]

### 8. Tests
```python
# [กำหนดหัวข้อเคสการทำ Unit Test หรือ Property-based test ที่ต้องการ]```

## Output
- ตอบกลับเฉพาะโค้ดของไฟล์โครงสร้างด้านบนเท่านั้น
- เขียนโค้ดเต็ม ไม่ย่อ ไม่ใช้คอมเมนต์ข้ามบรรทัด (`...`)
- เขียนคอมเมนต์ในโค้ด 2 ภาษา (ไทย+อังกฤษ) สไตล์สะอาดกระชับ
```

------------------------------
## ⚡ วิธีสั่ง OpenCode ใน Terminal ให้เร็วขึ้นไปอีก
หลังจากเซตอัปไฟล์โปรเจกต์ตามโครงสร้างนี้แล้ว เวลาที่คุณพิมพ์คุยต่อในแอร์เรียร์งานเดิม (ผ่าน opencode -c) ให้สั่งงานแบบใช้ "ไฟล์ปลายทาง" เป็นตัวล็อก เช่น:

opencode -c "สร้างไฟล์ application/use_cases.py ของโมดูล audit ตามเทมเพลตล่าสุด โดยไม่ต้องพิมพ์ไฟล์ใน layer อื่นซ้ำ"

การระบุเจาะจงแบบนี้ จะช่วยบล็อกไม่ให้ AI พิมพ์โค้ดเก่าในส่วนที่ทำงานเสร็จแล้วซ้ำซ้อน ส่งผลให้ ประหยัดค่า Token และได้ โค้ดส่งกลับมาเร็วขึ้นกว่าเดิมหลายเท่าตัวครับ
คุณต้องการให้ผมลองช่วยเอาเทมเพลตนี้ไปประกอบร่างเขียนตัวอย่างของ Module ถัดไป ตัวไหนเพิ่มไหมครับ? เช่น Module billing (ระบบจ่ายเงิน) หรือ Module inventory (ระบบคลังสินค้า) เพื่อทดสอบความสมบูรณ์ของโครงสร้างระบบคุณ?

