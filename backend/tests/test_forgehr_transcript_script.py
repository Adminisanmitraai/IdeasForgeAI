import json
import unittest
from unittest.mock import patch
from fastapi import HTTPException
from backend import forgehr_assistant_api as assistant
from backend.tests.test_forgehr_assistant_api import ORG, IDENTITY, CREDS, QUESTION

class TranscriptScriptTests(unittest.TestCase):
    def setUp(self): assistant._quotas.clear()

    def test_dominant_unexpected_script_is_rejected_before_auto_send(self):
        for language, text in [('en', 'کین یو ٹیل می سم تھنگ اباؤٹ دی کمپنی؟'), ('hi', 'مرحبا بالشركة'), ('bn', 'कंपनी के बारे में बताओ')]:
            with self.subTest(language=language), patch.object(assistant, '_identity', return_value=IDENTITY), patch.object(assistant, '_provider_json', return_value={'text': text}):
                with self.assertRaises(HTTPException) as caught:
                    assistant._transcribe(b'fixture', 'audio/mp4', language, CREDS, ORG)
                self.assertEqual(caught.exception.status_code, 422)
                self.assertNotIn(text, caught.exception.detail)

    def test_selected_scripts_proper_names_accents_and_numbers_are_preserved(self):
        for language, text in [('en', 'Can you tell me about the company?'), ('en', 'Who is অমিত?'), ('en', 'José works in HR'), ('hi', 'ForgeHR में मेरी छुट्टी कब है?'), ('bn', 'ForgeHR কোম্পানি সম্পর্কে বলুন'), ('en', '1234')]:
            with self.subTest(text=text), patch.object(assistant, '_identity', return_value=IDENTITY), patch.object(assistant, '_provider_json', return_value={'text': text}) as provider:
                self.assertEqual(assistant._transcribe(b'fixture', 'audio/mp4', language, CREDS, ORG), {'text': text})
                body = provider.call_args.args[1]
                self.assertIn(b'name="prompt"', body)
                self.assertIn(assistant.LANGUAGE_NAMES[language + '-IN'].encode(), body)
                self.assertIn(b'fixture', body)

    def test_wrong_script_text_reply_is_not_returned_for_voice_playback(self):
        result = {'output': [{'type': 'message', 'content': [{'type': 'output_text', 'text': 'مرحبا بالشركة'}]}]}
        with patch.object(assistant, '_identity', return_value=IDENTITY), patch.object(assistant, '_context', return_value=({'as_of': 'fixture', 'evidence': []}, [])), patch.object(assistant, '_provider_json', return_value=result):
            with self.assertRaises(HTTPException) as caught:
                assistant._answer(assistant.Question(**QUESTION), CREDS)
        self.assertEqual(caught.exception.status_code, 503)

    def test_transcription_prompt_does_not_include_company_record_or_user_content(self):
        with patch.object(assistant, '_identity', return_value={**IDENTITY, 'company': 'PRIVATE RECORD'}), patch.object(assistant, '_provider_json', return_value={'text': 'About the company'}) as provider:
            assistant._transcribe(b'fixture', 'audio/mp4', 'en', CREDS, ORG)
        self.assertNotIn(b'PRIVATE RECORD', provider.call_args.args[1])

    def test_old_or_client_supplied_wrong_script_answer_cannot_start_voice(self):
        with patch.object(assistant, '_provider_json') as provider:
            with self.assertRaises(HTTPException) as caught:
                assistant._speech_session(assistant.SpeechQuestion(organization_id=ORG, language='en-IN', text='مرحبا بالشركة', sdp='v=0 fixture offer'))
        self.assertEqual(caught.exception.status_code, 422)
        provider.assert_not_called()
