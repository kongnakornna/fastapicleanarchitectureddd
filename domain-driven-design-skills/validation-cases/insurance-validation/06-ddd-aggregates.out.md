# 06 — ผลผลิต ddd-aggregates (Blind Run)

> อินพุต: `02-ddd-discover.out.md` (ลำดับเหตุการณ์และคำสั่งผู้สมัคร) + `04-ddd-contexts.out.md` (สารบัญ Bounded Context และคำศัพท์) + `05-ddd-context-map.out.md` (แผนที่และลักษณะล้มเหลว)
> ไฟล์นี้เป็นผลลัพธ์การจำลองการทำงานของ `ddd-aggregates` ใน blind run โดย**ไม่ได้อ้างอิง**วัสดุ ground truth (กรณีนี้ไม่มีการอ้างอิงการใช้งานจริง)

## สารบัญ Aggregate

| Aggregate           | สังกัด Bounded Context | Aggregate Root        | Entity ที่รวม                        | Value Object ที่รวม                            | Invariant สำคัญ                                                           | คำสั่งสำคัญ                                                                               |
| :------------------ | :--------------------- | :-------------------- | :---------------------------------- | :--------------------------------------------- | :------------------------------------------------------------------------ | :--------------------------------------------------------------------------------------- |
| Application         | Quotation              | Application           | —                                   | CoverageRequest, QuotedTerms                   | ใบเสนอราคาไม่ผูกพัน; เลขที่คำขอเป็นหนึ่งเดียว                             | SubmitApplication, RequestQuote                                                          |
| UnderwritingCase    | Underwriting           | UnderwritingCase      | —                                   | Decision, ReinsuranceNeed                      | คำขอหนึ่งรายการมีการตัดสินใจที่มีผลบังคับได้ไม่เกินหนึ่งรายการ การตัดสินใจเปลี่ยนแปลงไม่ได้หลังออกกรมธรรม์แล้ว | MakeUnderwritingDecision                                                                 |
| Policy              | Policy                 | Policy                | Endorsement                         | TermsVersion, Deductible, WaitingPeriod        | เวอร์ชันเงื่อนไขเพิ่มขึ้นเรื่อยๆ ไม่เปลี่ยนแปลงได้ ระหว่างระงับเกิดเหตุไม่รับ (ร่วมกับ Claim) | IssuePolicy, ApplyEndorsement, RenewPolicy, LapsePolicy                                  |
| Claim               | Claim                  | Claim                 | SurveyRecord, AssessmentRecord      | LossDetails, AssessedLoss, TermsSnapshot       | ระหว่างสอบสวนห้ามจ่าย ความสูญเสียเดียวกันรวมเป็นแจ้งเหตุเดียว สแน็ปช็อตเงื่อนไขเปลี่ยนแปลงไม่ได้ | NotifyClaim, LinkToPolicy, CompleteSurvey, AssessLoss, OpenInvestigation, CloseClaim     |
| PaymentInstruction  | Payment                | PaymentInstruction    | —                                   | PaymentReceipt                                 | คีย์幂emsp;fontเป็นหนึ่งเดียว จ่ายแล้วเปลี่ยนจำนวนเงินไม่ได้              | ExecutePayment, RetryPayment                                                             |
| Party               | Party                  | Party                 | —                                   | LossHistory                                    | ประวัติเรียกร้องค่าสินไหมเป็นแบบอ่านอย่างเดียวสืบทอด                       | (ดูแลข้อมูลหลัก)                                                                         |
| ReserveView         | Regulatory             | ReserveView           | —                                   | —                                              | ฉายภาพอ่านอย่างเดียว ธุรกิจไม่เขียน                                       | (รีเฟรชฉายภาพ)                                                                          |

## ตาราง Invariant

