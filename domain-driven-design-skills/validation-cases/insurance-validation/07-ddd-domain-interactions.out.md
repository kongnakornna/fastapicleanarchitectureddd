# 07 — ผลผลิต ddd-domain-interactions (Blind Run)

> อินพุต: `01`~`06`
> ไฟล์นี้เป็นผลลัพธ์การจำลองการทำงานของ `ddd-domain-interactions` ใน blind run โดย**ไม่ได้อ้างอิง**วัสดุ ground truth (กรณีนี้ไม่มีการอ้างอิงการใช้งานจริง)

## สารบัญ Domain Event

### เผยแพร่โดย Quotation Bounded Context

| เหตุการณ์                   | Aggregate ต้นทาง   | เงื่อนไขที่กระตุ้น               | ช่องข้อมูลสำคัญ                                | ขอบเขต       |
| :-------------------------- | :------------------ | :------------------------------- | :--------------------------------------------- | :----------- |
| ApplicationSubmitted        | Application         | SubmitApplication สำเร็จ         | applicationId, partyId, coverageRequest        | Integration  |
| ApplicationQuarantined      | Application         | ข้อมูลสำคัญขาดหาย               | applicationId, missingFields                   | Domain       |
| QuotePresented              | Application         | ใบเสนอราคามา (รวมลดระดับ)      | applicationId, quoteTerms, degraded            | Integration  |

### เผยแพร่โดย Underwriting Bounded Context

| เหตุการณ์                   | Aggregate ต้นทาง      | เงื่อนไขที่กระตุ้น | ช่องข้อมูลสำคัญ                                                  | ขอบเขต       |
| :-------------------------- | :-------------------- | :--------------- | :--------------------------------------------------------------- | :----------- |
| UnderwritingStarted         | UnderwritingCase      | รับประกันภัยรับ   | caseId, applicationId                                             | Domain       |
| UnderwritingDecisionMade    | UnderwritingCase      | การตัดสินใจมีผลบังคับ | caseId, applicationId, decision, reason, premiumAdjustment        | Integration  |
| ReinsuranceRequested        | UnderwritingCase      | เกินจำนวนกันความเสี่ยงของตนเอง | caseId, reinsuranceNeed                                           | Domain       |

### เผยแพร่โดย Policy Bounded Context

| เหตุการณ์           | Aggregate ต้นทาง | เงื่อนไขที่กระตุ้น | ช่องข้อมูลสำคัญ                                                        | ขอบเขต       |
| :------------------ | :--------------- | :--------------- | :--------------------------------------------------------------------- | :----------- |
| PolicyIssued        | Policy           | ออกกรมธรรม์สำเร็จ | policyId, applicationId, termsVersion, deductible, waitingPeriod       | Integration  |
| EndorsementApplied  | Policy           | แก้ไขมีผลบังคับ   | policyId, newTermsVersion, effectiveAt                                 | Integration  |
| PolicyLapsed        | Policy           | ระงับ              | policyId, lapsedAt                                                     | Integration  |
| PolicyReinstated    | Policy           | กู้คืน             | policyId, newWaitingPeriodStart                                        | Integration  |
| PolicyRenewed       | Policy           | ต่ออายุ           | policyId, newPeriod                                                    | Domain       |

### เผยแพร่โดย Claim Bounded Context

