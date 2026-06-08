import json
repos = json.loads(open("data/repos.json", encoding="utf-8").read())
contributions = json.loads(open("data/contributions.json", encoding="utf-8").read())
languages = json.loads(open("data/languages.json", encoding="utf-8").read())

security = sum(1 for r in repos if any(t in (r.get("topics", []) + [r.get("name", "")]) for t in ["security", "pentest", "audit", "vulnerability", "ids", "nids"]))
viz = sum(1 for r in repos if any(t in (r.get("topics", []) + [r.get("name", "")]) for t in ["visualization", "simulator", "explorer", "particle", "fractal", "neural", "gravity", "maze", "wave", "spectrograph", "hexagonal", "cyberpunk"]))
os_proj = sum(1 for r in repos if any(t in (r.get("topics", []) + [r.get("name", "")]) for t in ["os", "linux", "pentestos", "shieldos", "vaultos", "androidfw", "firmware", "kernel"]))
fullstack = sum(1 for r in repos if any(t in (r.get("topics", []) + [r.get("name", "")]) for t in ["flask", "react", "fastapi", "admin", "dashboard", "studyhub", "devforge", "taskflow"]))

print("Security:", security)
print("Viz:", viz)
print("OS:", os_proj)
print("Fullstack:", fullstack)
print("Commits:", contributions["commits"])
print("PRs:", contributions["pull_requests"])
print("Issues:", contributions["issues"])
print("Languages:", len(languages["languages"]))
print("Repos:", len(repos))
