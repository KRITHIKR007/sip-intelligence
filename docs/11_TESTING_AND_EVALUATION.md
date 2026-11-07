# 11 Testing, Verification & Evaluation

## 1. Automated Test Suite

The test suite covers unit logic, integration boundaries, and ML model forward passes:

| Test Module | Coverage Scope | Verified Status |
|---|---|---|
| `test_chunker.py` | Text segmentation, table chunking, signal ID preservation | ✅ 100% Passed |
| `test_symbol_catalog.py` | 56-class catalog loading, category query, keyword search | ✅ 100% Passed |
| `test_security.py` | Direct bcrypt hashing, JWT access/refresh token signing & validation | ✅ 100% Passed |
| `test_seq2vec.py` | Seq2Vec BiLSTM attention pooling, output normalization, R-GCN conv forward | ✅ 100% Passed |
| `test_api_health.py` | Root endpoint, service connectivity probes | ✅ 100% Passed |

---

## 2. Evaluation Datasets & Ground Truth Policy

### Policy on Metrics
- **Strict Rule**: No fabricated evaluation metrics or synthetic benchmark numbers.
- Pretrained weights for YOLO and ConvNeXt are explicitly exposed as un-fine-tuned baselines.
- The evaluation dataset schema is versioned under `data/eval/` and supports ground-truth IoU evaluation via `ml.symbol_detection.evaluate.evaluate_detections`.

