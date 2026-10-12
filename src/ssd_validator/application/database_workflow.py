"""SQLite source workflow adapting immutable revisions to the existing engines."""

import json
import base64
from hashlib import sha256
from pathlib import Path

from ssd_validator.application.build_knowledge import compile_knowledge
from ssd_validator.application.desktop_workflow import DesktopWorkflow
from ssd_validator.application.experimental_validation import ExperimentalConfiguration
from ssd_validator.application.rule_pilot import _unique_object
from ssd_validator.models.runtime import RuntimeRule
from ssd_validator.knowledge.yaml_loader import load_document
from ssd_validator.storage.knowledge_db import KnowledgeDatabase, encode
from ssd_validator.application.knowledge_management import bundle_path, bundle_ids, entities, validate_metadata, change_entity


def config_path(bundle):
    return bundle_path(bundle)


def validate_sources(root):
    # Reuse candidate compiler, Builder, Resolver and strict domain schemas.
    workflow = DesktopWorkflow(root)
    for path in (root / 'knowledge').rglob('*'):
        if path.suffix in {'.yaml', '.yml'}:
            load_document(path)
    for catalog in (root / 'knowledge').rglob('catalog.yaml'):
        compile_knowledge(catalog.parent)
    workflow.candidates()
    sources = {path.relative_to(root).as_posix():path.read_text(encoding='utf-8')
               for parent in ('knowledge','candidates') for path in (root/parent).rglob('*')
               if path.is_file() and path.suffix in {'.json','.yaml','.yml'}}
    validate_metadata(sources)
    from ssd_validator.application.nvme_expansion import coverage
    coverage(sources)
    for bundle in bundle_ids(sources):
        config = ExperimentalConfiguration.model_validate(json.loads(
            (root / config_path(bundle)).read_text(encoding='utf-8'), object_pairs_hook=_unique_object))
        ids = [rule.rule_id for rule in config.rules]
        if len(ids) != len(set(ids)):
            raise ValueError('Duplicate rule ID')
        from ssd_validator.application.knowledge_management import yaml_read, metadata
        catalog = yaml_read(sources[f'knowledge/experimental/id_ctrl/{bundle}/catalog.yaml'])
        known = {(s['source_type'],s['source_document'],s['source_version']) for s in catalog['sources']}
        for rule in [*config.rules,*config.capabilities]:
            evidence = [rule.provenance, *getattr(rule,'supporting_evidence',())]
            if getattr(rule,'override',None):
                evidence.append(rule.override.provenance)
            for provenance in evidence:
                if provenance.key not in known:
                    raise ValueError('Unknown source document/version reference')
                if provenance.status == 'confirmed' and (not provenance.verified_by or not provenance.verified_date):
                    raise ValueError('Confirmed knowledge requires reviewer and date')
        docs = json.loads(sources['candidates/nvme/catalog.json'])['documents']
        page_limits = {d['document_id']:d['pages'] for d in docs}
        registered_docs = {s[1] for s in known}
        for evidence in config.field_evidence.values():
            for anchor in evidence.get('evidence', []):
                if anchor['document_id'] not in registered_docs:
                    raise ValueError('Field evidence references unknown document')
                if anchor.get('pdf_page',1) > page_limits.get(anchor['document_id'],float('inf')):
                    raise ValueError('Field evidence page is outside document')
        for rule in config.rules:
            if rule.check.type in {'LOOKUP', 'DERIVED'}:
                raise ValueError('Unsupported executable expression')
        result = workflow.analyze(b'NVME Identify Controller:\nsn:SOURCE_VALIDATION\n', 'SOURCE_VALIDATION.txt', bundle, experimental=True)
        from ssd_validator.models.runtime import EffectiveExpectedProfile
        from ssd_validator.models.actual_data import IdentifyQuery
        from ssd_validator.analyzer.actual_normalizer import layout_from_profile
        profile = EffectiveExpectedProfile.model_validate(result['validation']['profile'])
        binding_values = metadata(sources)['bindings'].get(bundle,{})
        for cns,csi in {(f.cns,f.csi) for f in profile.fields}:
            selected = [f for f in profile.fields if (f.cns,f.csi)==(cns,csi)]
            from ssd_validator.application.knowledge_management import Binding
            sizes = {Binding.model_validate(binding_values.get(f.schema_definition.field_id,{})).response_size for f in selected}
            if len(sizes)!=1:
                raise ValueError('Fields for one query disagree on response size')
            layout_from_profile(profile, IdentifyQuery(cns=cns,csi=csi), response_size=next(iter(sizes)),
                array_strides={key:item['array_stride'] for key,item in binding_values.items() if item.get('array_stride')})
        errors = [entry for entry in result['validation']['profile']['entries'] if entry['state']=='ERROR']
        if errors:
            details = '; '.join(f"{entry['rule']['rule_id']}: {entry['reason']}" for entry in errors[:6])
            raise ValueError('Rule resolution error; source revision was not saved: '+details)
    from ssd_validator.application.product_profiles import validate_products
    validate_products(root,sources)
    from ssd_validator.application.supplemental_requirements import validate_registry
    validate_registry(sources)
    # Persistent index projection is derived from these validated source documents.
    return entities(sources)


