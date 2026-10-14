# 📘 ERP + IoT System Architecture Guide for Food Group Companies
## ( FastAPI Clean Architecture + DDD Template)

> **Complete Document** — Merges the architecture from **ERPIoT** with the **ERP for Food Group Companies (Part 1-2)** and **Smart Mushroom Farm IoT** to create a Multi-company ERP + IoT system that covers every dimension of the food business.

--- 
## ตัวอย่าง การ ออกแบบ แล้วนำมา พัฒนาระบบ  แก้ปัญหา สร้างโอกการ เน้น ใช้งานจริง 
1. Business Model Canvas (BMC) คือ เครื่องมือเชิงกลยุทธ์ในรูปแบบแผนภาพ 1 หน้ากระดาษ ที่ใช้ใช้ออกแบบ วิเคราะห์ และสรุปรูปแบบการดำเนินธุรกิจ คิดค้นโดย Alexander Osterwalder และ Yves Pigneur เพื่อช่วยให้ผู้ประกอบการมองเห็นภาพรวมของธุรกิจทั้งระบบได้อย่างรวดเร็ว โดยไม่ต้องเขียนแผนธุรกิจยาวหลายสิบหน้า
2. Design Thinking  (การคิดเชิงออกแบบ) คือ กระบวนการคิดที่เน้นการทำความเข้าใจ "มนุษย์" หรือผู้ใช้อย่างลึกซึ้ง (Human-Centered) เพื่อแก้ไขปัญหาอย่างสร้างสรรค์และสร้างนวัตกรรมที่ตอบโจทย์ความต้องการที่แท้จริง
 • หัวใจสำคัญไม่ใช่แค่เรื่องความสวยงาม แต่เป็นการมองหา "ทางออก" ที่เป็นรูปธรรม โดยมี 5 ขั้นตอนมาตรฐาน
    1. Empathize (เข้าใจปัญหา): เข้าไปทำความเข้าใจผู้ใช้งานจริงผ่านการสังเกตและพูดคุย เพื่อหาความต้องการที่ซ่อนอยู่ (Insights)
    2. Define (ระบุปัญหา): นำข้อมูลที่ได้มาวิเคราะห์เพื่อสรุป "หัวใจของปัญหา" ให้ชัดเจนว่าเรากำลังจะแก้ปัญหาให้ใคร และเรื่องอะไร
    3. Ideate (ระดมความคิด): เน้นการหาไอเดียใหม่ๆ ให้ได้มากที่สุดโดยไม่มีการปิดกั้น เพื่อหาทางเลือกในการแก้ปัญหาที่หลากหลาย
    4. Prototype (สร้างต้นแบบ): เลือกไอเดียที่ดีที่สุดมาสร้างเป็นแบบจำลองอย่างง่ายที่จับต้องได้ เพื่อนำไปทดลอง
    5. Test (ทดสอบ): นำต้นแบบไปให้ผู้ใช้ทดลองจริง เพื่อรับข้อเสนอแนะและนำกลับมาปรับปรุงจนกว่าจะตอบโจทย์
    ทำไมถึงสำคัญ?
    • แก้ปัญหาได้ตรงจุด: เพราะเริ่มจากความเข้าใจผู้ใช้ ไม่ใช่การเดาเอาเอง
    • ลดความเสี่ยง: การสร้างต้นแบบและทดสอบก่อนช่วยให้เห็นข้อผิดพลาดได้เร็วโดยไม่ต้องเสียเงินทุนจำนวนมาก
    • สร้างนวัตกรรม: กระบวนการนี้ช่วยให้มองเห็นมุมมองใหม่ๆ ที่อาจไม่เคยนึกถึงมาก่อน
3. Ghost Mindset   การทำเพื่อมุ่งมั่นทุ่มเทพัฒนาตนเอง หรือทำงานให้สำเร็จตามเป้าหมาย โดยตัดสิ่งรบกวนจากภายนอกออกไป  
4. Microservices Architecture  (สถาปัตยกรรมแบบไมโครเซอร์วิส) คือรูปแบบการออกแบบซอฟต์แวร์ที่แบ่งระบบขนาดใหญ่ (Monolithic) ออกเป็นบริการย่อย ๆ หลายบริการ (Small Independent Services) โดยแต่ละบริการจะทำงานแยกจากกัน มีหน้าที่เฉพาะเจาะจงของตัวเอง และสามารถพัฒนา ทดสอบ อัปเดต หรือขยายขนาด (Scale) ได้อย่างอิสระ
5. Domain-Driven Design (DDD) คือ แนวคิดหรือกรอบการออกแบบซอฟต์แวร์ที่เน้น "การจำลองธุรกิจและปัญหาของโดเมน (Domain)" ให้มาสะท้อนอยู่ในโครงสร้างของโค้ดและสถาปัตยกรรม แทนที่จะเน้นการคิดจากมุมมองของฐานข้อมูลหรือเทคโนโลยีเป็นหลัก
6. Clean Architecture คือ แนวคิดหรือหลักการออกแบบสถาปัตยกรรมซอฟต์แวร์ (Software Architecture) ที่เสนอโดย Robert C. Martin (Uncle Bob) ซึ่งมีเป้าหมายหลักในการแยกตรรกะทางธุรกิจ (Business Logic) ออกจากเทคโนโลยีภายนอก เช่น ฐานข้อมูล (Database), เฟรมเวิร์ก (Framework), และส่วนติดต่อผู้ใช้ (UI) เพื่อให้ระบบมีความยืดหยุ่น บำรุงรักษาง่าย และทดสอบได้สะดวก
7. Risk Management (การบริหารความเสี่ยง) คือ กระบวนการค้นหา ประเมิน วิเคราะห์ และควบคุมเหตุการณ์หรือความไม่แน่นอนที่อาจเกิดขึ้นในอนาคต เพื่อลดโอกาสเกิดหรือลดความรุนแรงของความเสียหายให้อยู่ในระดับที่องค์กรหรือบุคคลยอมรับได้
8. POC (Proof of Concept) "การพิสูจน์แนวคิด" การทดสอบไอเดียหรือเทคโนโลยีในสเกลเล็กๆ ก่อนเริ่มลงทุนพัฒนาจริง เพื่อดูว่า "แนวคิดนี้จะทำงานได้จริงหรือไม่"
9. Project Management (การบริหารโครงการ) คือ กระบวนการวางแผน การดำเนินงาน การควบคุม และการใช้ทรัพยากรที่มีอยู่ (เช่น บุคลากร เวลา และงบประมาณ) อย่างคุ้มค่า เพื่อให้โครงการบรรลุวัตถุประสงค์ที่กำหนดไว้ภายในเวลาและงบประมาณที่จำกัด
10. Cost Management (การบริหารต้นทุน) คือ กระบวนการวางแผน ประมาณการ จัดทำงบประมาณ ควบคุม ติดตาม และวิเคราะห์ค่าใช้จ่ายต่างๆ ภายในโครงการหรือองค์กร เพื่อให้สามารถใช้ทรัพยากรที่มีอยู่ได้อย่างคุ้มค่า มีประสิทธิภาพสูงสุด และสร้างผลกำไรหรือความได้เปรียบในการแข่งขัน
11. KPI ย่อมาจาก Key Performance Indicator หรือแปลเป็นไทยว่า “ดัชนีชี้วัดผลงาน” คือ เครื่องมือที่ใช้วัดและประเมินประสิทธิภาพการทำงานของบุคคล ทีม หรือองค์กร ว่าสามารถบรรลุเป้าหมายหรือผลลัพธ์ที่กำหนดไว้ได้มากน้อยเพียงใด
ความหมายของแต่ละคำใน KPI มีดังนี้

• K = Key (เป้าหมายหลัก หรือหัวใจสำคัญ)
• P = Performance (ประสิทธิภาพ หรือผลลัพธ์ในการทำงาน)
• I = Indicator (ดัชนี หรือตัวชี้วัดที่ออกมาเป็นรูปธรรม)

> ประเภทของ KPI
1. เชิงปริมาณ (Quantitative / Direct): วัดผลออกมาเป็นตัวเลขชัดเจน เช่น ยอดขาย (บาท), จำนวนชิ้นงาน, จำนวนลูกค้า
2. เชิงคุณภาพ (Qualitative / Indirect): วัดผลจากความคิดเห็นหรือระดับความพึงพอใจ เช่น ความพึงพอใจของลูกค้า, ทักษะการทำงานเป็นทีม
ระดับของ KPI ในองค์กร

- ระดับองค์กร (Corporate): วัดภาพรวมความสำเร็จของบริษัท เช่น กำไรสุทธิ, ส่วนแบ่งทางการตลาด
- ระดับแผนก/หน่วยงาน (Department): วัดผลงานเฉพาะส่วน เช่น ยอดขายของทีมการตลาด, ความถูกต้องของบัญชี
- ระดับบุคคล (Individual): วัดผลงานของพนักงานแต่ละคน เพื่อใช้ประกอบการประเมินผลงาน โบนัส และการปรับเงินเดือน
- หลักการตั้ง KPI ที่ดี (SMART)
- การกำหนดตัวชี้วัดควรใช้หลัก SMART เพื่อให้ใช้งานได้จริง:
- Specific (เจาะจง ชัดเจน)
- Measurable (วัดผลเป็นตัวเลขได้)
- Achievable (เป็นไปได้จริง ไม่เกินกำลังเกินไป)
- Relevant (มีความเกี่ยวข้องกับเป้าหมายหลัก)
- Time-bound (มีกำหนดเวลาที่ชัดเจน เช่น ภายใน 3 เดือน หรือสิ้นปี)

12. CRM ย่อมาจาก Customer Relationship Management หรือ การบริหารความสัมพันธ์กับลูกค้า ซึ่งหมายถึงทั้ง "กลยุทธ์" ในการดูแลลูกค้า และ "ระบบซอฟต์แวร์" ที่ใช้เก็บข้อมูลและจัดการปฏิสัมพันธ์กับลูกค้า เพื่อสร้างความสัมพันธ์ระยะยาวและเพิ่มยอดขาย
13. ERP (Enterprise Resource Planning) คือ ระบบซอฟต์แวร์สำหรับบริหารจัดการและวางแผนทรัพยากรทางธุรกิจขององค์กร โดยรวบรวมข้อมูลและกระบวนการทำงานหลักจากทุกแผนกเข้าไว้บนฐานข้อมูลกลางเดียวกัน เพื่อให้ทุกคนทำงานร่วมกันและเห็นข้อมูลแบบเรียลไทม์



# 00 — สรุปธุรกิจแบบคลุมเครือ (Blind Input)

> สรุปนี้เป็น blind input สำหรับกรณีตรวจสอบ เนื้อหาอธิบายเฉพาะสถานการณ์ทางธุรกิจ บทบาท เป้าหมาย ข้อจำกัด และสถานการณ์ผิดปกติเท่านั้น
> **ถูกตัดออก**: DDD ทุกคำศัพท์ (Aggregate, Bounded Context, Entity, Value Object, Event, ACL เป็นต้น) และชื่อคลาส/การตัดสินใจออกแบบใดๆ

---

บริษัทประกันทรัพย์สินขนาดกลางกำลังดำเนินการแปลงระบบดิจิทัลสำหรับธุรกิจหลักด้านการรับประกันภัยและการเรียกร้องค่าสินไหมทดแทน ปัจจุบันสองกระบวนการนี้พึ่งพาแบบฟอร์มและการส่งต่อด้วยมือเป็นอย่างมาก ส่งผลให้ข้อมูลขาดความต่อเนื่องอย่างรุนแรง: ผู้รับประกันภัยไม่สามารถเห็นประวัติลูกค้าที่สมบูรณ์และผลงานการเรียกร้องค่าสินไหมทดแทนที่ผ่านมา พนักงานเรียกร้องค่าสินไหมทดแทนไม่ได้รับข้อมูลเงื่อนไขกรมธรรม์ที่แม่นยำ และฝ่ายบริหารไม่สามารถติดตามสถานะ "แจ้งเหตุแล้วยังไม่จ่ายค่าสินไหม" แบบเรียลไทม์ได้

## สถานการณ์ธุรกิจปัจจุบัน

