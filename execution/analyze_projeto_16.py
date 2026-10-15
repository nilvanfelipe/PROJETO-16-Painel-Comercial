"""
Análise detalhada do Projeto 16 - Painel Comercial
Analisa:
1. fVendas_1.xlsx (Tabela f_vendas)
2. PROJETO 16 - Painel Comercial.pbix (Estrutura do relatório, visuais, medidas DAX, modelo)
"""

import os
import sys
import json
import zipfile
import re
import pandas as pd
from datetime import datetime

PROJECT_DIR = r"c:\Users\Nilvan\Documents\07 - PROJETOS\01 - PROJETOS POWER BI\PROJETO 16 - Painel Comercial"
PBIX_PATH = os.path.join(PROJECT_DIR, "PROJETO 16 - Painel Comercial.pbix")
EXCEL_PATH = os.path.join(PROJECT_DIR, "fVendas_1.xlsx")
OUTPUT_DIR = os.path.join(PROJECT_DIR, ".tmp")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def analyze_excel():
    print(f"[1/4] Analisando arquivo Excel: {EXCEL_PATH}...")
    file_size_mb = os.path.getsize(EXCEL_PATH) / (1024 * 1024)
    print(f"Tamanho do arquivo: {file_size_mb:.2f} MB")
    
    # Inspeciona sheets
    excel_file = pd.ExcelFile(EXCEL_PATH, engine='openpyxl')
    sheet_names = excel_file.sheet_names
    print(f"Abas encontradas: {sheet_names}")
    
    # Carrega a planilha principal
    primary_sheet = sheet_names[0]
    print(f"Carregando amostra e metadados de '{primary_sheet}'...")
    
    # Leitura de uma amostra inicial de 10.000 linhas para inferência rápida e depois lê estatísticas completas
    df_sample = pd.read_excel(EXCEL_PATH, sheet_name=primary_sheet, nrows=50, engine='openpyxl')
    columns = list(df_sample.columns)
    print(f"Colunas identificadas ({len(columns)}): {columns}")
    
    # Agora lê dados completos (apenas colunas necessárias se for muito grande, ou lê inteiro)
    print("Carregando dataset completo para métricas exatas...")
    df = pd.read_excel(EXCEL_PATH, sheet_name=primary_sheet, engine='openpyxl')
    total_rows, total_cols = df.shape
    print(f"Total de registros: {total_rows:,} linhas x {total_cols} colunas")
    
    # Análise de nulos e tipos
    col_analysis = {}
    for col in df.columns:
        null_count = int(df[col].isnull().sum())
        null_pct = round((null_count / total_rows) * 100, 2)
        unique_vals = int(df[col].nunique())
        dtype = str(df[col].dtype)
        
        info = {
            "dtype": dtype,
            "null_count": null_count,
            "null_pct": null_pct,
            "unique_count": unique_vals,
        }
        
        # Numéricos
        if pd.api.types.is_numeric_dtype(df[col]):
            info["min"] = float(df[col].min()) if not pd.isna(df[col].min()) else None
            info["max"] = float(df[col].max()) if not pd.isna(df[col].max()) else None
            info["sum"] = float(df[col].sum()) if not pd.isna(df[col].sum()) else None
            info["mean"] = float(df[col].mean()) if not pd.isna(df[col].mean()) else None
        
        # Datas
        elif pd.api.types.is_datetime64_any_dtype(df[col]) or 'data' in col.lower() or 'date' in col.lower():
            try:
                date_series = pd.to_datetime(df[col], errors='coerce')
                info["min_date"] = str(date_series.min())
                info["max_date"] = str(date_series.max())
            except Exception:
                pass
        
        col_analysis[col] = info

    sample_records = df.head(5).to_dict(orient="records")
    # Converte timestamps para string
    for r in sample_records:
        for k, v in r.items():
            if isinstance(v, (pd.Timestamp, datetime)):
                r[k] = str(v)
            elif pd.isna(v):
                r[k] = None

    excel_summary = {
        "file_name": os.path.basename(EXCEL_PATH),
        "size_mb": round(file_size_mb, 2),
        "sheets": sheet_names,
        "primary_sheet": primary_sheet,
        "total_rows": total_rows,
        "total_columns": total_cols,
        "columns_analysis": col_analysis,
        "sample_records": sample_records
    }
    
    with open(os.path.join(OUTPUT_DIR, "analise_excel_fvendas.json"), "w", encoding="utf-8") as f:
        json.dump(excel_summary, f, indent=2, ensure_ascii=False)
        
    print("[SUCCESS] Análise do Excel concluída e salva em analise_excel_fvendas.json")
    return excel_summary

