"""Referential integrity and conservative, literal requirement conflict checks."""

from collections import defaultdict
from itertools import product

from ssd_validator.errors import KnowledgeError
from ssd_validator.models.identifiers import SpecFamily
from ssd_validator.models.provenance import KnowledgeStatus
from ssd_validator.models.rules import (
    ApplicabilityCheck, BitCheck, BoundCheck, CapabilityCheck, DerivedCheck,
    EnumCheck, ExactCheck, LookupCheck, MaskCheck, RangeCheck, RequirementRule,
)
from ssd_validator.models.identifiers import TargetRef
from ssd_validator.models.specs import BaseSpec, DeltaSpec, KnowledgeCatalog

# Public context paths explicitly described by the SDS. No product values live here.
CONTEXT_PATHS = frozenset({
    "product.model", "product.flavor", "fw.version", "fw.type",
    "hardware.form_factor", "hardware.capacity_tb", "controller.mode", "controller.role",
    "virtualization.vf_enabled", "image.type", "data_placement.type",
    "data_placement.fdp.supported", "data_placement.fdp.enabled", "data_placement.fdp.profile",
    "data_placement.fdp.reclaim_group_count", "data_placement.fdp.ruh_count",
    "data_placement.fdp.selected_config_id", "namespace.nsid", "namespace.configuration",
    "spec_profile.nvme", "spec_profile.ocp", "spec_profile.mfnd",
})


def _unique(items, key, label):
    result = {}
    for item in items:
        identity = key(item)
        if identity in result:
            raise KnowledgeError("DUPLICATE_CATALOG", f"Duplicate {label}: {identity}")
        result[identity] = item
    return result