| Invariant                                                                      | คำสั่งที่กระตุ้น                       | ตำแหน่งตรวจสอบ                              | พฤติกรรมเมื่อละเมิด                           |
| :----------------------------------------------------------------------------- | :------------------------------------- | :------------------------------------------- | :--------------------------------------------- |
| I-1 ลูกค้าเดียวกัน วัตถุเอาประกันเดียวกัน เลขที่คำขอเดียวเป็นหนึ่งเดียว    | SubmitApplication                      | ภายใน Aggregate Application                  | ปฏิเสธการส่งซ้ำ (幂emsp;fontคืนคำขอเดิม)     |
| I-2 ใบเสนอราคาอ้างอิงคำขอที่มีผลบังคับ ใบเสนอราคาไม่สัญญา                  | RequestQuote                           | ภายใน Aggregate Application                  | ไม่มีคำขอที่มีผลบังคับห้ามเสนอราคา            |
| I-3 คำขอหนึ่งรายการมีการตัดสินใจที่มีผลบังคับได้ไม่เกินหนึ่งรายการ หลังออกกรมธรรม์การตัดสินใจเปลี่ยนแปลงไม่ได้ | MakeUnderwritingDecision | ภายใน Aggregate UnderwritingCase             | การตัดสินใจซ้ำถูกปฏิเสธ; ออกกรมธรรม์แล้วปฏิเสธการเปลี่ยน |
| I-4 หมายเลขเวอร์ชันเงื่อนไขเพิ่มขึ้นเรื่อยๆ เวอร์ชันเก่าเปลี่ยนแปลงไม่ได้  | ApplyEndorsement                       | ภายใน Aggregate Policy                       | ขัดแย้งเวอร์ชันถูกปฏิเสธ                      |
| I-5 จ่ายสะสมแล้ว + ครั้งนี้ ≤ วงเงินประกัน - ค่า deductible                 | AssessLoss / PaymentExecuted (ผู้ใช้)  | ภายใน Aggregate Claim (ขอบเขตสะสม)           | จ่ายเกินวงเงินคำขอถูกปฏิเสธ                  |
| I-6 ระหว่างสอบสวน อนุมัติจ่ายถูกปฏิเสธทุกครั้ง                              | ApprovePayment                         | สถานะเครื่องจักร Claim                       | การอนุมัติถูกปฏิเสธและแจ้งเหตุระงับ          |
| I-7 สแน็ปช็อตเงื่อนไขขณะแจ้งเหตุเปลี่ยนแปลงไม่ได้ (TermsSnapshot)          | LinkToPolicy                           | ภายใน Aggregate Claim                        | สร้างสแน็ปช็อตแล้วอัปเดตไม่ได้              |
| I-8 แจ้งเหตุหลายครั้งสำหรับความสูญเสียเดียวกันรวมเป็น Aggregate เดียว (คีย์ตัดซ้ำ: วัตถุเอาประกัน+เวลาเกิดเหตุ+ลายนิ้วมือรายละเอียดความสูญเสีย) | NotifyClaim | 内部 Aggregate Claim                          | คืนเลขแจ้งเหตุหลัก ไม่สร้างใหม่               |
| I-9 ผลการจ่ายค่าสินไหม = จำนวนประเมิน - ค่า deductible - ส่วนไม่จ่าย         | AssessLoss                             | ภายใน Aggregate Claim                        | เปลี่ยนจำนวนด้วยมือถูกปฏิเสธ (ต้องประเมินใหม่) |
| I-10 กรมธรรม์ที่ระงับเชื่อมแจ้งเหตุใหม่ไม่ได้                                 | LinkToPolicy                           | ภายใน Aggregate Claim (ตามสถานะ TermsSnapshot) | เชื่อมล้มเหลว แจ้งกรมธรรม์ระงับ               |

## รายการ Entity และ Value Object

