# Security Policy

## Supported Versions
| Version | Supported |
|---|---|
| v0.1.0 | ✅ Active Development |

## Security Architecture
- **Airgapped Cloud AI Gateway**: External cloud connections disabled by default (`CLOUD_AI_ENABLED=false`).
- **Cryptographic Access Control**: JWT tokens signed using HS256 with user and role verification.
- **Tenant & Project Level Isolation**: Vector retrieval in Qdrant and relational queries in PostgreSQL enforce project permissions.
- **Direct Bcrypt Hashing**: Passwords hashed with salt rounds using `bcrypt`.
- **Audit Logging**: All administrative, validation, and feedback actions logged in `sip.audit_logs`.

## Reporting Vulnerabilities
Report security findings directly to the Railway S&T Cyber Security Directorate.

