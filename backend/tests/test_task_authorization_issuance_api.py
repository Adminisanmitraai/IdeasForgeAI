import os, time
from fastapi import FastAPI
from fastapi.testclient import TestClient
from backend.forge_commander.gateway_api import router
from backend.forge_commander.device_auth import issue_device_token
from backend.forge_commander.task_authorization import validate_task_authorization

GATEWAY_KEY="gateway-test-key"
TASK_KEY="task-test-key"

def client():
    os.environ["FORGE_COMMANDER_GATEWAY_SIGNING_KEY"]=GATEWAY_KEY
    os.environ["FORGE_COMMANDER_TASK_AUTH_SIGNING_KEY"]=TASK_KEY
    app=FastAPI(); app.include_router(router); return TestClient(app)

def token():
    return issue_device_token("owner-1","dev-1",signing_key=GATEWAY_KEY,expires_at=int(time.time())+300)

def base():
    return {"task_id":"TASK-1","environment":"training","project_root":r"D:\APPS\IdeasForgeAI\apps\forgewa-design-train\training\TASK-1","applications":["autocad"],"allowed_actions":["window.focus","screen.capture"],"ttl_seconds":300}

def test_issue_bounded_authorization():
    r=client().post("/forge-commander/task-authorization/issue",json=base(),headers={"Authorization":"Bearer "+token()})
    assert r.status_code==200
    body=r.json()
    claims=validate_task_authorization(body["task_authorization"],signing_key=TASK_KEY,owner_subject="owner-1",device_id="dev-1",action="screen.capture")
    assert claims["task_id"]=="TASK-1" and body["authorization_id"]==claims["authorization_id"]

def test_production_denied():
    p=base(); p["environment"]="production"
    assert client().post("/forge-commander/task-authorization/issue",json=p,headers={"Authorization":"Bearer "+token()}).status_code==403

def test_unbounded_action_denied():
    p=base(); p["allowed_actions"]=["file.delete"]
    assert client().post("/forge-commander/task-authorization/issue",json=p,headers={"Authorization":"Bearer "+token()}).status_code==403

def test_ttl_bounded():
    p=base(); p["ttl_seconds"]=3600
    assert client().post("/forge-commander/task-authorization/issue",json=p,headers={"Authorization":"Bearer "+token()}).status_code==400


def test_issue_ed25519_when_private_key_present(monkeypatch):
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization
    from backend.forge_commander.task_authorization_asymmetric import validate as validate_ed25519
    key = Ed25519PrivateKey.generate()
    private_pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    public_pem = key.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
    monkeypatch.setenv("FORGE_COMMANDER_TASK_AUTH_ED25519_PRIVATE_KEY_PEM", private_pem.decode())
    monkeypatch.setenv("FORGE_COMMANDER_TASK_AUTH_ED25519_PUBLIC_KEY_PEM", public_pem.decode())
    r = client().post("/forge-commander/task-authorization/issue", json=base(), headers={"Authorization":"Bearer "+token()})
    assert r.status_code == 200
    claims = validate_ed25519(r.json()["task_authorization"], public_pem, owner_subject="owner-1", device_id="dev-1", action="screen.capture")
    assert claims["task_id"] == "TASK-1"
