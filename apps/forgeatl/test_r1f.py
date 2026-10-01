from pathlib import Path
ROOT=Path(__file__).with_name("ui")
def run():
 r={}
 files={p.name:p.read_text(encoding="utf-8") for p in ROOT.iterdir() if p.is_file()}
 r["shell_files"]=all(n in files for n in ("index.html","styles.css","fixtures.js","app.js"))
 r["nine_routes"]=files["fixtures.js"].count('["')>=9 and "student/" in files["app.js"]
 r["six_panels"]=all(x in files["app.js"] for x in ("Live Classroom","Examination","Mastery","Failure Analysis","Timeline","Replay / Audit"))
 r["truthful_idle"]="state:\"idle\"" in files["fixtures.js"] and "SOURCE: NO EVENTS" in files["app.js"]
 r["fixture_only"]="certified-read-fixture" in files["fixtures.js"] and 'activation:"disabled"' in files["fixtures.js"]
 joined="\n".join(files.values()).lower()
 r["no_live_endpoints"]=not any(x in joined for x in ("fetch(","websocket","axios","/api/","http://","https://"))
 r["no_activation_controls"]=not any(x in joined for x in ("start training","provision gpu","activate teacher"))
 ok=all(r.values());print({"milestone":"FORGE-ATL.1A-R1F","result":"PASS" if ok else "FAIL","checks":r});raise SystemExit(0 if ok else 1)
if __name__=="__main__":run()
