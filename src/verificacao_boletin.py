import os
import re
from pathlib import Path
from datetime import datetime
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# --- CAMINHO RAIZ DA REDE ---
CAMINHO_RAIZ_REDE = r"M:\001 - Vistorias de Campo"

# Correção ortográfica
vistorias = {
    "manual"   : "Manual"  ,
    "mecânico" : "Mecânico",
    "mecanico" : "Mecânico",
}

def listar_rhs_disponiveis(caminho_base):
    """Detecta automaticamente as pastas de RHs existentes no servidor."""
    if not os.path.exists(caminho_base):
        return []
    rhs = []
    try:
        with os.scandir(caminho_base) as entradas:
            for entrada in entradas:
                if entrada.is_dir():
                    rhs.append(entrada.name)
    except Exception as e:
        print(f"Erro ao listar RHs: {e}")
    return sorted(rhs)

def obter_periodo_mais_recente(caminho_rh):
    """Localiza o período mais recente na pasta da RH."""
    padrao_data = re.compile(r'\d{2}\.\d{2}\.\d{4} a (\d{2}\.\d{2}\.\d{4})')
    periodos = []
    try:
        with os.scandir(caminho_rh) as entradas:
            for entrada in entradas:
                if entrada.is_dir():
                    match = padrao_data.search(entrada.name)
                    if match:
                        data_fim = datetime.strptime(match.group(1), "%d.%m.%Y")
                        periodos.append((data_fim, entrada.name))
    except Exception:
        return None

    if not periodos:
        return None

    periodos.sort(key=lambda item: item[0], reverse=True)
    return periodos[0][1]

def buscar_pasta_boletim(caminho_corpo_hidrico):
    """Localiza a subpasta de boletins (Boletim, Boletins, BTV, etc.) dentro de 'Município - Corpo Hídrico'."""
    # Adicione aqui qualquer outra nomenclatura de pasta que encontrar na rede
    termos_aceitos = ["boletim", "boletins", "btv", "BTV", "bvp", "BVP"]

    try:
        with os.scandir(caminho_corpo_hidrico) as sub_entradas:
            for item in sub_entradas:
                if item.is_dir():
                    nome_lower = item.name.lower()
                    # Verifica se o nome da pasta contém algum dos termos aceitos
                    if any(termo in nome_lower for termo in termos_aceitos):
                        return item.path
    except Exception:
        pass
    return None

def listar_boletins_pdfs(caminho_base, pasta_rh_nome, tipo_vistoria):
    caminho_rh = os.path.join(caminho_base, pasta_rh_nome)
    if not os.path.exists(caminho_rh):
        return None, f"Pasta da RH '{pasta_rh_nome}' não foi encontrada.", None

    periodo = obter_periodo_mais_recente(caminho_rh)
    if not periodo:
        return None, f"Nenhum período de vistoria encontrado em '{pasta_rh_nome}'.", None

    caminho_periodo = Path(caminho_rh) / periodo
    caminho_alvo =None
    tipo_normalizado = vistorias.get(tipo_vistoria.lower(), tipo_vistoria)  # Padrão "Mecânico")
    
    if caminho_periodo.exists():
        for subpasta in caminho_periodo.iterdir():
            if subpasta.is_dir():
                if vistorias.get(subpasta.name.lower()) == tipo_normalizado:
                    caminho_alvo = subpasta
                    break
    if not caminho_alvo or not caminho_alvo.exists():
        return (
            None,
            (
                f"Caminho da vistoria '{tipo_vistoria}' não existe em:\n"
                f"{caminho_periodo}"
            ),
            periodo,)


    resultados = []

    with os.scandir(caminho_alvo) as entradas:
        for entrada in entradas:
            if entrada.is_dir() and " - " in entrada.name:
                municipio, corpo_hidrico = entrada.name.split(" - ", 1)
                pasta_boletim = buscar_pasta_boletim(entrada.path)
                lista_pdfs = []

                if pasta_boletim and os.path.exists(pasta_boletim):
                    # --- NÃO RECURSIVO: Lê APENAS arquivos diretos na raiz da pasta Boletim ---
                    with os.scandir(pasta_boletim) as arquivos_boletim:
                        for item in arquivos_boletim:
                            # Garante que é ARQUIVO (ignora subpastas como 'PDFs') e que termina em .pdf
                            if item.is_file() and item.name.lower().endswith('.pdf'):
                                lista_pdfs.append(item.name)
                    
                    lista_pdfs.sort()

                resultados.append({
                    "RH": pasta_rh_nome,
                    "Tipo de Vistoria": tipo_vistoria,
                    "Município": municipio.strip(),
                    "Corpo Hídrico": corpo_hidrico.strip(),
                    "Qt": len(lista_pdfs),
                    "Nomes dos Arquivos": " | ".join(lista_pdfs) if lista_pdfs else "Nenhum PDF na pasta Boletim"
                })

    return pd.DataFrame(resultados), None, periodo


