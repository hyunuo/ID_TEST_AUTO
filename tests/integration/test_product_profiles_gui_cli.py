"""Real HTTP contracts; synthetic product data never reaches the user's database."""
import base64
import copy
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
PROV={'source_type':'fixture','source_document':'TEST_PRODUCT','source_version':'v1','source_section':'TEST only','status':'provisional'}

def test_gui_product_management_selection_suggestion_history_and_cli(tmp_path):
    database=tmp_path/'gui.sqlite3'
    server=create_server(0,root=ROOT,database=database)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    conn=http.client.HTTPConnection('127.0.0.1',server.server_address[1])
    try:
        conn.request('GET','/');page=conn.getresponse().read().decode()
        assert 'productprofile' in page and '/products.js' in page
        token=re.search("const token='([^']+)'",page)[1]
        conn.request('GET','/products.js');response=conn.getresponse()
        assert response.status==200 and b'/api/profiles/suggest' in response.read()
        def call(path,body,authorized=True):
            headers={'Content-Type':'application/json'}
            if authorized:headers['X-Session-Token']=token
            conn.request('POST',path,json.dumps(body),headers)
            response=conn.getresponse();return response.status,json.loads(response.read())
        def save(kind,payload,original=None,bundle=BUNDLE):
            body={'kind':kind,'bundle_id':bundle,'original_id':original,'payload':payload,
                'expected_revision':call('/api/products',{})[1]['revision'],'reason':'TEST management'}
            status,preview=call('/api/entity/preview',body)
            assert status==200,preview
            status,result=call('/api/entity/save',{**body,'preview_hash':preview['preview_hash']})
            assert status==200,result
            return result
        assert call('/api/products',{},False)[0]==403
        assert not call('/api/products',{})[1]['profiles']
        log=b'NVME Identify Controller:\nmn:TEST_MODEL\nfr:1.2.0\nsqes:0x66\ncqes:0x44\nnpss:4\nawun:0\nawupf:0\noacs:6\n'
        package={'captures':[{'capture_id':'TEST_CTRL','filename':'TEST.txt','command':'id-ctrl','content_base64':base64.b64encode(log).decode()}]}
        request={'package':package,'bundle_id':BUNDLE}
        assert call('/api/profiles/suggest',request,False)[0]==403
        assert call('/api/profiles/suggest',request)[1]['scopes'][0]['status']=='UNKNOWN'
        assert not call('/api/history',{})[1]['runs']
        save('document',{**{k:PROV[k] for k in ('source_type','source_document','source_version')},'title':'Synthetic TEST only'},bundle='')
        rule=next(r for r in call('/api/knowledge',{'bundle_id':BUNDLE})[1]['rules'] if r['check']['type']=='CAPABILITY')
        rule.update(rule_id='TEST.PRODUCT.REQUIRED',provenance=PROV,condition=None)
        policy={'policy_id':'TEST_POLICY','title':'TEST policy','bundle_id':BUNDLE,'rules':[rule],'provenance':PROV}
        save('product_policy',policy)
        context={'context_id':'TEST_CONTEXT','title':'TEST context','bundle_id':BUNDLE,
            'facts':{'logical_block_atomic_parameters_applicable':False},
            'fact_kinds':{'logical_block_atomic_parameters_applicable':'assumption'},'provenance':PROV}
        save('context',context)
        profile={'profile_id':'TEST_PROFILE','title':'TEST profile','bundle_id':BUNDLE,'policy_ids':['TEST_POLICY'],'context_id':'TEST_CONTEXT',
            'conditions':[{'source':'observed','path':'model','operator':'EQ','value':'TEST_MODEL'},
                {'source':'observed','path':'firmware','operator':'FW_RANGE','minimum':'1.2.0','maximum':'2.0.0'}],
            'firmware_comparison':{'method':'numeric_components','component_count':3},'provenance':PROV}
        save('profile',profile)
        suggestion=call('/api/profiles/suggest',request)[1]
        assert suggestion['scopes'][0]['candidates']==['TEST_PROFILE'] and suggestion['automatic_selection'] is False
        status,r=call('/api/analyze-captures',{**request,'profile_id':'TEST_PROFILE'})
        assert status==200 and r['report']['validation']['status']=='PASS'
        old=r['report'];rid=old['run_id']
        assert old['scopes'][0]['product_selection']['registry_source']['path'].endswith('/knowledge/products.json')
        assert call('/api/run',{'run_id':rid})[1]['report']==old
        policy=copy.deepcopy(policy);policy['rules'][0]['check']['support']='unsupported';save('product_policy',policy,'TEST_POLICY')
        assert call('/api/analyze-captures',{**request,'profile_id':'TEST_PROFILE'})[1]['report']['validation']['status']=='FAIL'
        assert call('/api/replay',{'run_id':rid})[1]['report']['scopes']==old['scopes']
        single={'filename':'TEST.txt','content_base64':base64.b64encode(log).decode(),'bundle_id':BUNDLE,'profile_id':'TEST_PROFILE','experimental':True}
        assert call('/api/analyze',single)[1]['report']['kind']=='saved_capture_inspection'
        assert call('/api/analyze',{**single,'profile_id':{}})[0]==400
        assert call('/api/analyze-captures',{**request,'profile_id':False})[0]==400
        assert call('/api/entities',{'kind':'profile','search':'TEST'})[1]['items']
        path=tmp_path/'TEST.json';path.write_text(json.dumps(package),encoding='utf-8')
        cli=CliRunner().invoke(app,['actual','review-captures','--input',str(path),'--bundle',BUNDLE,'--profile','TEST_PROFILE','--experimental','--database',str(database)])
        assert cli.exit_code==0,cli.output
        assert json.loads(cli.output)['scopes'][0]['product_selection']['profile']['profile_id']=='TEST_PROFILE'
    finally:
        conn.close();server.shutdown();server.server_close();thread.join()
