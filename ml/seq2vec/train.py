"""
Training script for Seq2Vec model.

Loss: L = L_SupCon + 0.2 * L_classification
- Supervised contrastive loss (SupCon)
- Optional cross-entropy classification loss

Status: EXPERIMENTAL — pending real SIP training data.
         Architecture and training loop validated with synthetic data.
"""

import argparse
import logging
import time
from pathlib import Path
from typing import Optional

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import DataLoader, random_split

from .dataset import (
    EntitySequenceDataset,
    collate_entity_sequences,
    generate_synthetic_data,
)
from .model import Seq2VecModel

logger = logging.getLogger(__name__)


class SupConLoss(nn.Module):
    """Supervised Contrastive Loss.

    Based on "Supervised Contrastive Learning" (Khosla et al., 2020).
    For each anchor, positives are samples with the same label.

    Args:
        temperature: Scaling temperature (default: 0.07).
    """

    def __init__(self, temperature: float = 0.07) -> None:
        super().__init__()
        self.temperature = temperature

    def forward(
        self, embeddings: torch.Tensor, labels: torch.Tensor
    ) -> torch.Tensor:
        """Compute SupCon loss.

        Args:
            embeddings: (batch, dim) L2-normalized embeddings.
            labels: (batch,) integer class labels.

        Returns:
            Scalar loss tensor.
        """
        device = embeddings.device
        batch_size = embeddings.shape[0]

        if batch_size <= 1:
            return torch.tensor(0.0, device=device, requires_grad=True)

        # Similarity matrix: (batch, batch)
        sim_matrix = torch.matmul(embeddings, embeddings.T) / self.temperature

        # Mask: same-label pairs (excluding self)
        labels = labels.view(-1, 1)
        label_mask = torch.eq(labels, labels.T).float().to(device)

        # Remove self-comparisons
        self_mask = torch.eye(batch_size, device=device)
        label_mask = label_mask - self_mask

        # Number of positives per anchor
        num_positives = label_mask.sum(dim=1)

        # For numerical stability
        logits_max, _ = sim_matrix.max(dim=1, keepdim=True)
        logits = sim_matrix - logits_max.detach()

        # Mask out self-comparisons in exp
        exp_logits = torch.exp(logits) * (1 - self_mask)
        log_prob = logits - torch.log(exp_logits.sum(dim=1, keepdim=True) + 1e-12)

        # Mean of log-likelihood over positive pairs
        # Only compute for anchors that have at least one positive
        has_positives = num_positives > 0
        if not has_positives.any():
            return torch.tensor(0.0, device=device, requires_grad=True)

        mean_log_prob = (label_mask * log_prob).sum(dim=1) / (num_positives + 1e-12)
        loss = -mean_log_prob[has_positives].mean()

        return loss


def train_epoch(
    model: Seq2VecModel,
    dataloader: DataLoader,
    optimizer: torch.optim.Optimizer,
    supcon_loss_fn: SupConLoss,
    ce_loss_fn: nn.CrossEntropyLoss,
    device: torch.device,
    classification_weight: float = 0.2,
) -> dict[str, float]:
    """Run one training epoch.

    Args:
        model: Seq2Vec model.
        dataloader: Training DataLoader.
        optimizer: Optimizer.
        supcon_loss_fn: Supervised contrastive loss function.
        ce_loss_fn: Cross-entropy loss function.
        device: Compute device.
        classification_weight: Weight for classification loss (default: 0.2).

    Returns:
        Dict with 'total_loss', 'supcon_loss', 'cls_loss' averages.
    """
    model.train()
    total_loss = 0.0
    total_supcon = 0.0
    total_cls = 0.0
    num_batches = 0

    for batch in dataloader:
        entity_types = batch["entity_types"].to(device)
        positions = batch["positions"].to(device)
        attributes = batch["attributes"].to(device)
        mask = batch["mask"].to(device)
        labels = batch["labels"].to(device)

        optimizer.zero_grad()

        # Forward pass
        output = model(
            entity_types=entity_types,
            positions=positions,
            attributes=attributes,
            mask=mask,
            return_logits=True,
        )

        embeddings = output["embedding"]

        # Filter out samples with label == -1 (unlabeled)
        valid = labels >= 0
        if valid.sum() < 2:
            continue

        valid_embeddings = embeddings[valid]
        valid_labels = labels[valid]

        # Supervised contrastive loss
        loss_supcon = supcon_loss_fn(valid_embeddings, valid_labels)

        # Classification loss (if classifier head exists)
        loss_cls = torch.tensor(0.0, device=device)
        if "logits" in output:
            valid_logits = output["logits"][valid]
            loss_cls = ce_loss_fn(valid_logits, valid_labels)

        # Combined loss: L = L_SupCon + 0.2 * L_classification
        loss = loss_supcon + classification_weight * loss_cls

        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()

        total_loss += loss.item()
        total_supcon += loss_supcon.item()
        total_cls += loss_cls.item()
        num_batches += 1

    if num_batches == 0:
        return {"total_loss": 0.0, "supcon_loss": 0.0, "cls_loss": 0.0}

    return {
        "total_loss": total_loss / num_batches,
        "supcon_loss": total_supcon / num_batches,
        "cls_loss": total_cls / num_batches,
    }


