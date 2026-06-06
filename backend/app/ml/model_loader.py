"""
模型加载器

策略:
1. 优先加载本地训练好的模型权重 (models/ 目录下)
2. 若不存在，使用 torchvision 预训练 ResNet-18 + 随机初始化的分类头
"""

import os
import torch
import torch.nn as nn
import torchvision.models as models
from pathlib import Path
from typing import Optional, Tuple

from app.core.config import BASE_DIR


class LungNoduleClassifier(nn.Module):
    """肺结节二分类器：ResNet-18 骨干 + 自定义分类头"""

    def __init__(self, num_classes: int = 2, pretrained: bool = True):
        super().__init__()
        # 使用 ResNet-18 骨干
        weights = models.ResNet18_Weights.IMAGENET1K_V1 if pretrained else None
        self.backbone = models.resnet18(weights=weights)

        # 替换最后的全连接层为二分类
        in_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(in_features, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, num_classes),
        )

        # 保存特征图（供 Grad-CAM 使用）
        self.gradients = None
        self.activations = None
        self._register_hooks()

    def _register_hooks(self):
        """注册 hook 以捕获最后卷积层的激活值和梯度"""
        target_layer = self.backbone.layer4[-1].conv2

        def forward_hook(module, input, output):
            self.activations = output

        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0]

        target_layer.register_forward_hook(forward_hook)
        target_layer.register_full_backward_hook(backward_hook)

    def forward(self, x):
        return self.backbone(x)


class ModelLoader:
    """模型加载与版本管理"""

    MODEL_DIR = BASE_DIR / "models"
    MODEL_VERSION = "resnet18_v1.0"
    INPUT_SIZE = (224, 224)

    def __init__(self, device: Optional[str] = None):
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        self.model: Optional[LungNoduleClassifier] = None

    def load(self) -> Tuple[LungNoduleClassifier, str]:
        """
        加载模型

        返回 (model, model_version)
        """
        local_model_path = self.MODEL_DIR / "resnet18_v1.0.pt"

        if local_model_path.exists():
            model = self._load_local(local_model_path)
            version = self.MODEL_VERSION
        else:
            model = self._load_pretrained()
            version = f"{self.MODEL_VERSION}_pretrained"

        model = model.to(self.device)
        model.eval()
        self.model = model
        print(f"[ModelLoader] 模型已加载: {version} (device={self.device})")
        return model, version

    def _load_local(self, path: Path) -> LungNoduleClassifier:
        """加载本地训练好的模型权重"""
        model = LungNoduleClassifier(num_classes=2, pretrained=False)
        state_dict = torch.load(path, map_location=self.device, weights_only=True)
        model.load_state_dict(state_dict)
        print(f"[ModelLoader] 本地模型已加载: {path}")
        return model

    def _load_pretrained(self) -> LungNoduleClassifier:
        """
        加载预训练 ResNet-18 作为基础模型

        注意：此模型未经医学影像微调，预测不具备临床准确性。
        仅用于演示系统流程的完整性。
        """
        print("[ModelLoader] 未找到本地模型，使用 ImageNet 预训练 ResNet-18")
        return LungNoduleClassifier(num_classes=2, pretrained=True)

    def get_device(self) -> torch.device:
        return self.device
