import base64
import http.client
import json
import re
import threading
from pathlib import Path

import pytest

from ssd_validator.analyzer.id_ctrl_log import analyze_id_ctrl
from ssd_validator.application.desktop_workflow import DesktopWorkflow
from ssd_validator.gui.server import create_server

ROOT = Path(__file__).resolve().parents[2]
LOG = b'NVME Identify Controller:\nmn : TEST MODEL\nsn : 001234\nfr : TEST_FW\nver : 0x10300\nvid : 0x1234\nnew_unknown : 17\nps 0 : mp:1.0W operational\n    rwt:0 rwl:0\n'


def test_observations_preserve_identity_and_power_state():
    result = analyze_id_ctrl(LOG, 'fixture.txt')
    assert result['identity']['sn'] == '001234'
    assert result['advertised_nvme_version'] == '1.3.0'
    assert len(result['power_states']) == 1
    assert 'rwt:0' in result['power_states'][0]['text']
    assert result['counts']['PASS'] == 0


def test_duplicate_is_not_last_write_wins():
    result = analyze_id_ctrl(LOG + b'vid : 0\n', 'fixture.txt')
    assert [r['status'] for r in result['fields'] if r['field'] == 'vid'] == ['ERROR','ERROR']


def test_bundle_knowledge_provenance_and_unknown():
    workflow = DesktopWorkflow(ROOT)
    for bundle, document in [('nvme-2.1-nvm-1.1','BASE_2_1'),('nvme-2.0e-nvm-1.0e','BASE_2_0E')]:
        result = workflow.analyze(LOG, 'fixture.txt', bundle)
        vid = next(r for r in result['fields'] if r['field'] == 'vid')
        assert vid['status'] == 'REVIEW'
        assert {d['document_id'] for d in vid['definitions']} == {document}
        assert vid['definitions'][0]['evidence']
        assert next(r for r in result['fields'] if r['field'] == 'new_unknown')['status'] == 'UNKNOWN'
        assert result['authoritative'] is False
        assert result['counts']['PASS'] == 0
    with pytest.raises(ValueError, match='Unknown Bundle'):
        workflow.analyze(LOG, 'fixture.txt', 'latest')


def test_existing_services_reused():
    workflow = DesktopWorkflow(ROOT)
    assert workflow.operation('pilot')['status'] == 'PASS'
    assert workflow.operation('builder')['snapshots']
    assert workflow.operation('normalize')['actual_facts']
    assert workflow.operation('bundle-diff')['schema_changes']
    with pytest.raises(ValueError):
        workflow.operation('../arbitrary')


def test_http_session_and_analysis(tmp_path):
    server = create_server(0, root=ROOT, database=tmp_path / 'gui.sqlite3')
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    connection = http.client.HTTPConnection('127.0.0.1', server.server_address[1])
    try:
        connection.request('GET','/')
        page = connection.getresponse().read().decode()
        token = re.search("const token='([^']+)'", page).group(1)
        body = json.dumps({'filename':'fixture.txt','content_base64':base64.b64encode(LOG).decode(),'bundle_id':'nvme-2.1-nvm-1.1'})
        connection.request('POST','/api/analyze',body,{'Content-Type':'application/json'})
        denied = connection.getresponse()
        assert denied.status == 403
        denied.read()
        connection.request('POST','/api/analyze',body,{'Content-Type':'application/json','X-Session-Token':token})
        response = connection.getresponse()
        assert response.status == 200
        assert json.loads(response.read())['report']['counts']['PASS'] == 0
    finally:
        connection.close()
        server.shutdown()
        server.server_close()
        thread.join()
