"""
SIP Intelligence — ConvNeXt-Tiny Fine-Grained Symbol Classifier
"""
from __future__ import annotations

import torch
import torch.nn as nn
from PIL import Image
import numpy as np


class ConvNeXtClassifier(nn.Module):
    """ConvNeXt-Tiny adapted for fine-grained SIP symbol classification."""

    def __init__(self, num_classes: int = 56, pretrained: bool = True):
        super().__init__()
        self.num_classes = num_classes
        try:
            import timm
            self.backbone = timm.create_model("convnext_tiny", pretrained=pretrained, num_classes=num_classes)
        except Exception:
            self.backbone = nn.Sequential(
                nn.AdaptiveAvgPool2d((1, 1)),
                nn.Flatten(),
                nn.Linear(3, num_classes),
            )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.backbone(x)

