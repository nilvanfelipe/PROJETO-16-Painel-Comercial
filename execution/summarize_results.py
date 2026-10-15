import json

with open(r"c:\Users\Nilvan\Documents\07 - PROJETOS\01 - PROJETOS POWER BI\PROJETO 16 - Painel Comercial\.tmp\analise_pbix_detalhada.json", encoding="utf-8") as f:
    data = json.load(f)

print("=== PAGINAS E VISUAIS ===")
for page_id, page_info in data["pages"].items():
    p_meta = page_info["metadata"]
    name = p_meta.get("displayName", "Sem Nome")
    w = p_meta.get("width")
    h = p_meta.get("height")
    p_type = p_meta.get("type", "Standard")
    print(f"\nPagina: '{name}' ({w}x{h}) - Tipo: {p_type}")
    
    for v in page_info["visuals"]:
        v_inner = v.get("visual", {})
        v_type = v_inner.get("visualType")
        v_title = "Sem Titulo"
        try:
            titles = v_inner.get("visualContainerObjects", {}).get("title", [])
            if titles:
                v_title = titles[0].get("properties", {}).get("text", {}).get("expr", {}).get("Literal", {}).get("Value", "Sem Titulo")
        except Exception:
            pass
        projections = []
        try:
            for k, val in v_inner.get("query", {}).get("queryState", {}).items():
                for p in val.get("projections", []):
                    projections.append(f"{k}: {p.get('queryRef')}")
        except Exception:
            pass
        print(f"  - [{v_type}] Titulo: {v_title} | Campos: {projections}")

print("\n=== MEDIDAS EXTRAIDAS ===")
for dax in data.get("extracted_dax", []):
    print(f"  * {dax['name']}: {dax['formula']}")

print("\n=== POWER QUERY M SCRIPTS EXTRAIDOS ===")
for i, m in enumerate(data.get("extracted_m", [])):
    print(f"--- M Script #{i+1} ---")
    print(m)
    print("----------------------")
