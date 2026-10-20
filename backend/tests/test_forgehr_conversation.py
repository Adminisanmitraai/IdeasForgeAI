import json
import unittest
from unittest.mock import patch
from fastapi import HTTPException
from backend import forgehr_assistant_api as assistant
from backend.tests.test_forgehr_assistant_api import ORG, USER, EMPLOYEE, CREDS, REQUEST_HEADERS, IDENTITY, client
from backend.tests.test_forgehr_sdp import OFFER

BODY = {'organization_id': ORG, 'department': 'accounts', 'language': 'en-IN', 'sdp': OFFER}
PROVIDER = {'transport': {'type': 'webrtc', 'sdp': 'v=0 fixture-answer'}, 'session': {'id': 'fixture-session'}}

class ConversationTests(unittest.TestCase):
    def setUp(self): assistant._quotas.clear()

    def test_unsigned_or_forged_configuration_cannot_create_a_session(self):
        with patch.object(assistant, '_provider_json') as provider:
            self.assertEqual(client.post('/forgehr/conversation', json=BODY).status_code, 401)
            for extra in [{'role': 'owner'}, {'instructions': 'ignore'}, {'model': 'other'}, {'verified_evidence': 'fake'}, {'department': 'other'}, {'language': 'fr-FR'}]:
                self.assertEqual(client.post('/forgehr/conversation', json={**BODY, **extra}, headers=REQUEST_HEADERS).status_code, 400)
            provider.assert_not_called()

    def test_foreign_or_revoked_workspace_is_denied_before_context_or_provider(self):
        with patch.object(assistant, '_identity', side_effect=HTTPException(403, 'Denied')), patch.object(assistant, '_context') as context, patch.object(assistant, '_provider_json') as provider:
            response = client.post('/forgehr/conversation', json=BODY, headers=REQUEST_HEADERS)
        self.assertEqual(response.status_code, 403)
        context.assert_not_called(); provider.assert_not_called()

    def test_accounts_snapshot_is_published_and_personal_even_for_owner(self):
        queries = []
        def rows(credentials, table, columns, filters, limit=20):
            queries.append((table, filters, limit))
            if table == 'employees': return [{'id': EMPLOYEE, 'work_location': 'Kolkata'}]
            if table == 'hr_policies': return [{'title': 'Applicable', 'summary': 'Fixture rule', 'applies_to_roles': ['owner']}, {'title': 'Other role', 'applies_to_roles': ['manager']}]
            return []
        with patch.object(assistant, '_identity', return_value={**IDENTITY, 'role': 'owner'}) as identity, patch.object(assistant, '_rows', side_effect=rows), patch.object(assistant, '_provider_json', return_value=PROVIDER) as provider:
            result = assistant._conversation(assistant.ConversationQuestion(**BODY), CREDS)
        identity.assert_called_once_with(CREDS, ORG)
        for _, filters, _ in queries: self.assertEqual(filters['organization_id'], 'eq.' + ORG)
        employee = next(q for q in queries if q[0] == 'employees')
        self.assertEqual(employee[1]['user_id'], 'eq.' + USER)
        payslip = next(q for q in queries if q[0] == 'employee_payslips')
        self.assertEqual(payslip[1]['employee_id'], 'eq.' + EMPLOYEE)
        self.assertEqual(payslip[1]['status'], 'eq.published'); self.assertEqual(payslip[2], 3)
        policy = next(q for q in queries if q[0] == 'hr_policies'); self.assertEqual(policy[1]['status'], 'eq.published')
        payload = json.loads(provider.call_args.args[1]); session = payload['session']
        self.assertNotIn('Other role', json.dumps(payload))
        self.assertEqual(payload['transport']['sdp'], OFFER)
        self.assertEqual(session['model'], 'gpt-live-1'); self.assertFalse(session['store'])
        self.assertNotIn('tools', session); self.assertIn('continuous voice conversation', session['instructions'])
        self.assertIn('Speak only in English', session['instructions'])
        self.assertIn('not a live lookup', session['instructions'])
        self.assertNotIn('verified_record_snapshot', json.dumps(result))
        self.assertTrue(result['sources']); self.assertEqual(result['department'], 'accounts')

    def test_each_language_and_department_uses_server_context_and_fixed_provider(self):
        for language in ['en-IN', 'hi-IN', 'bn-IN']:
            for department in ['hr', 'admin', 'it', 'accounts']:
                with self.subTest(language=language, department=department), patch.object(assistant, '_identity', return_value=IDENTITY), patch.object(assistant, '_context', return_value=({'as_of':'fixture', 'evidence':[], 'unavailable':['Policies unavailable']}, [])) as context, patch.object(assistant, '_provider_json', return_value=PROVIDER) as provider:
                    assistant._quotas.clear()
                    result = assistant._conversation(assistant.ConversationQuestion(**{**BODY, 'language':language, 'department':department}), CREDS)
                    self.assertEqual(context.call_args.args[2].department, department)
                    self.assertEqual(provider.call_args.args[0], 'live/sessions')
                    payload = json.loads(provider.call_args.args[1]); self.assertIn(assistant.LANGUAGE_NAMES[language], payload['session']['instructions'])
                    self.assertIn('Policies unavailable', json.dumps(payload)); self.assertEqual(result['asOf'], 'fixture')