- **ลูกค้าและการประกันภัย**: ลูกค้า (บุคคลและนิติบุคคล บางส่วนผ่านบริษัทนายหน้า) ยื่นคำขอประกันภัย ระบุวัตถุที่เอาประกัน (ยานพาหนะ ทรัพย์สิน สินค้า) วงเงินประกันที่ต้องการ ระยะเวลาประกัน และประวัติความสูญเสียที่ผ่านมา ลูกค้ารายเดียวกันอาจมีหลายกรมธรรม์และหลายวัตถุที่เอาประกัน
- **การตัดสินใจรับประกันภัย**: ผู้รับประกันภัยตัดสินใจรับประกันภัย เพิ่มเบี้ยประกัน กำหนดเงื่อนไขเพิ่มเติม หรือปฏิเสธ โดยพิจารณาจากเนื้อหาคำขอ ผลงานการเรียกร้องค่าสินไหมทดแทนของลูกค้าในอดีต และแนวทางการรับประกันภัยของบริษัท วัตถุที่เอาประกันความเสี่ยงสูงอาจต้องขอความช่วยเหลือจากการประกันต่อ
- **วงจรชีวิตกรมธรรม์**: หลังจากกรมธรรม์มีผลบังคับ ลูกค้าสามารถขอแก้ไข (เพิ่มวงเงินประกัน เปลี่ยนที่อยู่ เพิ่มวัตถุที่เอาประกัน) ประกันบางประเภทต่ออายุโดยอัตโนมัติทุกปี ลูกค้าที่ไม่ชำระเบี้ยประกันตรงเวลาอาจส่งผลให้กรมธรรม์ระงับ หลังระงับหากเกิดเหตุจะไม่จ่ายค่าสินไหม กรมธรรม์มีระยะเวลาคอย (หากเกิดเหตุภายในไม่กี่วันหลังออกกรมธรรม์จะไม่จ่าย) และค่า deductible (หากความสูญเสียต่ำกว่าจำนวนนี้จะไม่จ่าย)
- **กระบวนการเรียกร้องค่าสินไหมทดแทน**: หลังเกิดเหตุ ลูกค้าแจ้งเหตุ พนักงานเรียกร้องค่าสินไหมทดแทนจัดการตรวจสอบ (ภาพถ่ายออนไลน์หรือลงพื้นที่จริง) ประเมินจำนวนเงินความสูญเสียและความรับผิดชอบ เปรียบเทียบกับเงื่อนไขกรมธรรม์ (ค่า deductible ความรับผิดชอบที่ยกเว้น ระยะเวลาคอย) คำนวณจำนวนเงินที่ต้องจ่าย จ่ายหลังการอนุมัติเป็นขั้นตอน คดีที่มีข้อสงสัยเรื่องการทุจริตจะเข้าสู่กระบวนการสอบสวน ระหว่างสอบสวนจะระงับการจ่าย หลังจ่ายค่าสินไหมเสร็จสิ้นอาจไล่เบี้ยเรียกคืนจากฝ่ายที่รับผิดชอบ
- **การกำกับดูแลและการเงิน**: ข้อมูลกรมธรรม์และเรียกร้องค่าสินไหมทดแทนต้องส่งให้หน่วยงานกำกับดูแลตามระเบียบ เงินสำรองค่าสินไหมรอตัดบัญชีต้องคำนวณตามวิธีที่กฎหมายกำหนด ฝ่ายบริหารต้องการมุมมองแบบเรียลไทม์เพื่อติดตามขนาดและการกระจายของเหตุที่แจ้งแล้วยังไม่จ่ายค่าสินไหม

## สถานการณ์ผิดปกติ (โลกจริง)

- **ภัยพิบัติร้ายแรง**: พายุ ฝนตกหนัก และภัยธรรมชาติอื่นๆ ส่งผลให้จำนวนแจ้งเหตุเพิ่มขึ้นหลายเท่าในช่วงสั้นๆ แรงกดดันในการจ่ายค่าสินไหมเพิ่มขึ้นอย่างรวดเร็ว ระบบต้องรับมือกับการแจ้งเหตุจำนวนมากพร้อมกัน
- **แจ้งเหตุซ้ำและเท็จ**: ความสูญเสียเดียวกันถูกแจ้งหลายครั้ง หรือลูกค้าขยายความสูญเสียเกินจริง ต้องมีการระบุและรวมเข้าด้วยกัน
- **ข้อมูลมาช้า**: รายงานการตรวจสอบ ใบรับรองตำรวจ และเอกสารอื่นๆ มักมาล่าช้า กระบวนการเรียกร้องค่าสินไหมทดแทนต้องรอเอกสารให้ครบ บางแจ้งเหตุขาดข้อมูลสำคัญ (วัตถุที่เอาประกัน เวลา)
- **สถานะกรมธรรม์ขัดแย้ง**: เมื่อคำขอแก้ไขและการแจ้งเหตุเกิดขึ้นพร้อมกัน จะเกิดข้อผิดพลาดง่ายๆ ว่าจะยึดเงื่อนไขสถานะใด
- **การสอบสวนทุจริต**: ระหว่างการสอบสวน เรียกร้องค่าสินไหมจะถูกระงับ ผลการสอบสวนอาจพลิกผลการจ่ายค่าสินไหม

## เป้าหมาย

ทำให้กระบวนการรับประกันภัยและเรียกร้องค่าสินไหมทดแทนทั้งหมดเป็นดิจิทัล สร้างฐานข้อมูล "ลูกค้า—กรมธรรม์—เรียกร้องค่าสินไหม" ที่เป็นหนึ่งเดียว สนับสนุนการตัดสินใจรับประกันภัย กระบวนการเรียกร้องค่าสินไหมทดแทน ขั้นตอนอนุมัติ และการส่งข้อมูลให้หน่วยงานกำกับดูแล รวมทั้งให้ฝ่ายบริหารติดตามขนาดเรียกร้องค่าสินไหมรอตัดบัญชีแบบเรียลไทม์

## ไม่ใช่เป้าหมาย

- ไม่เกี่ยวข้องกับแบบจำลองคณิตศาสตร์ประกันภัยสำหรับการกำหนดอัตราเบี้ยประกันเอง (ถือว่าระบบคณิตศาสตร์ประกันภัยภายนอกให้อัตรา)
- ไม่เกี่ยวข้องกับการลงทุนและการใช้เงิน
- ไม่แทนที่ระบบฝั่งบริษัทนายหน้า (ถือว่ามีปฏิสัมพันธ์ผ่าน API)
- ไม่ครอบคลุมกระบวนการประกันชีวิต ประกันสุขภาพ

## ข้อจำกัด

- ต้องปฏิบัติตามข้อกำหนดของหน่วยงานกำกับดูด้านการส่งข้อมูลและการคำนวณเงินสำรอง
- การจ่ายค่าสินไหมทดแทนต้องมีการอนุมัติหลายขั้น จำนวนเงินมากต้องมีอำนาจสูงกว่า
- ช่องทางแจ้งเหตุต้องรองรับการเข้าใช้งานจำนวนมากพร้อมกัน และห้ามสูญเสียแจ้งเหตุในช่วงเวลาเร่งด่วน

---

## Table of Contents

