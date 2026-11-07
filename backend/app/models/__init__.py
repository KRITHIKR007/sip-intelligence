"""
SIP Intelligence — Models package. Import all models so Alembic discovers them.
"""
from app.models.users import (
    Department, User, ProjectPermission,
    UserRole, PermissionLevel,
)
from app.models.documents import (
    Project, Document, DocumentVersion, Page,
    ProjectStatus, FileType, DocumentStatus,
)
from app.models.chunks import TextChunk, VisualRegion, RegionType
from app.models.engineering import (
    EngineeringEntity, EntityAttribute, SymbolCatalogEntry, EntityType,
)
from app.models.validation import (
    ValidationRule, ValidationResult, ValidationJob,
    Severity, ValidationStatus, JobStatus,
)
from app.models.jobs import (
    ProcessingJob, AuditLog, ModelRegistry,
    ProcessingJobType, ProcessingJobStatus,
)

__all__ = [
    # Users
    "Department", "User", "ProjectPermission", "UserRole", "PermissionLevel",
    # Documents
    "Project", "Document", "DocumentVersion", "Page",
    "ProjectStatus", "FileType", "DocumentStatus",
    # Chunks
    "TextChunk", "VisualRegion", "RegionType",
    # Engineering
    "EngineeringEntity", "EntityAttribute", "SymbolCatalogEntry", "EntityType",
    # Validation
    "ValidationRule", "ValidationResult", "ValidationJob",
    "Severity", "ValidationStatus", "JobStatus",
    # Jobs
    "ProcessingJob", "AuditLog", "ModelRegistry",
    "ProcessingJobType", "ProcessingJobStatus",
]

