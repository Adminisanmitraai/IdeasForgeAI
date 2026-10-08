from __future__ import annotations

import json
import tempfile
from pathlib import Path

from rtx_pairing_recovery import (
    PairingRecoveryError,
    consume_pairing_ticket,
    repair_existing_launcher,
    request_pairing_ticket,
    write_pairing_ticket_file,
)


checks = {}

loader_source = __import__("inspect").getsource(__import__("rtx_pairing_recovery")._load_dpapi_token)
checks["dpapi_bom_whitespace_trim"] = (
    ".Trim([char]0xFEFF).Trim()" in loader_source
)

save_source = __import__("inspect").getsource(__import__("rtx_pairing_recovery")._save_dpapi_token)
checks["dpapi_save_no_powershell_args"] = (
    "$args[0]" not in save_source
    and "WriteAllText" in save_source
    and "compare_digest" in save_source
    and "paired_token_round_trip_failed" in save_source
)


secret_old = "old-device-token-never-log"
ticket_code = "pairing-code-never-chat"


def fake_token_loader(path: Path) -> str:
    return secret_old


ticket_calls = []


def fake_ticket_request(url, *, method, body=None, bearer_token=None, timeout_seconds=15):
    ticket_calls.append({
        "url": url,
        "method": method,
        "body": body,
        "bearer_token": bearer_token,
    })
    return {"pairing_code": ticket_code, "expires_at": 9999999999, "ttl_seconds": 600}


ticket = request_pairing_ticket(
    existing_token_file=Path("fake.dpapi"),
    token_loader=fake_token_loader,
    request_func=fake_ticket_request,
)
checks["ticket_uses_existing_device_auth"] = (
    len(ticket_calls) == 1
    and ticket_calls[0]["method"] == "POST"
    and ticket_calls[0]["bearer_token"] == secret_old
    and ticket["pairing_code"] == ticket_code
    and ticket["ttl_seconds"] == 600
)

with tempfile.TemporaryDirectory() as td:
    ticket_path = Path(td) / "pairing-code.txt"
    write_pairing_ticket_file(ticket, ticket_path)
    checks["ticket_written_locally"] = (
        ticket_path.read_text(encoding="utf-8") == ticket_code
    )

new_device_id = "fc-win-rtxunique000000001"
new_device_token = "new-rtx-device-token-never-log"


def good_preflight(*, existing_device_id=None):
    return {
        "derived_device_id": new_device_id,
        "matches_existing_device_id": False,
        "nvidia_smi_present": True,
        "nvidia_gpu_count": 1,
        "ready_for_distinct_enrollment": True,
        "gpus": [
            {
                "name": "NVIDIA GeForce RTX 5090",
                "memory_gb": 32.0,
            }
        ],
    }


pair_calls = []


def fake_pair_request(url, *, method, body=None, bearer_token=None, timeout_seconds=15):
    pair_calls.append({
        "url": url,
        "method": method,
        "body": body,
        "bearer_token": bearer_token,
    })
    return {
        "enrolled": True,
        "owner_subject": "ranjan",
        "device_id": new_device_id,
        "device_token": new_device_token,
        "expires_at": 9999999999,
    }


saved_tokens = []


def fake_save_token(token: str, path: Path):
    saved_tokens.append((token, path))


with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    state_dir = root / "state"
    project_root = root / "project"
    project_root.mkdir()

    result = consume_pairing_ticket(
        pairing_code=ticket_code,
        current_device_id="fc-win-01e79233a6a6bf3bdc89",
        state_dir=state_dir,
        project_root=project_root,
        preflight_func=good_preflight,
        request_func=fake_pair_request,
        save_token_func=fake_save_token,
    )

    config_text = (state_dir / "agent-config.json").read_text(encoding="utf-8")
    launcher_text = (state_dir / "agent-launcher.py").read_text(encoding="utf-8")
    serialized_result = json.dumps(result)

    checks["pair_uses_distinct_derived_id"] = (
        len(pair_calls) == 1
        and pair_calls[0]["method"] == "POST"
        and pair_calls[0]["body"]["device_id"] == new_device_id
        and pair_calls[0]["body"]["pairing_code"] == ticket_code
        and result["device_id"] == new_device_id
    )

    checks["token_non_disclosure"] = (
        len(saved_tokens) == 1
        and saved_tokens[0][0] == new_device_token
        and new_device_token not in config_text
        and new_device_token not in launcher_text
        and new_device_token not in serialized_result
        and result["token_exposed"] is False
        and result["token_persisted_dpapi"] is True
    )

    checks["new_config_and_launcher"] = (
        new_device_id in config_text
        and new_device_id in launcher_text
        and "run_persistent_agent" in launcher_text
        and "sys.path.insert(0" in launcher_text
        and str(project_root) in launcher_text
        and result["session_started"] is False
    )


with tempfile.TemporaryDirectory() as td:
    state_dir = Path(td) / "state"
    state_dir.mkdir()
    config = {
        "device_id": new_device_id,
        "owner_subject": "ranjan",
        "gateway_ws_url": "wss://example.invalid/ws",
        "credential_file": str(state_dir / "device-token.dpapi"),
        "project_root": r"C:\IdeasForgeAI-ForgeATL",
    }
    (state_dir / "agent-config.json").write_text(json.dumps(config), encoding="utf-8")
    repaired = repair_existing_launcher(state_dir=state_dir)
    repaired_text = (state_dir / "agent-launcher.py").read_text(encoding="utf-8")
    checks["repair_launcher_no_token_read"] = (
        repaired["launcher_repaired"] is True
        and repaired["token_read"] is False
        and repaired["token_exposed"] is False
        and "sys.path.insert(0" in repaired_text
        and r"C:\IdeasForgeAI-ForgeATL" in repaired_text
        and new_device_id in repaired_text
    )


def no_nvidia_preflight(*, existing_device_id=None):
    return {
        "derived_device_id": "fc-win-other",
        "matches_existing_device_id": False,
        "nvidia_smi_present": False,
        "nvidia_gpu_count": 0,
        "ready_for_distinct_enrollment": False,
    }


blocked = False
try:
    with tempfile.TemporaryDirectory() as td:
        consume_pairing_ticket(
            pairing_code=ticket_code,
            current_device_id="fc-win-old",
            state_dir=Path(td) / "state",
            project_root=Path(td) / "project",
            preflight_func=no_nvidia_preflight,
            request_func=fake_pair_request,
            save_token_func=fake_save_token,
        )
except PairingRecoveryError as exc:
    blocked = str(exc) == "nvidia_not_present"

checks["no_nvidia_no_pairing"] = blocked

result = "PASS" if all(checks.values()) else "FAIL"
print({"milestone": "FORGE-ATL.2D-R1A-R1", "result": result, "checks": checks})
raise SystemExit(0 if result == "PASS" else 1)