@torch.no_grad()
def validate(
    model: Seq2VecModel,
    dataloader: DataLoader,
    supcon_loss_fn: SupConLoss,
    ce_loss_fn: nn.CrossEntropyLoss,
    device: torch.device,
    classification_weight: float = 0.2,
) -> dict[str, float]:
    """Run validation.

    Returns:
        Dict with 'total_loss', 'supcon_loss', 'cls_loss', 'accuracy'.
    """
    model.eval()
    total_loss = 0.0
    total_supcon = 0.0
    total_cls = 0.0
    correct = 0
    total = 0
    num_batches = 0

    for batch in dataloader:
        entity_types = batch["entity_types"].to(device)
        positions = batch["positions"].to(device)
        attributes = batch["attributes"].to(device)
        mask = batch["mask"].to(device)
        labels = batch["labels"].to(device)

        output = model(
            entity_types=entity_types,
            positions=positions,
            attributes=attributes,
            mask=mask,
            return_logits=True,
        )

        embeddings = output["embedding"]
        valid = labels >= 0
        if valid.sum() < 2:
            continue

        valid_embeddings = embeddings[valid]
        valid_labels = labels[valid]

        loss_supcon = supcon_loss_fn(valid_embeddings, valid_labels)

        loss_cls = torch.tensor(0.0, device=device)
        if "logits" in output:
            valid_logits = output["logits"][valid]
            loss_cls = ce_loss_fn(valid_logits, valid_labels)
            preds = valid_logits.argmax(dim=-1)
            correct += (preds == valid_labels).sum().item()
            total += valid_labels.size(0)

        loss = loss_supcon + classification_weight * loss_cls
        total_loss += loss.item()
        total_supcon += loss_supcon.item()
        total_cls += loss_cls.item()
        num_batches += 1

    if num_batches == 0:
        return {
            "total_loss": 0.0,
            "supcon_loss": 0.0,
            "cls_loss": 0.0,
            "accuracy": 0.0,
        }

    accuracy = correct / total if total > 0 else 0.0

    return {
        "total_loss": total_loss / num_batches,
        "supcon_loss": total_supcon / num_batches,
        "cls_loss": total_cls / num_batches,
        "accuracy": accuracy,
    }


