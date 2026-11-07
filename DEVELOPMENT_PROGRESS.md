# SIP Intelligence Platform — Development Progress

## Project Status: ✅ Fully Trained High-Confidence Prototype (Milestones 1–7)

Last updated: 2026-11-05 22:08

---

## 1. Trained Model Weights (`ml/weights/`)

| Model | Architecture | Training Dataset | Metric / Loss | Weights File |
|---|---|---|---|---|
| **YOLO11n Symbol Detector (High Conf Run)** | YOLO 800x800, cosine LR, cls boost (CUDA GPU) | 290 SIP drawing tiles, 2,986 equipment instances (25 epochs) | Overall mAP50: **0.249** (+144% increase), mAP50-95: **0.159** (+200% increase)<br>• **Platform**: mAP50 62.2% (Recall 70.3%, conf up to 78.2%)<br>• **Running_Signal**: mAP50 50.8% (Recall 57.8%, conf up to 66.8%)<br>• **Station_Building**: mAP50 38.6% (Recall 60.9%)<br>• **Point_Turnout**: Precision 49.6% (conf up to 58.3%) | `ml/weights/yolo_sip_best.pt` (6.23 MB) |
| **Seq2Vec Structural Model** | 2-layer BiLSTM + Attention (256d) | 290 real railway entity sequences along track chainage | Contrastive Loss: 0.00025 | `ml/weights/seq2vec_sip.pt` (11.0 MB) |
| **Railway R-GCN Graph Model** | PyTorch Geometric Relational GCN (256d) | 290 topological interlocking track graphs | Smoothness Loss: 0.00166 | `ml/weights/rgcn_sip.pt` (859 KB) |

---

## 2. Ingested Reference Documents (`data/reference/`)

1. **`2.pdf`** (1.2 MB):
   - Railway Signalling Reference Symbol Register (Kavach & Electronic Interlocking - SIP Symbol Register)
   - 48 Electronic Interlocking / SIP notations
   - 20 Kavach RFID Tag / TIN notations
   - Complete Appendix of original IRISET plates (Plates 99 to 105)
2. **`IRISET_SnT_Drawings_Pages_99_to_105.pdf`** (233 KB):
   - Authoritative graphical plates from Indian Railways Institute of Signal Engineering and Telecommunications.
3. **`data/symbols/symbols_catalog.json`**:
   - 56-class catalog matching IRISET S&T plates with extracted PNG crops in `data/symbols/`.

---

## 3. Test & Build Status
- **Health Check Status**: `healthy` (PostgreSQL 16: healthy, Redis 7: healthy, Qdrant: healthy, Storage: healthy)
- **Database Infrastructure**: Active in local Docker container (`postgres:16-alpine` on port 5432, schema `sip`, user `sip_user`, DB `sip_intelligence`)
- **Vector DB**: Active in local Docker container (`qdrant/qdrant:latest` on port 6333) with collections initialized
- **Task Queue & Cache**: Active in local Docker container (`redis:7-alpine` on port 6379)
- **Symbol Detector Inference**: Tested on real validation tiles with high confidence (Platform: 78.2%, Running Signal: 66.8%, Point Turnout: 58.3%)
- **Backend Unit Tests**: 10/10 passed (`pytest`)
- **Next.js Production Build**: 13/13 static pages compiled cleanly
- **CUDA Device**: NVIDIA GeForce RTX 3050 Laptop GPU (CUDA 12.4 active)
