"""
SIP Intelligence — Drawing Entities, Symbols & Comparison API
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user_id
from app.db.session import get_db
from app.models.engineering import EngineeringEntity
from app.schemas import (
    CompareRequest,
    ComparisonResponse,
    EntityResponse,
)

router = APIRouter(prefix="/drawings", tags=["Drawings"])


@router.get("/{drawing_id}/entities", response_model=list[EntityResponse])
async def get_drawing_entities(
    drawing_id: uuid.UUID,
    entity_type: str | None = None,
    min_confidence: float = 0.0,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get all engineering entities detected in a drawing."""
    query = select(EngineeringEntity).where(EngineeringEntity.document_id == drawing_id)
    if entity_type:
        query = query.where(EngineeringEntity.entity_type == entity_type)
    if min_confidence > 0:
        query = query.where(EngineeringEntity.confidence >= min_confidence)
    query = query.order_by(EngineeringEntity.entity_type, EngineeringEntity.label)

    result = await db.execute(query)
    entities = result.scalars().all()
    return [
        EntityResponse(
            id=e.id,
            entity_type=e.entity_type,
            label=e.label,
            x=e.x, y=e.y, width=e.width, height=e.height,
            confidence=e.confidence,
            detection_model=e.detection_model,
            attributes=e.attributes_json,
        )
        for e in entities
    ]


@router.get("/{drawing_id}/symbols", response_model=list[EntityResponse])
async def get_drawing_symbols(
    drawing_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get detected symbols for a drawing."""
    return await get_drawing_entities(drawing_id, user_id=user_id, db=db)


@router.post("/compare", response_model=ComparisonResponse)
async def compare_drawings(
    body: CompareRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Compare two drawings to identify differences."""
    # Get entities for both drawings
    result_a = await db.execute(
        select(EngineeringEntity).where(EngineeringEntity.document_id == body.drawing_id_a)
    )
    entities_a = result_a.scalars().all()

    result_b = await db.execute(
        select(EngineeringEntity).where(EngineeringEntity.document_id == body.drawing_id_b)
    )
    entities_b = result_b.scalars().all()

    if not entities_a and not entities_b:
        return ComparisonResponse(
            drawing_a_id=body.drawing_id_a,
            drawing_b_id=body.drawing_id_b,
            summary="No entities found in either drawing. Process drawings first.",
        )

    # Build lookup maps by label+type
    map_a = {(e.entity_type, e.label or ""): e for e in entities_a}
    map_b = {(e.entity_type, e.label or ""): e for e in entities_b}

    from app.schemas import ComparisonDiff

    additions = []
    removals = []
    modifications = []

    # Find additions (in B but not A)
    for key, entity in map_b.items():
        if key not in map_a:
            additions.append(ComparisonDiff(
                entity_type=entity.entity_type,
                label=entity.label,
                change_type="ADDED",
                details={"x": entity.x, "y": entity.y},
            ))

    # Find removals (in A but not B)
    for key, entity in map_a.items():
        if key not in map_b:
            removals.append(ComparisonDiff(
                entity_type=entity.entity_type,
                label=entity.label,
                change_type="REMOVED",
                details={"x": entity.x, "y": entity.y},
            ))

    # Find modifications (same key, different attributes/position)
    for key in set(map_a.keys()) & set(map_b.keys()):
        ea, eb = map_a[key], map_b[key]
        changes = {}
        if abs(ea.x - eb.x) > 5 or abs(ea.y - eb.y) > 5:
            changes["position"] = {"old": [ea.x, ea.y], "new": [eb.x, eb.y]}
        if ea.attributes_json != eb.attributes_json:
            changes["attributes"] = {"old": ea.attributes_json, "new": eb.attributes_json}
        if changes:
            modifications.append(ComparisonDiff(
                entity_type=ea.entity_type,
                label=ea.label,
                change_type="MODIFIED",
                details=changes,
            ))

    total = len(additions) + len(removals) + len(modifications)
    summary = f"Found {total} differences: {len(additions)} additions, {len(removals)} removals, {len(modifications)} modifications."

    return ComparisonResponse(
        drawing_a_id=body.drawing_id_a,
        drawing_b_id=body.drawing_id_b,
        additions=additions,
        removals=removals,
        modifications=modifications,
        summary=summary,
    )

