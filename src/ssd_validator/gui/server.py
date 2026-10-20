"""Loopback-only GUI with revisioned local knowledge and saved validation runs."""

import base64
import json
import secrets
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from pathlib import Path

from ssd_validator.application.database_workflow import DatabaseWorkflow
from ssd_validator.errors import KnowledgeError


def create_server(port: int = 8765, sample: Path | None = None, root: Path | None = None, database: Path | None = None):
    workflow = DatabaseWorkflow(root or Path.cwd(), database)
    token = secrets.token_urlsafe(32)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass  # Do not print device identifiers or file contents to the terminal.

        def send(self, status, payload, content_type="application/json; charset=utf-8"):
            body = payload.encode("utf-8") if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(body)

        def allowed_host(self):
            port = self.server.server_address[1]
            return self.headers.get("Host") in {f"127.0.0.1:{port}", f"localhost:{port}"}

        def authorized(self):
            return self.allowed_host() and secrets.compare_digest(self.headers.get("X-Session-Token", ""), token)

        def do_GET(self):
            if not self.allowed_host():
                self.send(403, {"error": "Local host required"})
            elif self.path == "/":
                page = files('ssd_validator.gui').joinpath('index.html').read_text(encoding='utf-8').replace('__SESSION_TOKEN__', token)
                self.send(200, page, "text/html; charset=utf-8")
            elif self.path in {'/management.js','/entities.js','/captures.js','/products.js','/coverage.js','/supplemental.js','/visual.js'}:
                self.send(200, files('ssd_validator.gui').joinpath(self.path[1:]).read_text(encoding='utf-8'),
                          'text/javascript; charset=utf-8')
            elif self.path == "/api/sample":
                if not self.authorized():
                    self.send(403, {"error": "Invalid session"})
                    return
                if sample is None:
                    self.send(404, {"error": "No sample configured; choose a log file"})
                    return
                try:
                    data = sample.read_bytes()
                    if len(data) > 1024 * 1024:
                        raise ValueError('Log size exceeds 1 MiB')
                    self.send(200, {"filename": sample.name, "content_base64": base64.b64encode(data).decode("ascii")})
                except (OSError, ValueError, KnowledgeError) as error:
                    self.send(400, {"error": str(error)})
            else:
                self.send(404, {"error": "Not found"})

        def do_POST(self):
            if not self.authorized():
                self.send(403, {"error": "Invalid local session"})
                return
            if self.path not in {"/api/analyze", "/api/analyze-captures", "/api/products", "/api/profiles/suggest", "/api/nvme/coverage", "/api/supplemental", "/api/operation", "/api/knowledge", "/api/rule",
                                  "/api/sources/export", "/api/sources/import", "/api/history", "/api/run", "/api/replay",
                                  "/api/database/status", "/api/database/backup", "/api/database/restore",
                                  "/api/bundles", "/api/entities", "/api/entity/preview", "/api/entity/save",
                                  "/api/revision/preview", "/api/revision/revert"}:
                self.send(404, {"error": "Not found"})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                limit = (96 * 1024 * 1024 if self.path == '/api/database/restore' else
                         24 * 1024 * 1024 if self.path in {'/api/analyze-captures','/api/profiles/suggest'} else
                         32 * 1024 * 1024 if self.path == '/api/sources/import' else 2 * 1024 * 1024)
                if not 0 < length <= limit:
                    raise ValueError("Request exceeds size limit")
                def unique(pairs):
                    result = {}
                    for key, value in pairs:
                        if key in result:
                            raise ValueError("Duplicate JSON key")
                        result[key] = value
                    return result
                body = json.loads(self.rfile.read(length).decode("utf-8"), object_pairs_hook=unique)
                if not isinstance(body, dict):
                    raise ValueError('Request must be a JSON object')
                if self.path == '/api/bundles':
                    self.send(200, workflow.bundles())
                    return
                if self.path == '/api/products':
                    self.send(200,workflow.products())
                    return
                if self.path == '/api/supplemental':
                    self.send(200, workflow.supplemental_requirements())
                    return
                if self.path == '/api/nvme/coverage':
                    self.send(200,workflow.nvme_coverage())
                    return
                if self.path == '/api/profiles/suggest':
                    self.send(200,workflow.suggest_profiles(body['package'],body['bundle_id'],context_facts=body.get('context_facts')))
                    return
                if self.path == '/api/entities':
                    self.send(200, workflow.entity_search(kind=body.get('kind'),bundle_id=body.get('bundle_id'),search=body.get('search','')))
                    return
                if self.path in {'/api/entity/preview','/api/revision/preview'}:
                    self.send(200, workflow.preview_change(body))
                    return
                if self.path in {'/api/entity/save','/api/revision/revert'}:
                    self.send(200, workflow.save_change(body))
                    return
                if self.path == '/api/database/status':
                    self.send(200, workflow.database_status())
                    return
                if self.path == '/api/database/backup':
                    self.send(200, workflow.backup_database())
                    return
                if self.path == '/api/database/restore':
                    self.send(200, workflow.restore_database(body['content_base64'], expected_revision=body['expected_revision']))
                    return
                if self.path == '/api/knowledge':
                    self.send(200, workflow.knowledge(body['bundle_id']))
                    return
                if self.path == '/api/rule':
                    self.send(200, workflow.edit_rule(body['bundle_id'], expected_revision=body['expected_revision'],
                        reason=body['reason'], rule=body.get('rule'), original_rule_id=body.get('original_rule_id'),
                        delete=body.get('delete', False)))
                    return
                if self.path == '/api/sources/export':
                    self.send(200, workflow.export_sources(body.get('revision')))
                    return
                if self.path == '/api/sources/import':
                    self.send(200, workflow.import_sources(body['package'], expected_revision=body['expected_revision'], reason=body['reason']))
                    return
                if self.path == '/api/history':
                    self.send(200, workflow.history())
                    return
                if self.path in {'/api/run', '/api/replay'}:
                    result = workflow.load_run(body['run_id']) if self.path == '/api/run' else workflow.replay(body['run_id'])
                    self.send(200, {'report': result})
                    return
                if self.path == '/api/operation':
                    self.send(200, {'report': workflow.operation(body['operation'])})
                    return
                if self.path == '/api/analyze-captures':
                    self.send(200, {'report':workflow.analyze_captures(body['package'],body['bundle_id'],
                        experimental=body.get('experimental',True),context_facts=body.get('context_facts'),
                        policy_mode=body.get('policy_mode','assumed-development'),profile_id=body.get('profile_id'))})
                    return
                if not isinstance(body.get("filename"), str):
                    raise ValueError("A filename and base64 log are required")
                data = base64.b64decode(body["content_base64"], validate=True)
                experimental = body.get('experimental', True)
                if type(experimental) is not bool:
                    raise ValueError('experimental must be Boolean')
                selected = body.get('bundle_id')
                if selected is None:
                    selected = workflow.bundles()['bundles'][0]['bundle_id']
                self.send(200, {"report": workflow.analyze(data, body["filename"], selected,
                    experimental=experimental, context_facts=body.get('context_facts'),
                    policy_mode=body.get('policy_mode', 'assumed-development'),profile_id=body.get('profile_id'))})
            except (ValueError, KeyError, TypeError, OSError, KnowledgeError, sqlite3.Error) as error:
                self.send(400, {"error": str(error)})

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def serve(port: int = 8765, sample: Path | None = None, database: Path | None = None):
    server = create_server(port, sample, database=database)
    print(f"NVMe log viewer: http://127.0.0.1:{server.server_address[1]}/", flush=True)
    print("Ctrl+C to stop. Logs are processed locally.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