| เหตุการณ์                       | Aggregate ต้นทาง | เงื่อนไขที่กระตุ้น               | ช่องข้อมูลสำคัญ                          | ขอบเขต                     |
| :------------------------------ | :--------------- | :------------------------------- | :--------------------------------------- | :-------------------------- |
| ClaimNotified                   | Claim            | รับแจ้งเหตุ                       | claimId, policyId, lossDetails           | Integration                 |
| DuplicateClaimMerged            | Claim            | รวมแจ้งเหตุซ้ำ                    | claimId, mergedClaimId, primaryClaimId   | Domain                      |
| ClaimLinkedToPolicy             | Claim            | เชื่อมสำเร็จ                       | claimId, policyId, termsSnapshot         | Integration                 |
| ClaimPendingInformation         | Claim            | เอกสารมาช้า                       | claimId, missingInfo                     | Domain                      |
| SurveyCompleted                 | Claim            | ตรวจสอบบันทึก                     | claimId, surveyReport, estimate          | Domain                      |
| LossAssessed                    | Claim            | ผลการประเมินค่าเสียหาย            | claimId, assessedLoss                    | Integration                 |
| FraudInvestigationOpened        | Claim            | สงสัยทุจริต                       | claimId, reason                          | Integration                 |
| FraudInvestigationConcluded     | Claim            | สอบสวนสิ้นสุด                      | claimId, conclusion, (กู้คืนการจ่าย/ปฏิเสธจ่าย) | Integration           |
| PaymentApproved                 | Claim            | อนุมัติผ่าน                        | claimId, approvedAmount, approver        | Integration                 |
| PaymentRejected                 | Claim            | ปฏิเสธการอนุมัติ (รวมระหว่างระงับ) | claimId, reason                          | Domain                      |
| PaymentRequested                | Claim            | อนุมัติผ่านแล้วส่งคำสั่ง          | claimId, instructionId, amount           | Integration (→ Payment)     |
| ClaimClosed                     | Claim            | ปิดคดี                             | claimId, closedAt, totalPaid             | Integration                 |
| SubrogationRecovered            | Claim            | เงินไล่เบี้ยเข้า                   | claimId, recoveredAmount                 | Integration                 |

### เผยแพร่โดย Payment Bounded Context

| เหตุการณ์                       | Aggregate ต้นทาง      | เงื่อนไขที่กระตุ้น     | ช่องข้อมูลสำคัญ                                     | ขอบเขต       |
| :------------------------------ | :-------------------- | :--------------------- | :-------------------------------------------------- | :----------- |
| PaymentInstructionAccepted      | PaymentInstruction    | รับคำสั่ง              | instructionId, claimId                               | Domain       |
| PaymentExecuted                 | PaymentInstruction    | จ่ายสำเร็จใบเสร็จ     | instructionId, claimId, amount, paidAt               | Integration  |
| PaymentFailed                   | PaymentInstruction    | จ่ายล้มเหลว           | instructionId, claimId, failureType, retryCount      | Integration  |

## สัญญาเหตุการณ์ Integration (ภายนอก)

| สัญญา                                                                                                    | ทิศทาง                                    | ตัวกลาง    | เวอร์ชัน | หมายเหตุ                          |
| :------------------------------------------------------------------------------------------------------- | :---------------------------------------- | :--------- | :------- | :-------------------------------- |
| ApplicationSubmitted / QuotePresented                                                                    | Quotation → Underwriting                  | Event Bus  | v1       | Published Language                |
| UnderwritingDecisionMade                                                                                 | Underwriting → Policy                     | Event Bus  | v1       | ประเภทการตัดสินใจแบบมีเวอร์ชัน    |
| กลุ่ม PolicyEvent (PolicyIssued / EndorsementApplied / PolicyLapsed)                                     | Policy → Claim / Regulatory               | Event Bus  | v1       | OHS + PL; โครงสร้างย่อย TermsSnapshot |
| กลุ่ม ClaimEvent (ClaimNotified / ClaimLinkedToPolicy / LossAssessed / PaymentRequested / ClaimClosed)    | Claim → Policy? / Payment / Regulatory    | Event Bus  | v1       | Claim → Payment เป็นคำสั่ง        |
| PaymentInstruction / PaymentExecuted                                                                     | Claim ↔ Payment                           | Event Bus  | v1       | คีย์幂emsp;font rule เปลี่ยนแปลงไม่ได้ |
| ข้อมูลอินพุตฉายภาพส่ง                                                                                   | Policy / Claim / Payment → Regulatory     | Event Bus  | v1       | เหตุการณ์ธุรกิจฉายภาพเดิม         |

## กลยุทธ์幂emsp;fontและเล่นซ้ำ

