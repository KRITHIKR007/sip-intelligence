# Contributing to SIP Intelligence

## 1. Development Principles
1. **Engineering Integrity**: Never fabricate model accuracy, validation outcomes, or standards compliance.
2. **Deterministic Rules**: Keep rule validation independent of generative LLM hallucinations.
3. **Preserve Coordinates**: Every extracted entity must maintain its source coordinates and document DPI.
4. **Airgapped Safety**: Never transmit sensitive drawing data to external cloud APIs without authorized explicit approval.

---

## 2. Pull Request Checklist
- [ ] Code follows PEP 8 / `ruff format` for Python and ESLint for TypeScript.
- [ ] Unit tests added/maintained in `backend/tests/unit/`.
- [ ] All unit and integration tests pass cleanly (`pytest`).
- [ ] Next.js build succeeds with zero TypeScript errors (`npm run build`).
- [ ] Database schema modifications include an Alembic migration script.

