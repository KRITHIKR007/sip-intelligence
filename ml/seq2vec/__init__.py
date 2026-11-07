"""
Seq2Vec: BiLSTM + Attention model for structural embeddings.

Converts variable-length entity sequences from SIP engineering drawings
into fixed 256-dimensional structural embeddings.

Model: BiLSTM (2 layers, 256 hidden per direction) + Attention Pooling
Input: Entity type (128d) + Position (32d) + Attributes (32d) = 192d
Output: L2-normalized 256-dim embedding

Status: EXPERIMENTAL — architecture implemented, pending real training data.
"""

from .model import Seq2VecModel, AttentionPooling
from .inference import Seq2VecInference

__version__ = "0.1.0"
__model_name__ = "seq2vec-bilstm-attn"
__embedding_dim__ = 256