class KnowledgeValidator:
    def __init__(self, sources):
        catalogs = [source.document for source in sources if isinstance(source.document, KnowledgeCatalog)]
        self.sources = _unique((entry for catalog in catalogs for entry in catalog.sources), lambda entry: entry.key, "source")
        self.features = _unique((entry for catalog in catalogs for entry in catalog.features), lambda entry: entry.feature_id, "feature")
        self.capabilities = _unique((entry for catalog in catalogs for entry in catalog.capabilities), lambda entry: entry, "capability")
        self.functions = _unique((entry for catalog in catalogs for entry in catalog.derived_functions), lambda entry: entry, "function")
        for feature in self.features.values():
            self.provenance(feature.provenance)
        for source in sources:
            document = source.document
            if isinstance(document, (BaseSpec, DeltaSpec)):
                if document.spec_family == SpecFamily.TEST and document.data_kind != "fixture":
                    raise KnowledgeError("TEST_IS_FIXTURE", "TEST family is only valid for fixture data")
                self.provenance(document.provenance, document.data_kind)
                if document.data_kind == "fixture" and document.provenance.source_type != "fixture":
                    raise KnowledgeError("FIXTURE_PROVENANCE", "Fixture source must declare fixture provenance")
            if isinstance(document, DeltaSpec):
                for change in (*document.schema_changes, *document.changes):
                    if change.provenance is not None:
                        self.provenance(change.provenance, document.data_kind)
                if document.schema_ref_change and document.schema_ref_change.provenance:
                    self.provenance(document.schema_ref_change.provenance, document.data_kind)
            if isinstance(document, BaseSpec):
                self.schema_fields(document.fields, document.data_kind)

    def schema_fields(self, fields, data_kind):
        for field in fields:
            if data_kind == "fixture" and not field.field_id.startswith(("TEST.", "FIXTURE.")):
                raise KnowledgeError("UNMARKED_FIXTURE", field.field_id)
            for bit in field.bits:
                if bit.feature is not None and bit.feature not in self.features:
                    raise KnowledgeError("UNKNOWN_FEATURE", f"{field.field_id}[{bit.bit}] references {bit.feature}")
                if bit.feature is not None:
                    self.provenance(self.features[bit.feature].provenance, data_kind)

    def provenance(self, evidence, data_kind=None):
        if evidence.key not in self.sources:
            raise KnowledgeError("DANGLING_PROVENANCE", f"Unknown source document {evidence.key}")
        if evidence.status == KnowledgeStatus.CONFIRMED and (evidence.verified_by is None or evidence.verified_date is None):
            raise KnowledgeError("UNVERIFIED_CONFIRMED", "Confirmed evidence requires reviewer and review date")
        if data_kind == "production" and evidence.source_type == "fixture":
            raise KnowledgeError("FIXTURE_IN_PRODUCTION", "Production knowledge cannot use fixture evidence")

    def snapshot(self, snapshot, snapshots):
        fields = {item.schema.field_id: item.schema for item in snapshot.fields}
        effective_fields = {item.schema.field_id: item for item in snapshot.fields}
        if snapshot.schema_ref is not None:
            reference = snapshots.get(snapshot.schema_ref.key)
            if reference is None:
                raise KnowledgeError("UNKNOWN_SCHEMA", f"Unknown schema {snapshot.schema_ref.key}")
            if reference.spec.spec_family not in {SpecFamily.NVME, SpecFamily.TEST}:
                raise KnowledgeError("INVALID_SCHEMA_REF", "Requirement schemas must be NVME or TEST")
            if reference.data_kind != snapshot.data_kind:
                raise KnowledgeError("DATA_KIND_MISMATCH", "Requirement and schema data kinds disagree")
            for item in reference.fields:
                if item.schema.field_id in fields:
                    raise KnowledgeError("DUPLICATE_FIELD", item.schema.field_id)
                fields[item.schema.field_id] = item.schema
                effective_fields[item.schema.field_id] = item
        self.schema_fields(fields.values(), snapshot.data_kind)
        for record in snapshot.changes:
            self.provenance(record.provenance, snapshot.data_kind)
        rules = {entry.rule.rule_id: entry.rule for entry in snapshot.rules}
        for rule in rules.values():
            if snapshot.data_kind == "fixture" and not rule.rule_id.startswith(("TEST.", "FIXTURE.")):
                raise KnowledgeError("UNMARKED_FIXTURE", rule.rule_id)
            self.provenance(rule.provenance, snapshot.data_kind)
            for key in (*rule.applies_when, *rule.applicable_when):
                if key not in CONTEXT_PATHS:
                    raise KnowledgeError("UNKNOWN_CONDITION_KEY", f"{rule.rule_id}: {key}")
            for key in rule.applies_when.keys() & rule.applicable_when.keys():
                if _typed(rule.applies_when[key]) != _typed(rule.applicable_when[key]):
                    raise KnowledgeError("IMPOSSIBLE_CONDITION", f"{rule.rule_id}: incompatible {key} conditions")
            field = fields.get(rule.target.field_id)
            if field is None:
                raise KnowledgeError("UNKNOWN_FIELD", f"{rule.rule_id}: {rule.target.field_id}")
            if field.command != rule.target.command:
                raise KnowledgeError("TARGET_COMMAND", rule.rule_id)
            if field.lifecycle == "deprecated" and rule.provenance.status != KnowledgeStatus.DEPRECATED:
                raise KnowledgeError("DEPRECATED_TARGET", rule.rule_id)
            bit = rule.target.bit
            if isinstance(rule.check, BitCheck):
                bit = bit if bit is not None else rule.check.bit
            if bit is not None and bit not in {entry.bit for entry in field.bits}:
                raise KnowledgeError("UNKNOWN_BIT", f"{rule.rule_id}: {bit}")
            if (bit is not None and rule.provenance.status != KnowledgeStatus.DEPRECATED
                    and next(entry for entry in field.bits if entry.bit == bit).lifecycle == "deprecated"):
                raise KnowledgeError("DEPRECATED_TARGET", f"{rule.rule_id}: {field.field_id}[{bit}]")
            if isinstance(rule.check, MaskCheck):
                if bit is not None or field.value_type != "bitmask" or rule.check.mask >= 1 << (field.length * 8):
                    raise KnowledgeError("INVALID_MASK", rule.rule_id)
            if isinstance(rule.check, (BoundCheck, RangeCheck)) and field.value_type not in {"integer", "bitmask"}:
                raise KnowledgeError("CHECK_TYPE", rule.rule_id)
            if isinstance(rule.check, (ExactCheck, EnumCheck)):
                values = [rule.check.value] if isinstance(rule.check, ExactCheck) else rule.check.values
                expected_type = int if field.value_type in {"integer", "bitmask"} else str
                if any(type(value) is not expected_type for value in values):
                    raise KnowledgeError("CHECK_TYPE", rule.rule_id)
                if bit is not None and any(value not in (0, 1) for value in values):
                    raise KnowledgeError("CHECK_TYPE", f"{rule.rule_id}: bit values must be 0 or 1")
                if field.value_type == "bitmask" and any(value < 0 or value >= 1 << (field.length * 8) for value in values):
                    raise KnowledgeError("CHECK_TYPE", f"{rule.rule_id}: value outside bitmask width")
            if isinstance(rule.check, LookupCheck) and rule.check.key not in CONTEXT_PATHS:
                raise KnowledgeError("UNKNOWN_CONDITION_KEY", rule.check.key)
            if isinstance(rule.check, LookupCheck):
                expected_type = int if field.value_type in {"integer", "bitmask"} else str
                if any(type(entry.value) is not expected_type for entry in rule.check.values):
                    raise KnowledgeError("CHECK_TYPE", rule.rule_id)
            if isinstance(rule.check, DerivedCheck) and rule.check.function not in self.functions:
                raise KnowledgeError("UNKNOWN_FUNCTION", rule.check.function)
            if isinstance(rule.check, CapabilityCheck) and rule.check.capability_id not in self.capabilities:
                raise KnowledgeError("UNKNOWN_CAPABILITY", rule.check.capability_id)
            if rule.override is not None:
                self.provenance(rule.override.provenance, snapshot.data_kind)
                for identity in rule.override.overrides:
                    other = rules.get(identity)
                    if other is None:
                        raise KnowledgeError("UNKNOWN_OVERRIDE", f"{rule.rule_id}: {identity}")
                    if identity == rule.rule_id or other.target.field_id != rule.target.field_id:
                        raise KnowledgeError("INVALID_OVERRIDE", rule.rule_id)
                    if rule.override.enabled and other.override and other.override.enabled:
                        raise KnowledgeError("OVERRIDE_CHAIN_UNSUPPORTED", "Phase 1 does not resolve chained overrides")
                if rule.override.enabled and rule.override.provenance.status != KnowledgeStatus.CONFIRMED:
                    raise KnowledgeError("UNCONFIRMED_OVERRIDE", "Enabled override evidence must be reviewed and confirmed")
        _validate_override_cycles(rules)
        constraints = tuple(check for item in effective_fields.values() for check in _schema_constraints(item))
        _validate_literal_conflicts(rules.values(), fields, constraints)