| เหตุการณ์                   | คีย์幂emsp;font                        | หน้าต่างตัดซ้ำ | กฎเล่นซ้ำ                | การจัดการผิดปกติ        |
| :-------------------------- | :------------------------------------ | :------------- | :----------------------- | :----------------------- |
| ApplicationSubmitted        | applicationId                         | เก็บถาวร        | เล่นซ้ำไม่สร้างคำขอซ้ำ   | พื้นที่กักกันเติมด้วยมือ |
| UnderwritingDecisionMade    | caseId + decisionVersion              | เก็บถาวร        | เล่นซ้ำไม่เปลี่ยน        | ออกกรมธรรม์แล้วปฏิเสธเปลี่ยน |
| PolicyIssued                | policyId                              | เก็บถาวร        | เล่นซ้ำไม่ออกกรมธรรม์ซ้ำ | ออกกรมธรรม์ล้มเหลวลองใหม่ |
| EndorsementApplied          | policyId + endorsementId              | เก็บถาวร        | เวอร์ชันเพิ่มขึ้นเรื่อยๆ  | ขัดแย้งเวอร์ชันปฏิเสธ    |
| ClaimNotified               | คีย์ตัดซ้ำ (วัตถุเอาประกัน+ช่วงเวลา+รายละเอียด) | เก็บถาวร | รวมเข้าแจ้งเหตุหลัก      | คืนเลขแจ้งเหตุหลัก       |
| PaymentRequested            | instructionId                         | เก็บถาวร        | ส่งคำสั่งใหม่ (幂emsp;font) | คำสั่งสูญหายส่งอัตโนมัติ |
| PaymentExecuted             | paymentId + claimId                   | เก็บถาวร        | เล่นซ้ำคำนวณจ่ายสะสมใหม่ | กระทบยอดเติมเต็ม        |
| ClaimClosed                 | claimId                               | เก็บถาวร        | ปิดคดีแล้วห้ามจ่ายใหม่    | เงินไล่เบี้ยรับต่อเนื่อง |

## Domain Service

| บริการ                      | Bounded Context     | ความรับผิดชอบ                                                    | เหตุผลไม่วางใน Aggregate                           |
| :-------------------------- | :------------------ | :---------------------------------------------------------------- | :-------------------------------------------------- |
| QuoteService                | Quotation           | เรียก ACL อัตราภายนอก ประกอบ QuoteTerms กลยุทธ์ลดระดับ           | เรียกภายนอก + กลยุทธ์อัตรา ไม่ใช่ Invariant Application |
| UnderwritingService         | Underwriting        | จัดลำดับการตัดสิน UnderwritingAcceptanceSpec การประเมินการประกันต่อ | กลุ่มกฎวิวัฒนาการข้ามคำขอ อิสระจากสถานะ Aggregate |
| LossAssessmentService       | Claim               | ดำเนิน LossPayableSpec (ค่า deductible/ข้อยกเว้น/สะสม/ระงับ) คำนวณจ่าย | กลุ่มกฎ predicate วิวัฒนาการอิสระ ให้ขั้นตอนอนุมัติใช้ร่วมกัน |
| ClaimDeduplicationService   | Claim               | คำนวณลายนิ้วมือตัดซ้ำแจ้งเหตุและนำทางการรวม                       | บทบาทจัดลำดับที่ทำงานร่วมกับ Repository           |
| PaymentGateway              | Payment             | แปลงคำสั่ง → ข้อความระบบการเงินภายนอกและแปลงใบเสร็จ             | ขอบเขตโครงสร้างพื้นฐาน ป้องกันการทำให้ Domain Model สกปรก |

## รายการ Factory

