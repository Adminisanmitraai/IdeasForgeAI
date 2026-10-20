"""Authenticated reconnects must retire old transports without ASGI errors."""
import os
import time
import unittest
from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect
from backend.forge_commander import gateway_api
from backend.forge_commander.device_auth import issue_device_token
from backend.forge_commander.gateway_session_manager import GatewaySessionManager


class StaleSocketTests(unittest.TestCase):
    def test_superseded_heartbeat_and_result_close_without_detaching_replacement(self):
        for message in ({'type': 'heartbeat'}, {'type': 'result', 'task_id': 'old-task', 'succeeded': True}):
            with self.subTest(message=message), patch.dict(os.environ, {'FORGE_COMMANDER_GATEWAY_SIGNING_KEY': 'test-key'}), patch.object(gateway_api, 'session_manager', GatewaySessionManager()):
                app = FastAPI()
                app.include_router(gateway_api.router)
                token = issue_device_token('owner', 'test-device', signing_key='test-key', expires_at=int(time.time())+300)
                headers = {'Authorization': 'Bearer '+token}
                with TestClient(app) as client:
                    with client.websocket_connect('/forge-commander/device/ws/test-device?session_id=old&instance_id=old', headers=headers) as old:
                        with client.websocket_connect('/forge-commander/device/ws/test-device?session_id=new&instance_id=new', headers=headers) as new:
                            new.send_json({'type': 'heartbeat', 'at': 'new-heartbeat'})
                            self.assertEqual(new.receive_json()['type'], 'heartbeat_ack')
                            old.send_json(message)
                            with self.assertRaises(WebSocketDisconnect) as closed:
                                old.receive_json()
                            self.assertEqual(closed.exception.code, 4409)
                            self.assertEqual(gateway_api.session_manager.get('test-device').session.session_id, 'new')
                            new.send_json({'type': 'heartbeat', 'at': 'still-live'})
                            self.assertEqual(new.receive_json()['at'], 'still-live')
                    self.assertIsNone(gateway_api.session_manager.get('test-device'))

    def test_authentication_still_required(self):
        app=FastAPI();app.include_router(gateway_api.router)
        with TestClient(app) as client:
            with self.assertRaises(WebSocketDisconnect) as closed:
                with client.websocket_connect('/forge-commander/device/ws/test-device?session_id=s&instance_id=i'):
                    pass
            self.assertEqual(closed.exception.code, 4401)

    def test_same_session_id_reconnect_keeps_new_transport(self):
        with patch.dict(os.environ, {'FORGE_COMMANDER_GATEWAY_SIGNING_KEY': 'test-key'}), patch.object(gateway_api, 'session_manager', GatewaySessionManager()):
            app=FastAPI();app.include_router(gateway_api.router)
            token=issue_device_token('owner','test-device',signing_key='test-key',expires_at=int(time.time())+300)
            headers={'Authorization':'Bearer '+token}
            path='/forge-commander/device/ws/test-device?session_id=same&instance_id=same'
            with TestClient(app) as client:
                with client.websocket_connect(path,headers=headers) as old:
                    with client.websocket_connect(path,headers=headers) as new:
                        new.send_json({'type':'heartbeat','at':'replacement'})
                        self.assertEqual(new.receive_json()['at'],'replacement')
                        old.send_json({'type':'heartbeat'})
                        with self.assertRaises(WebSocketDisconnect) as closed:old.receive_json()
                        self.assertEqual(closed.exception.code,4409)
                        new.send_json({'type':'heartbeat','at':'replacement-still-live'})
                        self.assertEqual(new.receive_json()['at'],'replacement-still-live')

if __name__=='__main__':
    unittest.main()
