# FW-TRAIN.CADMAXD5.1A-R3-R2-R3-DEV1 — Local Development Signing Isolation

Status: PASS / COMPLETE. NO AUTOCAD LOAD.

## Production authority preserved
Certified production unsigned candidate remained untouched:
SHA-256 4cb2a6500320f78b37cf7cc1d3c50567b9009c7102b64f2b6a9aed5bb9884388
Re-attestation after DEV build/signing: exact match true.

The DEV artifact is byte-distinct and cannot replace this authority.

## Development-only signing identity
Subject: CN=ForgeWa Development Only - Local Test
Purpose: local development/test only.
Lifetime: approximately six months, expiring 2027-04-03 local time.
Key algorithm: RSA 3072, SHA-256.
Private key: created with NonExportable policy in CurrentUser\My.
Certificate extensions directly inspected:
- Extended Key Usage: Code Signing (1.3.6.1.5.5.7.3.3)
- Key Usage: Digital Signature

Trust is scoped to this Windows user on this test PC. Public-certificate copies exist in:
- CurrentUser\TrustedPeople
- CurrentUser\TrustedPublisher
- CurrentUser\Root

The CurrentUser\Root copy resulted from the initial Windows trust operation. A later removal attempt was blocked by Windows security UI and was not bypassed. No LocalMachine certificate store contains this DEV certificate.

No certificate password, PFX or private-key export was created.

## DEV build identity
Separate source metadata explicitly watermarks the assembly:
- Product: ForgeWa AutoCAD Semantic Bridge DEV
- Description: ForgeWa AutoCAD Semantic Bridge - DEVELOPMENT ONLY
- Configuration: DEVELOPMENT ONLY / LOCAL TEST
- informational version: 0.1.0-dev-local

Unsigned DEV SHA-256:
7b3d3ef113047fcf21b7d717d0d46ced0b6cd2847554e3a92422e39d0985eb97

Signed DEV SHA-256:
5f2688b51deb4b4814f2801d2b2bf4a39786dc49a918c4c6593c49c8c9732919

Windows SignTool signing: success.
SignTool verification: 1 file verified, 0 warnings, 0 errors.
Get-AuthenticodeSignature status: Valid.
Signer: ForgeWa Development Only - Local Test.

Final signed-binary scan found zero forbidden markers for SendStringToExecute, SendCommand,
acedCommand/acedCmd, LockDocument/DocumentLock, Transaction, Database, GetObject,
SetSystemVariable, CommandMethod, LispFunction or PipeDirection.InOut.
DEVELOPMENT ONLY and ForgeWa AutoCAD Semantic Bridge DEV watermarks are present in final bytes.

## DEV bundle
Isolated path:
D:\APPS\ForgeWa-Training-Cert-R3R2R3DEV1-20261003-A\ForgeWa.AutoCAD.Semantic.DEV.bundle

Bundle:
- Contents\ForgeWa.AutoCAD.Semantic.DEV.dll
  SHA-256 5f2688b51deb4b4814f2801d2b2bf4a39786dc49a918c4c6593c49c8c9732919
- PackageContents.xml
  SHA-256 4514a79b9a6d97626398cc4e47e7bd62ce5be30447167907b46f261bf7171d86
- DEVELOPMENT_ONLY.txt
  SHA-256 be543e39d9fe405d906e3d79461853a0792e93ec614f71b0784b4153f3358627

The DEV manifest targets AutoCAD R24.3 and explicitly sets LoadOnAutoCADStartup=False.

## Load boundary
Installed ForgeWa semantic plugin hits in Autodesk ApplicationPlugins: 0.
No NETLOAD.
No bundle installation.
No SECURELOAD weakening.
No TRUSTEDPATHS change.
No AutoCAD restart.
No AutoCAD plugin load.
No production promotion or activation.

AutoCAD PID 17272 remained running and no senddmp.exe crash reporter was present.

## Historical safety re-attestation
All 11 preserved callback-crash evidence files matched their certified SHA-256 manifest.
All four protected ForgeCommander production files matched their certified hashes.

## Disposition
DEV1 is COMPLETE. The signed DEV DLL is authorized only for a later explicitly bounded local-test load gate on this Windows user/test PC. It must never be distributed or promoted as an official IdeasForgeAI publisher build.

The production unsigned SHA remains the production signing authority and is unaffected by this DEV path.