def _schema_constraints(item):
    """Explicit, confirmed schema behavior contributes temporary constraints.

    Reserved alone contributes nothing; schema evidence remains the authority.
    """
    field = item.schema
    if field.lifecycle == "deprecated":
        return
    targets = [(None, field.validation)] + [(bit.bit, bit.validation) for bit in field.bits
                                           if bit.lifecycle != "deprecated"]
    for bit, validation in targets:
        if validation is None:
            continue
        target = field.field_id if bit is None else f"{field.field_id}[{bit}]"
        history = [record for record in item.history if record.target in {field.field_id, target}]
        evidence = history[-1].provenance
        if evidence.status != KnowledgeStatus.CONFIRMED:
            continue
        if bit is None and field.value_type not in {"integer", "bitmask"}:
            raise KnowledgeError("SCHEMA_VALIDATION_UNSUPPORTED", f"Static zero check: {field.field_id}")
        yield RequirementRule(
            rule_id=f"SCHEMA.VALIDATION.{field.field_id}.{bit if bit is not None else 'FIELD'}",
            target=TargetRef(command=field.command, field_id=field.field_id, bit=bit),
            check=ExactCheck(type="EXACT", value=0), provenance=evidence,
        )


def _validate_override_cycles(rules):
    for identity in sorted(rules):
        pending = [(identity, frozenset())]
        while pending:
            current, trail = pending.pop()
            if current in trail:
                raise KnowledgeError("OVERRIDE_CYCLE", current)
            override = rules[current].override
            if override and override.enabled:
                pending.extend((target, trail | {current}) for target in override.overrides)


def _typed(value):
    return type(value).__name__, value


