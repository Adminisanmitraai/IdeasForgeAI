from __future__ import annotations

import subprocess

from rtx_node_enrollment_preflight import enrollment_preflight, stable_windows_device_id


def fake_nvidia(argv, **kwargs):
    return subprocess.CompletedProcess(
        argv,
        0,
        stdout="0, NVIDIA GeForce RTX 5090, GPU-RTX5090, 32768, 580.88\n",
        stderr="",
    )


checks = {}

derived = stable_windows_device_id(hostname="RTX-LAB-01", node=123456789)
checks["deterministic_device_id"] = (
    derived == stable_windows_device_id(hostname="RTX-LAB-01", node=123456789)
    and derived.startswith("fc-win-")
    and len(derived) == 27
)

ready = enrollment_preflight(
    existing_device_id="fc-win-old-device",
    hostname="RTX-LAB-01",
    node=123456789,
    runner=fake_nvidia,
)
checks["rtx_ready"] = (
    ready["nvidia_smi_present"] is True
    and ready["nvidia_gpu_count"] == 1
    and ready["gpus"][0]["name"] == "NVIDIA GeForce RTX 5090"
    and ready["gpus"][0]["memory_gb"] == 32.0
    and ready["ready_for_distinct_enrollment"] is True
    and ready["matches_existing_device_id"] is False
    and ready["secret_values_exposed"] is False
)

same_id = enrollment_preflight(
    existing_device_id=derived,
    hostname="RTX-LAB-01",
    node=123456789,
    runner=fake_nvidia,
)
checks["duplicate_identity_detected"] = (
    same_id["matches_existing_device_id"] is True
    and same_id["ready_for_distinct_enrollment"] is False
)

def missing_nvidia(argv, **kwargs):
    raise FileNotFoundError("nvidia-smi")

missing = enrollment_preflight(
    hostname="NO-GPU",
    node=987654321,
    runner=missing_nvidia,
)
checks["missing_nvidia_fail_closed"] = (
    missing["nvidia_smi_present"] is False
    and missing["nvidia_gpu_count"] == 0
    and missing["ready_for_distinct_enrollment"] is False
)

result = "PASS" if all(checks.values()) else "FAIL"
print({"milestone": "FORGE-ATL.2D-R1A", "result": result, "checks": checks})
raise SystemExit(0 if result == "PASS" else 1)
