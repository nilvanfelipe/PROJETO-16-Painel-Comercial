import os
import json
import pandas as pd

EXCEL_PATH = r"c:\Users\Nilvan\Documents\07 - PROJETOS\01 - PROJETOS POWER BI\PROJETO 16 - Painel Comercial\fVendas_1.xlsx"
OUTPUT_PATH = r"c:\Users\Nilvan\Documents\07 - PROJETOS\01 - PROJETOS POWER BI\PROJETO 16 - Painel Comercial\.tmp\business_insights_fvendas.json"

print("Lendo fVendas_1.xlsx para extração de KPIs de negócio...")
df = pd.read_excel(EXCEL_PATH, engine="openpyxl")

# Converte data
df["Data"] = pd.to_datetime(df["Data"])
df["Ano"] = df["Data"].dt.year
df["Mes"] = df["Data"].dt.month

total_faturamento_bruto = float(df["VlrTotal"].sum())
total_desconto = float(df["Desconto_Item"].sum())
total_faturamento_liquido = float(df["VlrLiquido"].sum())
total_custo_medio = float((df["CustoMedio"] * df["Qtde"]).sum())
total_quantidade = int(df["Qtde"].sum())
total_pedidos = int(df["ID_Pedido"].nunique())
ticket_medio = total_faturamento_liquido / total_pedidos
preco_medio_unitario = float(df["VlrUnit"].mean())
margem_bruta = total_faturamento_liquido - total_custo_medio
margem_pct = (margem_bruta / total_faturamento_liquido) * 100 if total_faturamento_liquido > 0 else 0

# Devoluções (Qtde < 0)
devolucoes_df = df[df["Qtde"] < 0]
total_devolucoes_qtd = int(devolucoes_df["Qtde"].sum())
total_devolucoes_vlr = float(devolucoes_df["VlrTotal"].sum())

# Faturamento por Ano
vendas_por_ano = df.groupby("Ano").agg(
    Faturamento_Liquido=("VlrLiquido", "sum"),
    Faturamento_Bruto=("VlrTotal", "sum"),
    Quantidade=("Qtde", "sum"),
    Pedidos=("ID_Pedido", "nunique")
).reset_index().to_dict(orient="records")

# Top 10 Maiores Produtos por Faturamento Líquido
top10_maiores_produtos = df.groupby(["Item", "DescricaoItem"]).agg(
    Faturamento_Liquido=("VlrLiquido", "sum"),
    Quantidade=("Qtde", "sum"),
    Preco_Medio=("VlrUnit", "mean")
).reset_index().sort_values(by="Faturamento_Liquido", ascending=False).head(10).to_dict(orient="records")

# Top 10 Menores Produtos por Faturamento Líquido
top10_menores_produtos = df.groupby(["Item", "DescricaoItem"]).agg(
    Faturamento_Liquido=("VlrLiquido", "sum"),
    Quantidade=("Qtde", "sum"),
    Preco_Medio=("VlrUnit", "mean")
).reset_index().sort_values(by="Faturamento_Liquido", ascending=True).head(10).to_dict(orient="records")

# Vendas por Marca
vendas_marca = df.groupby("Marca").agg(
    Faturamento_Liquido=("VlrLiquido", "sum"),
    Quantidade=("Qtde", "sum")
).reset_index().sort_values(by="Faturamento_Liquido", ascending=False).to_dict(orient="records")

# Vendas por Grupo
vendas_grupo = df.groupby("Grupo").agg(
    Faturamento_Liquido=("VlrLiquido", "sum"),
    Quantidade=("Qtde", "sum")
).reset_index().sort_values(by="Faturamento_Liquido", ascending=False).to_dict(orient="records")

# Vendas por Loja (Nome_Fantasia)
vendas_loja = df.groupby("Nome_Fantasia").agg(
    Faturamento_Liquido=("VlrLiquido", "sum"),
    Quantidade=("Qtde", "sum"),
    Pedidos=("ID_Pedido", "nunique")
).reset_index().sort_values(by="Faturamento_Liquido", ascending=False).to_dict(orient="records")

result = {
    "kpis_gerais": {
        "total_pedidos": total_pedidos,
        "total_linhas": len(df),
        "total_quantidade": total_quantidade,
        "faturamento_bruto": round(total_faturamento_bruto, 2),
        "total_descontos": round(total_desconto, 2),
        "desconto_medio_pct": round((total_desconto / total_faturamento_bruto) * 100, 2),
        "faturamento_liquido": round(total_faturamento_liquido, 2),
        "custo_total": round(total_custo_medio, 2),
        "margem_bruta_valor": round(margem_bruta, 2),
        "margem_bruta_pct": round(margem_pct, 2),
        "ticket_medio": round(ticket_medio, 2),
        "preco_medio_unitario": round(preco_medio_unitario, 2),
        "total_devolucoes_qtd": total_devolucoes_qtd,
        "total_devolucoes_vlr": round(total_devolucoes_vlr, 2)
    },
    "vendas_por_ano": vendas_por_ano,
    "top10_maiores_produtos": top10_maiores_produtos,
    "top10_menores_produtos": top10_menores_produtos,
    "vendas_marca": vendas_marca,
    "vendas_grupo": vendas_grupo,
    "vendas_loja": vendas_loja
}

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"[SUCCESS] Métricas de negócio geradas em: {OUTPUT_PATH}")
