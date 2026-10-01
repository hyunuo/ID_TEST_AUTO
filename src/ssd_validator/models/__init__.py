"""Domain models and data contracts."""

from .effective import BuildManifest, EffectiveField, EffectiveRule, EffectiveSnapshot
from .identifiers import SpecFamily, SpecVersion, TargetRef
from .provenance import ChangeRecord, KnowledgeStatus, Provenance, SourceDocument
from .rules import LookupEntry, RequirementRule
from .schema import BitSchema, FieldSchema, SemanticState
from .specs import BaseSpec, DeltaAction, DeltaSpec, KnowledgeCatalog, RuleChange, SchemaChange, SchemaReferenceChange

__all__ = [
    "BaseSpec", "BitSchema", "BuildManifest", "ChangeRecord", "DeltaAction", "DeltaSpec",
    "EffectiveField", "EffectiveRule", "EffectiveSnapshot", "FieldSchema", "KnowledgeCatalog",
    "KnowledgeStatus", "LookupEntry", "Provenance", "RequirementRule", "RuleChange", "SchemaChange", "SchemaReferenceChange",
    "SemanticState", "SourceDocument", "SpecFamily", "SpecVersion", "TargetRef",
]
