"""Plant disease diagnosis domain"""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from app.modules.yolo.domain.value_objects import BBox, Detection


@dataclass(frozen=True, slots=True)
class DiseaseSeverity:
    level: str
    percentage: float
    score: float


@dataclass(frozen=True, slots=True)
class DiseaseInfo:
    code: str
    name_th: str
    name_en: str
    pathogen_type: str
    treatment: tuple[str, ...] = ()
    prevention: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class DiseaseDetection:
    bbox: BBox
    disease_code: str
    disease_name_th: str
    disease_name_en: str
    pathogen_type: str
    confidence: float
    severity: DiseaseSeverity
    affected_area_pct: float

    def to_dict(self) -> dict[str, Any]:
        return {"bbox": {"x_center": self.bbox.x_center,
                         "y_center": self.bbox.y_center,
                         "width": self.bbox.width,
                         "height": self.bbox.height},
                "disease_code": self.disease_code,
                "disease_name_th": self.disease_name_th,
                "disease_name_en": self.disease_name_en,
                "pathogen_type": self.pathogen_type,
                "confidence": self.confidence,
                "severity": {"level": self.severity.level,
                             "percentage": self.severity.percentage,
                             "score": self.severity.score},
                "affected_area_pct": self.affected_area_pct}


@dataclass(frozen=True, slots=True)
class PlantDiagnosis:
    image_id: uuid.UUID
    plant_species: str | None
    detections: tuple[DiseaseDetection, ...]
    overall_severity: str
    overall_health_score: float
    recommendations: tuple[str, ...]
    treatment_plan: tuple[dict[str, Any], ...]
    follow_up_days: int
    confidence: float
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {"image_id": str(self.image_id),
                "plant_species": self.plant_species,
                "overall_severity": self.overall_severity,
                "overall_health_score": self.overall_health_score,
                "detections": [d.to_dict() for d in self.detections],
                "recommendations": list(self.recommendations),
                "treatment_plan": list(self.treatment_plan),
                "follow_up_days": self.follow_up_days,
                "confidence": self.confidence,
                "generated_at": self.generated_at.isoformat()}


DISEASE_CATALOG: dict[str, DiseaseInfo] = {
    "rice-blast": DiseaseInfo("rice-blast", "โรคไหม้ข้าว", "Rice Blast",
        "fungal", ("พ่น tricyclazole 20% WP", "ลดปุ๋ยไนโตรเจน"),
        ("ใช้พันธุ์ต้านทาน", "ไม่ปลูกหนาแน่น")),
    "tomato-late-blight": DiseaseInfo("tomato-late-blight",
        "โรคใบไหม้มะเขือเทศ", "Tomato Late Blight", "fungal",
        ("พ่น chlorothalonil", "ตัดใบที่เป็นโรค"),
        ("ระบายอากาศดี", "หลีกเลี่ยงรดน้ำใบ")),
    "bacterial-leaf-blight": DiseaseInfo("bacterial-leaf-blight",
        "โรคใบข้าวแห้ง", "Bacterial Leaf Blight", "bacterial",
        ("ใช้ copper hydroxide", "ระบายน้ำ"),
        ("ไม่ใส่ปุ๋ยไนโตรเจนเกิน", "ใช้พันธุ์ต้านทาน")),
}


class PlantDiseaseDiagnoser:
    def diagnose(self, detections: list[Detection],
                  class_id_to_code: dict[int, str],
                  plant_species: str | None = None) -> PlantDiagnosis:
        disease_dets: list[DiseaseDetection] = []
        for d in detections:
            code = class_id_to_code.get(d.class_id)
            if not code or code not in DISEASE_CATALOG:
                continue
            info = DISEASE_CATALOG[code]
            sev = self.calc_severity(d.bbox)
            disease_dets.append(DiseaseDetection(
                bbox=d.bbox, disease_code=code,
                disease_name_th=info.name_th,
                disease_name_en=info.name_en,
                pathogen_type=info.pathogen_type,
                confidence=d.confidence, severity=sev,
                affected_area_pct=d.bbox.width * d.bbox.height))
        rank = {"healthy": 0, "mild": 1, "moderate": 2,
                 "severe": 3, "critical": 4}
        overall = "healthy"
        for dd in disease_dets:
            if rank[dd.severity.level] > rank[overall]:
                overall = dd.severity.level
        health_score = max(0.0, 100.0 - sum(
            dd.severity.percentage * 100 for dd in disease_dets))
        recommendations: list[str] = []
        for dd in disease_dets:
            info = DISEASE_CATALOG[dd.disease_code]
            recommendations.extend(info.treatment[:1])
        treatment_plan: list[dict[str, Any]] = []
        if disease_dets:
            info = DISEASE_CATALOG[disease_dets[0].disease_code]
            treatment_plan.append({"day": 0, "action": "spray",
                                    "product": info.treatment[0] if info.treatment else "-"})
            treatment_plan.append({"day": 7, "action": "inspect"})
            treatment_plan.append({"day": 14, "action": "spray",
                                    "product": info.treatment[0] if info.treatment else "-"})
        conf_avg = (sum(d.confidence for d in disease_dets) / len(disease_dets)
                     if disease_dets else 1.0)
        return PlantDiagnosis(
            image_id=uuid.uuid4(), plant_species=plant_species,
            detections=tuple(disease_dets), overall_severity=overall,
            overall_health_score=round(health_score, 2),
            recommendations=tuple(dict.fromkeys(recommendations)),
            treatment_plan=tuple(treatment_plan),
            follow_up_days=7, confidence=conf_avg)

    @staticmethod
    def calc_severity(bbox: BBox) -> DiseaseSeverity:
        pct = bbox.width * bbox.height
        if pct < 0.05:
            return DiseaseSeverity("mild", pct, pct / 0.05 * 0.25)
        if pct < 0.20:
            return DiseaseSeverity("moderate", pct,
                                    0.25 + (pct - 0.05) / 0.15 * 0.35)
        if pct < 0.50:
            return DiseaseSeverity("severe", pct,
                                    0.60 + (pct - 0.20) / 0.30 * 0.25)
        return DiseaseSeverity("critical", pct, 0.85 + min(pct, 1.0) * 0.15)