1. [Definitions](#1-definitions)
2. [Topics](#2-topics)
3. [Operating Structure](#3-operating-structure)
4. [Objectives](#4-objectives)
5. [Target Groups](#5-target-groups)
6. [Prerequisites](#6-prerequisites)
7. [Introduction](#7-introduction)
8. [Folder Structure: app/modules](#8-folder-structure-appmodules)
9. [Core Concepts](#9-core-concepts)
10. [Workflow and Dataflow](#10-workflow-and-dataflow)
11. [Case Studies](#11-case-studies)
12. [AI Prompt Template (template_modules.md)](#12-ai-prompt-template)
13. [AI Prompt per Module](#13-ai-prompt-per-module)
14. [Module Checklist](#14-module-checklist)
15. [Security Code](#15-security-code)
16. [Load Test (Development)](#16-load-test-development)
17. [Summary](#17-summary)
18. [Git Flow / Code Review / CI-CD](#18-git-flow--code-review--cicd)
19. [Root Cause Analysis](#19-root-cause-analysis)

---


## 1. Definitions

| Term | Meaning |
|---|---|
| **Clean Architecture** | An architecture that separates code into Domain, Application, Infrastructure, and Presentation layers, with dependencies always pointing inward |
| **DDD (Domain-Driven Design)** | Software design based on the real business domain, using Entities, Value Objects, Aggregates, and Domain Events |
| **Multi-company (Multi-tenant)** | One system serving multiple legal entities, with data isolated via Schema-per-Tenant |
| **Money Path** | The money trail: Order → Invoice → Ledger → Outbox → Cloud → Reconciliation |
| **Goods Path** | The goods trail: PO → Receive → Lot → Store → Issue → Produce → Ship → Sell |
| **Data Path** | The data trail: Sensor/RFID/GPS/POS → Kafka → Stream → OLAP → BI/KPI |
| **Idempotency** | The property that repeated calls produce the same result, preventing double-charges |
| **Outbox Pattern** | Write to the DB first, then sync with external systems via an outbox table |
| **FEFO/FIFO** | First-Expired-First-Out / First-In-First-Out stock rotation |
| **Traceability** | The ability to track products from farm → factory → store → customer |
| **Reconciliation** | The process of matching money/goods with the accounting system |
| **Saga Pattern** | Managing distributed transactions through a sequence of local transactions + compensating actions |
| **Domain Event** | An event in the domain, e.g., InvoiceIssued, StockLow, BatchCompleted |
| **Value Object** | An object without identity, e.g., Money, Email, Address |
| **Aggregate** | A group of Entities managed as a single unit |
| **MQTT** | A publish/subscribe messaging protocol suited to IoT |
| **Digital Twin** | A virtual model of a factory/farm used for simulation before real-world deployment |
| **KPI** | Key Performance Indicator, e.g., Gross margin, Waste %, NPS |
| **RCA** | Root Cause Analysis |

---

## 2. Topics

### 2.1 Operating Structure
The system is divided into **8 Layers** per ERP-Part-1-2:

| Layer | Name | Modules |
|---|---|---|
| **0** | Core (cross-cutting) | money, tenant_context, audit, idempotency, config, events |
| **1** | Foundation | tenancy, authentication, user, employee, customer, supplier, product, pricing |
| **2** | Money Path | order, invoice, ledger, payment, accounting_gateway, tax, reconciliation |
| **3** | Goods Path | inventory, warehouse, lot, production, recipe, quality, waste, procurement, traceability |
| **4** | Operations | transport, delivery, route, gps, retail, pos, shift, line_channel, promotion, loyalty |
| **5** | Intelligence | reporting, analytics, forecast, kpi, satisfaction, recommendation |
| **6** | Monitoring & Sensing | iot, cctv, monitoring, backup, alerting, audit_viewer |
| **7** | Templates | health, example, blank |

### 2.2 Objectives
- Build a central ERP (Multi-company) for a food group
- Support 3 main paths: Money Path, Goods Path, Data Path
- Connect IoT + Automation + AI for processing plants and farms
- Provide end-to-end Traceability (QR/RFID/GPS)
- Deliver reports and KPIs at every level (Daily → 5Y)
- Extend to affiliated companies (Multi-tenant)

### 2.3 Target Groups
- Owners of food group companies
- Factory/store/transport managers
- Accounting/finance teams
- IT teams and developers
- Data analysts
- Frontline staff (POS, warehouse, production)

### 2.4 Prerequisites
- Python 3.14+, FastAPI, Pydantic v2
- Clean Architecture + DDD
- PostgreSQL, Redis, Kafka
- MQTT, IoT protocols
- Machine Learning (LSTM, YOLO, XGBoost)
- Docker, CI/CD, Git Flow

### 2.5 Content Overview
This ERP system extends **ERPIoT**, which has 9 modules, 23 routes, and 7 tables, by adding **55 modules** per ERP-Part-1-2, covering every dimension of the food business — money, goods, production, transport, retail, traceability, analytics, people, customers, KPIs, config, and audit.

---

## 3. Operating Structure

### 3.1 Four-Layer Architecture (from the Template)

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  routers · schemas · docs · dependencies                    │
│  (payload → mapper → use case → mapper → return)           │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    APPLICATION LAYER                         │
│  use_cases · interfaces (Protocol) · mappers · exceptions   │
│  (business rules live here)                                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                      DOMAIN LAYER                           │
│  entities · value_objects · enums · domain events           │
│  (imports shared only — NO framework)                       │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                  INFRASTRUCTURE LAYER                        │
│  models (SQLAlchemy) · repositories · caches · services     │
│  (flush() never commit())                                    │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Module Structure (4 Layers × 4 Files)

```
app/modules/{module}/
├── domain/
│   ├── entities.py          # Dataclasses extending BaseEntity
│   ├── value_objects.py     # Plain classes: _normalize → _validate
│   └── enums.py             # (str, Enum)
├── application/
│   ├── interfaces.py        # Protocol contracts
│   ├── use_cases.py         # One {Module}UseCases class
│   ├── mappers.py           # ENTITY/DTOS · ENTITY/MODELS · ENTITY/CACHE
│   ├── exceptions.py        # {Module}Exception + one per rule
│   └── utils.py             # Module-local helpers
├── infrastructure/
│   ├── models.py            # SQLAlchemy extending BaseModel
│   ├── repositories.py      # Postgres{Entity}Repository — flush()
│   ├── caches.py            # Redis{Entity}Cache — never raises
│   └── services.py          # External systems behind Protocol
└── presentation/
    ├── routers.py           # payload → mapper → use case → mapper
    ├── schemas.py           # Pydantic v2 with full Field + ConfigDict
    ├── docs.py              # router_docs + {action}_docs
    └── dependencies.py      # Depends factories
```

```sh
    backend/
    │
    ├── app/                                   # 📦 แอปพลิเคชันหลัก
    │   │
    │   ├── __init__.py
    │   ├── app.py                             # Entry point — FastAPI()
    │   ├── routes.py                          # Router registration
    │   ├── middleware.py                      # Middleware registration
    │   │
    │   ├── core/                              # ⚙️ Cross-cutting concerns
    │   │   ├── __init__.py
    │   │   ├── settings.py                    # Settings (pydantic-settings)
    │   │   ├── security.py                    # Nested JWT (JWS + JWE)
    │   │   ├── database.py                    # SQLAlchemy async engine
    │   │   ├── cache.py                       # Redis client
    │   │   ├── logging.py                     # Loguru + orjson
    │   │   ├── middleware.py                  # ResponseFormatting, LogRequest, DeviceId
    │   │   └── exceptions.py                  # CoreException
    │   │
    │   └── modules/                           # 📚 9 modules (ตาม README)
    │       │
    │       ├── shared/                        # 🔗 Base types (ไม่ routed)
    │       │   ├── domain/
    │       │   │   ├── entities.py            # BaseEntity, DomainError, Pagination
    │       │   │   ├── value_objects.py       # UNSET, Email, Name, Phone
    │       │   │   └── enums.py               # Role, ResponseMessages, SortOrder
    │       │   ├── application/
    │       │   │   ├── use_cases.py           # SharedUseCases
    │       │   │   ├── exceptions.py          # StandardException, DomainException
    │       │   │   └── utils.py               # BRASILIA_TZ, resolve_client_ip
    │       │   ├── infrastructure/
    │       │   │   └── models.py              # Base, BaseModel
    │       │   └── presentation/
    │       │       ├── schemas.py             # StandardResponse, Pagination*
    │       │       └── dependencies.py        # Cross-module factories
    │       │
    │       ├── authentication/                # 🔐 Login/Refresh/Logout
    │       │   ├── domain/
    │       │   │   ├── entities.py            # Authentication
    │       │   │   ├── value_objects.py
    │       │   │   └── enums.py
    │       │   ├── application/
    │       │   │   ├── interfaces.py          # ITokenService
    │       │   │   ├── use_cases.py
    │       │   │   ├── mappers.py
    │       │   │   ├── exceptions.py
    │       │   │   └── utils.py
    │       │   ├── infrastructure/
    │       │   │   ├── models.py              # Authentication, RefreshToken, AccessToken
    │       │   │   ├── repositories.py
    │       │   │   ├── caches.py
    │       │   │   └── services.py            # TokenService
    │       │   └── presentation/
    │       │       ├── routers.py
    │       │       ├── schemas.py
    │       │       ├── docs.py
    │       │       └── dependencies.py
    │       │
    │       ├── user/                          # 👤 Accounts + Roles
    │       │   ├── domain/
    │       │   ├── application/
    │       │   ├── infrastructure/
    │       │   └── presentation/
    │       │
    │       ├── key/                           # 🔑 API Keys (canonical)
    │       │   ├── domain/
    │       │   ├── application/
    │       │   ├── infrastructure/
    │       │   └── presentation/
    │       │
    │       ├── knowledge/                     # 📚 CRUD + Broadcast
    │       │   ├── domain/
    │       │   ├── application/
    │       │   ├── infrastructure/
    │       │   └── presentation/
    │       │
    │       ├── notification/                  # 🔔 Role fan-out
    │       │   ├── domain/
    │       │   ├── application/
    │       │   ├── infrastructure/
    │       │   └── presentation/
    │       │
    │       ├── websocket/                     # 🔌 Real-time
    │       │   ├── application/
    │       │   ├── infrastructure/
    │       │   └── presentation/
    │       │
    │       ├── health/                        # ❤️ Liveness
    │       │   └── presentation/
    │       │
    │       └── example/                       # 📝 Minimal reference
    │           └── presentation/
    │
    ├── migrations/                            # 🗄️ Alembic
    │   ├── env.py                             # ⚠️ ต้อง import ทุก model
    │   ├── script.py.mako
    │   └── versions/                          # (empty)
    │
    ├── scripts/                               # 🛠️ Utility scripts
    │   ├── create_module.py
    │   ├── generate_secret.py
    │   ├── generate_fernet.py
    │   ├── directory_tree.py
    │   ├── websocket_test.html
    │   └── asyncapi.yaml
    │
    ├── secrets/keys/                          # 🔐 JWT keys (gitignored)
    │   ├── signing-private.pem
    │   ├── signing-public.pem
    │   ├── encryption-private.pem
    │   └── encryption-public.pem
    │
    ├── test/                                  # 🧪 Tests
    │   ├── core/
    │   └── modules/
    │       ├── authentication/
    │       ├── example/
    │       ├── health/
    │       ├── key/
    │       ├── knowledge/
    │       ├── notifications/
    │       ├── shared/
    │       ├── user/
    │       └── websocket/
    │
    ├── docs/                                  # 📘 Postman + specs
    │   └── postman_collection.json
    │
    ├── .env.example
    ├── .gitignore
    ├── .python-version
    ├── alembic.ini
    ├── docker-compose.yaml                    # FastAPI stack (standalone)
    ├── Dockerfile
    ├── Makefile
    ├── pyproject.toml
    ├── requirements.txt
    ├── README.md
    └── README-PTBR.md
```

```text
<3>WSL (70293 - Relay) ERROR: CreateProcessCommon:818: execvpe(/bin/bash) failed: No such file or directory
```

### 3.3 Three Error-Handling Shapes

| Shape | Used In | Branches |
|---|---|---|
| **3-branch** | Use cases + router handlers | `StandardException → DomainException → Exception` |
| **2-branch** | Repositories + services | `StandardException → Exception` |
| **Never-raise** | Caches | catch → log → return `None` |

---

## 4. Objectives (Detailed)

1. **Centralize data** — 5 legal entities, 3+ branches, one ERP
2. **Money stability** — Money recon discrepancy = 0, no duplicate invoices, correct VAT
3. **Goods stability** — Stock accuracy ≥ 99%, Lot traceability 100%
4. **Traceability** — Forward: lot → shipment → customer; Backward: customer → lot → supplier
5. **Automation** — Auto-control fans/misters/lights based on sensor values
6. **Forecasting** — Demand forecast MAPE < 20%
7. **KPI** — At every level (Company/Branch/Team/Individual)
8. **Scalability** — Multi-tenant for affiliated companies

---

## 5. Target Groups (Detailed)

| Group | Needs | Modules Used |
|---|---|---|
| Owners | Profit/loss overview | reporting, analytics, kpi |
| Factory managers | Production, yield, waste | production, recipe, quality |
| Store managers | Sales, stock, shifts | pos, retail, inventory |
| Accounting teams | Invoices, ledger, VAT | invoice, ledger, tax |
| Transport teams | Routes, GPS, POD | transport, route, gps |
| Analysts | Forecast, trends | forecast, analytics |
| Frontline staff | Daily operations | pos, shift, inventory |
| B2B/B2C customers | Ordering, tracking | order, line_channel, loyalty |

---

## 6. Prerequisites

| Topic | Details | Learning Resource |
|---|---|---|
| Python 3.14+ | Syntax, async/await, type hints | python.org |
| FastAPI | Routing, DI, middleware | fastapi.tiangolo.com |
| Pydantic v2 | Schema, validation | docs.pydantic.dev |
| SQLAlchemy 2.0 | ORM, async | sqlalchemy.org |
| Clean Architecture | Dependency inversion | Uncle Bob |
| DDD | Entity, VO, Aggregate | Eric Evans |
| PostgreSQL 17 | Schema, JSONB | postgresql.org |
| Redis 8 | Cache, pub/sub | redis.io |
| Kafka | Event streaming | kafka.apache.org |
| MQTT | IoT messaging | mqtt.org |

---

## 7. Introduction

**ERPIoT** is a template unlike any other — it doesn't just give you empty folders and a diagram, it gives you a **working application** with cookie-based authentication using nested JWTs, API-key management with rotation, two-layer RBAC, Redis cache-aside with tombstone invalidation, real-time WebSocket, notifications with role fan-out, and a Docker stack that migrates itself on boot. It has **9 modules, 23 routes, 7 tables** — all following the same pattern you can copy for the 10th module.

**ERP-Part-1-2** extends this template to **55 modules** covering every dimension of the food business — Money Path, Goods Path, Data Path — with Traceability (QR/RFID/GPS), IoT, AI Forecast, KPI, and Multi-tenant roll-out.

**IoT Design** adds the **Data Acquisition → Connectivity → Data Platform → AI & Analytics → Automation & Control** layers for smart mushroom farms using DHT22, MH-Z19B sensors, RGB/Thermal cameras, MQTT, Kafka, InfluxDB, LSTM, YOLOv8, and Reinforcement Learning.

This combined system answers the needs of **food group companies** that want a central ERP + IoT + AI spanning upstream (farm), midstream (processing plant), and downstream (retail/transport/customer).

---

## 8. Folder Structure: app/modules

### 8.1 Original Structure (from the Template)

```
app/modules/
├── shared/           # Base types: BaseEntity, BaseModel, SharedUseCases
├── authentication/   # Login, refresh, logout; nested JWT
├── user/             # Internal accounts and roles
├── key/              # API keys — canonical reference
├── knowledge/        # CRUD + broadcast notification
├── notification/     # Per-user and role fan-out
├── websocket/        # Real-time delivery
├── health/           # Liveness and Alembic version
└── example/          # Minimal reference module
```

### 8.2 New Structure (from ERP-Part-1-2) — 55 Modules

```
app/modules/
│
├── shared/                          # Base types (not routed)
│
├── LAYER 0: CORE (cross-cutting)
│   ├── money/                       # Decimal primitive, VAT
│   ├── tenant_context/              # Multi-company context
│   ├── audit/                       # Append-only log
│   ├── idempotency/                 # Retry-safe operations
│   ├── config/                      # VAT, waste%, pricing rules
│   ├── events/                      # Domain event bus
│   └── security/                    # Auth, RBAC
│
├── LAYER 1: FOUNDATION
│   ├── tenancy/                     # Multi-company provisioning
│   ├── authentication/              # Login, refresh, logout
│   ├── user/                        # Internal accounts
│   ├── employee/                    # Employees + shift
│   ├── customer/                    # B2B/B2C
│   ├── supplier/                    # Procurement
│   ├── product/                     # Products + barcode
│   └── pricing/                     # Multi-tier pricing
│
├── LAYER 2: MONEY PATH
│   ├── order/                       # Order origin
│   ├── invoice/                     # Invoice (core)
│   ├── ledger/                      # Accounting
│   ├── payment/                     # Payment
│   ├── accounting_gateway/          # Cloud sync
│   ├── tax/                         # VAT, WHT
│   └── reconciliation/              # Audit engine
│
├── LAYER 3: GOODS PATH
│   ├── inventory/                   # Stock
│   ├── warehouse/                   # Warehouse
│   ├── lot/                         # Lot/Expiry
│   ├── production/                  # Production
│   ├── recipe/                      # Recipe/BOM
│   ├── quality/                     # QC
│   ├── waste/                       # Waste
│   ├── procurement/                 # PO, receive
│   └── traceability/                # QR/RFID
│
├── LAYER 4: OPERATIONS
│   ├── transport/                   # Shipment, carrier
│   ├── delivery/                    # POD, signature
│   ├── route/                       # Route planning
│   ├── gps/                         # Real-time tracking
│   ├── retail/                      # Store, branch
│   ├── pos/                         # Sale, return, void
│   ├── shift/                       # Shift, cash drawer
│   ├── line_channel/                # LINE webhook
│   ├── promotion/                   # Discount, bundle
│   └── loyalty/                     # Member, points
│
├── LAYER 5: INTELLIGENCE
│   ├── reporting/                   # D/W/M/Q/Y/3Y/5Y
│   ├── analytics/                   # Sales, customer, profit
│   ├── forecast/                    # Demand, production
│   ├── kpi/                         # Company/Branch/Team
│   ├── satisfaction/                # NPS, CSAT
│   └── recommendation/              # Recommender
│
├── LAYER 6: MONITORING & SENSING
│   ├── iot/                         # MQTT, temp/humidity
│   ├── cctv/                        # Camera footage
│   ├── monitoring/                  # Health, metrics
│   ├── backup/                      # Per-schema pg_dump
│   ├── alerting/                    # LINE, email
│   └── audit_viewer/                # Audit log viewer
│
└── LAYER 7: TEMPLATES
    ├── health/                      # Liveness
    ├── example/                     # Minimal demo
    └── blank/                       # Template
```

### 8.3 Standard Module Structure (4 Layers)

```
app/modules/{module}/
├── domain/
│   ├── entities.py          # Dataclasses extending BaseEntity
│   ├── value_objects.py     # Plain classes
│   └── enums.py             # (str, Enum)
├── application/
│   ├── interfaces.py        # Protocol contracts
│   ├── use_cases.py         # {Module}UseCases
│   ├── mappers.py           # ENTITY/DTOS · ENTITY/MODELS · ENTITY/CACHE
│   ├── exceptions.py        # {Module}Exception
│   └── utils.py             # Helpers
├── infrastructure/
│   ├── models.py            # SQLAlchemy extending BaseModel
│   ├── repositories.py      # Postgres{Entity}Repository — flush()
│   ├── caches.py            # Redis{Entity}Cache — never raises
│   └── services.py          # External systems
└── presentation/
    ├── routers.py           # payload → mapper → use case → mapper
    ├── schemas.py           # Pydantic v2
    ├── docs.py              # router_docs + {action}_docs
    └── dependencies.py      # Depends factories
```

---

## 9. Core Concepts

### 9.1 Twelve Design Principles

```
[1]  Money is Domain Invariant — Decimal + transaction + read-back
[2]  Read-Back Verification — write then read back to compare before commit
[3]  Idempotency Everywhere on Money/Goods Path
[4]  Append-Only Audit — INSERT only
[5]  Schema-Per-Tenant — isolate companies at the PostgreSQL schema level
[6]  Outbox for External Sync — write DB first, then sync to cloud
[7]  Reversible Ledger — never delete an entry; use reversal
[8]  Observable by Default — log + money/goods-path probe
[9]  Lot Traceability — every lot must be traceable forward + backward
[10] FEFO/FIFO by Default — stock must rotate by expiry/receipt
[11] Event-Driven for Analytics — use Kafka/outbox for BI/KPI
[12] Config over Code — VAT, waste%, pricing must be config, not hardcoded
```

### 9.2 Cross-cutting Invariants

| Invariant | Scope | Verified By |
|---|---|---|
| Invoice total = sum(lines) + VAT | Money | Money VO + test |
| sum(debit) = sum(credit) | Ledger | Domain invariant |
| Stock in − Stock out = Stock on hand | Inventory | Reconciliation |
| Σ(lot.qty) = Σ(movement.qty) | Inventory | Reconciliation |
| Batch input = output + waste | Production | Yield check |
| Shipment contents = Invoice contents | Transport | Dispatch check |
| KPI actual = Σ(source events) | KPI | Aggregation check |
| Every action touching money/stock → audit log | All modules | Middleware |

### 9.3 Three Error-Handling Shapes

```python
# ===== 3-branch: use cases and router handlers =====
try:
    ...
except StandardException:
    raise  # Must come first — StandardException extends HTTPException
except DomainError as e:
    raise DomainException(e)  # Convert domain error to HTTP error
except Exception as e:
    logger.opt(exception=e).error("An error occurred in the create key endpoint.")
    raise KeyException()

# ===== 2-branch: repositories and services (no domain rule evaluation) =====
try:
    ...
except StandardException:
    raise
except Exception as e:
    logger.opt(exception=e).error("An error occurred in the create key repository.")
    raise KeyException()

# ===== Never-raise: caches (catch → log → return None) =====
try:
    ...
except Exception as e:
    logger.opt(exception=e).error(
        "An error occurred in the get key by hashed key cache. Falling back to the database."
    )
    return None
```

```text
C:\Users\kongn\AppData\Local\Temp\md-notebook\md_notebook.py:2: SyntaxWarning: "\g" is an invalid escape sequence. Such sequences will not work in the future. Did you mean "\\g"? A raw string is also an option.
  sys.path.append("c:\github\fastapicleanarchitectureddd")
  File "C:\Users\kongn\AppData\Local\Temp\md-notebook\md_notebook.py", line 3
    sys.path.append("C:\Users\kongn\AppData\Local\Temp\md-notebook")
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
SyntaxError: (unicode error) 'unicodeescape' codec can't decode bytes in position 2-3: truncated \UXXXXXXXX escape
```

### 9.4 Three Error-Handling Shapes (Table)

| Shape | Used In | Branches | Principle |
|---|---|---|---|
| **3-branch** | Use cases, routers | 3 | `StandardException → DomainError → Exception` |
| **2-branch** | Repositories, services | 2 | `StandardException → Exception` |
| **Never-raise** | Caches | 1 | catch → log → return `None` |

> ⚠️ **`except StandardException` must come first** because `StandardException` extends `HTTPException` — wrong ordering swallows 404/409 into 500.

---

## 10. Workflow and Dataflow

### 10.1 Money Path

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│  Order  │───▶│ Invoice │───▶│ Ledger  │───▶│ Outbox  │───▶│ Cloud   │
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
                                                                   │
                    ┌──────────────────────────────────────────────┘
                    ▼
             ┌──────────────┐
             │Reconciliation│
             └──────────────┘
```

**Rules:** Idempotency · DB Transaction · Domain Invariant · Audit · Read-Back

### 10.2 Goods Path

```
┌─────┐   ┌─────────┐   ┌─────┐   ┌───────┐   ┌───────┐   ┌─────────┐   ┌──────┐   ┌──────┐
│ PO  │──▶│ Receive │──▶│ Lot │──▶│ Store │──▶│ Issue │──▶│ Produce │──▶│ Ship │──▶│ Sell │
└─────┘   └─────────┘   └─────┘   └───────┘   └───────┘   └─────────┘   └──────┘   └──────┘
```

**Rules:** FEFO/FIFO · Lot traceability · Cold-chain · Cycle count

### 10.3 Data Path

```
┌──────────────────┐   ┌───────┐   ┌─────────────────┐   ┌───────┐   ┌────────┐
│Sensor/RFID/GPS/  │──▶│ Kafka │──▶│Stream Processor │──▶│ OLAP  │──▶│BI/KPI  │
│POS               │   └───────┘   │   (Flink)       │   └───────┘   └────────┘
└──────────────────┘               └─────────────────┘
```

**Rules:** At-least-once · Dedup · Time-window · Late data handling

### 10.4 Dataflow Diagram (IoT + ERP Integration)

```
┌──────────┐   MQTT    ┌──────────┐   produce   ┌──────────┐
│ Sensors  │──────────▶│ Gateway  │────────────▶│  Kafka   │
│ (DHT22,  │           │ (RPi)    │             │  Topic   │
│  CO₂,pH) │           └──────────┘             └────┬─────┘
└──────────┘                                         │ consume
                                                     ▼
┌──────────┐   query   ┌──────────┐   write    ┌──────────┐
│Grafana/  │◀──────────│ InfluxDB │◀───────────│  Flink   │
│Dashboard │           │PostgreSQL│            │ Stream   │
└──────────┘           └────┬─────┘            └────┬─────┘
                            │                       │
                            ▼                       ▼
                     ┌──────────┐            ┌──────────┐
                     │ AI Model │───────────▶│ Actuator │
                     │ (LSTM,   │  control   │ (Fan,    │
                     │  YOLO)   │            │  Pump)   │
                     └────┬─────┘            └──────────┘
                          │
                          ▼
                   ┌──────────┐
                   │  ERP /   │
                   │ LINE API │
                   └──────────┘
```

### 10.5 Request Lifecycle (from the Template)

```
Client
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ Middleware Stack: CORS → ResponseFormatting → LogRequest →  │
│ DeviceId → scoped request                                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ Router: authenticate_* dependency (role + path allowlist)  │
│ → payload + Authentication                                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ Mapper: payload → domain entity                             │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ Use Case: business rules                                    │
│ → Cache read-through?                                       │
│   • Hit → return entity                                     │
│   • Miss/Redis down → Repo → DB → populate cache           │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ Mapper: entity → response schema                            │
│ → Middleware wraps in StandardResponse envelope            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
                        JSON Response
```

**Key principle:** Handlers never build the response envelope — `ResponseFormattingMiddleware` does that. Handlers never contain business logic — the use case does. The body of every handler is exactly `payload → mapper → use case → mapper → return`.

---

## 11. Case Studies

### 11.1 Case Study: Food Group with 5 Legal Entities

**Original problems:**
- Each company used a separate system; data was not connected
- Duplicate invoices, wrong VAT, mismatched stock
- No traceability when problems occurred
- Reports had to be compiled manually, taking 3–5 days

**Solution:**

| Phase | Month | Activities |
|---|---|---|
| 0 | 0 | Recon 3 paths (Money/Goods/Data) |
| 1 | 1–2 | Stabilize Money & Goods |
| 2 | 3 | Harden + Traceability foundation |
| 3 | 4 | Handoff (bus factor ≥ 2) |
| 4 | 5–7 | Transport + Retail + LINE + IoT |
| 5 | 8–10 | Reporting + KPI + Forecast |
| 6 | 11–12 | Rollout to Affiliates |

**Results:**

| KPI | Before | After | Change |
|---|---|---|---|
| Money recon discrepancy | 2–3% | 0% | −100% |
| Stock accuracy | 85% | 99% | +14% |
| Reports | 3–5 days | Real-time | Immediate |
| Traceability | None | 100% | +100% |
| Bus factor | 1 | 2 | +100% |

### 11.2 Case Study: Oyster Mushroom Farm, Chiang Rai (IoT)

**Original problems:**
- Temperature fluctuated 22–32°C
- 25% yield loss from disease
- Electricity cost ฿45,000/month

**Solution:**
1. Installed 12 DHT22 sensors + 4 MH-Z19B sensors
2. Raspberry Pi gateway + MQTT
3. LSTM AI forecasting temperature 6 hours ahead
4. Auto-control fans/misters
5. YOLOv8 detecting white mold

**Results (6 months):**

| KPI | Before | After | Change |
|---|---|---|---|
| Yield/month | 800 kg | 1,050 kg | +31% |
| Waste | 25% | 8% | −68% |
| Electricity | ฿45,000 | ฿34,000 | −24% |
| Net profit | ฿85,000 | ฿142,000 | +67% |

### 11.3 Troubleshooting Guide

| Problem | Cause | Solution |
|---|---|---|
| Money unstable in month 1 | Bug fixes distort money | Stop everything, focus on money path, defer goods path |
| Stock mismatch | No recon | Goods recon + cycle count |
| Lot/expiry lost | No FEFO | FEFO + alert |
| Duplicate invoice numbers | No unique constraint | SELECT FOR UPDATE + unique constraint |
| Cloud sync double-charge | No outbox | Outbox + idempotency |
| Low forecast accuracy | Insufficient data | Backtest + human override |
| Multi-tenant leak | No isolation test | Isolation test + RLS |

---

## 12. AI Prompt Template

### 12.1 File `docs/template_modules.md`

```markdown
# AI Prompt Template — Creating a New Module in ERP + IoT

## Module Information

| Topic | Details |
|---|---|
| **Module Name** | `{module_name}` |
| **Layer** | `{layer_number}` (0-7) |
| **Priority** | `{priority}` (🔴/🟠/🟡/🟢) |
| **Phase** | `{phase}` (0-6) |
| **Dependencies** | `{list_of_modules}` |
| **Domain Concepts** | `{entities}, {value_objects}, {enums}` |

## Prompt Template

### Create Module `{module_name}`

**Context:**
- Food group ERP (Multi-company)
- Clean Architecture + DDD (4 layers)
- Python 3.14+, FastAPI, Pydantic v2, SQLAlchemy 2.0
- PostgreSQL 17 (schema-per-tenant), Redis 8, Kafka
- Every action touching money/stock → audit log
- Money Path + Goods Path must be idempotent

**Requirements:**

1. **Domain Layer** (`domain/`)
   - `entities.py`: Dataclasses extending `BaseEntity`
   - `value_objects.py`: Plain classes with `_normalize → _validate → __str__ → __eq__`
   - `enums.py`: All enums as `(str, Enum)`
   - **No framework imports**

2. **Application Layer** (`application/`)
   - `interfaces.py`: Protocol contracts (`I{Entity}Repository`, `I{Entity}Cache`, `I{Entity}Service`)
   - `use_cases.py`: One `{Module}UseCases` class with business rules
   - `mappers.py`: `# ENTITY/DTOS`, `# ENTITY/MODELS`, `# ENTITY/CACHE`
   - `exceptions.py`: `{Module}Exception` + one per business rule
   - `utils.py`: Module-local helpers

3. **Infrastructure Layer** (`infrastructure/`)
   - `models.py`: SQLAlchemy extending `BaseModel` (inherits id, is_active, created_at, updated_at)
   - `repositories.py`: `Postgres{Entity}Repository` — `flush()` never `commit()`
   - `caches.py`: `Redis{Entity}Cache` — namespaced, tombstoned, never raises
   - `services.py`: External systems behind Protocol

4. **Presentation Layer** (`presentation/`)
   - `routers.py`: `payload → mapper → use case → mapper → return`
   - `schemas.py`: Pydantic v2 with full `Field` + `ConfigDict`
   - `docs.py`: `router_docs` + one `{action}_docs` per endpoint
   - `dependencies.py`: `Depends` factories returning Protocol type

5. **Error Handling** (3 shapes)
   - Use cases + routers: 3-branch (`StandardException → DomainError → Exception`)
   - Repositories + services: 2-branch (`StandardException → Exception`)
   - Caches: never-raise (catch → log → return `None`)

6. **Invariants to preserve:**
   - `{module_specific_invariants}`

7. **Domain Events:**
   - `{Module}Created`, `{Module}Updated`, `{Module}Deleted`
   - `{module_specific_events}`

8. **Tests:**
   - Unit tests for use cases (in-memory fakes)
   - Integration tests for repositories
   - Property-based tests for invariants

**Output:**
- All 16 files (4 layers × 4 files)
- Bilingual comments (Thai + English)
- Ready to run with `uvicorn app.app:app --reload`
```

### 12.2 Example AI Prompt for the `invoice` Module

```
Create the `invoice` module per template_modules.md

Context:
- Layer 2 (Money Path), Priority 🔴, Phase 1
- Dependencies: money, order, tax, ledger, audit, idempotency
- Domain: Invoice (entity), InvoiceLine (VO), InvoiceStatus (enum), VAT (VO)
- Invariants: total = sum(lines) + VAT, sum(debit) = sum(credit)
- Events: InvoiceIssued, InvoicePaid, InvoiceVoided

Use 4 layers:
- domain/entities.py → Invoice (extends BaseEntity)
- application/use_cases.py → InvoiceUseCases (issue, pay, void)
- infrastructure/repositories.py → PostgresInvoiceRepository
- presentation/routers.py → POST /invoice/, GET /invoice/{id}/

Error handling: 3-branch in use cases, 2-branch in repos
Idempotency: use idempotency key on every money path
Read-back: after create, read back to verify before return
```

---

## 13. AI Prompt per Module

### 13.1 Module: `money` (Layer 0, Core)

```
Create the `money` module per template_modules.md

Context:
- Layer 0 (Core), Priority 🔴, Phase 1
- Dependencies: none (primitive module)
- Domain: Money (VO), Currency (enum), VAT (VO)
- Invariants: Decimal precision, sum(debit) = sum(credit)
- Events: MoneyAdded, MoneySubtracted

Use 4 layers:
- domain/value_objects.py → Money (Decimal, currency, __add__, __sub__, __eq__)
- application/use_cases.py → MoneyUseCases (add, subtract, convert, calculate_vat)
- infrastructure/models.py → no model (pure VO)
- presentation/schemas.py → MoneySchema (amount: Decimal, currency: str)

Error handling:
- money.py: 3-branch (validate, raise DomainError)
- caches.py: no cache (pure computation)

Tests:
- Property-based: a + b == b + a (commutative)
- Property-based: (a + b) + c == a + (b + c) (associative)
- Property-based: a + 0 == a (identity)
- Unit: VAT calculation 7% for 100.00 = 7.00
```

### 13.2 Module: `invoice` (Layer 2, Money Path)

```
Create the `invoice` module per template_modules.md

Context:
- Layer 2 (Money Path), Priority 🔴, Phase 1
- Dependencies: money, order, tax, ledger, audit, idempotency
- Domain: Invoice (entity), InvoiceLine (VO), InvoiceStatus (enum)
- Invariants: total = sum(lines) + VAT, invoice_number unique
- Events: InvoiceIssued, InvoicePaid, InvoiceVoided

Use 4 layers:
- domain/entities.py → Invoice (extends BaseEntity)
  - fields: id, invoice_number, customer_id, lines, subtotal, vat, total, status, issued_at
  - methods: issue(), pay(), void(), add_line()
  - validation in __post_init__
- domain/value_objects.py → InvoiceLine (product_id, qty, unit_price, amount), InvoiceNumber (format INV-YYYYMM-XXXX)
- domain/enums.py → InvoiceStatus (DRAFT, ISSUED, PAID, VOIDED, OVERDUE)

- application/interfaces.py → IInvoiceRepository, IInvoiceCache, IInvoiceService
- application/use_cases.py → InvoiceUseCases
  - create_invoice(payload) → validate → save → audit → event
  - issue_invoice(id) → validate status → generate number → save → outbox
  - pay_invoice(id, payment) → validate → update → ledger → event
  - void_invoice(id, reason) → validate → reversal → audit
- application/exceptions.py → InvoiceException, InvoiceNotFoundException, InvoiceAlreadyPaidException, InvoiceInvalidStatusException

- infrastructure/models.py → InvoiceModel (extends BaseModel)
  - table: {prefix}_invoices
  - unique: uq_invoices_invoice_number
  - index: ix_invoices_customer_id, ix_invoices_status
- infrastructure/repositories.py → PostgresInvoiceRepository
  - flush() never commit()
  - SELECT FOR UPDATE for number generation
- infrastructure/caches.py → RedisInvoiceCache
  - key: {namespace}:invoice:{id}
  - tombstone on update/delete

- presentation/routers.py
  - POST /api/v1/invoice/ → create
  - GET /api/v1/invoice/ → list (paginated)
  - GET /api/v1/invoice/{id}/ → detail
  - PATCH /api/v1/invoice/{id}/issue/ → issue
  - PATCH /api/v1/invoice/{id}/pay/ → pay
  - DELETE /api/v1/invoice/{id}/ → void (soft delete)
- presentation/schemas.py → InvoiceCreate, InvoiceUpdate, InvoiceResponse, InvoiceListResponse

Error handling: 3-branch in use cases, 2-branch in repos, never-raise in caches
Idempotency: use idempotency key on every create/pay
Read-back: after create/issue, read back to verify

Tests:
- Unit: create_invoice with valid/invalid payload
- Unit: issue_invoice when status != DRAFT → raise
- Integration: concurrent invoice number generation
- Property-based: total always equals sum(lines) + VAT
- Chaos: kill worker → retry → idempotent
```

### 13.3 Module: `inventory` (Layer 3, Goods Path)

```
Create the `inventory` module per template_modules.md

Context:
- Layer 3 (Goods Path), Priority 🔴, Phase 1
- Dependencies: product, warehouse, lot, audit
- Domain: StockMovement (entity), StockBalance (VO), MovementType (enum)
- Invariants: Stock in − Stock out = Stock on hand, Σ(lot.qty) = Σ(movement.qty)
- Events: StockPosted, StockLow, StockAdjusted

Use 4 layers:
- domain/entities.py → StockMovement (extends BaseEntity)
  - fields: id, product_id, warehouse_id, lot_id, type, qty, reference, created_at
  - methods: post(), reverse()
- domain/value_objects.py → StockBalance (product_id, warehouse_id, on_hand, reserved, available)
- domain/enums.py → MovementType (IN, OUT, ADJUST, TRANSFER, PRODUCE, CONSUME)

- application/use_cases.py → InventoryUseCases
  - post_movement(payload) → validate → update balance → audit → event
  - adjust_stock(payload) → validate → create adjustment → audit
  - transfer_stock(payload) → validate → out + in → audit
  - get_balance(product_id, warehouse_id) → cache-aside
- application/exceptions.py → InventoryException, InsufficientStockException

- infrastructure/models.py → StockMovementModel, StockBalanceModel
  - table: {prefix}_stock_movements, {prefix}_stock_balances
  - index: ix_movements_product_warehouse
- infrastructure/repositories.py → PostgresInventoryRepository
  - flush() never commit()

- presentation/routers.py
  - POST /api/v1/inventory/movement/ → post
  - GET /api/v1/inventory/balance/ → get balance
  - PATCH /api/v1/inventory/adjust/ → adjust
  - POST /api/v1/inventory/transfer/ → transfer

Error handling: 3-branch, 2-branch, never-raise
Reconciliation: Σmovement = balance

Tests:
- Unit: post IN + OUT → balance correct
- Unit: post OUT > balance → raise
- Integration: concurrent movements
- Property-based: Σmovement = balance
```

### 13.4 Module: `traceability` (Layer 3, Goods Path)

```
Create the `traceability` module per template_modules.md

Context:
- Layer 3 (Goods Path), Priority 🔴, Phase 2
- Dependencies: lot, inventory, transport, product
- Domain: TraceEvent (entity), TraceCode (VO), TraceDirection (enum)
- Invariants: Every lot traceable forward + backward
- Events: TraceEventRecorded, TraceCodeGenerated, TraceQueried

Use 4 layers:
- domain/entities.py → TraceEvent (extends BaseEntity)
  - fields: id, trace_code, event_type, ref_id, ref_type, location, timestamp, metadata
  - methods: record()
- domain/value_objects.py → TraceCode (prefix + lot_id + hash)
- domain/enums.py → TraceEventType (HARVEST, RECEIVE, PRODUCE, PACK, SHIP, DELIVER, SELL), TraceDirection (FORWARD, BACKWARD)

- application/use_cases.py → TraceabilityUseCases
  - generate_code(lot_id) → create QR code → save → event
  - record_event(payload) → validate → save → index → event
  - forward_trace(code) → lot → shipments → customers
  - backward_trace(code) → customer → shipments → lot → supplier
- infrastructure/services.py → QRCodeService, RFIDService, ElasticsearchIndexService

- presentation/routers.py
  - POST /api/v1/traceability/generate/ → generate QR
  - GET /api/v1/traceability/forward/{code}/ → forward trace
  - GET /api/v1/traceability/backward/{code}/ → backward trace
  - GET /api/v1/traceability/{code}/ → full trace

Tests:
- Unit: forward_trace returns correct path
- Unit: backward_trace returns correct path
- Integration: end-to-end farm → factory → store → customer
- Property-based: every event has valid trace_code
```

### 13.5 Module: `iot` (Layer 6, Monitoring & Sensing)

```
Create the `iot` module per template_modules.md

Context:
- Layer 6 (Monitoring & Sensing), Priority 🟠, Phase 4
- Dependencies: monitoring, alerting, events
- Domain: SensorReading (entity), SensorType (enum), Threshold (VO)
- Invariants: Reading within valid range, Alert when threshold exceeded
- Events: SensorReadingReceived, ThresholdExceeded, SensorOffline

Use 4 layers:
- domain/entities.py → SensorReading (extends BaseEntity)
  - fields: id, sensor_id, sensor_type, value, unit, timestamp, location
  - methods: validate(), is_out_of_range()
- domain/value_objects.py → Threshold (min, max, unit)
- domain/enums.py → SensorType (TEMPERATURE, HUMIDITY, CO2, LIGHT, PH, EC)

- application/interfaces.py → ISensorRepository, ISensorCache, IIoTService
- application/use_cases.py → IoTUseCases
  - ingest_reading(payload) → validate → save → check threshold → alert → event
  - get_latest(sensor_id) → cache-aside
  - get_range(sensor_id, from, to) → time-series query
  - check_thresholds(sensor_id) → evaluate rules → trigger alert
- infrastructure/services.py → MQTTService (subscribe/publish), InfluxDBService

- presentation/routers.py
  - POST /api/v1/iot/reading/ → ingest
  - GET /api/v1/iot/{sensor_id}/latest/ → get latest
  - GET /api/v1/iot/{sensor_id}/range/ → get range
  - GET /api/v1/iot/sensors/ → list sensors

Error handling: 3-branch, 2-branch, never-raise
MQTT: QoS 1, auto-reconnect, idempotent key

Tests:
- Unit: ingest valid reading → save + no alert
- Unit: ingest out-of-range → save + alert
- Integration: MQTT → use case → DB
- Load: 10,000 msg/s
```

### 13.6 Module: `forecast` (Layer 5, Intelligence)

```
Create the `forecast` module per template_modules.md

Context:
- Layer 5 (Intelligence), Priority 🟠, Phase 5
- Dependencies: analytics, reporting, production, inventory
- Domain: Forecast (entity), ForecastMethod (enum), ForecastResult (VO)
- Invariants: MAPE < 20%, Non-negative forecast
- Events: ForecastGenerated, ForecastUpdated, ForecastAccuracyDropped

Use 4 layers:
- domain/entities.py → Forecast (extends BaseEntity)
  - fields: id, product_id, branch_id, forecast_date, predicted_qty, actual_qty, method, mape
- domain/value_objects.py → ForecastResult (predicted, actual, error, mape)
- domain/enums.py → ForecastMethod (LSTM, PROPHET, XGBOOST, ARIMA, ENSEMBLE)

- application/use_cases.py → ForecastUseCases
  - generate_forecast(product_id, branch_id, days) → load data → train/predict → save → event
  - update_actual(forecast_id, actual_qty) → calculate MAPE → update
  - get_forecast(product_id, branch_id) → cache-aside
  - backtest(product_id, days) → evaluate accuracy
- infrastructure/services.py → MLService (LSTM, Prophet, XGBoost), MLflowService

- presentation/routers.py
  - POST /api/v1/forecast/generate/ → generate
  - GET /api/v1/forecast/{product_id}/{branch_id}/ → get
  - PATCH /api/v1/forecast/{id}/actual/ → update actual
  - POST /api/v1/forecast/backtest/ → backtest

Tests:
- Unit: generate_forecast returns non-negative
- Unit: MAPE calculation correct
- Integration: retrain → predict → compare
- Property-based: MAPE >= 0
```

### 13.7 Module: `kpi` (Layer 5, Intelligence)

```
Create the `kpi` module per template_modules.md

Context:
- Layer 5 (Intelligence), Priority 🟠, Phase 5
- Dependencies: reporting, analytics, employee, satisfaction
- Domain: KPI (entity), KPITarget (VO), KPILevel (enum)
- Invariants: KPI actual = Σ(source events), Target >= 0
- Events: KPICalculated, KPITargetMissed, KPIAchieved

Use 4 layers:
- domain/entities.py → KPI (extends BaseEntity)
  - fields: id, name, level, target, actual, period, owner_id, source_module
  - methods: calculate(), is_achieved()
- domain/value_objects.py → KPITarget (value, unit, period), KPIResult (actual, target, achievement_pct)
- domain/enums.py → KPILevel (COMPANY, BRANCH, TEAM, INDIVIDUAL)

- application/use_cases.py → KPIUseCases
  - define_kpi(payload) → validate → save → event
  - calculate_kpi(kpi_id) → aggregate source events → update actual → event
  - check_target(kpi_id) → compare → alert if missed
  - get_scorecard(level, owner_id) → aggregate all KPIs
- infrastructure/services.py → KPIAggregationService

- presentation/routers.py
  - POST /api/v1/kpi/ → define
  - GET /api/v1/kpi/ → list
  - GET /api/v1/kpi/{id}/ → detail
  - PATCH /api/v1/kpi/{id}/calculate/ → calculate
  - GET /api/v1/kpi/scorecard/ → scorecard

Tests:
- Unit: calculate KPI from source events
- Unit: achievement_pct calculation
- Integration: KPI cascade company → branch → team
```

### 13.8 Module: `pos` (Layer 4, Operations)

```
Create the `pos` module per template_modules.md

Context:
- Layer 4 (Operations), Priority 🟠, Phase 4
- Dependencies: retail, shift, pricing, promotion, loyalty, product, inventory
- Domain: POSSale (entity), POSLine (VO), PaymentMethod (enum)
- Invariants: Sale total = sum(lines) - discount + VAT, Cash drawer = sum(payments)
- Events: POSSaleCompleted, POSReturnProcessed, ShiftClosed

Use 4 layers:
- domain/entities.py → POSSale (extends BaseEntity)
  - fields: id, shift_id, lines, subtotal, discount, vat, total, payment_method, status
  - methods: complete(), return_items(), void()
- domain/value_objects.py → POSLine (product_id, qty, unit_price, discount, amount)
- domain/enums.py → POSSaleStatus (OPEN, COMPLETED, VOIDED, RETURNED), PaymentMethod (CASH, CARD, QR, TRANSFER)

- application/use_cases.py → POSUseCases
  - create_sale(payload) → validate → save → update inventory → event
  - complete_sale(id, payment) → validate → payment → close → event
  - return_items(id, items) → validate → reversal → inventory → event
  - void_sale(id) → validate → reversal → audit
- infrastructure/services.py → ReceiptPrinterService, PaymentGatewayService

- presentation/routers.py
  - POST /api/v1/pos/sale/ → create
  - PATCH /api/v1/pos/sale/{id}/complete/ → complete
  - PATCH /api/v1/pos/sale/{id}/return/ → return
  - DELETE /api/v1/pos/sale/{id}/ → void
  - GET /api/v1/pos/sale/{id}/ → detail

Tests:
- Unit: create sale → total correct
- Unit: return → inventory restored
- Integration: offline mode → sync
- Property-based: total = sum(lines) - discount + VAT
```

### 13.9 Module: `production` (Layer 3, Goods Path)

```
Create the `production` module per template_modules.md

Context:
- Layer 3 (Goods Path), Priority 🔴, Phase 1
- Dependencies: recipe, inventory, lot, waste, quality, audit
- Domain: ProductionBatch (entity), BatchInput (VO), BatchOutput (VO)
- Invariants: Batch input = output + waste, Yield% within range
- Events: BatchStarted, BatchCompleted, BatchAborted, YieldRecorded

Use 4 layers:
- domain/entities.py → ProductionBatch (extends BaseEntity)
  - fields: id, batch_number, recipe_id, inputs, outputs, waste, start_time, end_time, status
  - methods: start(), complete(), abort(), record_yield()
- domain/value_objects.py → BatchInput (product_id, lot_id, qty), BatchOutput (product_id, lot_id, qty, yield_pct)
- domain/enums.py → BatchStatus (PLANNED, IN_PROGRESS, COMPLETED, ABORTED)

- application/use_cases.py → ProductionUseCases
  - plan_batch(payload) → validate recipe → save → event
  - start_batch(id) → validate status → issue materials → event
  - complete_batch(id, outputs) → validate yield → receive output → waste → event
  - abort_batch(id, reason) → validate → return materials → waste
- infrastructure/services.py → YieldCalculatorService

- presentation/routers.py
  - POST /api/v1/production/batch/ → plan
  - PATCH /api/v1/production/batch/{id}/start/ → start
  - PATCH /api/v1/production/batch/{id}/complete/ → complete
  - PATCH /api/v1/production/batch/{id}/abort/ → abort
  - GET /api/v1/production/batch/{id}/ → detail

Tests:
- Unit: complete batch → yield = output / input
- Unit: yield < min → alert
- Integration: batch → inventory movement
- Property-based: input = output + waste
```

### 13.10 Module: `transport` (Layer 4, Operations)

```
Create the `transport` module per template_modules.md

Context:
- Layer 4 (Operations), Priority 🟠, Phase 4
- Dependencies: delivery, route, gps, invoice, inventory
- Domain: Shipment (entity), ShipmentItem (VO), ShipmentStatus (enum)
- Invariants: Shipment contents = Invoice contents, Cold-chain within range
- Events: ShipmentCreated, ShipmentDispatched, ShipmentArrived, TempExceeded

Use 4 layers:
- domain/entities.py → Shipment (extends BaseEntity)
  - fields: id, shipment_number, invoice_id, items, carrier_id, route_id, status, dispatched_at, arrived_at
  - methods: dispatch(), arrive(), record_temp()
- domain/value_objects.py → ShipmentItem (product_id, lot_id, qty, temp_range)
- domain/enums.py → ShipmentStatus (PLANNED, LOADING, IN_TRANSIT, DELIVERED, CANCELLED)

- application/use_cases.py → TransportUseCases
  - create_shipment(payload) → validate → save → event
  - dispatch_shipment(id) → validate → load → event
  - arrive_shipment(id, pod) → validate → deliver → event
  - record_temperature(id, temp) → validate range → save → alert if exceeded
- infrastructure/services.py → GPSTrackingService, TemperatureLoggerService

- presentation/routers.py
  - POST /api/v1/transport/shipment/ → create
  - PATCH /api/v1/transport/shipment/{id}/dispatch/ → dispatch
  - PATCH /api/v1/transport/shipment/{id}/arrive/ → arrive
  - POST /api/v1/transport/shipment/{id}/temp/ → record temp
  - GET /api/v1/transport/shipment/{id}/ → detail

Tests:
- Unit: dispatch → status changed
- Unit: temp exceeded → alert
- Integration: shipment → invoice match
- Property-based: shipment contents = invoice contents
```

### 13.11 Module: `reporting` (Layer 5, Intelligence)

```
Create the `reporting` module per template_modules.md

Context:
- Layer 5 (Intelligence), Priority 🔴, Phase 5
- Dependencies: analytics, invoice, inventory, production, kpi
- Domain: Report (entity), ReportPeriod (enum), ReportType (enum)
- Invariants: Report data consistent across periods
- Events: ReportGenerated, ReportExported

Use 4 layers:
- domain/entities.py → Report (extends BaseEntity)
  - fields: id, type, period, start_date, end_date, data, generated_at
- domain/value_objects.py → ReportPeriod (DAILY, WEEKLY, MONTHLY, QUARTERLY, YEARLY, Y3, Y5)
- domain/enums.py → ReportType (SALES, CASH, STOCK, P&L, VAT, KPI, PRODUCTION)

- application/use_cases.py → ReportingUseCases
  - generate_report(type, period, branch_id) → aggregate → save → event
  - export_report(id, format) → PDF/Excel → LINE notify
  - schedule_report(type, period, cron) → schedule
- infrastructure/services.py → PDFService, ExcelService, LINEChannelService

- presentation/routers.py
  - POST /api/v1/reporting/generate/ → generate
  - GET /api/v1/reporting/{id}/ → detail
  - GET /api/v1/reporting/{id}/export/ → export
  - POST /api/v1/reporting/schedule/ → schedule

Tests:
- Unit: generate daily report → correct totals
- Integration: materialized view refresh
- Performance: report < 5s for 1M records
```

### 13.12 Module: `line_channel` (Layer 4, Operations)

```
Create the `line_channel` module per template_modules.md

Context:
- Layer 4 (Operations), Priority 🟠, Phase 4
- Dependencies: order, customer, pricing, notification
- Domain: LINEOrder (entity), LINEUser (VO), LINEStatus (enum)
- Invariants: Order total = sum(items), LINE user mapped to customer
- Events: LINEOrderReceived, LINEOrderConfirmed, LINEOrderCancelled

Use 4 layers:
- domain/entities.py → LINEOrder (extends BaseEntity)
  - fields: id, line_user_id, customer_id, items, total, status, raw_message
  - methods: confirm(), cancel()
- domain/value_objects.py → LINEUser (user_id, display_name, picture_url)
- domain/enums.py → LINEOrderStatus (RECEIVED, PARSED, CONFIRMED, CANCELLED)

- application/use_cases.py → LINEChannelUseCases
  - receive_webhook(payload) → verify signature → parse → save → event
  - parse_order(message) → NLP parse → create order
  - confirm_order(id) → validate → invoice → reply
  - reply_message(user_id, message) → LINE API
- infrastructure/services.py → LINEAPIService (webhook verify, reply, push)

- presentation/routers.py
  - POST /api/v1/line/webhook/ → receive
  - GET /api/v1/line/order/ → list
  - PATCH /api/v1/line/order/{id}/confirm/ → confirm

Tests:
- Unit: parse order from text
- Integration: webhook → order → invoice
- Security: verify LINE signature
```

### 13.13 Module: `reconciliation` (Layer 2, Money Path)

```
Create the `reconciliation` module per template_modules.md

Context:
- Layer 2 (Money Path), Priority 🔴, Phase 1
- Dependencies: invoice, ledger, payment, accounting_gateway, inventory
- Domain: ReconCheck (entity), ReconResult (VO), ReconStatus (enum)
- Invariants: Discrepancy = 0, All checks pass
- Events: ReconStarted, ReconPassed, ReconFailed, DiscrepancyDetected

Use 4 layers:
- domain/entities.py → ReconCheck (extends BaseEntity)
  - fields: id, check_type, source, target, expected, actual, discrepancy, status, checked_at
- domain/value_objects.py → ReconResult (expected, actual, discrepancy, pass)
- domain/enums.py → ReconType (INVOICE_LEDGER, STOCK_MOVEMENT, LOT_BALANCE, BATCH_YIELD, CLOUD_SYNC)

- application/use_cases.py → ReconciliationUseCases
  - run_check(type) → query source + target → compare → save → event
  - run_all_checks() → run 5 checks → aggregate
  - resolve_discrepancy(id, note) → mark resolved → audit
- infrastructure/repositories.py → PostgresReconRepository

- presentation/routers.py
  - POST /api/v1/reconciliation/run/ → run check
  - GET /api/v1/reconciliation/ → list checks
  - GET /api/v1/reconciliation/{id}/ → detail
  - PATCH /api/v1/reconciliation/{id}/resolve/ → resolve

Tests:
- Unit: invoice_ledger check → discrepancy 0
- Unit: stock_movement check → discrepancy 0
- Integration: cloud sync idempotent
- Property-based: sum(debit) = sum(credit)
```

### 13.14 Module: `payment` (Layer 2, Money Path)

```
Create the `payment` module per template_modules.md

Context:
- Layer 2 (Money Path), Priority 🔴, Phase 2
- Dependencies: invoice, ledger, accounting_gateway, tax
- Domain: Payment (entity), PaymentMethod (enum), PaymentStatus (enum)
- Invariants: Payment amount = invoice balance, sum(payments) <= invoice total
- Events: PaymentReceived, PaymentMatched, PaymentVoided

Use 4 layers:
- domain/entities.py → Payment (extends BaseEntity)
  - fields: id, payment_number, invoice_id, amount, method, reference, paid_at, status
  - methods: match(), void()
- domain/value_objects.py → PaymentReference (bank_ref, date, amount)
- domain/enums.py → PaymentMethod (CASH, TRANSFER, CHEQUE, CARD), PaymentStatus (PENDING, MATCHED, VOIDED, OVERPAID)

- application/use_cases.py → PaymentUseCases
  - record_payment(payload) → validate → match invoice → ledger → event
  - match_payment(id, invoice_id) → validate amount → update invoice
  - void_payment(id, reason) → validate → reversal → audit
- infrastructure/services.py → BankGatewayService, PaymentGatewayService

- presentation/routers.py
  - POST /api/v1/payment/ → record
  - PATCH /api/v1/payment/{id}/match/ → match
  - DELETE /api/v1/payment/{id}/ → void
  - GET /api/v1/payment/ → list

Tests:
- Unit: record payment → invoice status updated
- Unit: overpay → raise
- Integration: payment → ledger entry
- Property-based: sum(payments) <= invoice total
```

### 13.15 Module: `warehouse` (Layer 3, Goods Path)

```
Create the `warehouse` module per template_modules.md

Context:
- Layer 3 (Goods Path), Priority 🔴, Phase 1
- Dependencies: inventory, lot, product, audit
- Domain: Warehouse (entity), Location (VO), Bin (VO)
- Invariants: Location unique within warehouse, Bin unique within location
- Events: WarehouseCreated, LocationAdded, StockMoved, StockCounted

Use 4 layers:
- domain/entities.py → Warehouse (extends BaseEntity)
  - fields: id, code, name, address, locations, is_active
  - methods: add_location(), remove_location()
- domain/value_objects.py → Location (code, name, bins), Bin (code, capacity, current)
- domain/enums.py → LocationType (RECEIVING, STORAGE, PICKING, SHIPPING, QUARANTINE)

- application/use_cases.py → WarehouseUseCases
  - create_warehouse(payload) → validate → save → event
  - add_location(warehouse_id, payload) → validate → save
  - move_stock(from_bin, to_bin, qty) → validate → inventory → event
  - cycle_count(warehouse_id) → snapshot → compare → adjust
- infrastructure/repositories.py → PostgresWarehouseRepository

- presentation/routers.py
  - POST /api/v1/warehouse/ → create
  - GET /api/v1/warehouse/ → list
  - POST /api/v1/warehouse/{id}/location/ → add location
  - POST /api/v1/warehouse/move/ → move stock
  - POST /api/v1/warehouse/{id}/count/ → cycle count

Tests:
- Unit: move stock → inventory updated
- Unit: cycle count → discrepancy detected
- Integration: warehouse → inventory balance
```

---

## 14. Module Checklist

| # | Module | Layer | Priority | Phase | Status |
|---|---|---|---|---|---|
| 1 | money | 0 | 🔴 | 1 | ☐ |
| 2 | tenant_context | 0 | 🔴 | 1 | ☐ |
| 3 | audit | 0 | 🔴 | 1 | ☐ |
| 4 | idempotency | 0 | 🔴 | 1 | ☐ |
| 5 | config | 0 | 🔴 | 1 | ☐ |
| 6 | events | 0 | 🔴 | 1 | ☐ |
| 7 | tenancy | 1 | 🔴 | 1 | ☐ |
| 8 | authentication | 1 | 🔴 | 1 | ☐ |
| 9 | user | 1 | 🔴 | 1 | ☐ |
| 10 | employee | 1 | 🟠 | 1 | ☐ |
| 11 | customer | 1 | 🔴 | 1 | ☐ |
| 12 | supplier | 1 | 🟠 | 1 | ☐ |
| 13 | product | 1 | 🔴 | 1 | ☐ |
| 14 | pricing | 1 | 🔴 | 1 | ☐ |
| 15 | order | 2 | 🔴 | 1 | ☐ |
| 16 | invoice | 2 | 🔴 | 1 | ☐ |
| 17 | ledger | 2 | 🔴 | 1 | ☐ |
| 18 | payment | 2 | 🔴 | 2 | ☐ |
| 19 | accounting_gateway | 2 | 🔴 | 2 | ☐ |
| 20 | tax | 2 | 🔴 | 2 | ☐ |
| 21 | reconciliation | 2 | 🔴 | 1 | ☐ |
| 22 | inventory | 3 | 🔴 | 1 | ☐ |
| 23 | warehouse | 3 | 🔴 | 1 | ☐ |
| 24 | lot | 3 | 🔴 | 1 | ☐ |
| 25 | production | 3 | 🔴 | 1 | ☐ |
| 26 | recipe | 3 | 🟠 | 1 | ☐ |
| 27 | quality | 3 | 🟠 | 1 | ☐ |
| 28 | waste | 3 | 🟠 | 1 | ☐ |
| 29 | procurement | 3 | 🟠 | 1 | ☐ |
| 30 | traceability | 3 | 🔴 | 2 | ☐ |
| 31 | transport | 4 | 🟠 | 4 | ☐ |
| 32 | delivery | 4 | 🟠 | 4 | ☐ |
| 33 | route | 4 | 🟠 | 4 | ☐ |
| 34 | gps | 4 | 🟠 | 4 | ☐ |
| 35 | retail | 4 | 🟠 | 4 | ☐ |
| 36 | pos | 4 | 🟠 | 4 | ☐ |
| 37 | shift | 4 | 🟠 | 4 | ☐ |
| 38 | line_channel | 4 | 🟠 | 4 | ☐ |
| 39 | promotion | 4 | 🟡 | 4 | ☐ |
| 40 | loyalty | 4 | 🟡 | 4 | ☐ |
| 41 | reporting | 5 | 🔴 | 5 | ☐ |
| 42 | analytics | 5 | 🟠 | 5 | ☐ |
| 43 | forecast | 5 | 🟠 | 5 | ☐ |
| 44 | kpi | 5 | 🟠 | 5 | ☐ |
| 45 | satisfaction | 5 | 🟡 | 5 | ☐ |
| 46 | recommendation | 5 | 🟡 | 5 | ☐ |
| 47 | iot | 6 | 🟠 | 4 | ☐ |
| 48 | cctv | 6 | 🟡 | 4 | ☐ |
| 49 | monitoring | 6 | 🔴 | 1 | ☐ |
| 50 | backup | 6 | 🔴 | 1 | ☐ |
| 51 | alerting | 6 | 🟠 | 1 | ☐ |
| 52 | audit_viewer | 6 | 🟠 | 2 | ☐ |
| 53 | health | 7 | 🔴 | 1 | ☐ |
| 54 | example | 7 | 🟢 | 1 | ☐ |
| 55 | blank | 7 | 🟢 | 1 | ☐ |

---

## 15. Security Code

### 15.1 Nested JWT (from the Template)

```python
# app/core/security.py
# The JWT is designed in 2 layers: JWS (Ed25519) + JWE (ECDH-ES + A256GCM)

# Layer 1: Sign the claims with Ed25519
jws_token = jwt.encode(
    payload=claims, key=settings.JWT_SIGNING_PRIVATE_KEY, algorithm="EdDSA"
)

# Layer 2: Encrypt the JWS with ECDH-ES + A256GCM
jwe_token = jwe.encrypt(
    plaintext=jws_token,
    key=settings.JWT_ENCRYPTION_PUBLIC_KEY,
    algorithm="ECDH-ES",
    encryption="A256GCM",
)

# Store the HMAC fingerprint of the jti in the DB (never the token itself)
hashed_jti = hmac.new(
    settings.JWT_HASH_FINGERPRINT.encode(), jti.encode(), hashlib.sha256
).hexdigest()
```

```text
C:\Users\kongn\AppData\Local\Temp\md-notebook\md_notebook.py:2: SyntaxWarning: "\g" is an invalid escape sequence. Such sequences will not work in the future. Did you mean "\\g"? A raw string is also an option.
  sys.path.append("c:\github\fastapicleanarchitectureddd")
  File "C:\Users\kongn\AppData\Local\Temp\md-notebook\md_notebook.py", line 3
    sys.path.append("C:\Users\kongn\AppData\Local\Temp\md-notebook")
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
SyntaxError: (unicode error) 'unicodeescape' codec can't decode bytes in position 2-3: truncated \UXXXXXXXX escape
```

### 15.2 Role-Based Access (2 Gates)

```python
# app/modules/authentication/presentation/dependencies.py

# Gate 1: Dependency — check role level
async def authenticate_admin(
    authentication: Authentication = Depends(authenticate_user),
):
    if authentication.user.role != Role.ADMIN:
        raise AuthorizationException()
    return authentication


# Gate 2: Path allowlist — enforced in middleware
SECURITY_ADMIN_ALLOWED_PATHS = (
    _path_rule("/api/v1/key/", "POST"),
    _path_rule("/api/v1/key", "POST"),
    _path_rule("/api/v1/key/{id}/", "GET"),
    # ...
)
```

```text
C:\Users\kongn\AppData\Local\Temp\md-notebook\md_notebook.py:2: SyntaxWarning: "\g" is an invalid escape sequence. Such sequences will not work in the future. Did you mean "\\g"? A raw string is also an option.
  sys.path.append("c:\github\fastapicleanarchitectureddd")
  File "C:\Users\kongn\AppData\Local\Temp\md-notebook\md_notebook.py", line 3
    sys.path.append("C:\Users\kongn\AppData\Local\Temp\md-notebook")
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
SyntaxError: (unicode error) 'unicodeescape' codec can't decode bytes in position 2-3: truncated \UXXXXXXXX escape
```

### 15.3 API Key (HMAC + Constant-Time Compare)

```python
# app/modules/key/application/utils.py


def generate_api_key() -> tuple[str, str, str]:
    """Generate raw key, hash, and prefix."""
    raw = secrets.token_urlsafe(32)  # 32 bytes entropy
    raw_key = f"{settings.API_KEY_PREFIX}_{raw}"

    hashed = hmac.new(
        settings.API_KEY_HASH_FINGERPRINT.encode(), raw_key.encode(), hashlib.sha256
    ).hexdigest()

    prefix = raw_key[:8]
    last_four = raw_key[-4:]

    return raw_key, hashed, prefix, last_four


def verify_api_key(raw_key: str, hashed_key: str) -> bool:
    """Verify with constant-time comparison."""
    computed = hmac.new(
        settings.API_KEY_HASH_FINGERPRINT.encode(), raw_key.encode(), hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(computed, hashed_key)
```

```text
C:\Users\kongn\AppData\Local\Temp\md-notebook\md_notebook.py:2: SyntaxWarning: "\g" is an invalid escape sequence. Such sequences will not work in the future. Did you mean "\\g"? A raw string is also an option.
  sys.path.append("c:\github\fastapicleanarchitectureddd")
  File "C:\Users\kongn\AppData\Local\Temp\md-notebook\md_notebook.py", line 3
    sys.path.append("C:\Users\kongn\AppData\Local\Temp\md-notebook")
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
SyntaxError: (unicode error) 'unicodeescape' codec can't decode bytes in position 2-3: truncated \UXXXXXXXX escape
```

### 15.4 Redis Cache with Tombstone

```python
# app/modules/key/infrastructure/caches.py


class RedisKeyCache:
    """Cache that never raises — degrades to database."""

    async def get(self, key: str) -> Optional[KeyEntity]:
        try:
            data = await self.redis.get(f"{self.namespace}:{key}")
            return self._deserialize(data) if data else None
        except Exception as e:
            logger.opt(exception=e).error("Cache get failed. Falling back to database.")
            return None  # Never raise — always return None

    async def delete(self, key: str) -> None:
        try:
            # Write tombstone BEFORE delete
            await self.redis.setex(
                f"{self.namespace}:tombstone:{key}",
                settings.REDIS_TOMBSTONE_TTL_SECONDS,
                "1",
            )
            await self.redis.delete(f"{self.namespace}:{key}")
        except Exception as e:
            logger.opt(exception=e).error("Cache delete failed.")

    async def insert(self, key: str, entity: KeyEntity) -> None:
        try:
            # Check tombstone BEFORE writing
            tombstone = await self.redis.get(f"{self.namespace}:tombstone:{key}")
            if tombstone:
                return  # Suppress repopulation
            await self.redis.setex(
                f"{self.namespace}:{key}",
                settings.REDIS_DEFAULT_TTL_SECONDS,
                self._serialize(entity),
            )
        except Exception as e:
            logger.opt(exception=e).error("Cache insert failed.")
```

```text
C:\Users\kongn\AppData\Local\Temp\md-notebook\md_notebook.py:2: SyntaxWarning: "\g" is an invalid escape sequence. Such sequences will not work in the future. Did you mean "\\g"? A raw string is also an option.
  sys.path.append("c:\github\fastapicleanarchitectureddd")
  File "C:\Users\kongn\AppData\Local\Temp\md-notebook\md_notebook.py", line 3
    sys.path.append("C:\Users\kongn\AppData\Local\Temp\md-notebook")
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
SyntaxError: (unicode error) 'unicodeescape' codec can't decode bytes in position 2-3: truncated \UXXXXXXXX escape
```

### 15.5 Security Checklist

| # | Item | Status |
|---|---|---|
| 1 | HTTPS/TLS on every endpoint | ☐ |
| 2 | Nested JWT (JWS + JWE) | ☐ |
| 3 | HTTP-only cookies | ☐ |
| 4 | HMAC fingerprint of jti | ☐ |
| 5 | RBAC 2 gates (role + path) | ☐ |
| 6 | API key rotation | ☐ |
| 7 | Constant-time compare | ☐ |
| 8 | Cache tombstone | ☐ |
| 9 | Rate limit (100 req/min/IP) | ☐ |
| 10 | Input sanitization | ☐ |
| 11 | Encrypt at rest (AES-256) | ☐ |
| 12 | MFA for admin | ☐ |
| 13 | Secrets in Vault/K8s Secret | ☐ |
| 14 | Audit log (append-only) | ☐ |
| 15 | PDPA consent | ☐ |

---

## 16. Load Test (Development)

### 16.1 Money Path Load Test

```python
# tests/load/test_money_path.py
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_invoice_throughput(client: AsyncClient):
    """Test 1,000 invoices/sec with idempotency."""

    import time

    start = time.time()

    for i in range(1000):
        response = await client.post(
            "/api/v1/invoice/",
            json={
                "customer_id": f"cust-{i}",
                "lines": [{"product_id": "p1", "qty": 10, "unit_price": 100}],
            },
            headers={"Idempotency-Key": f"inv-{i}"},
        )
        assert response.status_code == 201

    elapsed = time.time() - start
    print(f"Created 1000 invoices in {elapsed:.2f}s")
```

```text
C:\Users\kongn\AppData\Local\Temp\md-notebook\md_notebook.py:2: SyntaxWarning: "\g" is an invalid escape sequence. Such sequences will not work in the future. Did you mean "\\g"? A raw string is also an option.
  sys.path.append("c:\github\fastapicleanarchitectureddd")
  File "C:\Users\kongn\AppData\Local\Temp\md-notebook\md_notebook.py", line 3
    sys.path.append("C:\Users\kongn\AppData\Local\Temp\md-notebook")
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
SyntaxError: (unicode error) 'unicodeescape' codec can't decode bytes in position 2-3: truncated \UXXXXXXXX escape
```

### 16.2 MQTT Load Test

```go
// tests/load/sensor_load_test.go
package load

import (
	"testing"
	"time"
	mqtt "github.com/eclipse/paho.mqtt.golang"
)

func TestSensorThroughput(t *testing.T) {
	opts := mqtt.NewClientOptions().AddBroker("tcp://localhost:1888")
	c := mqtt.NewClient(opts)
	if token := c.Connect(); token.Wait() && token.Error() != nil {
		t.Fatalf("connect failed: %v", token.Error())
	}
	defer c.Disconnect(250)

	const total = 10000
	start := time.Now()
	for i := 0; i < total; i++ {
		payload := `{"id":"s1","type":"temperature","value":25.5}`
		c.Publish("farm/s1/sensor/temp", 1, false, payload)
	}
	elapsed := time.Since(start)
	t.Logf("published %d msgs in %v (%.0f msg/s)",
		total, elapsed, float64(total)/elapsed.Seconds())
}
```

```text
main.go:4:8: no required module provides package github.com/eclipse/paho.mqtt.golang: go.mod file not found in current directory or any parent directory; see 'go help modules'
```

### 16.3 Load Test Tools

| Tool | Use Case | Command |
|---|---|---|
| **k6** | HTTP load test | `k6 run script.js` |
| **JMeter** | MQTT plugin | GUI + CLI |
| **Gatling** | Streaming | `gatling.sh` |
| **Vegeta** | Constant rate | `vegeta attack -rate=1000/s` |
| **Locust** | Python load test | `locust -f locustfile.py` |

### 16.4 Load Test Checklist

| # | Item | Target | Status |
|---|---|---|---|
| 1 | Money Path throughput | 1,000 invoice/s | ☐ |
| 2 | Goods Path throughput | 10,000 movement/s | ☐ |
| 3 | MQTT ingest | 10,000 msg/s | ☐ |
| 4 | POS concurrent users | 100 users | ☐ |
| 5 | Report generation | < 5s for 1M records | ☐ |
| 6 | Cache hit rate | > 90% | ☐ |
| 7 | DB connection pool | 50 connections | ☐ |
| 8 | Redis memory | < 256MB | ☐ |
| 9 | Kafka lag | < 100 messages | ☐ |
| 10 | API p95 latency | < 200ms | ☐ |

---

## 17. Summary

### 17.1 Benefits

- **Centralized** — 5 legal entities use one ERP
- **Money stability** — Money recon discrepancy = 0
- **Goods stability** — Stock accuracy ≥ 99%
- **Traceability** — 100% forward + backward
- **Automation** — Reduces labor, runs 24/7
- **Forecasting** — MAPE < 20%
- **Reporting** — Real-time at every level
- **Scalable** — Multi-tenant

### 17.2 Cautions

- Sensors must be calibrated every 6 months
- Network outage → need a buffer at the Edge
- AI must be retrained when conditions change
- PDPA: farmer data requires consent
- Schema migration failure → must have a backup first
- Cloud API changes → need an abstraction layer

### 17.3 Pros

- Clean Architecture + DDD — maintainable
- 4 layers per module — testable
- Idempotency + Outbox — retry-safe
- Append-only audit — traceable
- Schema-per-tenant — isolated
- Cache with tombstone — race-free
- Event-driven — scalable

### 17.4 Cons

- High initial cost
- Requires technical expertise
- Depends on electricity/network
- Takes 12 months
- Needs at least 2 people (bus factor ≥ 2)

### 17.5 Prohibitions

- ❌ Never open an actuator without a safety interlock
- ❌ Never store passwords in plaintext
- ❌ Never use default credentials
- ❌ Never delete a ledger entry (use reversal)
- ❌ Never hardcode VAT/waste%/pricing
- ❌ Never sync to cloud before writing to the DB (use outbox)
- ❌ Never `commit` in a repository (only `flush`)
- ❌ Never place `except StandardException` after `except Exception`

### 17.6 Working Code Examples

```sh
# 1. Clone
git clone fastapi-clean-architecture-ddd-erp-iot
cd fastapi-clean-architecture-ddd-template

# 2. Configure
cp .env.example .env

# 3. Install
uv sync

# 4. Start dependencies
make dependencies-up-silent

# 5. Run API
make dev

# 6. Test
curl http://localhost:8000/health/

# 7. Login
curl -X POST http://localhost:8000/api/v1/authentication/login/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$SECURITY_ADMIN_EMAIL&password=$SECURITY_ADMIN_PASSWORD" \
  -c cookies.txt

# 8. Create invoice
curl -X POST http://localhost:8000/api/v1/invoice/ \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: inv-001" \
  -d '{"customer_id":"c1","lines":[{"product_id":"p1","qty":10,"unit_price":100}]}'
```

```text
<3>WSL (70877 - Relay) ERROR: CreateProcessCommon:818: execvpe(/bin/bash) failed: No such file or directory
```

---

# Ollama Commands

```sh
# Run a specific model in interactive chat mode
ollama run qwen3.6:latest

# Remove a model to free up space
ollama rm deepseek-r1:7b

# Pull a new model from the Ollama library
ollama pull llama3.1:8b

# Check active/currently loaded models in RAM/VRAM
ollama ps
```

---

**Author:** Kongnakorn Jantakun
**Email:** kongnakornjantakun@gmail.com
**Version:** 2.0.0
**Updated:** 2026-09-17

---

```powershell
powershell -ExecutionPolicy Bypass -File C:\AI\KoboldCpp\start.ps1
```

```sh
opencode --continue
```