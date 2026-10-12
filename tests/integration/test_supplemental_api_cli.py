"""HTTP/CLI supplemental registry using TEST associations in temporary databases."""
import base64
import http.client
import json
import re
import threading
from pathlib import Path
from typer.testing import CliRunner
from ssd_validator.application.database_workflow import DatabaseWorkflow
from ssd_validator.application.nvme_expansion import PACK_PATH,prepare_sources as nvme_sources
from ssd_validator.application.supplemental_requirements import CANDIDATE_PATH,prepare_sources,parse
from ssd_validator.cli import app
from ssd_validator.gui.server import create_server
ROOT=Path(__file__).resolve().parents[2]

def test_registered_policies_mapping_gui_trace_and_cli(tmp_path):
    database=tmp_path/'TEST.sqlite3';w=DatabaseWorkflow(ROOT,database)
    assert w.supplemental_requirements()['registered'] is False
    sources=nvme_sources(w.repository.sources(),json.loads((ROOT/PACK_PATH).read_text(encoding='utf-8')))
    sources=prepare_sources(sources,parse((ROOT/CANDIDATE_PATH).read_text(encoding='utf-8')))
    w.import_sources({'format':'ssd-validator-source-v1','sources':sources},expected_revision=1,reason='TEST supplemental')
    server=create_server(0,root=ROOT,database=database);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    conn=http.client.HTTPConnection('127.0.0.1',server.server_address[1])
    try:
        conn.request('GET','/');page=conn.getresponse().read().decode();token=re.search("const token='([^']+)'",page)[1]
        assert '/supplemental.js' in page
        conn.request('GET','/supplemental.js');response=conn.getresponse();assert response.status==200 and b'/api/supplemental' in response.read()
        def call(path,body,authorized=True):
            headers={'Content-Type':'application/json'}
            if authorized:headers['X-Session-Token']=token
            conn.request('POST',path,json.dumps(body),headers);response=conn.getresponse();return response.status,json.loads(response.read())
        assert call('/api/supplemental',{},False)[0]==403
        status,result=call('/api/supplemental',{});assert status==200 and result['registered'] and result['revision']==2
        assert result['document']['source_version']=='2.6' and all(not b['bound_profiles'] for b in result['bundles'])
        bundle='nvme-2.1-nvm-1.1'
        assert len(call('/api/entities',{'kind':'product_policy','bundle_id':bundle,'search':'OCP'})[1]['items'])==1
        rules=call('/api/knowledge',{'bundle_id':bundle})[1]['capabilities'];assert any(c['capability_id']=='OCP.ADVERTISED.NVME_MI' for c in rules)
        log=b'NVME Identify Controller:\nsqes:0x66\ncqes:0x44\nnpss:0\nawun:0\nawupf:0\noacs:6\n'
        body={'bundle_id':bundle,'filename':'TEST.txt','content_base64':base64.b64encode(log).decode(),'experimental':True}
        status,r=call('/api/analyze',body);assert status==200,r
        assert all(q['execution']=='not_selected' for q in r['report']['supplemental_trace']['requirements'])
        assert call('/api/replay',{'run_id':r['report']['run_id']})[1]['report']['supplemental_trace']==r['report']['supplemental_trace']
        cli=CliRunner().invoke(app,['knowledge','register-supplemental','--recipe',str(ROOT/CANDIDATE_PATH),'--pdf-dir',str(tmp_path),'--expected-revision','1','--reason','TEST stale','--database',str(database)])
        assert cli.exit_code!=0 and 'REVISION_CONFLICT' in cli.output
    finally:
        conn.close();server.shutdown();server.server_close();thread.join(timeout=5)