def stable_paths(value, root, revision):
    """Replace ephemeral projection paths with persistent DB revision references."""
    if isinstance(value, dict):
        return {key: stable_paths(child, root, revision) for key, child in value.items()}
    if isinstance(value, list):
        return [stable_paths(child, root, revision) for child in value]
    if isinstance(value, str):
        for prefix in (str(root) + '\\', root.as_posix() + '/'):
            if value.startswith(prefix):
                return f'sqlite://knowledge/revisions/{revision}/' + value[len(prefix):].replace('\\', '/')
    return value


class DatabaseWorkflow:
    def __init__(self, root: Path, database: Path | None = None):
        self.root = root
        self.repository = KnowledgeDatabase(database or root / 'data/validator.sqlite3')
        self.repository.bootstrap(root, validate_sources)

    def analyze(self, data, filename, bundle_id, *, experimental=False, context_facts=None,
                policy_mode='assumed-development', revision=None,profile_id=None):
        if profile_id is not None and (type(profile_id) is not str or not profile_id.strip()):
            raise ValueError('Profile ID must be nonempty text or null')
        if profile_id:
            return self.analyze_captures({'captures':[{'capture_id':'SAVED_ID_CTRL_LOG','filename':filename,
                'command':'id-ctrl','content_base64':base64.b64encode(data).decode('ascii')}]},bundle_id,
                experimental=experimental,context_facts=context_facts,policy_mode=policy_mode,revision=revision,profile_id=profile_id)
        # A restore cannot replace revisions between reading sources and saving a run.
        with self.repository.lock:
            return self._analyze(data, filename, bundle_id, experimental=experimental,
                context_facts=context_facts, policy_mode=policy_mode, revision=revision)

    def _analyze(self, data, filename, bundle_id, *, experimental=False, context_facts=None,
                 policy_mode='assumed-development', revision=None):
        revision = self.repository.head() if revision is None else revision
        sources = self.repository.sources(revision)
        with self.repository.project(sources) as root:
            report = DesktopWorkflow(root).analyze(data, filename, bundle_id, experimental=experimental,
                context_facts=context_facts, policy_mode=policy_mode)
            report = stable_paths(report, root, revision)
        report['repository'] = {'kind': 'sqlite_source', 'revision': revision}
        options = dict(bundle_id=bundle_id, experimental=experimental, context_facts=context_facts, policy_mode=policy_mode)
        identity = self.repository.save_run(revision, filename, data, options, report)
        report['run_id'] = identity
        return report

    def operation(self, name):
        # Fixture operations remain explicitly file-based; candidate comparisons use DB.
        if name != 'bundle-diff':
            return DesktopWorkflow(self.root).operation(name)
        with self.repository.project(self.repository.sources()) as root:
            return DesktopWorkflow(root).operation(name)

    def analyze_captures(self, package, bundle_id, *, experimental=True, context_facts=None,
                         policy_mode='assumed-development', revision=None,profile_id=None):
        from ssd_validator.application.saved_capture_workflow import analyze_captures
        from ssd_validator.models.saved_captures import SavedCaptureSet
        if type(experimental) is not bool:
            raise ValueError('experimental must be Boolean')
        if profile_id is not None and (type(profile_id) is not str or not profile_id.strip()):
            raise ValueError('Profile ID must be nonempty text or null')
        package = SavedCaptureSet.model_validate(package).model_dump(mode='json')
        with self.repository.lock:
            revision = self.repository.head() if revision is None else revision
            with self.repository.project(self.repository.sources(revision)) as root:
                report = analyze_captures(root, package, bundle_id, experimental=experimental,
                    context_facts=context_facts,policy_mode=policy_mode,profile_id=profile_id)
                report = stable_paths(report, root, revision)
            report['repository'] = {'kind':'sqlite_source','revision':revision}
            options = dict(input_kind='saved-captures-v1',bundle_id=bundle_id,experimental=experimental,
                context_facts=context_facts,policy_mode=policy_mode)
            if profile_id:
                options['profile_id']=profile_id
            # Existing immutable run storage hashes the whole versioned envelope, including original bytes.
            report['run_id'] = self.repository.save_run(revision,'saved-captures.json',encode(package).encode('utf-8'),options,report)
            return report

    def products(self):
        from ssd_validator.application.product_profiles import registry
        revision=self.repository.head()
        return {'revision':revision,**registry(self.repository.sources(revision)).model_dump(mode='json')}

    def supplemental_requirements(self):
        from ssd_validator.application.supplemental_requirements import overview
        with self.repository.lock:
            revision=self.repository.head()
            return {'revision':revision,**overview(self.repository.sources(revision))}

    def nvme_coverage(self):
        from ssd_validator.application.nvme_expansion import coverage
        revision=self.repository.head()
        return {'revision':revision,'bundles':coverage(self.repository.sources(revision)),'authoritative':False}

    def suggest_profiles(self,package,bundle_id,*,context_facts=None):
        from ssd_validator.application.product_profiles import read_registry,match_profile,observed_identity
        from ssd_validator.application.saved_capture_workflow import analyze_captures
        with self.repository.lock:
            revision=self.repository.head()
            with self.repository.project(self.repository.sources(revision)) as root:
                report=analyze_captures(root,package,bundle_id,experimental=False,context_facts=context_facts)
                data=read_registry(root)
            suggestions=[]
            for scope in report['scopes']:
                observed,conflicts=observed_identity([c for c in report['captures'] if c['capture_id'] in scope['capture_ids']])
                if type(scope['nsid']) is int:
                    observed['namespace.nsid']=scope['nsid']
                matches=[match_profile(p,observed,context_facts or {}) for p in data.profiles if p.provenance.status!='deprecated']
                candidates=[m['profile_id'] for m in matches if m['state']=='TRUE'] if not conflicts else []
                pending=[m['profile_id'] for m in matches if m['state']=='UNKNOWN']
                status='CONFLICT' if conflicts else 'AMBIGUOUS' if len(candidates)>1 else 'CANDIDATE' if len(candidates)==1 and not pending else 'UNKNOWN'
                suggestions.append({'scope_id':scope['scope_id'],'capture_ids':scope['capture_ids'],'nsid':scope['nsid'],
                    'observed':observed,'observation_conflicts':conflicts,'status':status,'candidates':candidates,
                    'pending':pending,'matches':matches,'selected_profile_id':None})
            return {'revision':revision,'scopes':suggestions,'automatic_selection':False}

    def knowledge(self, bundle):
        path = config_path(bundle)
        revision = self.repository.head()
        sources = self.repository.sources(revision)
        if bundle not in bundle_ids(sources):
            raise ValueError('Unknown Bundle')
        config = json.loads(sources[path])
        registered = self.repository.entity_list(revision=revision, kind='field', bundle=bundle)
        return {'revision': revision, 'bundle': config['bundle'],
                'rules': self.repository.rules(bundle, revision), 'assumptions': config['assumptions'],
                'fields': sorted(e['entity_id'] for e in registered), 'field_entities': registered,
                'capabilities': config['capabilities'], 'revisions': self.repository.revisions()}

    def bundles(self):
        revision = self.repository.head()
        return {'revision':revision, 'bundles':[item['payload'] for item in self.repository.entity_list(revision=revision,kind='bundle')],
                'documents':[item['payload'] for item in self.repository.entity_list(revision=revision,kind='document')]}

    def entity_search(self, *, kind=None, bundle_id=None, search=''):
        revision = self.repository.head()
        if not isinstance(search,str):
            raise ValueError('Search must be text')
        return {'revision':revision, 'items':self.repository.entity_list(revision=revision,kind=kind,bundle=bundle_id,search=search)}

    def _prepare_change(self, request):
        revision = request['expected_revision']
        if type(revision) is not int or self.repository.head() != revision:
            raise ValueError('REVISION_CONFLICT: Reload before editing')
        if not isinstance(request.get('reason'),str) or not request['reason'].strip():
            raise ValueError('A change reason is required')
        original = self.repository.sources(revision)
        if 'target_revision' in request:
            changed = self.repository.sources(request['target_revision'])
        else:
            changed = change_entity(original, kind=request['kind'], bundle_id=request.get('bundle_id',''),
                original_id=request.get('original_id'), payload=request.get('payload'),
                delete=request.get('delete',False), review=request.get('review'))
            if original['candidates/nvme/catalog.json'] != changed['candidates/nvme/catalog.json']:
                # Only explicit catalog edits reach here; no source pin is silently refreshed on import.
                from ssd_validator.application.candidate_knowledge import compile_candidates
                with self.repository.project(changed) as root:
                    _,_,manifest,_ = compile_candidates(root/'candidates/nvme')
                for bundle in bundle_ids(changed):
                    cfg = json.loads(changed[config_path(bundle)])
                    cfg['candidate_knowledge_hash'] = manifest['knowledge_hash']
                    changed[config_path(bundle)] = encode(cfg)
        if changed == original:
            raise ValueError('No source changes to save')
        with self.repository.project(changed) as root:
            validate_sources(root)
        digest = sha256(encode(changed).encode()).hexdigest()
        return original, changed, digest

    def preview_change(self, request):
        original, changed, digest = self._prepare_change(request)
        before = {(e['kind'],e['bundle_id'],e['entity_id']):e for e in entities(original)}
        after = {(e['kind'],e['bundle_id'],e['entity_id']):e for e in entities(changed)}
        changes = [{'kind':key[0], 'bundle_id':key[1], 'entity_id':key[2], 'before':before.get(key), 'after':after.get(key)}
                   for key in sorted(before.keys() | after.keys()) if before.get(key) != after.get(key)]
        return {'revision':request['expected_revision'], 'preview_hash':digest, 'changes':changes,
                'files':sorted(p for p in original.keys() | changed.keys() if original.get(p) != changed.get(p))}

    def save_change(self, request):
        _,changed,digest = self._prepare_change(request)
        if request.get('preview_hash') != digest:
            raise ValueError('PREVIEW_CHANGED: Preview and review the current edit before saving')
        revision = self.repository.commit(changed, expected_revision=request['expected_revision'],
            reason=request['reason'], validate=validate_sources)
        return {'revision':revision}

    def edit_rule(self, bundle, *, expected_revision, reason, rule, original_rule_id=None, delete=False):
        if type(delete) is not bool:
            raise ValueError('delete must be Boolean')
        if self.repository.head() != expected_revision:
            raise ValueError('REVISION_CONFLICT: Reload before editing')
        path = config_path(bundle)
        sources = self.repository.sources(expected_revision)
        config = json.loads(sources[path])
        old = next((item for item in config['rules'] if item['rule_id'] == original_rule_id), None)
        if original_rule_id is not None and old is None:
            raise ValueError('Unknown rule ID')
        if delete:
            if old is None:
                raise ValueError('Choose a rule to delete')
            config['rules'].remove(old)
        else:
            parsed = RuntimeRule.model_validate(rule).model_dump(mode='json', exclude_none=True)
            # Confirmed requires a reviewed import; the simple editor cannot manufacture approval.
            if parsed['provenance']['status'] == 'confirmed' and (old is None or parsed !=
                    RuntimeRule.model_validate(old).model_dump(mode='json', exclude_none=True)):
                raise ValueError('Edited/new knowledge must be candidate or provisional; confirmed requires review evidence')
            if old is not None:
                config['rules'][config['rules'].index(old)] = parsed
            else:
                config['rules'].append(parsed)
        # Display active policy requirements from the rules rather than stale prose assumptions.
        assumptions = [item for item in config['assumptions'] if not item['id'].startswith('LAB.')]
        for item in config['rules']:
            if item['provenance']['source_type'] == 'policy' and item['check']['type'] == 'CAPABILITY':
                assumptions.append({'id': item['check']['capability_id'], 'rule_id': item['rule_id'],
                    'value': item['check']['support'],
                    'reason': '해당 정책 규칙의 조건에서 적용하는 Capability 요구. 실제 제품 정책으로 확인되지 않음.'})
        config['assumptions'] = assumptions
        sources[path] = encode(config)
        return {'revision': self.repository.commit(sources, expected_revision=expected_revision,
                    reason=reason, validate=validate_sources)}

    def export_sources(self, revision=None):
        revision = self.repository.head() if revision is None else revision
        return {'format': 'ssd-validator-source-v1', 'revision': revision,
                'sources': self.repository.sources(revision)}

    def import_sources(self, package, *, expected_revision, reason):
        if not isinstance(package, dict) or package.get('format') != 'ssd-validator-source-v1':
            raise ValueError('Unsupported source export format')
        return {'revision': self.repository.commit(package.get('sources'), expected_revision=expected_revision,
                    reason=reason, validate=validate_sources)}

    def history(self):
        return {'runs': self.repository.runs(), 'revisions': self.repository.revisions()}

    def database_status(self):
        return self.repository.status()

    def backup_database(self):
        with self.repository.lock:
            data = self.repository.backup()
            status = self.repository.status()
        return {'filename': f'validator-r{status["revision"]}-v{status["schema_version"]}.sqlite3',
                'content_base64': base64.b64encode(data).decode('ascii'), 'sha256': sha256(data).hexdigest(),
                'bytes': len(data)}

    def restore_database(self, content_base64, *, expected_revision):
        data = base64.b64decode(content_base64, validate=True)
        if len(data) > 64 * 1024 * 1024:
            raise ValueError('Database backup must be no more than 64 MiB')
        return self.repository.restore(data, expected_revision=expected_revision, validate=validate_sources)

    def load_run(self, identity):
        item = self.repository.run(identity)
        result = json.loads(item['result'])
        result['run_id'] = item['id']
        return result

    def replay(self, identity):
        item = self.repository.run(identity)
        options = json.loads(item['options'])
        if options.pop('input_kind',None) == 'saved-captures-v1':
            return self.analyze_captures(json.loads(item['input']), revision=item['revision'], **options)
        return self.analyze(item['input'], item['filename'], revision=item['revision'], **options)