def analyze_pbix():
    print(f"\n[2/4] Analisando arquivo PBIX: {PBIX_PATH}...")
    file_size_mb = os.path.getsize(PBIX_PATH) / (1024 * 1024)
    print(f"Tamanho do arquivo: {file_size_mb:.2f} MB")
    
    pbix_data = {
        "file_name": os.path.basename(PBIX_PATH),
        "size_mb": round(file_size_mb, 2),
        "zip_files": [],
        "pages": {},
        "diagram_layout": None,
        "theme": None,
        "extracted_dax": [],
        "extracted_m": []
    }
    
    with zipfile.ZipFile(PBIX_PATH, 'r') as z:
        pbix_data["zip_files"] = z.namelist()
        
        # 1. Diagram Layout
        if "DiagramLayout" in z.namelist():
            try:
                dl_raw = z.read("DiagramLayout").decode("utf-16-le")
                pbix_data["diagram_layout"] = json.loads(dl_raw)
            except Exception as e:
                pbix_data["diagram_layout_error"] = str(e)
                
        # 2. Themes
        for name in z.namelist():
            if "RegisteredResources" in name and name.endswith(".json"):
                try:
                    theme_raw = z.read(name).decode("utf-8")
                    pbix_data["theme"] = json.loads(theme_raw)
                except Exception:
                    pass
                    
        # 3. Report Definition (Pages & Visuals)
        pages_dict = {}
        # Lista páginas
        for name in z.namelist():
            if name.startswith("Report/definition/pages/") and name.endswith("page.json"):
                page_folder = os.path.dirname(name)
                try:
                    page_meta = json.loads(z.read(name).decode("utf-8"))
                    page_name = page_meta.get("displayName", page_meta.get("name", "Unknown"))
                    pages_dict[page_folder] = {
                        "metadata": page_meta,
                        "visuals": []
                    }
                except Exception as e:
                    print(f"Erro ao ler page {name}: {e}")
                    
        # Visuals
        for name in z.namelist():
            if "/visuals/" in name and name.endswith("visual.json"):
                parts = name.split("/visuals/")
                page_folder = parts[0]
                try:
                    vis_meta = json.loads(z.read(name).decode("utf-8"))
                    if page_folder in pages_dict:
                        pages_dict[page_folder]["visuals"].append(vis_meta)
                except Exception as e:
                    print(f"Erro ao ler visual {name}: {e}")
                    
        pbix_data["pages"] = pages_dict
        
        # 4. Inspeciona DataModel em busca de texto, expressões DAX, medidas e M
        if "DataModel" in z.namelist():
            print("Escaneando DataModel em busca de expressões DAX e Queries M...")
            dm_raw = z.read("DataModel")
            # Converte em texto ignorando erros (utf-16-le e utf-8)
            text_u16 = dm_raw.decode("utf-16-le", errors="ignore")
            text_u8 = dm_raw.decode("utf-8", errors="ignore")
            full_text = text_u16 + "\n" + text_u8
            
            # Padrões DAX comuns
            # Procura por medidas: [Nome da Medida] := ou Measure Name =
            dax_patterns = [
                r'([A-Za-z0-9_ %]+)\s*=\s*(CALCULATE[\s\S]*?)(?=\x00|\r\n\r\n|\n\n|\Z)',
                r'([A-Za-z0-9_ %]+)\s*=\s*(DIVIDE[\s\S]*?)(?=\x00|\r\n\r\n|\n\n|\Z)',
                r'([A-Za-z0-9_ %]+)\s*=\s*(SUMX?[\s\S]*?)(?=\x00|\r\n\r\n|\n\n|\Z)',
                r'([A-Za-z0-9_ %]+)\s*=\s*(COUNTROWS[\s\S]*?)(?=\x00|\r\n\r\n|\n\n|\Z)',
                r'([A-Za-z0-9_ %]+)\s*=\s*(AVERAGE[\s\S]*?)(?=\x00|\r\n\r\n|\n\n|\Z)',
                r'\[([A-Za-z0-9_ %]+)\]\s*:=\s*([^\r\n]+)'
            ]
            
            found_measures = set()
            for pat in dax_patterns:
                for match in re.finditer(pat, full_text):
                    m_name = match.group(1).strip()
                    m_formula = match.group(2).strip()
                    # Limita tamanho e caracteres imprimíveis
                    m_formula_clean = "".join([c for c in m_formula if c.isprintable() or c in '\r\n\t'])
                    if len(m_name) < 50 and len(m_formula_clean) > 3:
                        found_measures.add((m_name, m_formula_clean[:300]))
                        
            pbix_data["extracted_dax"] = [{"name": m[0], "formula": m[1]} for m in sorted(found_measures)]
            
            # M Queries
            m_pattern = r'(let\s+[\s\S]*?\bin\b\s+[#\w\"\s_]+)'
            found_m = []
            for match in re.finditer(m_pattern, full_text):
                m_code = match.group(1).strip()
                m_clean = "".join([c for c in m_code if c.isprintable() or c in '\r\n\t'])
                if len(m_clean) > 20 and len(m_clean) < 4000:
                    found_m.append(m_clean)
            pbix_data["extracted_m"] = found_m[:10]
            
    with open(os.path.join(OUTPUT_DIR, "analise_pbix_detalhada.json"), "w", encoding="utf-8") as f:
        json.dump(pbix_data, f, indent=2, ensure_ascii=False)
        
    print("[SUCCESS] Análise do PBIX concluída e salva em analise_pbix_detalhada.json")
    return pbix_data

if __name__ == "__main__":
    print("Iniciando auditoria técnica completa...")
    excel_res = analyze_excel()
    pbix_res = analyze_pbix()
    print("\nAuditoria técnica finalizada com sucesso!")