def train(
    data_path: Optional[str] = None,
    output_dir: str = "checkpoints/seq2vec",
    num_entity_types: int = 128,
    num_classes: int = 10,
    epochs: int = 50,
    batch_size: int = 32,
    lr: float = 1e-3,
    weight_decay: float = 1e-4,
    classification_weight: float = 0.2,
    val_split: float = 0.2,
    device_str: str = "auto",
    use_synthetic: bool = False,
    num_synthetic_samples: int = 500,
) -> Path:
    """Full training pipeline for Seq2Vec.

    Args:
        data_path: Path to training data JSON. If None and use_synthetic=True,
                   generates synthetic data for testing.
        output_dir: Directory to save checkpoints.
        num_entity_types: Size of entity type vocabulary.
        num_classes: Number of classification classes.
        epochs: Number of training epochs.
        batch_size: Training batch size.
        lr: Learning rate.
        weight_decay: Weight decay for AdamW.
        classification_weight: Weight for classification loss component.
        val_split: Fraction of data for validation.
        device_str: Device string ('auto', 'cpu', 'cuda').
        use_synthetic: Whether to use synthetic data if data_path is None.
        num_synthetic_samples: Number of synthetic samples to generate.

    Returns:
        Path to best model checkpoint.
    """
    # Setup
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    if device_str == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(device_str)

    logger.info(f"Training on device: {device}")

    # Load or generate data
    if data_path is not None:
        dataset = EntitySequenceDataset(data_path=data_path)
    elif use_synthetic:
        logger.warning(
            "Using SYNTHETIC data for testing. "
            "Model will NOT have meaningful accuracy. "
            "Real SIP training data is required for production use."
        )
        synthetic_data = generate_synthetic_data(
            num_samples=num_synthetic_samples,
            num_classes=num_classes,
        )
        dataset = EntitySequenceDataset(data=synthetic_data)
    else:
        raise ValueError(
            "No data_path provided and use_synthetic=False. "
            "Provide training data or set use_synthetic=True for testing."
        )

    # Split
    val_size = int(len(dataset) * val_split)
    train_size = len(dataset) - val_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        collate_fn=collate_entity_sequences,
        num_workers=0,
        pin_memory=device.type == "cuda",
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        collate_fn=collate_entity_sequences,
        num_workers=0,
        pin_memory=device.type == "cuda",
    )

    # Model
    model = Seq2VecModel(
        num_entity_types=num_entity_types,
        num_classes=num_classes,
    ).to(device)

    logger.info(
        f"Model parameters: {sum(p.numel() for p in model.parameters()):,}"
    )

    # Losses
    supcon_loss_fn = SupConLoss(temperature=0.07)
    ce_loss_fn = nn.CrossEntropyLoss()

    # Optimizer and scheduler
    optimizer = AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = CosineAnnealingLR(optimizer, T_max=epochs, eta_min=lr * 0.01)

    # Training loop
    best_val_loss = float("inf")
    best_checkpoint_path = output_path / "best_model.pt"

    for epoch in range(1, epochs + 1):
        start_time = time.time()

        train_metrics = train_epoch(
            model=model,
            dataloader=train_loader,
            optimizer=optimizer,
            supcon_loss_fn=supcon_loss_fn,
            ce_loss_fn=ce_loss_fn,
            device=device,
            classification_weight=classification_weight,
        )

        val_metrics = validate(
            model=model,
            dataloader=val_loader,
            supcon_loss_fn=supcon_loss_fn,
            ce_loss_fn=ce_loss_fn,
            device=device,
            classification_weight=classification_weight,
        )

        scheduler.step()
        elapsed = time.time() - start_time

        logger.info(
            f"Epoch {epoch}/{epochs} ({elapsed:.1f}s) | "
            f"Train Loss: {train_metrics['total_loss']:.4f} "
            f"(SupCon: {train_metrics['supcon_loss']:.4f}, "
            f"Cls: {train_metrics['cls_loss']:.4f}) | "
            f"Val Loss: {val_metrics['total_loss']:.4f} "
            f"Acc: {val_metrics['accuracy']:.4f}"
        )

        # Save best model
        if val_metrics["total_loss"] < best_val_loss:
            best_val_loss = val_metrics["total_loss"]
            checkpoint = {
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "scheduler_state_dict": scheduler.state_dict(),
                "val_loss": best_val_loss,
                "val_accuracy": val_metrics["accuracy"],
                "config": {
                    "num_entity_types": num_entity_types,
                    "num_classes": num_classes,
                    "output_dim": 256,
                    "model_name": "seq2vec-bilstm-attn",
                    "version": "0.1.0",
                },
            }
            torch.save(checkpoint, best_checkpoint_path)
            logger.info(f"  → Saved best model (val_loss={best_val_loss:.4f})")

        # Save periodic checkpoint
        if epoch % 10 == 0:
            periodic_path = output_path / f"checkpoint_epoch_{epoch}.pt"
            torch.save(
                {
                    "epoch": epoch,
                    "model_state_dict": model.state_dict(),
                },
                periodic_path,
            )

    logger.info(f"Training complete. Best val loss: {best_val_loss:.4f}")
    logger.info(f"Best checkpoint: {best_checkpoint_path}")

    return best_checkpoint_path


def main() -> None:
    """CLI entry point for training."""
    parser = argparse.ArgumentParser(description="Train Seq2Vec model")
    parser.add_argument("--data-path", type=str, default=None, help="Training data JSON path")
    parser.add_argument("--output-dir", type=str, default="checkpoints/seq2vec")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--num-classes", type=int, default=10)
    parser.add_argument("--device", type=str, default="auto")
    parser.add_argument(
        "--use-synthetic",
        action="store_true",
        help="Use synthetic data for testing (not for production)",
    )

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    train(
        data_path=args.data_path,
        output_dir=args.output_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        num_classes=args.num_classes,
        device_str=args.device,
        use_synthetic=args.use_synthetic,
    )


if __name__ == "__main__":
    main()