class AplicacaoVerificacaoBoletins:
    def __init__(self, root):
        self.root = root
        self.root.title("Verificação de Boletins de Vistoria")
        self.root.geometry("1150x700")

        self.df_atual = None

        # --- PAINEL SUPERIOR: CONTROLES DE SELEÇÃO (LISTAS SUSPENSAS) ---
        frame_controles = ttk.LabelFrame(self.root, text=" ⚙️ Opções de Seleção ")
        frame_controles.pack(fill=tk.X, padx=10, pady=10)

        # Seleção de RH
        ttk.Label(frame_controles, text="Região Hidrográfica (RH):", font=("Calibri", 10, "bold")).grid(row=0, column=0, padx=8, pady=10, sticky=tk.W)
        self.cb_rh = ttk.Combobox(frame_controles, state="readonly", width=30)
        self.cb_rh.grid(row=0, column=1, padx=8, pady=10)

        # Seleção do Tipo de Vistoria
        ttk.Label(frame_controles, text="Tipo de Vistoria:", font=("Calibri", 10, "bold")).grid(row=0, column=2, padx=8, pady=10, sticky=tk.W)
        self.cb_vistoria = ttk.Combobox(frame_controles, values=["Manual", "Mecânico"], state="readonly", width=15)
        self.cb_vistoria.set("Manual")
        self.cb_vistoria.grid(row=0, column=3, padx=8, pady=10)

        # Botão de Consulta
        btn_buscar = ttk.Button(frame_controles, text="Consultar", command=self.executar_consulta)
        btn_buscar.grid(row=0, column=4, padx=15, pady=10)

        # Rótulo com o período encontrado
        self.lbl_periodo = ttk.Label(frame_controles, text="Período: -", font=("Calibri", 10, "italic"))
        self.lbl_periodo.grid(row=0, column=5, padx=10, pady=10, sticky=tk.W)

        # Carrega a lista de RHs
        self.carregar_rhs()

        # --- PAINEL DIVIDIDO (TABELA E DETALHES) ---
        paned = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Tabela Superior
        frame_tabela = ttk.Frame(paned)
        paned.add(frame_tabela, weight=3)

        scroll_y = ttk.Scrollbar(frame_tabela, orient=tk.VERTICAL)
        scroll_x = ttk.Scrollbar(frame_tabela, orient=tk.HORIZONTAL)

        self.colunas = ["RH", "Tipo de Vistoria", "Município", "Corpo Hídrico", "Qt", "Nomes dos Arquivos"]
        self.tabela = ttk.Treeview(
            frame_tabela, 
            columns=self.colunas, 
            show="headings", 
            yscrollcommand=scroll_y.set, 
            xscrollcommand=scroll_x.set
        )

        scroll_y.config(command=self.tabela.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.config(command=self.tabela.xview)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tabela.pack(fill=tk.BOTH, expand=True)

        larguras = {"RH": 130, "Tipo de Vistoria": 120, "Município": 150, "Corpo Hídrico": 180, "Qt": 50, "Nomes dos Arquivos": 480}
        for col in self.colunas:
            self.tabela.heading(col, text=col)
            alinhamento = tk.CENTER if col in ["Qt", "RH", "Tipo de Vistoria"] else tk.W
            self.tabela.column(col, width=larguras.get(col, 150), anchor=alinhamento)

        # Painel Inferior de Detalhes
        frame_detalhes = ttk.LabelFrame(paned, text=" 📄 Lista Detalhada dos Arquivos do Local Selecionado ")
        paned.add(frame_detalhes, weight=2)

        scroll_txt = ttk.Scrollbar(frame_detalhes, orient=tk.VERTICAL)
        self.txt_detalhes = tk.Text(frame_detalhes, yscrollcommand=scroll_txt.set, wrap=tk.WORD, font=("Consolas", 10))
        scroll_txt.config(command=self.txt_detalhes.yview)
        scroll_txt.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_detalhes.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.txt_detalhes.insert(tk.END, "Selecione a RH, o Tipo de Vistoria e clique em 'Consultar'...")

        self.tabela.bind("<<TreeviewSelect>>", self.ao_selecionar_linha)

        # Botão de Exportar para Excel
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        btn_exportar = ttk.Button(btn_frame, text="📊 Exportar para Excel", command=self.exportar_excel)
        btn_exportar.pack(side=tk.RIGHT)

    def carregar_rhs(self):
        rhs = listar_rhs_disponiveis(CAMINHO_RAIZ_REDE)
        if rhs:
            self.cb_rh['values'] = rhs
            self.cb_rh.set(rhs[0])
        else:
            self.cb_rh['values'] = ["Caminho não encontrado"]

    def executar_consulta(self):
        rh = self.cb_rh.get()
        tipo = self.cb_vistoria.get()

        if not rh or rh == "Caminho não encontrado":
            messagebox.showwarning("Aviso", "Selecione uma RH válida.")
            return

        df_res, erro, periodo = listar_boletins_pdfs(CAMINHO_RAIZ_REDE, rh, tipo)

        if erro:
            messagebox.showerror("Erro na Consulta", erro)
            self.lbl_periodo.config(text="Período: Não encontrado")
            return

        self.lbl_periodo.config(text=f"Período: {periodo}")
        self.df_atual = df_res

        # Limpa tabela anterior
        for item in self.tabela.get_children():
            self.tabela.delete(item)

        # Preenche com os novos dados
        for _, linha in df_res.iterrows():
            self.tabela.insert("", tk.END, values=[linha[col] for col in self.colunas])

        self.txt_detalhes.delete("1.0", tk.END)
        self.txt_detalhes.insert(tk.END, "Clique em uma linha da tabela acima para ver os arquivos em detalhes...")

    def ao_selecionar_linha(self, event):
        item_selecionado = self.tabela.selection()
        if not item_selecionado:
            return

        valores = self.tabela.item(item_selecionado[0], "values")
        tipo_vist, municipio, corpo_hidrico, qt, arquivos_str = valores[1], valores[2], valores[3], valores[4], valores[5]

        self.txt_detalhes.delete("1.0", tk.END)
        self.txt_detalhes.insert(tk.END, f"VISTORIA: {tipo_vist.upper()} | MUNICÍPIO: {municipio} | CORPO HÍDRICO: {corpo_hidrico} | TOTAL: {qt} PDF(s)\n")
        self.txt_detalhes.insert(tk.END, "-" * 90 + "\n\n")

        if arquivos_str and "Nenhum PDF" not in arquivos_str:
            lista_arquivos = arquivos_str.split(" | ")
            for idx, arq in enumerate(lista_arquivos, start=1):
                self.txt_detalhes.insert(tk.END, f"{idx:02d}. {arq}\n")
        else:
            self.txt_detalhes.insert(tk.END, "Nenhum arquivo PDF encontrado na pasta Boletim.")

    def exportar_excel(self):
        if self.df_atual is None or self.df_atual.empty:
            messagebox.showwarning("Aviso", "Não há dados para exportar. Faça uma consulta primeiro.")
            return

        caminho_salvar = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Planilha do Excel", "*.xlsx")],
            title="Salvar como Excel"
        )
        if caminho_salvar:
            self.df_atual[self.colunas].to_excel(caminho_salvar, index=False)
            messagebox.showinfo("Sucesso", f"Relatório salvo com sucesso em:\n{caminho_salvar}")


# --- EXECUÇÃO ---
if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacaoVerificacaoBoletins(root)
    root.mainloop()