| ชื่อ                        | ประเภท         | สังกัด Aggregate      | กลยุทธ์ระบุตัวตน / นิยามความเท่ากัน                            |
| :-------------------------- | :------------- | :-------------------- | :------------------------------------------------------------- |
| Application                 | Entity (Root)  | Application           | applicationId ระบุตัวตนเป็นหนึ่งเดียว                          |
| CoverageRequest             | VO             | Application           | เท่ากันตามค่า (วัตถุเอาประกัน+วงเงินประกัน+ระยะเวลา+ประวัติความสูญเสีย) |
| QuotedTerms                 | VO             | Application           | เท่ากันตามค่า (เบี้ยประกัน+ค่า deductible+ระยะเวลาคอย+รายชื่อข้อยกเว้น+อายุการใช้งาน) |
| UnderwritingCase            | Entity (Root)  | UnderwritingCase      | caseId ระบุตัวตนเป็นหนึ่งเดียว                                  |
| Decision                    | VO             | UnderwritingCase      | เท่ากันตามค่า (decision+reason+premiumAdjustment)               |
| ReinsuranceNeed             | VO             | UnderwritingCase      | เท่ากันตามค่า (สัดส่วนต้องประกันต่อ+ตัวเลือกบริษัทประกันต่อ)  |
| Policy                      | Entity (Root)  | Policy                | policyId ระบุตัวตนเป็นหนึ่งเดียว                                |
| Endorsement                 | Entity         | Policy                | endorsementId; เพิ่มต่อเนื่องตลอดวงจรชีวิต                     |
| TermsVersion                | VO             | Policy                | หมายเลขเวอร์ชันเท่ากัน; เนื้อหาเปลี่ยนแปลงไม่ได้              |
| Deductible / WaitingPeriod  | VO             | Policy                | เท่ากันตามค่า; ตรึงอยู่ใน TermsVersion                          |
| Claim                       | Entity (Root)  | Claim                 | claimId ระบุตัวตนเป็นหนึ่งเดียว (หลังรวมเป็นเลขแจ้งเหตุหลัก)    |
| SurveyRecord                | Entity         | Claim                 | surveyId; เพิ่มตามเวลา                                          |
| AssessmentRecord            | Entity         | Claim                 | assessmentId; ผลการประเมินค่าเสียหายเปลี่ยนแปลงไม่ได้ (แก้ไขใช้บันทึกใหม่) |
| LossDetails                 | VO             | Claim                 | เท่ากันตามค่า (วัตถุเอาประกัน+เวลาเกิดเหตุ+รายละเอียดความสูญเสีย+ลายนิ้วมือ) |
| AssessedLoss                | VO             | Claim                 | เท่ากันตามค่า (จำนวนเงิน+การใช้ค่า deductible+การใช้ข้อยกเว้น)  |
| TermsSnapshot               | VO             | Claim                 | **การอ้างอิงภายนอก** (จาก Policy): เก็บเฉพาะสแน็ปช็อตเวอร์ชันขณะแจ้งเหตุ |
| PaymentInstruction          | Entity (Root)  | PaymentInstruction    | instructionId + claimId คีย์幂emsp;font                           |
| PaymentReceipt              | VO             | PaymentInstruction    | ใบเสร็จเท่ากันตามค่า (สถานะ+จำนวนเงิน+เวลา)                   |
| Party                       | Entity (Root)  | Party                 | partyId ระบุตัวตนเป็นหนึ่งเดียว                                  |
| LossHistory                 | VO             | Party                 | สืบทอดอ่านอย่างเดียว (จำนวน+金额+ช่วงเวลา)                     |
| ReserveView                 | Entity (Root)  | ReserveView           | ฉายภาพอ่านอย่างเดียว (key: วันที่สถิติ+ขอบเขต)                |

## คำอธิบายกฎขอบเขต

- **การทบทวนการอ้างอิงภายนอก** (วัตถุอ้างอิงภายนอกแต่ละชิ้นตอบ "วงจรชีวิตของมันจัดการโดยฝ่ายเราหรือไม่"):
  - `TermsSnapshot` (Claim อ้างอิงเงื่อนไข Policy): **ไม่** — วงจรชีวิตเงื่อนไขจัดการโดย Policy Claim ถือเฉพาะสแน็ปช็อตขณะแจ้งเหตุ ไม่ยกระดับเป็น Aggregate ภายใน ✅
  - `LossHistory` (Underwriting อ้างอิง Party): **ไม่** — ข้อมูลหลักจัดการโดย Party ผู้รับประกันภัยอ่านอย่างเดียว ✅
  - `QuotedTerms` (Underwriting อ้างอิง Quotation): **ไม่** — ใบเสนอราคาจัดการโดย Quotation การตัดสินใจอ้างอิงเฉพาะผลลัพธ์ ✅
  - `PaymentReceipt` (Claim อ้างอิง Payment): **ไม่** — ใบเสร็จวงจรชีวิตจัดการโดย Payment Claim ใช้ใบเสร็จอัปเดตขอบเขตสะสม ✅
- **การระบุรูปแบบ Specification** (กฎธุรกิจแบบ predicate ดึงออกมาชัดเจน):
  - `UnderwritingAcceptanceSpec` (isSatisfiedBy(Application, LossHistory, QuoteTerms) → รับ/เพิ่มเบี้ย/จำกัดความรับผิดชอบ/ปฏิเสธ): กฎการรับประกันภัยอยู่ในรูป predicate "คำขอ X ได้รับหรือไม่" ดึงออกมาเป็น Specification แทนที่จะยัดใน if ของ UnderwritingCase
  - `LossPayableSpec` (isSatisfiedBy(AssessedLoss, TermsSnapshot, CumulativePaid) → จ่ายได้หรือไม่): หลังประเมินค่าเสียหาย "ผ่านเงื่อนไขจ่ายหรือไม่" (รวมค่า deductible ข้อยกเว้น วงเงินสะสม การระงับแยกกัน) ดึงออกมาเป็น Specification ให้ขั้นตอนอนุมัติใช้ร่วมกัน
