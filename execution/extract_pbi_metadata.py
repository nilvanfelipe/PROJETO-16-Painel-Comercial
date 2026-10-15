import os
import json
import zipfile
import csv
import glob

def parse_m_files(project_path):
    powerquery_dir = os.path.join(project_path, "powerquery")
    m_queries = {}
    if os.path.exists(powerquery_dir):
        for root, _, files in os.walk(powerquery_dir):
            for file in files:
                if file.endswith(".m"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            m_queries[file] = f.read()
                    except UnicodeDecodeError:
                        with open(file_path, "r", encoding="latin-1") as f:
                            m_queries[file] = f.read()
    return m_queries

def parse_dax_files(project_path):
    dax_data = {}
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith(".dax"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        dax_data[file] = f.read()
                except UnicodeDecodeError:
                    with open(file_path, "r", encoding="latin-1") as f:
                        dax_data[file] = f.read()
    return dax_data

def parse_text_briefs(project_path):
    briefs = {}
    brief_extensions = ('.md', '.txt')
    for root, _, files in os.walk(project_path):
        # Ignore target output README.md or temporary files
        for file in files:
            if file.lower().endswith(brief_extensions) and file.lower() != "readme.md":
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        briefs[file] = f.read()
                except Exception as e:
                    briefs[file] = f"Error reading brief: {str(e)}"
    return briefs

def parse_data_files(project_path):
    datasets_info = []
    for root, _, files in os.walk(project_path):
        for file in files:
            file_path = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            if ext in ['.csv', '.tsv']:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        headers = next(reader, [])
                        sample_row = next(reader, [])
                    datasets_info.append({
                        "file_name": file,
                        "relative_path": os.path.relpath(file_path, project_path),
                        "size_bytes": os.path.getsize(file_path),
                        "headers": headers,
                        "sample_row": sample_row
                    })
                except Exception:
                    datasets_info.append({
                        "file_name": file,
                        "relative_path": os.path.relpath(file_path, project_path),
                        "size_bytes": os.path.getsize(file_path),
                        "info": "Could not parse CSV headers directly."
                    })
            elif ext in ['.xlsx', '.xls', '.parquet', '.json', '.sql']:
                datasets_info.append({
                    "file_name": file,
                    "relative_path": os.path.relpath(file_path, project_path),
                    "size_bytes": os.path.getsize(file_path),
                    "type": ext[1:].upper()
                })
    return datasets_info

def parse_pbix_metadata(project_path):
    pbix_info = []
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith(".pbix"):
                file_path = os.path.join(root, file)
                meta = {
                    "file_name": file,
                    "relative_path": os.path.relpath(file_path, project_path),
                    "size_bytes": os.path.getsize(file_path),
                    "has_datamodel_schema": False
                }
                try:
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        namelist = zip_ref.namelist()
                        meta["zip_contents"] = namelist
                        if "DataModelSchema" in namelist:
                            meta["has_datamodel_schema"] = True
                            # Extract schema string snippet if possible
                            schema_bytes = zip_ref.read("DataModelSchema")
                            # Convert UTF-16 or UTF-8 if present
                            try:
                                schema_text = schema_bytes.decode('utf-16-le')
                                # Read first 2000 chars for preview
                                meta["schema_preview"] = schema_text[:2000]
                            except Exception:
                                pass
                except Exception as e:
                    meta["error"] = str(e)
                pbix_info.append(meta)
    return pbix_info

def generate_project_dossier(project_path):
    project_name = os.path.basename(os.path.normpath(project_path))
    dossier = {
        "project_name": project_name,
        "project_path": project_path,
        "powerquery_m_scripts": parse_m_files(project_path),
        "dax_measures": parse_dax_files(project_path),
        "text_briefs": parse_text_briefs(project_path),
        "datasets": parse_data_files(project_path),
        "pbix_files": parse_pbix_metadata(project_path),
    }

    output_dir = os.path.join(project_path, ".tmp")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "dossier_projeto.json")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(dossier, f, indent=2, ensure_ascii=False)

    print(f"[SUCCESS] Dossier gerado em: {output_file}")
    return output_file

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    generate_project_dossier(target)
