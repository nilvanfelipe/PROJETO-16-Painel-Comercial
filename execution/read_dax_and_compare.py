import json

with open(r"c:\Users\Nilvan\Documents\07 - PROJETOS\01 - PROJETOS POWER BI\PROJETO 31 - Comercial(Xperiun-Bussiness-Case)\.codex-analysis\dax-model-current.json", encoding="utf-8") as f:
    d = json.load(f)

measures = d.get("measures", [])
print(f"Total de medidas encontradas: {len(measures)}")
for m in measures:
    name = m.get("Name")
    expr = m.get("Expression")
    display_folder = m.get("DisplayFolder")
    print(f"[{display_folder}] {name} =\n  {expr}\n")
