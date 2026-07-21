# ECMP Ontology (Semantic Knowledge Layer)

| Field | Value |
|---|---|
| ID | ONT-000 |
| Version | 1.0 |
| Owner | Enterprise Architecture |
| Reviewer | BA / Solution Architect |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Define canonical node/relation types for Engineering Intelligence.

## Source
- Schema: `ontology.yaml`
- Graph output: `../knowledge-graph/graph.generated.yaml`
- Generator: `../../tools/generate_knowledge_graph.py`

## Core chain
`BusinessGoal → Capability/Domain → BusinessRule → FRD → API → Event → Test`  
(+ Sprint delivers, ADR decides)
