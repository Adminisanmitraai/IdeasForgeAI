import json
import unittest
from unittest.mock import patch
from backend import forgehr_assistant_api as assistant
from backend.tests.test_forgehr_assistant_api import client, REQUEST_HEADERS, IDENTITY, ORG

OFFER = ('v=0\r\no=- 123 2 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\n'
         'a=group:BUNDLE 0\r\nm=audio 9 UDP/TLS/RTP/SAVPF 111\r\n'
         'c=IN IP4 0.0.0.0\r\na=mid:0\r\na=recvonly\r\na=rtpmap:111 opus/48000/2\r\n')

class SDPPreservation(unittest.TestCase):
    def setUp(self):assistant._quotas.clear()
    def test_schema_preserves_browser_offer_exactly(self):
        question=assistant.SpeechQuestion(organization_id=ORG,text=' Read aloud ',sdp=OFFER)
        self.assertEqual(question.sdp,OFFER)
        self.assertTrue(question.sdp.endswith('\r\n'))
        self.assertEqual(question.text,'Read aloud')
    def test_lf_and_extra_terminal_lines_are_not_normalized(self):
        for offer in [OFFER.replace('\r\n','\n'),OFFER+'\r\n']:
            question=assistant.SpeechQuestion(organization_id=ORG,text='Read aloud',sdp=offer)
            self.assertEqual(question.sdp,offer)
    def test_authenticated_route_forwards_unmodified_offer_to_provider(self):
        answer={'transport':{'type':'webrtc','sdp':'v=0 fixture-answer'},'session':{'id':'fixture-session'}}
        with patch.dict('os.environ',{'OPENAI_API_KEY':'fixture-key'}),patch.object(assistant,'_identity',return_value=IDENTITY),patch.object(assistant,'_json_request',return_value=answer) as provider:
            result=client.post('/forgehr/speak',headers=REQUEST_HEADERS,json={'organization_id':ORG,'text':'Read aloud','language':'en-IN','sdp':OFFER})
        self.assertEqual(result.status_code,200)
        payload=json.loads(provider.call_args.args[2])
        self.assertEqual(payload['transport']['sdp'].encode(),OFFER.encode())
        self.assertFalse(payload['session']['store'])
        self.assertEqual(payload['session']['model'],'gpt-live-1')
