import os
import tempfile
from datetime import datetime
from collections import Counter

import pandas as pd
import webview

class API:
    def get_file_type(self, extension):
        ALLOWED_EXTENSIONS = {
            'Documento': {'.pdf', '.doc', '.docx', '.txt', '.odt'},
            'Planilha': {'.xls', '.xlsx', '.csv', '.ods'},
            'Imagem': {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'},
            'Executável': {'.exe', '.msi', '.dmg', '.sh'},
            'Compactado': {'.zip', '.rar', '.7z', '.tar.gz'}
        }
        for tipo, exts in ALLOWED_EXTENSIONS.items():
            if extension in exts:
                return tipo
        return "Outro"

    def analisar(self, path):
        try:
            counter = Counter()
            subdir_stats = Counter()
            main_dir_stats = Counter()
            file_details = []

            if not os.path.isdir(path):
                return {"status": "error", "message": f"O caminho {path} não é um diretório válido."}

            for root, _, files in os.walk(path):
                rel_path = os.path.relpath(root, path)
                main_dir = rel_path.split(os.sep)[0] if os.sep in rel_path else rel_path

                for file in files:
                    if file.startswith(('~', '.')):
                        continue
                    ext = os.path.splitext(file)[1].lower()
                    tipo = self.get_file_type(ext)
                    counter[(ext or "(sem extensão)", tipo)] += 1
                    subdir_stats[rel_path] += 1
                    main_dir_stats[main_dir] += 1
                    file_details.append({
                    "Arquivo": file,
                    "Caminho": os.path.join(root, file),
                    "Extensão": ext,
                    "Tipo": tipo
                })

            dfs = {
                'Resumo por Tipo': pd.DataFrame(
                    [{"Extensão": ext, "Tipo": tipo, "Quantidade": qtd}
                    for (ext, tipo), qtd in sorted(counter.items())]
                ),
                'Subpastas Detalhadas': pd.DataFrame(
                    [{"Subpasta": sub, "Arquivos": qtd}
                    for sub, qtd in sorted(subdir_stats.items())]
                ),
                'Total por Pasta': pd.DataFrame(
                    [{"Pasta": main, "Arquivos": qtd}
                    for main, qtd in sorted(main_dir_stats.items())]
                ),
                'Detalhes dos Arquivos': pd.DataFrame(file_details)
            }

            report_name = f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            temp_path = os.path.join(tempfile.gettempdir(), report_name)

            with pd.ExcelWriter(temp_path, engine='openpyxl') as writer:
                for name, df in dfs.items():
                    df.to_excel(writer, sheet_name=name, index=False)

            return {"status": "success", "file": temp_path}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def ler_relatorio(self, path):
        try:
            with open(path, "rb") as f:
                return {"status": "success", "data": f.read().hex()}
        except Exception as e:
            return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    api = API()
    webview.create_window("Contador de Arquivos", "index.html", js_api=api, width=600, height=600)
    webview.start()
