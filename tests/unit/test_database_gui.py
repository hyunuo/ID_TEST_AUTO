import base64
import http.client
import json
import re
import threading
from pathlib import Path

from ssd_validator.gui.server import create_server

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = 'nvme-2.1-nvm-1.1'
LOG = b'NVME Identify Controller:\nsqes:0x66\ncqes:0x44\nnpss:4\nawun:0\nawupf:0\noacs:6\n'


def test_gui_sqlite_rule_edit_history_replay_and_session(tmp_path):
    server = create_server(0, root=ROOT, database=tmp_path / 'gui.sqlite3')
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    conn = http.client.HTTPConnection('127.0.0.1', server.server_address[1])
    try:
        conn.request('GET', '/')
        page = conn.getresponse().read().decode()
        token = re.search("const token='([^']+)'", page).group(1)
        assert '규칙·정책 편집' in page and '검사 이력' in page and 'id="managetab"' in page
        conn.request('GET', '/management.js')
        response = conn.getresponse()
        assert response.status == 200 and b'/api/rule' in response.read()
        assert '/visual.js' in page and 'id="verdictviz"' in page and 'id="bitmap"' in page
        conn.request('GET', '/visual.js')
        response = conn.getresponse()
        assert response.status == 200 and b'function renderBitMap' in response.read()

        def call(path, body, authorized=True):
            headers = {'Content-Type': 'application/json'}
            if authorized:
                headers['X-Session-Token'] = token
            conn.request('POST', path, json.dumps(body), headers)
            response = conn.getresponse()
            return response.status, json.loads(response.read())

        assert call('/api/knowledge', {'bundle_id': BUNDLE}, False)[0] == 403
        _, knowledge = call('/api/knowledge', {'bundle_id': BUNDLE})
        payload = {'filename': 'test.txt', 'content_base64': base64.b64encode(LOG).decode(),
                   'bundle_id': BUNDLE, 'experimental': True}
        status, old = call('/api/analyze', payload)
        assert status == 200 and old['report']['validation']['status'] == 'PASS'
        rule = next(rule for rule in knowledge['rules'] if rule['check']['type'] == 'CAPABILITY')
        rule['check']['support'] = 'unsupported'
        edit = {'bundle_id': BUNDLE, 'expected_revision': knowledge['revision'], 'reason': 'TEST policy change',
                'original_rule_id': rule['rule_id'], 'rule': rule}
        assert call('/api/rule', edit, False)[0] == 403
        assert call('/api/rule', edit)[1]['revision'] == 2
        assert call('/api/rule', edit)[0] == 400
        assert call('/api/analyze', payload)[1]['report']['validation']['status'] == 'FAIL'
        run_id = old['report']['run_id']
        assert call('/api/run', {'run_id': run_id})[1] == old
        replay = call('/api/replay', {'run_id': run_id})[1]['report']
        assert replay['validation']['status'] == 'PASS' and replay['repository']['revision'] == 1
        assert len(call('/api/history', {})[1]['runs']) == 3
        assert call('/api/sources/export', {})[1]['format'] == 'ssd-validator-source-v1'
        assert call('/api/run', {'run_id': 999999})[0] == 400
        assert call('/api/database/backup', {}, False)[0] == 403
        status = call('/api/database/status', {})[1]
        assert status['schema_version'] == '3' and status['runs'] == 3
        backup = call('/api/database/backup', {})[1]
        assert backup['filename'].endswith('.sqlite3')
        assert call('/api/database/restore', {'content_base64': base64.b64encode(b'bad').decode(),
                                             'expected_revision': 2})[0] == 400
        assert call('/api/database/status', {})[1]['revision'] == 2
        restored = call('/api/database/restore', {'content_base64': backup['content_base64'], 'expected_revision': 2})
        assert restored[0] == 200 and restored[1]['revision'] == 3
        assert call('/api/run', {'run_id': run_id})[1] == old
        assert call('/api/bundles',{})[1]['bundles']
        listing=call('/api/entities',{'kind':'rule','bundle_id':BUNDLE,'search':'POWER_STATE_LIMIT'})[1]
        target=listing['items'][0]
        changed=target['payload']; changed['check']['value']=3
        body={'kind':'rule','bundle_id':BUNDLE,'original_id':target['entity_id'],
              'payload':changed,'expected_revision':3,'reason':'TEST preview endpoint'}
        assert call('/api/entity/preview',body,False)[0]==403
        code,preview=call('/api/entity/preview',body)
        assert code==200 and preview['changes']
        assert call('/api/database/status',{})[1]['revision']==3
        assert call('/api/entity/save',{**body,'preview_hash':'bad'})[0]==400
        assert call('/api/entity/save',{**body,'preview_hash':preview['preview_hash']})[1]['revision']==4
        assert call('/api/entity/save',{**body,'preview_hash':preview['preview_hash']})[0]==400
        revert={'target_revision':3,'expected_revision':4,'reason':'TEST GUI revert'}
        before=call('/api/revision/preview',revert)[1]
        assert call('/api/revision/revert',{**revert,'preview_hash':before['preview_hash']})[1]['revision']==5
        assert call('/api/run',{'run_id':run_id})[1]==old
    finally:
        conn.close()
        server.shutdown()
        server.server_close()
        thread.join()
