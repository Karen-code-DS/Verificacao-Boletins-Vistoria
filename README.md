# 📊 Verificação de Boletins de Vistoria

Aplicação Desktop com interface gráfica em Python para automação, e contagem de boletins de vistoria (PDFs) armazenados em servidor de rede, com recurso para exportação de relatórios em Excel.

---

## 📌 Descrição do Projeto

Este projeto automatiza a auditoria de arquivos de vistoria técnica dispostos no servidor local. A ferramenta varre a estrutura de diretórios das Regiões Hidrográficas (RHs), identifica a pasta com o período mais recente e contabiliza os boletins em formato PDF encontrados, permitindo a visualização clara em tabela e exportação simplificada dos dados.

---

## 🚀 Funcionalidades

- **Detecção Automática:** Localiza pastas de Regiões Hidrográficas (RH) dinamicamente na rede.
- **Identificação de Período Recente:** Utiliza Expressões Regulares (Regex) para encontrar e ordenar as subpastas de períodos (ex: `01_RH-I_2024-1`).
- **Mapeamento Flexível:** Busca por variações de nomenclaturas de subpastas (ex: `Boletim`, `Boletins`, `BTV`, `BVP`).
- **Interface Gráfica (GUI):** Exibição em tabela (`Treeview`) interativa com contagem detalhada de arquivos.
- **Painel Detalhado:** Exibição da lista individual de arquivos PDF encontrados por seleção de linha.
- **Exportação de Relatórios:** Geração instantânea de planilhas Excel (`.xlsx`).

---

## 🛠️ Tecnologias Utilizadas

- **[Python 3.x](https://www.python.org/):** Linguagem base da aplicação.
- **[Tkinter](https://docs.python.org/3/library/tkinter.html):** Criação da interface gráfica do usuário (GUI).
- **[Pandas](https://pandas.pydata.org/):** Manipulação, consolidação e exportação dos dados.
- **[OpenPyXL](https://openpyxl.readthedocs.io/):** Suporte para salvar e formatar relatórios em formato Excel (`.xlsx`).

---

## 📋 Pré-requisitos
- ** Ter o Python 3.8+ instalado.
- ** Acesso à unidade de rede configurada (Mapeamento padrão: M:\001 - Vistorias de Campo).

---

## 📂 Estrutura do Repositório

```text
verificacao-boletins-vistoria/
│
├── src/
│   └── verificacao_boletin.py   # Código-fonte principal da aplicação
│
├── .gitignore                   # Arquivos ignorados pelo controle de versão
├── README.md                    # Documentação do projeto
└── requirements.txt             # Dependências da aplicação 


