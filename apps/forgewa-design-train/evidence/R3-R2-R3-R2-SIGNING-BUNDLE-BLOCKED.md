# FW-TRAIN.CADMAXD5.1A-R3-R2-R3-R2 — Semantic Bridge Signing + Bundle Candidate

Status: BLOCKED AT APPROVED CODE-SIGNING AUTHORITY. Pre-sign bundle staging complete. NO INSTALL / NO AUTOCAD LOAD.

## Sole unsigned authority
Certified input DLL:
ForgeWa.AutoCAD.Semantic.dll
SHA-256: 4cb2a6500320f78b37cf7cc1d3c50567b9009c7102b64f2b6a9aed5bb9884388

The input was re-attested before signing work:
- SHA-256 exact match: true
- Authenticode: NotSigned
- signer certificate present: false

No alternate DLL was accepted.

## Signing authority discovery
Windows SDK signtool.exe is installed.

Certificate-store scan:
- CurrentUser certificate stores: no currently valid certificate with accessible private key + Code Signing EKU.
- LocalMachine certificate stores: no currently valid certificate with accessible private key + Code Signing EKU.
- Total usable code-signing certificates: 0.

Read-only candidate-certificate-file discovery under the inspected IdeasForgeAI development trees found no .pfx, .p12, .p7b, .cer or .crt files.

No certificate/private key was exported or exposed.
No self-signed certificate was generated.
No substitute signing identity was created.
No signing command was attempted because no approved signing authority exists on this PC.

Therefore signed SHA-256, Authenticode chain verification and timestamp verification are intentionally unavailable in this gate.

## Pre-sign bundle staging
Staging path, outside Autodesk ApplicationPlugins:
D:\APPS\ForgeWa-Training-Cert-R3R2R3R2-20261003-A\ForgeWa.AutoCAD.Semantic.bundle

Files:
- Contents\ForgeWa.AutoCAD.Semantic.dll — SHA-256 4cb2a6500320f78b37cf7cc1d3c50567b9009c7102b64f2b6a9aed5bb9884388
- PackageContents.xml — SHA-256 ca437ff6d274bbe028485212eb6e42c7b6bc50911e4b6f8089c48c83c45a84a4
- UNSIGNED_DO_NOT_INSTALL.txt — explicit pre-sign safety marker

Package review:
- AppVersion 0.1.0
- Runtime SeriesMin R24.3
- Runtime SeriesMax R24.3
- Module ./Contents/ForgeWa.AutoCAD.Semantic.dll
- LoadOnAutoCADStartup True

LoadOnAutoCADStartup=True is retained from the reviewed candidate manifest but must not take effect until a later explicit installation/load gate after signing certification.

The staged bundle is PRE_SIGN_BLOCKED. It is not the final signed bundle authority because signing will change DLL bytes and therefore requires a new bundle manifest/hash attestation.

## Safety re-attestation
Installed ForgeWa semantic plugin hits in Autodesk ApplicationPlugins locations: 0.
AutoCAD PID 17272 remained running.
senddmp.exe crash reporter count: 0.
No NETLOAD, ApplicationPlugins install, AutoCAD restart, SECURELOAD/TRUSTEDPATHS change or production activation occurred.

All 11 preserved callback-crash evidence files matched their certified SHA-256 manifest.
All four protected ForgeCommander production files matched their certified hashes.

## Disposition
R3-R2-R3-R2 cannot be declared COMPLETE because the required approved IdeasForgeAI code-signing certificate/private-key authority is not provisioned.

To resume this exact gate, provision an approved code-signing certificate into a Windows certificate store accessible to signtool (preferred) or provide the approved enterprise signing mechanism. Do not send certificate passwords or private-key material in chat.

After provisioning, resume from the exact unsigned SHA above:
1. re-attest unsigned SHA;
2. sign an exact copy with the approved identity;
3. verify Authenticode signer/chain and timestamp policy;
4. capture signed SHA-256;
5. replace only the staged bundle DLL with the signed bytes;
6. re-attest dependencies, forbidden API surface and complete bundle hashes;
7. still do not install or load AutoCAD in this gate.
