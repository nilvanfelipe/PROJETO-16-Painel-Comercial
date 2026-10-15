import zipfile

with zipfile.ZipFile(r"c:\Users\Nilvan\Documents\07 - PROJETOS\01 - PROJETOS POWER BI\PROJETO 16 - Painel Comercial\PROJETO 16 - Painel Comercial.pbix") as z:
    dm = z.read("DataModel")
    print(f"DataModel total size: {len(dm)} bytes")
    
    terms = [b"Faturamento", b"Ticket", b"Atingimento", b"Cresc", b"Medidas", b"fMetas", b"fDevolu", b"dCalendario", b"dProduto"]
    for t in terms:
        # Search ascii
        pos_ascii = dm.find(t)
        # Search utf-16le
        t_u16 = t.decode("latin-1").encode("utf-16-le")
        pos_u16 = dm.find(t_u16)
        print(f"Term '{t.decode('latin-1')}': ascii={pos_ascii}, utf16={pos_u16}")
