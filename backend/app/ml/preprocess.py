"""
图像预处理

流程（对应详细设计 §9.1）:
1. 读取切片图片文件
2. 转换为 RGB 三通道格式
3. 缩放到模型输入尺寸 (224×224)
4. 像素值归一化到模型要求范围
5. 转换为 Tensor
6. 增加 batch 维度
7. 放入目标设备
"""

import torch
import torchvision.transforms as transforms
from PIL import Image, UnidentifiedImageError
from pathlib import Path
from typing import Optional, Tuple

from app.core.config import UPLOAD_DIR


# ImageNet 标准均值和标准差（ResNet 预训练时使用）
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

# CT 影像专用的归一化参数（肺窗: WL=-600, WW=1500，对应 HU 范围约 [-1350, 150]）
# 用于将 CT 值裁剪到肺窗范围后做 min-max 归一化
CT_LUNG_WINDOW_CENTER = -600
CT_LUNG_WINDOW_WIDTH = 1500


class Preprocessor:
    """CT 切片图像预处理器"""

    def __init__(self, input_size: Tuple[int, int] = (224, 224)):
        self.input_size = input_size

        # 标准预处理流程：中心裁剪 224x224 → 归一化
        # 模型训练时使用 224x224 的结节区域 patch，
        # 推理时对完整 CT 切片做中心裁剪以匹配训练输入分布
        self.transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.CenterCrop(input_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ])

    def load_image(self, file_path: str) -> Tuple[Optional[Image.Image], Optional[str]]:
        """
        从文件路径加载 PIL Image

        返回 (Image, None) 表示成功，(None, error_message) 表示失败
        """
        # 解析路径：可能是相对路径（如 ct_slices/1/slice_0_xxx.png）
        if not Path(file_path).is_absolute():
            full_path = UPLOAD_DIR / file_path
        else:
            full_path = Path(file_path)

        if not full_path.exists():
            return None, f"文件不存在: {full_path}"

        try:
            image = Image.open(full_path)
            return image, None
        except UnidentifiedImageError:
            return None, f"无法识别的图像格式: {file_path}"
        except Exception as e:
            return None, f"图像加载失败: {str(e)}"

    def preprocess(self, image: Image.Image) -> torch.Tensor:
        """
        预处理 PIL Image → 模型输入 Tensor

        步骤：统一通道 → resize → ToTensor → Normalize → add batch dim
        """
        # 1. 统一为 RGB 三通道
        if image.mode != "RGB":
            image = image.convert("RGB")

        # 2-4. resize + ToTensor + Normalize
        tensor = self.transform(image)

        # 5. 增加 batch 维度 (C, H, W) → (1, C, H, W)
        tensor = tensor.unsqueeze(0)

        return tensor

    def process(self, file_path: str, device: torch.device) -> Tuple[Optional[torch.Tensor], Optional[str]]:
        """
        完整的预处理流程：加载 → 预处理 → 放到设备

        返回 (Tensor, None) 表示成功，(None, error_message) 表示失败
        """
        image, error = self.load_image(file_path)
        if error:
            return None, error

        tensor = self.preprocess(image)
        tensor = tensor.to(device)

        return tensor, None
