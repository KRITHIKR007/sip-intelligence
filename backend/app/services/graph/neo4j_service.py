"""
SIP Intelligence — Neo4j Knowledge Graph Service
"""
from __future__ import annotations

from typing import Any, Optional

import structlog

from app.core.config import settings

logger = structlog.get_logger()


class Neo4jService:
    """Engineering knowledge graph operations via Neo4j."""

    _driver = None

    @classmethod
    def _get_driver(cls):
        if cls._driver is None:
            try:
                from neo4j import GraphDatabase
                cls._driver = GraphDatabase.driver(
                    settings.neo4j_uri,
                    auth=(settings.neo4j_user, settings.neo4j_password),
                )
                cls._driver.verify_connectivity()
                logger.info("Neo4j connected")
            except Exception as e:
                logger.error("Neo4j connection failed", error=str(e))
                raise
        return cls._driver

    @classmethod
    def close(cls):
        if cls._driver:
            cls._driver.close()
            cls._driver = None

    # ---- Node operations --------------------------------------------------

    @classmethod
    def create_drawing_node(cls, drawing_id: str, name: str, project_id: str, **props) -> str:
        driver = cls._get_driver()
        with driver.session() as session:
            result = session.run(
                "MERGE (d:Drawing {id: $id}) "
                "SET d.name = $name, d.project_id = $project_id, d += $props "
                "RETURN d.id AS id",
                id=drawing_id, name=name, project_id=project_id, props=props,
            )
            return result.single()["id"]

    @classmethod
    def create_entity_node(
        cls,
        entity_id: str,
        entity_type: str,
        label: str,
        drawing_id: str,
        **props,
    ) -> str:
        driver = cls._get_driver()
        with driver.session() as session:
            # Create typed node
            query = (
                f"MERGE (e:{entity_type} {{id: $id}}) "
                "SET e.label = $label, e.drawing_id = $drawing_id, e += $props "
                "RETURN e.id AS id"
            )
            result = session.run(
                query,
                id=entity_id, label=label, drawing_id=drawing_id, props=props,
            )
            return result.single()["id"]

    @classmethod
    def create_relationship(
        cls,
        from_id: str,
        to_id: str,
        rel_type: str,
        properties: Optional[dict] = None,
    ):
        """Create a typed relationship between two nodes."""
        driver = cls._get_driver()
        props = properties or {}
        with driver.session() as session:
            session.run(
                f"MATCH (a {{id: $from_id}}), (b {{id: $to_id}}) "
                f"MERGE (a)-[r:{rel_type}]->(b) "
                "SET r += $props",
                from_id=from_id, to_id=to_id, props=props,
            )

    # ---- Query operations -------------------------------------------------

    @classmethod
    def get_drawing_entities(cls, drawing_id: str) -> list[dict]:
        driver = cls._get_driver()
        with driver.session() as session:
            result = session.run(
                "MATCH (e {drawing_id: $drawing_id}) "
                "RETURN e.id AS id, labels(e) AS labels, "
                "e.label AS label, properties(e) AS props",
                drawing_id=drawing_id,
            )
            return [dict(record) for record in result]

    @classmethod
    def get_entity_relationships(cls, entity_id: str) -> list[dict]:
        driver = cls._get_driver()
        with driver.session() as session:
            result = session.run(
                "MATCH (a {id: $id})-[r]-(b) "
                "RETURN type(r) AS relationship, "
                "b.id AS related_id, labels(b) AS related_labels, "
                "b.label AS related_label",
                id=entity_id,
            )
            return [dict(record) for record in result]

    @classmethod
    def search_entities(cls, query: str) -> list:
        """Search graph entities by label/name (returns RetrievalResults)."""
        driver = cls._get_driver()
        from app.services.retrieval.hybrid_retriever import RetrievalResult

        with driver.session() as session:
            result = session.run(
                "MATCH (e) WHERE toLower(e.label) CONTAINS toLower($query) "
                "RETURN e.id AS id, labels(e) AS labels, e.label AS label, "
                "e.drawing_id AS drawing_id LIMIT 20",
                query=query,
            )
            return [
                RetrievalResult(
                    document_id=record.get("drawing_id", ""),
                    chunk_id=record["id"],
                    text=f"{record['labels']}: {record.get('label', '')}",
                    score=0.5,
                    source_type="graph",
                )
                for record in result
            ]

    @classmethod
    def export_graph(cls, drawing_id: Optional[str] = None) -> dict:
        """Export graph as nodes + edges."""
        driver = cls._get_driver()
        with driver.session() as session:
            if drawing_id:
                nodes = session.run(
                    "MATCH (n {drawing_id: $did}) RETURN n", did=drawing_id
                )
                edges = session.run(
                    "MATCH (a {drawing_id: $did})-[r]->(b) "
                    "RETURN a.id, type(r), b.id",
                    did=drawing_id,
                )
            else:
                nodes = session.run("MATCH (n) RETURN n LIMIT 1000")
                edges = session.run(
                    "MATCH (a)-[r]->(b) RETURN a.id, type(r), b.id LIMIT 5000"
                )
            return {
                "nodes": [dict(r["n"]) for r in nodes],
                "edges": [dict(r) for r in edges],
            }

