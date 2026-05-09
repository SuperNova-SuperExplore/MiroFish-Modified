"""Blueprint Lab ontology guardrails.

This module prevents the legacy social ontology prompt from leaking into
Blueprint Lab mode. Blueprint flow needs design/audit entities, not social
actors or social-media relations.
"""

from __future__ import annotations

from typing import Any, Dict, List

BLUEPRINT_ENTITY_TYPES: List[Dict[str, Any]] = [
    {"name": "Objective", "description": "Blueprint goal or desired outcome.", "attributes": [{"name": "objective_text", "type": "text", "description": "Goal statement"}], "examples": ["reduce user sadness", "launch one-page gift"]},
    {"name": "TargetUser", "description": "User or audience served by the blueprint.", "attributes": [{"name": "user_segment", "type": "text", "description": "Target segment"}], "examples": ["partner", "first-time visitor"]},
    {"name": "Feature", "description": "Product feature or capability.", "attributes": [{"name": "feature_summary", "type": "text", "description": "Feature summary"}], "examples": ["mood message", "photo section"]},
    {"name": "UserFlow", "description": "Step or journey in the experience.", "attributes": [{"name": "flow_step", "type": "text", "description": "Flow step"}], "examples": ["open page", "read note"]},
    {"name": "TechnicalRequirement", "description": "Technical need or implementation constraint.", "attributes": [{"name": "requirement_text", "type": "text", "description": "Requirement"}], "examples": ["single HTML file", "mobile responsive"]},
    {"name": "Dependency", "description": "External or internal dependency.", "attributes": [{"name": "dependency_text", "type": "text", "description": "Dependency"}], "examples": ["copywriting", "image assets"]},
    {"name": "Risk", "description": "Risk that can weaken the blueprint.", "attributes": [{"name": "risk_text", "type": "text", "description": "Risk"}], "examples": ["message feels generic", "privacy leak"]},
    {"name": "Assumption", "description": "Unverified assumption behind the design.", "attributes": [{"name": "assumption_text", "type": "text", "description": "Assumption"}], "examples": ["recipient likes jokes", "mobile only"]},
    {"name": "Metric", "description": "Signal used to judge success.", "attributes": [{"name": "metric_text", "type": "text", "description": "Metric"}], "examples": ["read completion", "reply sentiment"]},
    {"name": "RoadmapPhase", "description": "Delivery or revision phase.", "attributes": [{"name": "phase_text", "type": "text", "description": "Phase"}], "examples": ["next 7 days", "version 2"]},
]

BLUEPRINT_EDGE_TYPES: List[Dict[str, Any]] = [
    {"name": "TARGETS_USER", "description": "Objective or feature targets a user.", "source_targets": [{"source": "Objective", "target": "TargetUser"}, {"source": "Feature", "target": "TargetUser"}], "attributes": []},
    {"name": "RESOLVES_OBJECTIVE", "description": "Feature or flow supports an objective.", "source_targets": [{"source": "Feature", "target": "Objective"}, {"source": "UserFlow", "target": "Objective"}], "attributes": []},
    {"name": "DEPENDS_ON", "description": "Item depends on another item.", "source_targets": [{"source": "Feature", "target": "Dependency"}, {"source": "UserFlow", "target": "Dependency"}], "attributes": []},
    {"name": "CREATES_RISK", "description": "Item creates or increases a risk.", "source_targets": [{"source": "Feature", "target": "Risk"}, {"source": "Assumption", "target": "Risk"}], "attributes": []},
    {"name": "MITIGATES", "description": "Requirement or phase mitigates a risk.", "source_targets": [{"source": "TechnicalRequirement", "target": "Risk"}, {"source": "RoadmapPhase", "target": "Risk"}], "attributes": []},
    {"name": "VALIDATES", "description": "Metric validates objective or assumption.", "source_targets": [{"source": "Metric", "target": "Objective"}, {"source": "Metric", "target": "Assumption"}], "attributes": []},
    {"name": "BELONGS_TO_PHASE", "description": "Feature or requirement belongs to a roadmap phase.", "source_targets": [{"source": "Feature", "target": "RoadmapPhase"}, {"source": "TechnicalRequirement", "target": "RoadmapPhase"}], "attributes": []},
]

SOCIAL_ENTITY_NAMES = {"MediaOutlet", "Influencer", "Journalist", "Celebrity", "Student", "Professor", "University", "GovernmentAgency", "NGO", "Company", "Person", "Organization"}
SOCIAL_EDGE_NAMES = {"FOLLOWS", "LIKES", "REPLIES_TO", "SHARES", "MENTIONS", "COMMENTS_ON", "REPORTS_ON", "RESPONDS_TO", "SUPPORTS", "OPPOSES"}


def is_blueprint_context(additional_context: str | None, simulation_requirement: str | None = None) -> bool:
    haystack = f"{additional_context or ''}\n{simulation_requirement or ''}".lower()
    return "blueprint lab" in haystack or "mode operasi: blueprint" in haystack or "mode: blueprint lab" in haystack


def blueprint_ontology() -> Dict[str, Any]:
    return {
        "entity_types": BLUEPRINT_ENTITY_TYPES,
        "edge_types": BLUEPRINT_EDGE_TYPES,
        "analysis_summary": "Ontologi Blueprint Lab native: fokus pada objective, target user, fitur, flow, requirement, risk, assumption, dependency, metric, dan roadmap. Tidak memakai schema sosial."
    }


def has_social_leak(ontology: Dict[str, Any]) -> bool:
    entities = {item.get("name") for item in ontology.get("entity_types", [])}
    edges = {item.get("name") for item in ontology.get("edge_types", [])}
    return bool(entities & SOCIAL_ENTITY_NAMES) or bool(edges & SOCIAL_EDGE_NAMES)
