import json
import unittest
from unittest.mock import patch
from fastapi import HTTPException
from backend import forgehr_agent_team as team
from backend import forgehr_assistant_api as api

ORG = 'f6f72cb8-fc9f-4743-aea9-e94c12589b61'
RUN = 'cc056a2a-537a-4156-a2c9-9128eaf0316b'
Q = team.RunRequest(organization_id=ORG, run_id=RUN)
CREDS = {'Authorization': 'Bearer caller-token', 'apikey': 'public'}
OWNER = {'user_id': 'founder', 'role': 'owner'}


class TeamTests(unittest.TestCase):
    def invoke(self, role='owner', provider=None, patcher=None, rows=None, identity=None):
        row = {'id': RUN, 'agent_key': 'divyansh', 'status': 'queued', 'instruction': 'Prepare a bounded ForgeHR delivery plan.'}
        def scoped(c, table, cols, filters, limit):
            self.assertEqual(c, CREDS)
            self.assertEqual(filters['organization_id'], 'eq.' + ORG)
            return [row]
        with patch.object(api, '_identity', side_effect=identity, return_value={**OWNER, 'role': role}), \
             patch.object(api, '_rows', side_effect=rows or scoped), \
             patch.object(api, '_take_quota'), \
             patch.object(api, '_provider_json', side_effect=provider or self.provider), \
             patch.object(team, '_patch', side_effect=patcher or (lambda *args: {})):
            return team._execute(Q, CREDS)

    def provider(self, path, raw):
        payload = json.loads(raw)
        self.assertFalse(payload['store'])
        self.assertNotIn('tools', payload)
        self.assertLessEqual(payload['max_output_tokens'], 1800)
        self.assertIn('draft awaiting human review', payload['instructions'])
        self.assertNotIn('Bearer caller-token', raw.decode())
        return {'status': 'completed', 'output': [{'type': 'message', 'content': [{'type': 'output_text', 'text': 'Delivery plan. Evidence missing. Founder decision required.'}]}]}

    def test_owner_output_is_submitted_and_not_accepted(self):
        calls = []
        result = self.invoke(patcher=lambda *args: calls.append(args) or {})
        self.assertEqual(result['status'], 'submitted')
        self.assertEqual(calls[0][-1], {'status': 'running'})
        self.assertEqual(calls[1][-1]['status'], 'submitted')
        self.assertIn('Evidence missing', calls[1][-1]['output'])

    def test_other_roles_cannot_call_provider(self):
        for role in ['employee', 'manager', 'hr_admin', 'auditor']:
            with self.subTest(role=role), self.assertRaises(HTTPException) as error:
                self.invoke(role=role, provider=lambda *_: self.fail('Provider reached'))
            self.assertEqual(error.exception.status_code, 403)

    def test_duplicate_claim_prevents_provider(self):
        def conflict(*args):
            raise HTTPException(409, 'Claim already taken')
        with self.assertRaises(HTTPException):
            self.invoke(patcher=conflict, provider=lambda *_: self.fail('Provider reached'))

    def test_cancelled_run_does_not_publish_output(self):
        calls = []
        def patcher(*args):
            calls.append(args)
            if args[-2] == 'running':
                raise HTTPException(409, 'Cancelled')
            return {}
        with self.assertRaises(HTTPException):
            self.invoke(patcher=patcher)
        self.assertEqual(calls[1][-2], 'running')
        self.assertEqual(calls[1][-1]['status'], 'submitted')

    def test_revoked_owner_is_rechecked_after_provider(self):
        calls = []
        with self.assertRaises(HTTPException):
            self.invoke(identity=[OWNER, {**OWNER, 'role': 'employee'}], patcher=lambda *args: calls.append(args) or {})
        self.assertFalse(any(args[-1].get('status') == 'submitted' for args in calls))

    def test_incomplete_response_records_failure(self):
        calls = []
        with self.assertRaises(HTTPException):
            self.invoke(provider=lambda *_: {'status': 'incomplete'}, patcher=lambda *args: calls.append(args) or {})
        self.assertEqual(calls[-1][-1], {'status': 'failed'})

    def test_request_rejects_client_role_tools_and_instruction(self):
        for extra in ['role', 'tools', 'instruction']:
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                team.RunRequest.model_validate({'organization_id': ORG, 'run_id': RUN, extra: 'override'})

if __name__ == '__main__':
    unittest.main()

