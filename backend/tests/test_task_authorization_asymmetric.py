import time, pytest
from base64 import urlsafe_b64decode, urlsafe_b64encode
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from backend.forge_commander.task_authorization_asymmetric import issue, validate

def keys():
    k = Ed25519PrivateKey.generate()
    return (
        k.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        ),
        k.public_key().public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        ),
    )

def claims():
    return {
        "authorization_id": "A1",
        "task_id": "T1",
        "owner_subject": "ranjan",
        "device_id": "dev1",
        "environment": "training",
        "project_root": r"D:\train\T1",
        "applications": ["autocad"],
        "allowed_actions": ["window.focus"],
        "issued_at": int(time.time()) - 1,
        "expires_at": int(time.time()) + 60,
    }

def test_valid():
    pr, pu = keys()
    assert validate(
        issue(claims(), pr),
        pu,
        owner_subject="ranjan",
        device_id="dev1",
        action="window.focus",
    )["authorization_id"] == "A1"

def test_tamper():
    pr, pu = keys()
    token = issue(claims(), pr)

    body64, sig64 = token.split(".", 1)

    signature = bytearray(
        urlsafe_b64decode(sig64 + "=" * (-len(sig64) % 4))
    )

    # Mutate an actual Ed25519 signature byte.
    signature[0] ^= 1

    tampered_signature = (
        urlsafe_b64encode(bytes(signature))
        .decode("ascii")
        .rstrip("=")
    )

    tampered_token = body64 + "." + tampered_signature

    with pytest.raises(PermissionError):
        validate(
            tampered_token,
            pu,
            owner_subject="ranjan",
            device_id="dev1",
            action="window.focus",
        )

def test_wrong_key():
    pr, pu = keys()
    _, pu2 = keys()

    with pytest.raises(PermissionError):
        validate(
            issue(claims(), pr),
            pu2,
            owner_subject="ranjan",
            device_id="dev1",
            action="window.focus",
        )

def test_scope():
    pr, pu = keys()

    with pytest.raises(PermissionError):
        validate(
            issue(claims(), pr),
            pu,
            owner_subject="ranjan",
            device_id="dev1",
            action="app.open",
        )

def test_prod_issue():
    pr, _ = keys()
    c = claims()
    c["environment"] = "production"

    with pytest.raises(PermissionError):
        issue(c, pr)
