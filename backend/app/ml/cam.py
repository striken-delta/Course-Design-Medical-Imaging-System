"""
Grad-CAM 热力图生成器

Grad-CAM (Gradient-weighted Class Activation Mapping):
一种模型可解释性方法，通过可视化模型"关注"的图像区域，
帮助医生理解模型的判断依据。

流程:
1. 获取目标卷积层的激活值和梯度
2. 对梯度做全局平均池化得到权重
3. 权重加权激活值得到热力图
4. 上采样到原始图像尺寸
5. 与原始图像叠加，保存为 PNG
"""

import cv2
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from pathlib import Path
from typing import Optional

from app.core.config import HEATMAP_DIR


class GradCAMGenerator:
    """Grad-CAM 热力图生成器"""

    def __init__(self, predictor):
        self.predictor = predictor

    def generate(
        self,
        file_path: str,
        prediction_id: int,
        target_class: int = 1,  # 默认针对 nodule 类别生成热力图
    ) -> Optional[str]:
        """
        生成 Grad-CAM 热力图

        Args:
            file_path: 切片文件路径
            prediction_id: 关联的预测 ID
            target_class: 目标类别（0=non_nodule, 1=nodule），默认针对 nodule

        Returns:
            热力图保存路径（相对路径），失败返回 None
        """
        try:
            # 执行带梯度的前向传播
            self.predictor.forward_for_cam(target_class)

            # 获取激活值和梯度
            activations, gradients = self.predictor.get_activations_and_gradients()
            if activations is None or gradients is None:
                print("[GradCAM] 无法获取激活值/梯度，跳过热力图生成")
                return None

            # 计算权重：梯度全局平均池化
            weights = torch.mean(gradients, dim=(2, 3), keepdim=True)  # (1, C, 1, 1)

            # 加权求和得到 CAM
            cam = torch.sum(weights * activations, dim=1, keepdim=True)  # (1, 1, H, W)
            cam = F.relu(cam)  # 只关注对目标类别有正向贡献的区域

            # 上采样到原始图像尺寸
            cam = F.interpolate(cam, size=(224, 224), mode="bilinear", align_corners=False)

            # 归一化到 [0, 1]
            cam = cam.squeeze().cpu().detach().numpy()
            cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)

            # 加载原始图像
            if not Path(file_path).is_absolute():
                from app.core.config import UPLOAD_DIR
                full_path = UPLOAD_DIR / file_path
            else:
                full_path = Path(file_path)

            if not full_path.exists():
                return None

            original = Image.open(full_path).convert("RGB")
            original = original.resize((224, 224))
            original_np = np.array(original).astype(np.float32) / 255.0

            # 应用热力图颜色映射
            heatmap = cv2.applyColorMap(np.uint8(255 * cam), cv2.COLORMAP_JET)
            heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0

            # 叠加：热力图 × 0.4 + 原图 × 0.6
            superimposed = heatmap * 0.4 + original_np * 0.6
            superimposed = np.uint8(255 * superimposed / superimposed.max())

            # 保存
            save_dir = HEATMAP_DIR / str(prediction_id)
            save_dir.mkdir(parents=True, exist_ok=True)
            save_path = save_dir / "cam.png"
            Image.fromarray(superimposed).save(save_path)

            # 返回相对路径
            return f"heatmaps/{prediction_id}/cam.png"

        except Exception as e:
            print(f"[GradCAM] 热力图生成失败: {e}")
            return None
