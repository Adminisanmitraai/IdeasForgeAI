from __future__ import annotations
import json,time
from base64 import urlsafe_b64decode,urlsafe_b64encode
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey,Ed25519PublicKey
from cryptography.hazmat.primitives import serialization

VERSION="forge-commander.task-authorization.ed25519.v1"
REQ={"authorization_id","task_id","owner_subject","device_id","environment","project_root","applications","allowed_actions","issued_at","expires_at"}

def _b64(b:bytes)->str:return urlsafe_b64encode(b).decode("ascii").rstrip("=")
def _unb64(s:str)->bytes:return urlsafe_b64decode(s+"="*(-len(s)%4))
def issue(claims:dict,private_pem:bytes)->str:
 if set(claims)!=REQ: raise ValueError("task_authorization_claims_invalid")
 if claims["environment"]=="production": raise PermissionError("autonomous_production_authorization_denied")
 body=json.dumps(claims,sort_keys=True,separators=(",",":")).encode()
 key=serialization.load_pem_private_key(private_pem,password=None)
 if not isinstance(key,Ed25519PrivateKey): raise ValueError("task_authorization_private_key_invalid")
 return _b64(body)+"."+_b64(key.sign(body))
def validate(token:str,public_pem:bytes,*,owner_subject:str,device_id:str,action:str)->dict:
 try: body64,sig64=token.split(".",1);body=_unb64(body64);sig=_unb64(sig64)
 except Exception as e: raise PermissionError("task_authorization_malformed") from e
 try:
  key=serialization.load_pem_public_key(public_pem)
  if not isinstance(key,Ed25519PublicKey): raise ValueError()
  key.verify(sig,body)
 except Exception as e: raise PermissionError("task_authorization_signature_invalid") from e
 c=json.loads(body)
 if c.get("owner_subject")!=owner_subject or c.get("device_id")!=device_id: raise PermissionError("task_authorization_principal_mismatch")
 if c.get("environment")=="production": raise PermissionError("autonomous_production_authorization_denied")
 if int(c.get("expires_at",0))<=int(time.time()): raise PermissionError("task_authorization_expired")
 if action not in set(c.get("allowed_actions") or ()): raise PermissionError("action_outside_task_authorization")
 return c
