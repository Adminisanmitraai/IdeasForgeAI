import json
import unittest
from unittest.mock import patch
from backend import forgehr_assistant_api as api
from backend import forgehr_demo_guide as guide
ORG='f6f72cb8-fc9f-4743-aea9-e94c12589b61'
USER='2eacc2b1-0e49-43b6-8c7f-2a2abc0fc3a1'
class DemoGuideTests(unittest.TestCase):
 def test_no_record_reads_in_demo(self):
  with patch.object(api,'_rows',side_effect=AssertionError('read')):
   context,sources=api._context({}, {'demo_guide':True},api.Question(organization_id=ORG,department='hr',message='salary'))
  self.assertEqual(context['persona'],'gauri-demo-manager');self.assertEqual(len(sources),1)
 def test_trusted_slug_not_metadata_or_name(self):
  for slug,expected in [('forgehr-demo',True),('client',False)]:
   with patch.object(api,'_json_request',return_value={'id':USER,'user_metadata':{'demo_guide':True}}),patch.object(api,'_rows',return_value=[{'role':'employee','organizations':{'status':'active','name':'ForgeHR Demo — SAMPLE DATA','slug':slug}}]):self.assertEqual(api._identity({},ORG)['demo_guide'],expected)
 def test_catalogue_marks_pending_features(self):
  statuses={x['feature']:x['status'] for x in guide.CATALOGUE};self.assertEqual(statuses['Organization designer and identity registry'],'proposed_not_deployed');self.assertEqual(statuses['Real-project agent execution'],'not_available')
 def test_text_persona_payload(self):
  captured=[]
  def provider(path,body):captured.append(json.loads(body));return {'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':'I am Gauri, an AI demo guide.'}]}]}
  with patch.object(api,'_identity',return_value={'user_id':USER,'demo_guide':True}),patch.object(api,'_take_quota'),patch.object(api,'_provider_json',side_effect=provider),patch.object(api,'_rows',side_effect=AssertionError('read')):api._answer(api.Question(organization_id=ORG,department='hr',message='tour'),{})
  self.assertIn('You are Gauri',captured[0]['instructions']);self.assertFalse(captured[0]['store']);self.assertNotIn('tools',captured[0])
 def test_voice_persona_payload(self):
  captured=[]
  def provider(path,body):captured.append(json.loads(body));return {'transport':{'type':'webrtc','sdp':'test'},'session':{'id':'session'}}
  with patch.object(api,'_identity',return_value={'user_id':USER,'demo_guide':True}),patch.object(api,'_take_quota'),patch.object(api,'_provider_json',side_effect=provider),patch.object(api,'_rows',side_effect=AssertionError('read')):api._conversation(api.ConversationQuestion(organization_id=ORG,department='hr',language='en-IN',sdp='v=0\r\n0123456789'),{})
  self.assertIn('You are Gauri',captured[0]['session']['instructions']);self.assertIn('Gauri, ForgeHR AI Demo Manager',captured[0]['session']['input'][0]['content'][0]['text'])
