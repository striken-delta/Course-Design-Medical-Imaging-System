"""患者端业务服务"""

from typing import Optional
from sqlalchemy.orm import Session

from app.repositories.prediction_repository import PredictionRepository
from app.repositories.review_repository import ReviewRepository
from app.repositories.patient_repository import PatientRepository, StudyRepository
from app.repositories.slice_repository import SliceRepository
from app.models.user import User


class PatientPortalService:
    def __init__(self, db: Session):
        self.db = db
        self.pred_repo = PredictionRepository(db)
        self.review_repo = ReviewRepository(db)
        self.patient_repo = PatientRepository(db)
        self.study_repo = StudyRepository(db)
        self.slice_repo = SliceRepository(db)

    def get_reports(self, patient_id: int) -> list:
        """获取患者本人的所有报告"""
        studies = self.study_repo.list_by_patient(patient_id)
        results = []
        for study in studies:
            slices = self.slice_repo.list_slices(study_id=study.id, page_size=1000)[0]
            for s in slices:
                preds = self.pred_repo.get_by_slice(s.id)
                for p in preds:
                    has_review = self.review_repo.has_review(p.id)
                    summary, color_code, icon = self._build_summary(p.label, has_review)
                    results.append({
                        "prediction_id": p.id,
                        "study_id": study.id,
                        "study_date": study.created_at.isoformat()[:10] if study.created_at else "",
                        "label": p.label,
                        "confidence": p.confidence,
                        "review_status": "reviewed" if has_review else "unreviewed",
                        "summary": summary,
                        "color_code": color_code,
                        "icon": icon,
                    })
        return results

    def get_report_detail(self, patient_id: int, prediction_id: int) -> Optional[dict]:
        """获取报告详情，校验数据归属"""
        pred = self.pred_repo.get_by_id(prediction_id)
        if not pred:
            return None
        s = self.slice_repo.get_by_id(pred.slice_id)
        if not s:
            return None
        study = self.study_repo.get_by_id(s.study_id)
        if not study or study.patient_id != patient_id:
            return None  # 不属于该患者，返回 None

        has_review = self.review_repo.has_review(pred.id)
        summary, color_code, icon = self._build_summary(pred.label, has_review)

        return {
            "prediction_id": pred.id,
            "study_id": study.id,
            "summary": summary,
            "color_code": color_code,
            "icon": icon,
            "explanation": "以上结果由人工智能辅助分析，仅供您参考。如有疑问请咨询医生。",
            "term_definitions": [
                {"term": "结节", "explanation": "肺部的一个小肿块或阴影，大多数是良性的，但也需要医生进一步评估。"},
                {"term": "置信度", "explanation": "人工智能对分析结果的确信程度。置信度越高，表示 AI 越确信这个结果。"},
                {"term": "复核", "explanation": "医生对 AI 结果进行人工确认的过程，确保结果的准确性。"},
            ],
            "has_3d": has_review,
            "study_id_for_3d": study.id,
            "slice_preview_url": ("/uploads/" + s.file_path) if s.file_path and not s.file_path.startswith("/") else s.file_path,
        }

    def get_progress(self, patient_id: int) -> dict:
        """获取检查进度"""
        studies = self.study_repo.list_by_patient(patient_id)
        study_list = []
        overall_status = "pending_upload"
        for study in studies:
            slices = self.slice_repo.list_slices(study_id=study.id, page_size=1000)[0]
            if not slices:
                status = "pending_upload"
                label = "等待上传"
            else:
                has_prediction = any(self.pred_repo.get_by_slice(sl.id) for sl in slices)
                if not has_prediction:
                    status = "processing"
                    label = "检测中"
                else:
                    has_review = any(
                        self.review_repo.has_review(p.id)
                        for sl in slices for p in self.pred_repo.get_by_slice(sl.id)
                    )
                    status = "reviewed" if has_review else "result_ready"
                    label = "已复核" if has_review else "已出结果"

            study_list.append({
                "study_id": study.id,
                "study_date": study.created_at.isoformat()[:10] if study.created_at else "",
                "status": status,
                "status_label": label,
            })
            # 提升整体状态
            order = {"pending_upload": 0, "processing": 1, "result_ready": 2, "reviewed": 3}
            if order.get(status, 0) > order.get(overall_status, 0):
                overall_status = status

        status_labels = {"pending_upload": "等待上传切片", "processing": "AI 正在分析中",
                         "result_ready": "结果已出，等待医生确认", "reviewed": "医生已复核确认"}
        return {
            "status": overall_status,
            "status_label": status_labels.get(overall_status, "未知"),
            "description": "当前检查进度状态",
            "studies": study_list,
        }

    def _build_summary(self, label: str, has_review: bool):
        if label == "non_nodule" and has_review:
            return "本次检查未发现明显异常，请按医生建议定期复查", "green", "check"
        elif label == "nodule" and not has_review:
            return "本次检查发现疑似异常，医生正在进一步确认", "yellow", "warning"
        elif label == "nodule" and has_review:
            return "本次检查发现疑似结节，建议咨询医生了解下一步安排", "red", "close"
        else:
            return "当前检查结果暂未生成，请稍后查看或联系医生", "yellow", "warning"