| Factory / เมธอด                                                   | เป้าหมายที่สร้าง         | เงื่อนไขที่สร้าง        | กฎตรวจสอบ                       | สถานะเริ่มต้น              |
| :---------------------------------------------------------------- | :----------------------- | :---------------------- | :------------------------------ | :------------------------ |
| ApplicationFactory.fromSubmission(input)                          | Application              | ตัวตนลูกค้ามีอยู่       | I-1 ป้องกันซ้ำ; ช่องข้อมูลครบถ้วน | ยื่นแล้ว                   |
| QuoteFactory.fromRateResult(application, quoteTerms)              | QuotedTerms              | คำขอที่มีผลบังคับ      | I-2 ใบเสนอราคาไม่สัญญา; สร้างอายุการใช้งาน | เสนอราคาแล้ว              |
| UnderwritingCaseFactory.start(application, quote)                 | UnderwritingCase         | คำขอเสนอราคาแล้ว       | I-3 ไม่มีกรณีรับประกันภัยซ้ำ    | กำลังรับประกันภัย        |
| PolicyFactory.issue(decision, terms)                              | Policy                   | การตัดสินใจรับประกัน   | I-3 การตัดสินใจเปลี่ยนแปลงไม่ได้; เงื่อนไขครบ | มีผลบังคับ               |
| EndorsementFactory.apply(policy, change)                          | Endorsement              | กรมธรรม์ที่มีผลบังคับ   | I-4 เวอร์ชันเพิ่มขึ้นเรื่อยๆ    | รอผลบังคับ (กฎจุดมีผลบังคับ) |
| ClaimFactory.notify(policySnapshot, lossDetails)                  | Claim                    | กรมธรรม์ไม่ระงับ       | I-10 ระงับเชื่อมไม่ได้; I-8 ตัดซ้ำ | แจ้งเหตุแล้ว               |
| PaymentInstructionFactory.create(claim, approvedAmount)           | PaymentInstruction       | อนุมัติผ่านและไม่ระงับ | I-6 ระงับห้ามจ่าย; I-5 วงเงินสะสม | รอดำเนินการ               |

## ผู้สมัครรับและผลข้างเคียง

| เหตุการณ์                       | ผู้สมัครรับ         | การกระทำที่กระตุ้น                          | กลยุทธ์ชดเชย           | ตัวชี้วัดตรวจสอบ          |
| :------------------------------ | :----------------- | :-------------------------------------------- | :--------------------- | :------------------------ |
| UnderwritingDecisionMade        | Policy             | ออกกรมธรรม์ (เมื่อรับประกัน)                 | ออกกรมธรรม์ล้มเหลวลองใหม่ | ความล่าช้าการตัดสินใจ→ออกกรมธรรม์ |
| PaymentExecuted                 | Claim              | อัปเดตจ่ายสะสม → เมื่อจำเป็นตรวจสอบปิดคดี | เล่นซ้ำคำนวณใหม่      | ขอบเขตสะสมเบี่ยงเบน      |
| EndorsementApplied              | Claim              | แจ้งเหตุที่เชื่อมแล้วไม่ย้อนกลับ (สแน็ปช็อตเปลี่ยนแปลงไม่ได้) | ไม่มี (รับประกันการออกแบบ) | ความขัดแย้งพร้อมกัน      |
| ClaimLinkedToPolicy             | Regulatory         | รีเฟรชฉายภาพเรียกร้องค่าสินไหมรอตัดบัญชี     | กระทบยอดเติมเต็ม      | ความล่าช้าฉายภาพ          |
| PaymentExecuted                 | Regulatory         | รีเฟรชฉายภาพเรียกร้องค่าสินไหมรอตัดบัญชี     | กระทบยอดเติมเต็ม      | ความล่าช้าฉายภาพ          |
| ClaimClosed                     | Regulatory         | ฉายภาพส่ง (ขอบเขตปิดคดี)                     | ส่งย้อนหลัง            | ความคลาดเคลื่อนกระทบยอดส่ง |
| PolicyIssued / PolicyLapsed     | Regulatory         | ฉายภาพส่ง (ขอบเขตกรมธรรม์)                   | ส่งย้อนหลัง            | ความคลาดเคลื่อนกระทบยอดส่ง |
| PaymentRequested                | Payment            | รับและดำเนินการคำสั่ง                          | ลองใหม่แบบ幂emsp;font    | อัตราความสำเร็จจ่าย/ความล่าช้า |
| FraudInvestigationOpened        | การปฏิบัติตาม (สอบสวน) | สร้างงานสอบสวน                               | แยกกันระงับ            | วงจรสอบสวน               |
| QuotePresented                  | Underwriting       | รับประกันภัยรับ                                | ไม่มี                   | อัตราการเปลี่ยนใบเสนอราคา→การตัดสินใจ |