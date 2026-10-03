# ForgeWa AutoCAD Semantic Bridge — Load Security Gate

This candidate MUST NOT be loaded into AutoCAD until a later explicit live-load gate.

Required before first AutoCAD load:
1. Build specifically against the installed AutoCAD 2024 managed SDK and .NET Framework 4.8.
2. Re-run static tests against the exact release source and inspect the exact release DLL.
3. Digitally sign the release DLL with the approved IdeasForgeAI code-signing certificate.
4. Verify the signature and record SHA-256 before installation.
5. Package only the signed DLL and reviewed PackageContents.xml in a dedicated .bundle.
6. Install only to an Autodesk ApplicationPlugins trusted location or another explicitly approved read-only trusted location.
7. Do not lower SECURELOAD and do not broaden TRUSTEDPATHS to a writable project/download directory.
8. First live load must use a disposable/test drawing and certify load/unload plus idle event subscription before any command event test.

Current R3-R2-R3 candidate status:
- source/static candidate only;
- no release DLL exists;
- no .bundle is installed;
- no signing certificate was used;
- no NETLOAD/APPAUTOLOADER/load action occurred;
- no AutoCAD process was modified or restarted.
