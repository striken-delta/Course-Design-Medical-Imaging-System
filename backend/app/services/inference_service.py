"""
推理业务服务

使用真实的 ResNet-18 模型进行肺结节二分类推理。
若 ML 库不可用或加载失败，回退到模拟存根。
"""

import random
import logging
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.repositories.slice_repository import SliceRepository
from app.repositories.prediction_repository import PredictionRepository
from app.repositories.marker_repository import MarkerRepository
from app.core.errors import ErrorCode
from app.models.prediction import Prediction

logger = logging.getLogger(__name__)

# 全局单例：模型加载器和预测器（进程内复用，避免每次推理重复加载）
_predictor = None
_ml_available = None  # None=未检测, True=可用, False=不可用


def _get_predictor():
    """获取预测器单例（进程内复用）"""
    global _predictor, _ml_available

    if _predictor is not None:
        return _predictor

    if _ml_available is False:  # 已尝试过且失败
        return None

    try:
        from app.ml.model_loader import ModelLoader
        from app.ml.preprocess import Preprocessor
        from app.ml.predictor import Predictor

        loader = ModelLoader()
        preprocessor = Preprocessor(input_size=ModelLoader.INPUT_SIZE)
        _predictor = Predictor(loader, preprocessor)
        _predictor.ensure_loaded()
        _ml_available = True
        logger.info("[Inference] ML 模型加载成功")
    except ImportError as e:
        logger.warning(f"[Inference] ML 库未安装 ({e})，回退到模拟模式")
        _ml_available = False
        _predictor = None
    except Exception as e:
        logger.warning(f"[Inference] ML 模型加载失败 ({e})，回退到模拟模式")
        _ml_available = False
        _predictor = None

    return _predictor


class InferenceService:
    """推理服务"""

    def __init__(self, db: Session):
        self.slice_repo = SliceRepository(db)
        self.pred_repo = PredictionRepository(db)
        self.marker_repo = MarkerRepository(db)

    def run_inference(self, slice_id: int) -> Tuple[Optional[Prediction], Optional[ErrorCode]]:
        """执行推理"""
        s = self.slice_repo.get_by_id(slice_id)
        if not s:
            return None, ErrorCode.NOT_FOUND

        predictor = _get_predictor()

        if predictor is not None and _ml_available:
            return self._ml_inference(slice_id, s.file_path, s.study_id)
        else:
            return self._stub_inference(slice_id, s.study_id)

    def _ml_inference(self, slice_id: int, file_path: str, study_id: int
                      ) -> Tuple[Optional[Prediction], Optional[ErrorCode]]:
        """使用 ML 模型推理"""
        try:
            result = _predictor.predict(file_path)
        except Exception as e:
            logger.error(f"[Inference] 推理失败: {e}")
            return None, ErrorCode.INFERENCE_FAILED

        # 写入预测记录
        pred = self.pred_repo.create(
            slice_id=slice_id,
            label=result["label"],
            confidence=result["confidence"],
            model_version=result["model_version"],
            inference_time_ms=result["inference_time_ms"],
        )

        # 生成 Grad-CAM 热力图（扩展功能，失败不影响主流程）
        try:
            from app.core.config import BASE_DIR
            import os
            if os.getenv("ENABLE_GRAD_CAM", "0") == "1":
                from app.ml.cam import GradCAMGenerator
                cam_gen = GradCAMGenerator(_predictor)
                heatmap_path = cam_gen.generate(file_path, pred.id)
                if heatmap_path:
                    pred.heatmap_path = heatmap_path
                    pred = self.pred_repo.db.merge(pred)
                    self.pred_repo.db.commit()
        except Exception as e:
            logger.warning(f"[Inference] Grad-CAM 生成失败: {e}")

        # 若预测为 nodule，生成 3D 标记点（演示用途）
        if result["label"] == "nodule":
            self._generate_marker(study_id, slice_id, result["confidence"])

        return pred, None

    def _stub_inference(self, slice_id: int, study_id: int
                        ) -> Tuple[Optional[Prediction], Optional[ErrorCode]]:
        """模拟推理存根（ML 不可用时的回退方案）"""
        label = "nodule" if random.random() < 0.4 else "non_nodule"
        confidence = round(random.uniform(0.60, 0.99), 4)
        inference_time_ms = random.randint(200, 1800)
        model_version = "resnet18_v1.0_stub"

        pred = self.pred_repo.create(
            slice_id=slice_id, label=label, confidence=confidence,
            model_version=model_version, inference_time_ms=inference_time_ms)

        if label == "nodule":
            self._generate_marker(study_id, slice_id, confidence)

        return pred, None

    def _generate_marker(self, study_id: int, slice_id: int, confidence: float):
        """生成演示用 3D 标记点"""
        self.marker_repo.create(
            study_id=study_id, slice_id=slice_id,
            x=round(random.uniform(-1.5, 1.5), 2),
            y=round(random.uniform(-1.0, 1.5), 2),
            z=round(random.uniform(-1.2, 1.2), 2),
            confidence=confidence,
        )
