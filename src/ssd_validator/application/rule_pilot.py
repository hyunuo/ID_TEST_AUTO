"""Build fixture Source with the existing Builder, then resolve offline rules."""

import json
from hashlib import sha256
from pathlib import Path

from ssd_validator.application.build_knowledge import compile_knowledge
from ssd_validator.errors import KnowledgeError
from ssd_validator.models.effective import SourceFile
from ssd_validator.models.runtime import FieldRegistration, PilotInput, PilotMappings
from ssd_validator.resolver import evaluate, resolve


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def run_pilot(source: Path, input_path: Path):
    input_bytes = input_path.read_bytes()
    configuration = PilotInput.model_validate(json.loads(input_bytes.decode("utf-8"), object_pairs_hook=_unique_object))
    built = compile_knowledge(source)
    by_key = {s.spec.key: s for s in built.snapshots}
    if any(k not in by_key for k in configuration.bundle.snapshot_keys):
        raise KnowledgeError("SNAPSHOT_SELECTION", "Unknown selected snapshot")
    snapshots = tuple(by_key[k] for k in sorted(configuration.bundle.snapshot_keys))
    fields = {}
    for snapshot in snapshots:
        for item in snapshot.fields:
            key = item.schema.field_id
            if key in fields and fields[key] != item:
                raise KnowledgeError("FIELD_LAYER_CONFLICT", key)
            fields[key] = item
    registrations = []
    for binding in configuration.bindings:
        if binding.field_id not in fields:
            raise KnowledgeError("UNKNOWN_FIELD_BINDING", binding.field_id)
        item = fields[binding.field_id]
        history = [h for h in item.history if h.target == binding.field_id]
        evidence = history[-1].provenance if history else item.history[-1].provenance
        registrations.append(FieldRegistration(schema_definition=item.schema, cns=binding.cns, csi=binding.csi,
                                                array_count=binding.array_count, provenance=evidence, history=item.history))
    mappings = PilotMappings(bundle=configuration.bundle, fields=tuple(registrations), rules=configuration.rules,
                             capabilities=configuration.capabilities,
                             input_source=SourceFile(path=input_path.as_posix(), sha256=sha256(input_bytes).hexdigest()))
    profile = resolve(configuration.context, snapshots, mappings)
    return evaluate(profile, configuration.actual_facts)
