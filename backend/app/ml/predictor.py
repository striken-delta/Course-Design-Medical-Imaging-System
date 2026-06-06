"""
推理预测器

流程（对应详细设计 §9.2）:
1. 根据 slice_id 查询切片路径
2. 调用预处理函数得到输入 Tensor
3. 模型执行前向推理
4. 对输出 logits 执行 softmax
5. 取得最大概率类别作为预测标签
6. 将概率作为置信度
7. 写入 predictions 表
"""

import time
import torch
import torch.nn.functional as F
from typing import Tuple

from app.ml.model_loader import ModelLoader, LungNoduleClassifier
from app.ml.preprocess import Preprocessor


# 标签映射（对应详细设计 §9.2）
LABEL_MAP = {
    0: "non_nodule",
    1: "nodule",
}

LABEL_CN = {
    "non_nodule": "未发现结节",
    "nodule": "疑似结节",
}


class Predictor:
    """肺结节二分类预测器"""

    def __init__(self, model_loader: ModelLoader, preprocessor: Preprocessor):
        self.model_loader = model_loader
        self.preprocessor = preprocessor
        self.model: LungNoduleClassifier = None
        self.model_version: str = ""

        # 缓存最近一次用于 CAM 的数据
        self._last_tensor: torch.Tensor = None
        self._last_file_path: str = ""

    def ensure_loaded(self):
        """确保模型已加载（延迟加载）"""
        if self.model is None:
            self.model, self.model_version = self.model_loader.load()

    def predict(self, file_path: str) -> dict:
        """
        对单张切片执行推理

        返回:
        {
            "label": "nodule" | "non_nodule",
            "confidence": float,
            "model_version": str,
            "inference_time_ms": int,
            "logits": [float, float],  # raw logits for CAM
        }
        """
        self.ensure_loaded()
        device = self.model_loader.get_device()

        # 预处理
        tensor, error = self.preprocessor.process(file_path, device)
        if error:
            raise RuntimeError(f"预处理失败: {error}")

        # 保存 tensor 供后续 CAM 使用
        self._last_tensor = tensor
        self._last_file_path = file_path

        # 前向推理 (no_grad 减少内存)
        start_time = time.perf_counter()
        with torch.no_grad():
            logits = self.model(tensor)
            probs = F.softmax(logits, dim=1)
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)

        # 取最大概率类别
        pred_class = int(torch.argmax(probs, dim=1).item())
        confidence = round(float(probs[0, pred_class].item()), 4)
        label = LABEL_MAP[pred_class]

        return {
            "label": label,
            "confidence": confidence,
            "model_version": self.model_version,
            "inference_time_ms": elapsed_ms,
            "logits": logits,
            "probabilities": probs,
        }

    def forward_for_cam(self, target_class: int):
        """
        为 Grad-CAM 执行带梯度的前向传播

        在目标类别上做反向传播，使 hook 捕获梯度
        """
        self.ensure_loaded()
        if self._last_tensor is None:
            raise RuntimeError("请先调用 predict() 再进行 CAM 生成")

        # 使用带梯度的 tensor 重新前向
        tensor = self._last_tensor.clone().detach().requires_grad_(True)
        self.model.zero_grad()

        logits = self.model(tensor)
        # 对目标类别的 logit 做反向传播
        target = logits[0, target_class]
        target.backward()

        return tensor

    def get_activations_and_gradients(self):
        """获取最后卷积层的激活值和梯度（供 Grad-CAM 使用）"""
        self.ensure_loaded()
        return self.model.activations, self.model.gradients