- **ขอบเขตธุรกรรม**: โดยปกติ 1 ธุรกรรมแก้ไข 1 Aggregate; ความสอดคล้องข้าม Aggregate ดูตารางด้านล่าง
- **กลยุทธ์并发/ล็อก**: หมายเลขเวอร์ชันเงื่อนไข Policy ใช้ Optimistic Lock; ขอบเขตสะสม Claim ใช้ 「消费เหตุการณ์幂emsp;font + คำนวณใหม่」เพื่อหลีกเลี่ยงจุดร้อนล็อก

## กลยุทธ์ความสอดคล้องข้าม Aggregate

| สถานการณ์                  | เหตุการณ์ที่กระตุ้น              | การชดเชย                              | การรับประกัน幂emsp;font | กลยุทธ์ลองใหม่          |
| :-------------------------- | :------------------------------- | :------------------------------------ | :--------------------- | :---------------------- |
| การตัดสินใจมีผลบังคับ → ออกกรมธรรม์ | UnderwritingDecisionMade         | ออกกรมธรรม์ล้มเหลว → เก็บการตัดสินใจไว้ ลองใหม่ออกกรมธรรม์ | eventId การตัดสินใจ     | ≤3 ครั้ง เกินจำนวนส่งคน |
| เปลี่ยนแปลงเงื่อนไข → สแน็ปช็อตแจ้งเหตุใหม่ | EndorsementApplied         | แจ้งเหตุที่เชื่อมแล้วไม่ได้รับผลกระทบ (สแน็ปช็อตเปลี่ยนแปลงไม่ได้) | —                      | ไม่มี (รับประกันโดยการออกแบบ) |
| ใบเสร็จการจ่าย → อัปเดตจ่ายสะสม | PaymentExecuted                | ใบเสร็จเล่นซ้ำคำนวณใหม่สะสม         | paymentId + claimId     | เล่นซ้ำจนกว่าจะตรงกัน  |
| จ่ายสำเร็จ → ฉายภาพเรียกร้องค่าสินไหมรอตัดบัญชี | PaymentExecuted        | Regulatory ฉายภาพคำนวณใหม่           | เหตุการณ์幂emsp;font      | งานกระทบยอดเติมเต็ม    |
| เงินไล่เบี้ยเข้า → หักหลังปิดคดี | SubrogationRecovered           | หักหลังปิดคดี计入เงินไล่เบี้ยรับแล้ว | recoveryId              | ลองใหม่                 |

## ฉบับร่าง Repository Interface

| Aggregate           | เมธอด (ความหมาย)                                      | คำอธิบายความหมาย     | ขอบเขตการสอบถาม           |
| :------------------ | :----------------------------------------------------- | :------------------- | :------------------------ |
| Application         | findByApplicationId / save                             | เก็บถาวร Aggregate คำขอ | ตามเลขที่คำขอ            |
| Application         | findPendingByPartyAndCoverage                          | ตรวจสอบก่อนส่งซ้ำ    | ตามลูกค้า+วัตถุเอาประกัน |
| UnderwritingCase    | findByApplicationId / save                             | เก็บถาวรกรณีรับประกันภัย | ตามเลขที่คำขอ            |
| Policy              | findByPolicyId / save                                  | เก็บถาวร Aggregate กรมธรรม์ | ตามเลขกรมธรรม์          |
| Policy              | findByPartyId(active)                                  | สถานการณ์ต่ออายุและแก้ไข | ตามลูกค้า (เฉพาะกรมธรรม์ที่มีผลบังคับ) |
| Claim               | findByClaimId / save                                   | เก็บถาวร Aggregate เรียกร้องค่าสินไหม | ตามเลขที่แจ้งเหตุ       |
| Claim               | findByPolicyAndLossWindow(policyId, lossDate)          | ตรวจสอบก่อนรวมแจ้งเหตุซ้ำ | ตามกรมธรรม์+ช่วงเวลาเกิดเหตุ |
| PaymentInstruction  | findById / save                                        | เก็บถาวรคำสั่งจ่าย     | ตามเลขคำสั่ง             |
| PaymentInstruction  | findByClaimId                                          | กระทบยอดและลองใหม่   | ตามเลขที่แจ้งเหตุ       |
| Party               | findByPartyId / save                                   | เก็บถาวรข้อมูลหลัก    | ตามเลขลูกค้า             |
| ReserveView         | refresh(dimension, asOf)                               | รีเฟรชฉายภาพอ่านอย่างเดียว | ตามมิติสถิติ            |
