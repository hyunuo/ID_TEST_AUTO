import base64
import http.client
import json
import re
import threading
from pathlib import Path
from typer.testing import CliRunner
from ssd_validator.cli import app
from ssd_validator.gui.server import create_server

ROOT=Path(__file__).resolve().parents[2]
BUNDLE='nvme-2.1-nvm-1.1'

def inputs():
    return {'format':'ssd-validator-captures-v1','captures':[
        {'capture_id':'TEST_CTRL','filename':'TEST_ctrl.txt','command':'id-ctrl','dut_id':'TEST_DUT','session_id':'TEST_SESSION',
         'content_base64':base64.b64encode(b'NVME Identify Controller:\nsqes:0x66\ncqes:0x44\nnpss:4\nawun:0\nawupf:0\noacs:6\n').decode()},
        {'capture_id':'TEST_NS','filename':'TEST_ns.txt','command':'id-ns','dut_id':'TEST_DUT','session_id':'TEST_SESSION','nsid':1,
         'content_base64':base64.b64encode(b'NVME Identify Namespace:\nnsze:100\nncap:90\n').decode()}]}

def test_multi_input_api_history_replay_and_no_invalid_save(tmp_path):
    server=create_server(0,root=ROOT,database=tmp_path/'api.sqlite3')
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    conn=http.client.HTTPConnection('127.0.0.1',server.server_address[1])
    try:
        conn.request('GET','/');page=conn.getresponse().read().decode()
        assert 'captureinputs' in page and '/captures.js' in page
        token=re.search("const token='([^']+)'",page)[1]
        conn.request('GET','/captures.js');response=conn.getresponse()
        assert response.status==200 and b'/api/analyze-captures' in response.read()
        def call(path,body,authorized=True):
            headers={'Content-Type':'application/json'}
            if authorized:headers['X-Session-Token']=token
            conn.request('POST',path,json.dumps(body),headers)
            response=conn.getresponse();return response.status,json.loads(response.read())
        body={'package':inputs(),'bundle_id':BUNDLE}
        assert call('/api/analyze-captures',body,False)[0]==403
        code,r=call('/api/analyze-captures',body)
        assert code==200 and r['report']['validation']['status']=='PASS'
        rid=r['report']['run_id']
        assert call('/api/run',{'run_id':rid})[1]==r
        assert call('/api/replay',{'run_id':rid})[1]['report']['scopes']==r['report']['scopes']
        body['package']['captures'][0]['cns']=True
        assert call('/api/analyze-captures',body)[0]==400
        assert len(call('/api/history',{})[1]['runs'])==2
    finally:
        conn.close();server.shutdown();server.server_close();thread.join()

def test_multi_input_cli(tmp_path):
    path=tmp_path/'TEST-input.json';path.write_text(json.dumps(inputs()),encoding='utf-8')
    result=CliRunner().invoke(app,['actual','review-captures','--input',str(path),'--bundle',BUNDLE,'--experimental','--database',str(tmp_path/'cli.sqlite3')])
    assert result.exit_code==0,result.output
    report=json.loads(result.output)
    assert report['kind']=='saved_capture_inspection' and report['validation']['status']=='PASS'
    assert len(report['scopes'])==1 and report['captures'][1]['metadata']['cns']=='UNKNOWN'
