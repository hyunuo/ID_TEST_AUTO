"""Compile all source versions before exposing any generated artifacts."""

from collections import defaultdict
from dataclasses import dataclass

from ssd_validator.errors import KnowledgeError
from ssd_validator.knowledge.validation import KnowledgeValidator
from ssd_validator.knowledge.yaml_loader import LoadedSource
from ssd_validator.models.effective import BuildManifest, EffectiveField, EffectiveRule, EffectiveSnapshot
from ssd_validator.models.specs import BaseSpec, DeltaSpec
from .delta import apply_delta, change_record
from .manifest import build_manifest
from .version_graph import version_order


@dataclass(frozen=True)
class BuildResult:
    snapshots: tuple[EffectiveSnapshot, ...]
    manifest: BuildManifest

    def get(self, spec_family, version: str) -> EffectiveSnapshot:
        key = f"{str(spec_family).upper()}:{version}"
        for snapshot in self.snapshots:
            if snapshot.spec.key == key:
                return snapshot
        raise KnowledgeError("UNKNOWN_VERSION", key)


def _build_base(sources: list[LoadedSource]) -> EffectiveSnapshot:
    first = sources[0].document
    fields, rules, events = {}, {}, []
    for source in sources:
        base = source.document
        if base.data_kind != first.data_kind or base.schema_ref != first.schema_ref:
            raise KnowledgeError("BASE_FRAGMENT_MISMATCH", first.spec.key)
        for field in base.fields:
            if field.field_id in fields:
                raise KnowledgeError("DUPLICATE_FIELD", field.field_id, source=source.path)
            record = change_record(source, field.field_id, "BASE")
            events.append(record)
            fields[field.field_id] = EffectiveField(
                schema=field.model_copy(deep=True), introduced_in=base.spec, last_changed_in=base.spec, history=(record,),
            )
        for rule in base.rules:
            if rule.rule_id in rules:
                raise KnowledgeError("DUPLICATE_RULE", rule.rule_id, source=source.path)
            evidence = rule.provenance or base.provenance
            record = change_record(source, rule.rule_id, "BASE", evidence)
            events.append(record)
            payload = rule.model_dump(mode="json")
            payload["provenance"] = evidence.model_dump(mode="json")
            resolved_rule = type(rule).model_validate(payload)
            rules[rule.rule_id] = EffectiveRule(
                rule=resolved_rule, introduced_in=base.spec, last_changed_in=base.spec, history=(record,),
            )
    return EffectiveSnapshot(
        spec=first.spec, data_kind=first.data_kind, schema_ref=first.schema_ref,
        fields=tuple(fields[key] for key in sorted(fields)), rules=tuple(rules[key] for key in sorted(rules)),
        changes=tuple(sorted(events, key=lambda record: (record.source_file, record.target))),
    )


def build_knowledge(sources: tuple[LoadedSource, ...], *, git_commit: str | None = None) -> BuildResult:
    ordered_sources = sorted(sources, key=lambda source: source.path)
    validator = KnowledgeValidator(ordered_sources)
    grouped = defaultdict(list)
    for source in ordered_sources:
        if isinstance(source.document, (BaseSpec, DeltaSpec)):
            grouped[source.document.spec.key].append(source)
    if not grouped:
        raise KnowledgeError("NO_SPECS", "No base/delta specs found")
    portable_keys = {}
    for key in sorted(grouped):
        portable = key.casefold()
        if portable in portable_keys:
            raise KnowledgeError("ARTIFACT_PATH_COLLISION", f"{portable_keys[portable]} and {key}")
        portable_keys[portable] = key
    parents = {}
    for key, group in sorted(grouped.items()):
        deltas = [source for source in group if isinstance(source.document, DeltaSpec)]
        if deltas and len(group) != 1:
            raise KnowledgeError("DUPLICATE_VERSION", key)
        parents[key] = f"{deltas[0].document.spec_family.value}:{deltas[0].document.inherits}" if deltas else None
    snapshots = {}
    for key in version_order(parents):
        group = grouped[key]
        try:
            snapshots[key] = apply_delta(snapshots[parents[key]], group[0]) if parents[key] else _build_base(group)
            validator.schema_fields((entry.schema for entry in snapshots[key].fields), snapshots[key].data_kind)
        except KnowledgeError as error:
            if error.source is None:
                raise KnowledgeError(error.code, error.message, source=group[0].path) from error
            raise
    # Cross-family schema references are checked only after every version exists.
    for key in sorted(snapshots):
        validator.snapshot(snapshots[key], snapshots)
    result = tuple(snapshots[key] for key in sorted(snapshots))
    return BuildResult(result, build_manifest(ordered_sources, result, git_commit))
