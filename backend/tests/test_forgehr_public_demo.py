import os
import unittest
from unittest.mock import patch
from fastapi import FastAPI
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