def _validate_literal_conflicts(rules, fields, schema_constraints=()):
    """Check confirmed literal constraints within one snapshot and equality scopes.

    LOOKUP/DERIVED/CAPABILITY execution and cross-profile resolution are out of scope.
    The finite check fails explicitly when its context partition becomes too large.
    """
    by_field = defaultdict(list)
    for rule in rules:
        if rule.provenance.status == KnowledgeStatus.CONFIRMED:
            by_field[rule.target.field_id].append(rule)
    schema_by_field = defaultdict(list)
    for rule in schema_constraints:
        schema_by_field[rule.target.field_id].append(rule)
        by_field.setdefault(rule.target.field_id, [])
    for field_id, group in sorted(by_field.items()):
        dimensions = defaultdict(set)
        for rule in group:
            for key, value in {**rule.applies_when, **rule.applicable_when}.items():
                dimensions[key].add(_typed(value))
        keys = sorted(dimensions)
        size = 1
        for key in keys:
            size *= len(dimensions[key]) + 1
        if size > 4096:
            raise KnowledgeError("CONFLICT_CHECK_LIMIT", f"{field_id}: equality partition exceeds 4096 contexts")
        domains = [sorted(dimensions[key], key=repr) + [("OTHER", None)] for key in keys]
        for assignment in product(*domains):
            facts = dict(zip(keys, assignment))
            active = [rule for rule in group if all(
                facts[key] == _typed(value) for key, value in {**rule.applies_when, **rule.applicable_when}.items()
            )]
            excluded = {identity for rule in active if rule.override and rule.override.enabled for identity in rule.override.overrides}
            active = [rule for rule in active if rule.rule_id not in excluded]
            checked = [*active, *schema_by_field[field_id]]
            if not _literal_compatible(checked, fields[field_id]):
                raise KnowledgeError("EXPLICIT_CONFLICT", f"{field_id}: {', '.join(sorted(rule.rule_id for rule in checked))}")


def _literal_compatible(rules, field):
    lower, upper, choices, mask, value = None, None, None, 0, 0
    checks = [rule.check for rule in rules]
    if any(isinstance(check, ApplicabilityCheck) and check.type == "NOT_APPLICABLE" for check in checks):
        if any(not isinstance(check, ApplicabilityCheck) for check in checks):
            return False
    for rule in rules:
        check = rule.check
        target_bit = rule.target.bit
        if isinstance(check, BitCheck):
            target_bit = target_bit if target_bit is not None else check.bit
            next_mask = 1 << target_bit
            next_value = next_mask if check.type == "BIT_SET" else 0
        elif isinstance(check, MaskCheck):
            next_mask, next_value = check.mask, check.value
        elif isinstance(check, ExactCheck) and target_bit is not None:
            next_mask, next_value = 1 << target_bit, check.value << target_bit
        elif target_bit is not None and isinstance(check, (EnumCheck, BoundCheck, RangeCheck)):
            options = {0, 1}
            if isinstance(check, EnumCheck):
                options &= set(check.values)
            elif isinstance(check, RangeCheck):
                options = {item for item in options if check.min <= item <= check.max}
            elif check.type == "MIN":
                options = {item for item in options if item >= check.value}
            else:
                options = {item for item in options if item <= check.value}
            if not options:
                return False
            next_mask = 1 << target_bit if len(options) == 1 else 0
            next_value = (next(iter(options)) << target_bit) if next_mask else 0
        else:
            next_mask, next_value = 0, 0
        if (value ^ next_value) & mask & next_mask:
            return False
        mask |= next_mask
        value |= next_value
        if target_bit is not None or isinstance(check, MaskCheck):
            continue
        if isinstance(check, (ExactCheck, EnumCheck)):
            options = {_typed(check.value)} if isinstance(check, ExactCheck) else {_typed(item) for item in check.values}
            choices = options if choices is None else choices & options
        if isinstance(check, (BoundCheck, RangeCheck)):
            low = check.min if isinstance(check, RangeCheck) else check.value if check.type == "MIN" else None
            high = check.max if isinstance(check, RangeCheck) else check.value if check.type == "MAX" else None
            if low is not None:
                lower = low if lower is None else max(lower, low)
            if high is not None:
                upper = high if upper is None else min(upper, high)
    if lower is not None and upper is not None and lower > upper:
        return False
    if choices is not None:
        return any(
            (lower is None or item >= lower) and (upper is None or item <= upper)
            and (not mask or item & mask == value)
            for _, item in choices
        )
    if mask or field.value_type == "bitmask":
        # A bitmask is bounded by its declared width. Find the smallest satisfying
        # value >= lower without enumerating every possible field value.
        width = field.length * 8
        low = max(lower or 0, 0)
        high = min(upper if upper is not None else (1 << width) - 1, (1 << width) - 1)
        candidate = low
        for bit in range(width):
            flag = 1 << bit
            if mask & flag and bool(candidate & flag) != bool(value & flag):
                if value & flag:
                    candidate |= flag
                else:
                    candidate = ((candidate >> (bit + 1)) + 1) << (bit + 1)
                candidate = (candidate & ~((1 << bit) - 1)) | (value & ((1 << bit) - 1))
        return candidate <= high
    return True
