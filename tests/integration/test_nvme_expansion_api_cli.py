"""Candidate coverage and normalizer/Resolver through the same GUI/CLI service."""
import base64
import http.client
import json
import re
import threading
from pathlib import Path
from typer.testing import CliRunner
from ssd_validator.application.database_workflow import DatabaseWorkflow
from ssd_validator.application.nvme_expansion import PACK_PATH,prepare_sources
from ssd_validator.cli import app
from ssd_validator.gui.server import create_server

ROOT=Path(__file__).resolve().parents[2]
BUNDLE='nvme-2.1-nvm-1.1'

def test_coverage_api_candidate_pipeline_and_historical_sources(tmp_path):
    database=tmp_path/'TEST.sqlite3';w=DatabaseWorkflow(ROOT,database)
    initial=w.nvme_coverage()
    assert initial['revision']==1
    assert all(r['registration_state']=='not_registered' for b in initial['bundles'] for r in b['rules'])
    pack=json.loads((ROOT/PACK_PATH).read_text(encoding='utf-8'))
    w.import_sources({'format':'ssd-validator-source-v1','sources':prepare_sources(w.repository.sources(),pack)},expected_revision=1,reason='TEST candidates only')
    server=create_server(0,root=ROOT,database=database)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    conn=http.client.HTTPConnection('127.0.0.1',server.server_address[1])
    try:
        conn.request('GET','/');page=conn.getresponse().read().decode();token=re.search("const token='([^']+)'",page)[1]
        assert '/coverage.js' in page and '<option>GE</option>' in page
        conn.request('GET','/coverage.js');response=conn.getresponse();assert response.status==200 and b'/api/nvme/coverage' in response.read()
        def call(path,body,authorized=True):
            headers={'Content-Type':'application/json'}
            if authorized:headers['X-Session-Token']=token
            conn.request('POST',path,json.dumps(body),headers);response=conn.getresponse();return response.status,json.loads(response.read())
        assert call('/api/nvme/coverage',{},False)[0]==403
        status,coverage=call('/api/nvme/coverage',{})
        assert status==200 and coverage['revision']==2 and coverage['authoritative'] is False
        assert all(r['registration_state']=='matches_candidate' for b in coverage['bundles'] for r in [*b['rules'],*b['replacements']])
        # Old Context=false cannot disable the mandatory controller field invariant.
        log=b'NVME Identify Controller:\nsqes:0x66\ncqes:0x44\nnpss:0\nawun:1\nawupf:2\noacs:6\nhmpre:0\nhmmin:0\nrpmbs:0\nfuses:0\nacwu:0\ndsto:0\n'
        body={'bundle_id':BUNDLE,'filename':'TEST.txt','content_base64':base64.b64encode(log).decode(),
            'experimental':True,'context_facts':{'logical_block_atomic_parameters_applicable':False}}
        status,result=call('/api/analyze',body);assert status==200,result
        report=result['report'];assert report['validation']['status']=='FAIL' and not report['validation']['authoritative']
        assert next(r for r in report['validation']['results'] if r['rule']['rule_id']=='EXPERIMENTAL.ATOMIC_POWER_FAIL_BOUND')['status']=='FAIL'
        assert all(r['status']=='N/A' for r in report['validation']['results'] if r['rule']['target']['field_id'].startswith('NVME.CNS00.'))
        assert call('/api/replay',{'run_id':report['run_id']})[1]['report']['validation']==report['validation']
        package={'captures':[{'capture_id':'TEST','filename':'TEST.txt','command':'id-ctrl','content_base64':body['content_base64']}]}
        path=tmp_path/'TEST.json';path.write_text(json.dumps(package),encoding='utf-8')
        cli=CliRunner().invoke(app,['actual','review-captures','--input',str(path),'--bundle',BUNDLE,'--experimental','--database',str(database)])
        assert cli.exit_code==0,cli.output
        assert json.loads(cli.output)['validation']['status']=='FAIL'
    finally:
        conn.close();server.shutdown();server.server_close();thread.join(timeout=5)
