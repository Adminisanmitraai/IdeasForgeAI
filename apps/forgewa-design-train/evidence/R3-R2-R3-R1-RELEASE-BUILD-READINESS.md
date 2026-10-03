# FW-TRAIN.CADMAXD5.1A-R3-R2-R3-R1 — AutoCAD 2024 Semantic Bridge Release-Build Readiness

Status: PASS for real-reference unsigned release-build readiness. NO AUTOCAD LOAD.

## Installed AutoCAD 2024 references
Running AutoCAD executable:
C:\Program Files\Autodesk\AutoCAD 2024\acad.exe
Observed AutoCAD PID during certification: 17272.

Read-only reference inspection:
- AcMgd.dll — assembly 24.3.0.0, file/product 24.3.61.0.0, SHA-256 3f495f7afd430306925ebc10d7f706108fd0ec54630571db8e6c01cd63d3ba2c
- AcCoreMgd.dll — assembly 24.3.0.0, file/product 24.3.61.0.0, SHA-256 2b613b1ec6e68300e71b17d3d50702992f8460484cea17c03214ce4c9d2b4434
- AcDbMgd.dll — assembly 24.3.0.0, file/product 24.3.61.0.0, SHA-256 fc48a2d62c133d9ade32acc99ef14588bfa9286d7cf2cecba8be82a00506bf4a

These identities match the intended AutoCAD 2024 / 24.3 managed API line.

## Real-reference build
Isolated workspace:
D:\APPS\ForgeWa-Training-Cert-R3R2R3R1-20261003-A

The certified bridge source was compiled outside AutoCAD using the installed AcMgd/AcCoreMgd/AcDbMgd assemblies. No Autodesk assembly was copied or modified.

Final candidate build settings:
- target: library
- platform: x64 / AMD64
- optimized release build
- assembly version: 0.1.0.0
- file version: 0.1.0.0
- CLR image runtime: v4.0.30319
- Authenticode: NotSigned

Final unsigned DLL:
release\ForgeWa.AutoCAD.Semantic.dll
SHA-256: 4cb2a6500320f78b37cf7cc1d3c50567b9009c7102b64f2b6a9aed5bb9884388
Length: 8704 bytes.

Managed references declared by the final DLL:
- mscorlib 4.0.0.0
- Acdbmgd 24.3.0.0
- accoremgd 24.3.0.0
- System 4.0.0.0
- System.Core 4.0.0.0

ProcessorArchitecture is Amd64.

## Frozen release package hashes
- src\ForgeWaSemanticBridge.cs — 9b73b87d64830e28bbe83c602adec52386c646d99974ec02e9395aeead6fe81c
- src\ReleaseAssemblyInfo.cs — 25fd496b0f8bf954d31e24f9604f50eb58082a6d075a6aff77c327a5ef31b3b6
- release\ForgeWa.AutoCAD.Semantic.dll — 4cb2a6500320f78b37cf7cc1d3c50567b9009c7102b64f2b6a9aed5bb9884388
- release\PackageContents.xml — ca437ff6d274bbe028485212eb6e42c7b6bc50911e4b6f8089c48c83c45a84a4

## Binary/static API inspection
No forbidden binary markers were found for:
SendStringToExecute, SendCommand, acedCommand, acedCmd, LockDocument, DocumentLock,
Transaction, Database, GetObject, SetSystemVariable, CommandMethod, LispFunction,
or PipeDirection.InOut.

Expected markers were present:
CommandWillStart, CommandEnded, CommandCancelled, GlobalCommandName, NamedPipeClientStream.

This inspection supplements, but does not replace, the R3-R2-R3 source/static tests.

## Signing authority
Windows SDK signtool.exe is installed.
The release DLL currently has no Authenticode signature.
No unexpired code-signing certificate with an accessible private key and Code Signing EKU was found in CurrentUser\My or LocalMachine\My.

Therefore this PC currently has tooling to sign, but no approved signing identity available. No self-signed or substitute certificate was generated because the load-security gate requires an approved IdeasForgeAI signing authority.

## Load boundary
ForgeWa semantic plugin hits in Autodesk ApplicationPlugins locations: 0.
No NETLOAD was invoked.
No ApplicationPlugins installation occurred.
SECURELOAD and TRUSTEDPATHS were not changed.
AutoCAD was not restarted.
The release DLL was not loaded into AutoCAD.
Production activation did not occur.

Post-build AutoCAD PID 17272 remained running and no senddmp.exe crash reporter was present.

## Re-attestation
All 11 preserved callback-crash evidence files matched the prior SHA-256 manifest.
All four protected ForgeCommander production files matched their certified hashes.

## Disposition
R3-R2-R3-R1 is COMPLETE for unsigned real-reference release-build readiness.
The unsigned SHA-256 above is the sole candidate authority for the next signing gate.

Do not load this unsigned DLL into AutoCAD. The next gate should provision/identify an approved code-signing certificate, sign an exact copy of the certified unsigned candidate, verify Authenticode chain/timestamp policy, capture the signed SHA-256, and build a reviewed .bundle without installing or loading it.
