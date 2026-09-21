import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('client',ROOT/'scripts/lensrhyme_api.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class Response:
    def __init__(self,value):self.value=value
    def __enter__(self):return self
    def __exit__(self,*a):pass
    def read(self):return json.dumps(self.value).encode()

class ClientTests(unittest.TestCase):
    def setUp(self):self.c=m.Client(token='ltr_unit_test',workspace='workspace-a')
    def test_bearer_workspace_json(self):
        with patch.object(self.c.opener,'open',return_value=Response({'id':'t'})) as op:
            self.assertEqual(self.c.request('POST','/tasks/',{'payload':{'prompt':'陶瓷杯'}}),{'id':'t'})
            req=op.call_args.args[0]
            self.assertEqual(req.full_url,'https://lensrhyme.com/api/v1/tasks/')
            self.assertEqual(req.get_header('Authorization'),'Bearer ltr_unit_test')
            self.assertEqual(req.get_header('X-workspace-id'),'workspace-a')
            self.assertEqual(json.loads(req.data)['payload']['prompt'],'陶瓷杯')
    def test_redirect_never_carries_credentials(self):
        req=urllib.request.Request('https://lensrhyme.com/api/v1/tasks/',headers={'Authorization':'Bearer ltr_unit_test'})
        self.assertIsNone(m.NoRedirect().redirect_request(req,None,307,'',{},'https://other.example/'))
    def test_paths(self):
        for p in ['https://other.example','//other.example','/../auth','/%2e%2e/auth','/a\\b','/a#x']:
            with self.subTest(p=p),self.assertRaises(ValueError):self.c.request('GET',p)
    def test_plain_http_base_rejected(self):
        with self.assertRaises(ValueError):m.Client(base='http://lensrhyme.com/api/v1',token='ltr_test')
    def test_failed_mutation_not_retried_or_body_leaked(self):
        with patch.object(self.c.opener,'open',side_effect=urllib.error.HTTPError('u',500,'secret',{},None)) as op:
            with self.assertRaisesRegex(RuntimeError,'HTTP 500') as err:self.c.request('POST','/tasks/',{})
            self.assertNotIn('secret',str(err.exception));self.assertEqual(op.call_count,1)
    def test_poll_completion(self):
        with patch.object(self.c,'request',side_effect=[{'status':'running'},{'id':'t','status':'completed','result_url':'https://media.example/a.mp4'}]),patch.object(m.time,'sleep'):
            self.assertEqual(self.c.wait('t')['status'],'completed')
    def test_poll_timeout_does_not_resubmit(self):
        with patch.object(self.c,'request',return_value={'status':'running'}) as req:
            self.assertTrue(self.c.wait('t',0)['poll_timeout']);self.assertEqual(req.call_args.args,('GET','/tasks/t'))
    def test_poll_failure(self):
        with patch.object(self.c,'request',return_value={'status':'failed','error_code':'MODEL_ERROR'}):self.assertEqual(self.c.wait('t')['error_code'],'MODEL_ERROR')
    def test_upload(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'test.txt';f.write_text('hello')
            with patch.object(self.c,'request',return_value={'url':'https://media.example/a'}) as req:
                self.c.upload('/upload/',f,{'category':'reference'})
                args=req.call_args.args;self.assertIn(b'name="file"',args[2]);self.assertIn(b'hello',args[2]);self.assertIn('boundary=',args[3])
    def test_studio_default_models_reach_wire(self):
        for kind, model in m.STUDIO_DEFAULT_MODELS.items():
            payload = {'seed_audio': {'text': '你好'}} if kind == 'audio' else {'prompt': 'cup'}
            body = {'entrypoint': 'studio', 'task_type': kind + '_generation', 'payload': payload}
            with self.subTest(kind=kind), patch.object(self.c.opener, 'open', return_value=Response({'id':'t'})) as op:
                self.c.request('POST', '/tasks/', body)
                self.assertEqual(json.loads(op.call_args.args[0].data)['payload']['model'], model)
                self.assertNotIn('model', body['payload'])
    def test_explicit_override_preserved(self):
        body = {'entrypoint':'studio','task_type':'image_generation','payload':{'model':'another-model'}}
        self.assertEqual(m.prepare_studio_body('POST','/tasks/',body)['payload']['model'],'another-model')
    def test_project_models_unchanged(self):
        for owner in ['canvas','workbench',None]:
            body={'entrypoint':owner,'task_type':'image_generation','payload':{}}
            self.assertIs(m.prepare_studio_body('POST','/tasks/',body),body)
    def test_null_blank_and_alias(self):
        for value in [None,'','  ','doubao-seedream-5.0-pro']:
            body={'entrypoint':'studio','task_type':'image_generation','payload':{'model':value}}
            self.assertEqual(m.prepare_studio_body('POST','/tasks/',body)['payload']['model'],m.STUDIO_DEFAULT_MODELS['image'])
    def test_audio_wrong_payload_fails_before_network(self):
        with patch.object(self.c.opener,'open') as op:
            with self.assertRaisesRegex(ValueError,'seed_audio.text'):
                self.c.request('POST','/tasks/',{'entrypoint':'studio','task_type':'audio_generation','payload':{'text':'wrong shape'}})
            op.assert_not_called()
    def test_nested_audio_model_conflict(self):
        body={'entrypoint':'studio','task_type':'audio_generation','payload':{'seed_audio':{'text':'hello','model':'other'}}}
        with self.assertRaisesRegex(ValueError,'Conflicting'):
            m.prepare_studio_body('POST','/tasks/',body)

    def test_audio_explicit_legacy_model(self):
        body={'entrypoint':'studio','task_type':'audio_generation','payload':{'model':'other-tts','text':'hello'}}
        self.assertEqual(m.prepare_studio_body('POST','/tasks/',body)['payload'],body['payload'])
    def test_studio_cli_applies_default(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'payload.json';p.write_text('{"seed_audio":{"text":"hello"}}')
            args=['client','studio','audio','--json-file',str(p)]
            with patch.object(m.sys,'argv',args),patch.dict(m.os.environ,{'LENSRHYME_API_KEY':'ltr_test'}),patch('urllib.request.OpenerDirector.open',return_value=Response({'id':'t'})) as op,patch('builtins.print'):
                m.main()
                body=json.loads(op.call_args.args[0].data)
                self.assertEqual(body['entrypoint'],'studio')
                self.assertEqual(body['payload']['model'],'seed-audio-1.0')

    def test_packages_self_contained(self):
        for d in (ROOT/'skills').iterdir():
            self.assertEqual((d/'scripts/lensrhyme_api.py').read_bytes(),(ROOT/'scripts/lensrhyme_api.py').read_bytes())
            contract=json.loads((d/'references/api-contract.json').read_text())
            def walk(v):
                if isinstance(v,dict):
                    if '$ref' in v:self.assertIn(v['$ref'].split('/')[-1],contract['components']['schemas'])
                    for x in v.values():walk(x)
                elif isinstance(v,list):
                    for x in v:walk(x)
            walk(contract)

if __name__=='__main__':unittest.main()
