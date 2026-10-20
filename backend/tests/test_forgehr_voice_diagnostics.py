import io
import json
import unittest
import urllib.error
from unittest.mock import patch
from fastapi import HTTPException
from backend import forgehr_assistant_api as assistant

class VoiceDiagnostics(unittest.TestCase):
    def reject(self, status, body):
        error = urllib.error.HTTPError('https://api.openai.com/v1/live/sessions', status, 'secret-message', {}, io.BytesIO(body))
        with patch.dict('os.environ', {'OPENAI_API_KEY':'fixture-secret-key'}), patch.object(assistant, '_json_request', side_effect=error), self.assertLogs(assistant.logger, level='WARNING') as logs:
            with self.assertRaises(HTTPException) as caught:
                assistant._provider_json('live/sessions', b'private-employee-answer-and-sdp')
        self.assertEqual(caught.exception.status_code, 503)
        return '\n'.join(logs.output)
    def test_captures_safe_rejection_fields_only(self):
        logs=self.reject(403,json.dumps({'error':{'code':'model_not_found','param':'session.model','message':'secret-message'}}).encode())
        self.assertIn('status=403 code=model_not_found parameter=session.model', logs)
        for secret in ['secret-message','fixture-secret-key','private-employee-answer-and-sdp']:
            self.assertNotIn(secret,logs)
    def test_provider_controlled_strings_are_not_logged(self):
        logs=self.reject(400,b'{"error":{"code":"private-secret-code","param":"private-secret-param","message":"private-secret"}}')
        self.assertIn('code=unknown parameter=unknown',logs)
        self.assertNotIn('private-secret',logs)
    def test_invalid_provider_error_keeps_safe_http_status(self):
        for body in [b'not-json', b'[]', b'{"error":[]}']:
            self.assertIn('status=429',self.reject(429,body))
    def test_transport_failure_is_separate_from_provider_rejection(self):
        with patch.dict('os.environ', {'OPENAI_API_KEY':'fixture-secret-key'}), patch.object(assistant,'_json_request',side_effect=OSError('private-secret')), self.assertLogs(assistant.logger,level='WARNING') as logs:
            with self.assertRaises(HTTPException):assistant._provider_json('live/sessions',b'private-question')
        self.assertIn('category=transport', '\n'.join(logs.output));self.assertNotIn('private-secret','\n'.join(logs.output))
