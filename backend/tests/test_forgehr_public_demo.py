import os
import json
import unittest
from unittest.mock import patch
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from backend import forgehr_public_demo as demo


class PublicDemoTest(unittest.TestCase):
    def setUp(self):
        app = FastAPI(); app.include_router(demo.router)
        self.client = TestClient(app)
        demo._calls.clear()
        self.addCleanup(demo._calls.clear)
        self.env = patch.dict(os.environ, {'FORGEHR_PUBLIC_DEMO_ENABLED': 'true', 'FORGEHR_PUBLIC_DEMO_PROXY_SECRET': 'x' * 32})
        self.env.start(); self.addCleanup(self.env.stop)

    def call(self, body=None, secret='x' * 32):
        return self.client.post('/public-demo/chat', json=body or {'question': 'Show payroll', 'section': 'overview', 'history': []}, headers={'X-ForgeHR-Demo-Secret': secret})

    def test_disabled_and_wrong_secret(self):
        self.assertEqual(self.call(secret='wrong').status_code, 403)
        with patch.dict(os.environ, {'FORGEHR_PUBLIC_DEMO_ENABLED': 'false'}):
            self.assertEqual(self.call().status_code, 503)

    def test_strict_request(self):
        self.assertEqual(self.call({'question': 'hello', 'section': 'https://evil.test', 'history': []}).status_code, 422)
        self.assertEqual(self.call({'question': 'hello', 'section': 'overview', 'history': [], 'organization_id': 'private'}).status_code, 422)

    def test_valid_answer_and_untrusted_action_rejection(self):
        def result(text):
            return {'output': [{'type': 'message', 'content': [{'type': 'output_text', 'text': text}]}]}
        with patch('backend.forgehr_assistant_api._provider_json', return_value=result('{"answer":"Illustrative payslip only.","section":"payroll"}')) as provider:
            response = self.call()
            self.assertEqual(response.status_code, 200)
            payload = provider.call_args.args[1].decode()
            self.assertIn('"store": false', payload)
            self.assertNotIn('Authorization', payload)
        with patch('backend.forgehr_assistant_api._provider_json', return_value=result('{"answer":"Open","section":"https://evil.test"}')):
            self.assertEqual(self.call().status_code, 503)

    def test_quota(self):
        for _ in range(6): demo._quota()
        with self.assertRaises(Exception) as error: demo._quota()
        self.assertEqual(error.exception.status_code, 429)

    def speech(self, **changes):
        body = {'text': 'Hello, I am Gauri.', 'language': 'en-IN', 'sdp': 'v=0\r\ns=demo\r\n'}
        body.update(changes)
        return self.client.post('/public-demo/speak', json=body, headers={'X-ForgeHR-Demo-Secret': 'x' * 32})

    def test_public_voice_has_its_own_release_switch(self):
        with patch.dict(os.environ, {'FORGEHR_PUBLIC_DEMO_VOICE_ENABLED': 'false'}):
            self.assertEqual(self.speech().status_code, 503)
        with patch.dict(os.environ, {'FORGEHR_PUBLIC_DEMO_VOICE_ENABLED': 'true'}):
            self.assertEqual(self.client.post('/public-demo/speak', json={}, headers={'X-ForgeHR-Demo-Secret': 'wrong'}).status_code, 403)
            self.assertEqual(self.speech(organization_id='private').status_code, 422)
            self.assertEqual(self.speech(text='x' * 1801).status_code, 422)
            self.assertEqual(self.speech(text='   ').status_code, 422)
            self.assertEqual(self.speech(language='invalid').status_code, 422)

    def test_voice_uses_original_read_aloud_without_workspace_authority(self):
        provider_result = {'transport': {'type': 'webrtc', 'sdp': 'v=0\r\ns=answer\r\n'}, 'session': {'id': 'public-voice'}}
        with patch.dict(os.environ, {'FORGEHR_PUBLIC_DEMO_VOICE_ENABLED': 'true'}), patch('backend.forgehr_assistant_api._provider_json', return_value=provider_result) as provider, patch('backend.forgehr_assistant_api._identity', side_effect=AssertionError('No identity lookup')):
            for text, language in [('Hello, I am Gauri.', 'en-IN'), ('नमस्ते, मैं गौरी हूँ।', 'hi-IN'), ('নমস্কার, আমি গৌরী।', 'bn-IN')]:
                response = self.speech(text=text, language=language)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.headers['cache-control'], 'no-store')
                self.assertEqual(response.json()['model'], 'gpt-live-1')
                self.assertEqual(set(response.json()), {'model', 'session', 'transport'})
                self.assertEqual(provider.call_args.args[0], 'live/sessions')
                payload = json.loads(provider.call_args.args[1])
                self.assertEqual(payload['session']['model'], 'gpt-live-1')
                self.assertFalse(payload['session']['store'])
                self.assertEqual(payload['session']['input'][1]['content'][0]['text'], text)
                self.assertNotIn('tools', payload['session'])
                self.assertNotIn('organization_id', payload['session'])
                self.assertEqual(payload['transport']['sdp'], 'v=0\r\ns=demo\r\n')

    def test_voice_shares_demo_quota_and_releases_provider_slot_on_error(self):
        with patch.dict(os.environ, {'FORGEHR_PUBLIC_DEMO_VOICE_ENABLED': 'true'}), patch('backend.forgehr_assistant_api._speech_session', side_effect=HTTPException(503, 'Unavailable')):
            for _ in range(6):
                self.assertEqual(self.speech().status_code, 503)
            self.assertEqual(self.speech().status_code, 429)
