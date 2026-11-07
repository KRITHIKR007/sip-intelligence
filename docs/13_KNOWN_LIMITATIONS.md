# 13 Known Technical Limitations & Constraints

In alignment with engineering integrity rules, all current boundaries, un-fine-tuned models, and environmental assumptions are explicitly identified below:

1. **Symbol Detection Models**:
   - `yolo11n` and `convnext_tiny` run with pretrained weights.
   - Domain-specific high-accuracy detection requires a verified, labelled SIP bounding-box dataset.
   - The UI and API clearly label detections as un-fine-tuned candidate suggestions.

2. **DWG File Conversion**:
   - `ezdxf` does not parse proprietary binary `.DWG` files directly.
   - Direct DWG processing requires an external ODA File Converter license or prior export to `.DXF`.

3. **Seq2Vec and R-GCN Structural Models**:
   - The model architectures are fully implemented and unit-tested with synthetic topological graphs.
   - Production weights require an annotated dataset of sequential railway track entities.

4. **Deterministic Validation Engine**:
   - The engine strictly executes deterministic algorithms against configured rules.
   - Does not use generative LLMs to invent compliance verdicts.
   - Rules must be explicitly configured by qualified railway signalling engineers.

5. **Hardware Constraints**:
   - Designed for local 4GB–16GB edge VRAM environments. Batch sizes are throttled accordingly.

