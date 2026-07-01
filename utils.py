import base64
import csv
import io
import unicodedata
from pathlib import Path
from difflib import SequenceMatcher
from itertools import groupby

import streamlit as st
from PIL import Image

# Constantes do Sistema
MARCAS = [
    "Eudora", "O Boticário", "Jequiti", "Avon", "Mary Kay", "Natura", 
    "Oui-Original-Unique-Individuel", "Pierre Alexander", "Tupperware", "Pierre-cosmeticos", "Quem Disse Berenice","Outra"
]

ESTILOS = [
    "Perfumaria", "Skincare", "Cabelo", "Corpo e Banho", "Make", "Masculinos", 
    "Femininos Nina Secrets", "Marcas", "Infantil", "Casa", "Solar", "Maquiage", 
    "Teen", "Kits e Presentes", "Cuidados com o Corpo", "Lançamentos", 
    "Acessórios de Casa", "Outro"
]

TIPOS = [
    "Perfumaria masculina", "Perfumaria feminina", "Body splash", "Body spray", 
    "Eau de parfum", "Desodorantes", "Perfumaria infantil", "Perfumaria vegana", 
    "Família olfativa", "Clareador de manchas", "Anti-idade", "Protetor solar facial", 
    "Rosto", "Tratamento para o rosto", "Acne", "Limpeza", "Esfoliante", "Tônico facial", 
    "Kits de tratamento", "Tratamento para cabelos", "Shampoo", "Condicionador", 
    "Leave-in e Creme para Pentear", "Finalizador", "Modelador", "Acessórios", 
    "Kits e looks", "Boca", "Olhos", "Pincis", "Paleta", "Unhas", "Sobrancelhas", 
    "Hidratante", "Cuidados pós-banho", "Cuidados para o banho", "Barba", "Óleo corporal", 
    "Cuidados íntimos", "Unissex", "Bronzeamento", "Protetor solar", "Depilação", 
    "Mãos", "Lábios", "Pés", "Pés sol", "Protetor solar corporal", "Colônias", 
    "Estojo", "Sabonetes", "Sabonete líquido", "Sabonete em barra", 
    "Creme hidratante para as mãos", "Creme hidratante para os pés", "Miniseries", 
    "Kits de perfumes", "Antissinais", "Máscara", "Creme bisnaga", 
    "Roll On Fragrânciado", "Roll On On Duty", "Shampoo 2 em 1", "Spray corporal", 
    "Booster de Tratamento", "Creme para Pentear", "Óleo de Tratamento", 
    "Pré-shampoo", "Sérum de Tratamento", "Shampoo e Condicionador", "Garrafas", 
    "Armazenamentos", "Micro-ondas", "Servir", "Preparo", "Lazer/Outdoor", 
    "Presentes", "Outro"
]

# Paleta de Cores
COLOR_BG = "#E9E9E9"
COLOR_TEXT_SMALL = "#2D2D2D"
COLOR_TEXT_LARGE_1 = "#B57D0A"
COLOR_TEXT_LARGE_2 = "#2D2D2D"


def get_product_image_source(product_row):
    """
    Returns the image source for st.image.
    Fetches directly from database blob to ensure persistence.
    Ignores local file system to avoid issues with ephemeral storage (Streamlit Cloud).
    """
    img_data = product_row.get('image')
    
    # Se houver dados e forem bytes não vazios
    if img_data is not None and isinstance(img_data, bytes) and len(img_data) > 0:
        return io.BytesIO(img_data)
        
    return None



def ensure_directories():
    """Garante que diretórios essenciais existam"""
    try:
        Path("assets").mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Erro ao criar diretórios: {e}")

def apply_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Great+Vibes&family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&display=swap');

        html, body, .stApp {
            background-color: #E9E9E9 !important;
        }
        .stApp, .stApp p, .stApp span, .stApp div, .stApp input, .stApp textarea, .stApp select {
            font-family: 'Playfair Display', serif;
            color: #2D2D2D;
        }

        h1, h2, h3, h4, h5, h6, strong, b, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
            font-family: 'Playfair Display', serif;
            color: #B57D0A;
            text-align: center;
        }

        .stMarkdown, .stText, .stMetric {
            text-align: center;
        }

        .stButton>button,
        div[data-testid="baseButton-secondary"] button {
            display: block;
            margin-left: auto;
            margin-right: auto;
        }

        .st-emotion-cache-hzygls,
        .st-emotion-cache-4man113,
        div[data-testid="stStatusContainer"],
        div[data-testid="stCacheContainer"] {
            background-color: #F3E06A !important;
            color: #2D2D2D !important;
            padding: 5px;
            border-radius: 3px;
        }

        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }

        ::-webkit-scrollbar-track {
            background: #F3E06A; /* Amarelo-suave */
            border-radius: 10px;
        }

        ::-webkit-scrollbar-thumb {
            background: #C9981A; /* Dourado */
            border-radius: 10px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #B57D0A; /* Dourado escuro */
        }

        * {
            scrollbar-color: #C9981A #F3E06A;
            scrollbar-width: thin;
        }

        *::-moz-scrollbar-thumb:hover {
            background: #B57D0A;
        }

        header,
        header.st-emotion-cache-18nibws,
        header.st-emotion-cache-1rq341t,
        header.st-emotion-cache-1l02z8d,
        div[data-testid="stHeader"] {
            background-color: #F3E06A !important;
        }

        footer,
        div[data-testid="stFooter"] {
            background-color: #F3E06A !important;
            color: #2D2D2D !important;
        }
        footer a,
        div[data-testid="stFooter"] a {
            color: #C9981A !important;
        }

        .stSidebar,
        .stSidebar > div:first-child,
        div[data-testid="stSidebar"] {
            background-color: #F3E06A !important;
        }
        .stSidebar .stMarkdown, .stSidebar .stSelectbox label,
        .stSidebar p, .stSidebar span {
            color: #2D2D2D !important;
        }

        .stSidebar nav ul li a, .stSidebar nav ul li div[role="button"],
        div[data-testid="stVerticalNav"] li a {
            background-color: #FFFFFF !important;
            color: #2D2D2D !important;
        }
        .stSidebar nav ul li a:hover, .stSidebar nav ul li div[role="button"]:hover,
        div[data-testid="stVerticalNav"] li a:hover {
            background-color: #EBCB34 !important;
            color: #FFFFFF !important;
        }
        .stSidebar nav ul li a[aria-current="page"], .stSidebar nav ul li div[aria-selected="true"],
        div[data-testid="stVerticalNav"] li a[aria-current="page"] {
            background-color: #EBCB34 !important;
            color: #FFFFFF !important;
            font-weight: bold;
        }

        div[data-testid="stMainMenu"] {
            background-color: #F3E06A !important;
        }
        div[data-testid="stMainMenu"] button, div[data-testid="stMainMenu"] div {
            color: #2D2D2D !important;
            background-color: #F3E06A !important;
        }
        div[data-testid="stMainMenu"] button:hover, div[data-testid="stMainMenu"] div:hover {
            background-color: #EBCB34 !important;
            color: #FFFFFF !important;
        }

        .stForm {
            background-color: #FFFFFF;
            border: 1px solid #C9981A;
            padding: 10px;
            border-radius: 5px;
        }

        .stTextInput>div>div>input,
        .stNumberInput>div>div>input,
        .stDateInput>div>div>input,
        .stTextArea>div>div>textarea,
        .stSelectbox div[data-baseweb="select"] div[role="button"],
        .stTextInput input, .stNumberInput input, .stDateInput input, .stTextArea textarea,
        div[data-testid="stSelectbox"] div[role="button"] {
            background-color: #FFFFFF !important;
            color: #2D2D2D !important;
            border-color: #C9981A !important;
            
            -webkit-appearance: none;
            -moz-appearance: none;
            appearance: none;
            -webkit-transition: border-color 0.3s ease, box-shadow 0.3s ease;
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
        }

        .stTextInput>div>div>input:focus,
        .stNumberInput>div>div>input:focus,
        .stDateInput>div>div>input:focus,
        .stTextArea>div>div>textarea:focus,
        .stTextInput input:focus, .stNumberInput input:focus, .stDateInput input:focus, .stTextArea textarea:focus {
            border-color: #B57D0A !important;
            
            -webkit-box-shadow: 0 0 0 1px #B57D0A !important;
            -moz-box-shadow: 0 0 0 1px #B57D0A !important;
            box-shadow: 0 0 0 1px #B57D0A !important;
            
            outline: none !important;
        }

        .stChatInputContainer,
        div[data-testid="stChatInput"] {
            background-color: #F3E06A !important;
            border-top: 1px solid #C9981A;
            padding: 10px 0;
        }
        .stChatInputContainer input,
        div[data-testid="stChatInput"] input {
            background-color: #FFFFFF !important;
            color: #2D2D2D !important;
            border-color: #C9981A !important;
        }
        .stChatInputContainer button svg,
        div[data-testid="stChatInput"] button svg {
            fill: #B57D0A !important;
        }
        .stChatInputContainer button,
        div[data-testid="stChatInput"] button {
            background-color: #F3E06A !important;
            border-color: #C9981A !important;
        }
        .stChatInputContainer button:hover,
        div[data-testid="stChatInput"] button:hover {
            background-color: #EBCB34 !important;
        }

        .stButton>button,
        div[data-testid="baseButton-secondary"] button {
            background-color: #EBCB34;
            color: #FFFFFF;
            border-color: #B57D0A;
            
            -webkit-transition: all 0.2s ease-in-out;
            transition: all 0.2s ease-in-out;
        }
        .stButton>button:hover,
        div[data-testid="baseButton-secondary"] button:hover {
            background-color: #B57D0A !important;
            color: #FFFFFF !important;
            border-color: #B57D0A !important;
        }
        </style>
    """, unsafe_allow_html=True)

from fpdf import FPDF


def _normalize_text(value):
    text = "" if value is None else str(value)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return text.lower().strip()


def filter_products(products, query):
    """
    Busca inteligente com:
    - normalização de acentos e caixa
    - múltiplos termos
    - tolerância a pequenos erros de digitação
    - ordenação por relevância
    """
    if not products or not query:
        return products

    tokens = [t for t in _normalize_text(query).split() if t]
    if not tokens:
        return products

    weighted_cols = [
        ("name", 4.0),
        ("brand", 3.0),
        ("type", 3.0),
        ("style", 2.0),
        ("id", 1.5),
        ("expiration_date", 1.0),
        ("price", 0.8),
        ("quantity", 0.8),
    ]

    def token_score_in_text(token, text):
        if not text:
            return 0.0
        if token == text:
            return 1.0
        if token in text:
            return min(0.95, 0.60 + (len(token) / max(len(text), len(token))) * 0.35)

        words = text.split()
        if not words:
            return 0.0
        best = 0.0
        for word in words:
            ratio = SequenceMatcher(None, token, word).ratio()
            if ratio > best:
                best = ratio
        return best if best >= 0.74 else 0.0

    scored = []
    for row in products:
        row_score = 0.0
        token_hits = 0
        for token in tokens:
            best_token_score = 0.0
            for col, weight in weighted_cols:
                raw = token_score_in_text(token, _normalize_text(row.get(col, "")))
                weighted = raw * weight
                if weighted > best_token_score:
                    best_token_score = weighted
            if best_token_score > 0:
                token_hits += 1
                row_score += best_token_score

        if token_hits == len(tokens):
            row_score += 1.2

        if token_hits >= 1 and row_score > 0:
            scored.append((row_score, row))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [row for _, row in scored]


def process_image(image_source):
    """
    Processa imagem vinda de caminho local, bytes ou arquivo-like para exibição no Streamlit.
    """
    try:
        if image_source is None:
            return None
        if isinstance(image_source, (bytes, bytearray)):
            return Image.open(io.BytesIO(image_source))
        if hasattr(image_source, "read"):
            return Image.open(image_source)
        return Image.open(str(image_source))
    except Exception:
        return None

def paginate_dataframe(df, key_prefix, page_size=24):
    """
    Pagina uma lista de registros para reduzir tempo de renderização no Streamlit.
    Retorna (recortes, total_paginas, pagina_atual_1_based).
    """
    if not df:
        return df, 1, 1

    total_items = len(df)
    total_pages = max(1, (total_items + page_size - 1) // page_size)
    page = st.number_input(
        "Página",
        min_value=1,
        max_value=total_pages,
        value=1,
        step=1,
        key=f"{key_prefix}_page",
    )

    start = (page - 1) * page_size
    end = start + page_size
    return df[start:end], total_pages, page


def generate_pdf(products_df, sales_summary_df=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    def clean_text(text):
        try:
            return str(text).encode("latin-1", "replace").decode("latin-1")
        except Exception:
            return "?"

    pdf.cell(200, 10, txt=clean_text("Relatório Completo de Produtos"), ln=1, align="C")
    pdf.set_font("Arial", size=9)
    pdf.cell(200, 8, txt=clean_text("Listagem por tipo com características"), ln=1, align="C")
    pdf.ln(4)

    def write_wrapped(text, line_size=95):
        safe = clean_text(text)
        chunks = [safe[i:i + line_size] for i in range(0, len(safe), line_size)] or [""]
        for chunk in chunks:
            pdf.cell(0, 6, txt=chunk, ln=1)

    if not products_df:
        pdf.set_font("Arial", size=11)
        pdf.cell(0, 8, txt=clean_text("Nenhum produto cadastrado."), ln=1)
    else:
        sold_map = {}
        if sales_summary_df:
            for sale_row in sales_summary_df:
                try:
                    sold_map[int(sale_row.get("product_id"))] = int(sale_row.get("sold_quantity") or 0)
                except Exception:
                    continue

        ordered_df = sorted(
            products_df,
            key=lambda row: (
                clean_text(row.get("type", "")) or "zzzz",
                clean_text(row.get("brand", "")) or "zzzz",
                clean_text(row.get("name", "")) or "zzzz",
            ),
        )

        def type_key(row):
            value = row.get("type")
            return value if value is not None and str(value).strip() else "Sem tipo"

        for product_type, group in groupby(ordered_df, key=type_key):
            type_label = clean_text(product_type if product_type else "Sem tipo")
            pdf.set_font("Arial", "B", 11)
            pdf.multi_cell(0, 8, txt=f"Tipo: {type_label}")
            pdf.set_font("Arial", size=10)

            for row in group:
                product_id = row.get("id", 0)
                try:
                    sold_qty = int(sold_map.get(int(product_id), 0))
                except Exception:
                    sold_qty = 0
                sold_status = "Sim" if sold_qty > 0 else "Nao"

                line = (
                    f"ID: {row.get('id', '')} | Nome: {clean_text(row.get('name', ''))} | "
                    f"Marca: {clean_text(row.get('brand', ''))} | Estilo: {clean_text(row.get('style', ''))}"
                )
                line2 = (
                    f"Preco: R$ {row.get('price', 0)} | Estoque: {row.get('quantity', 0)} | "
                    f"Validade: {clean_text(row.get('expiration_date', ''))} | Vendido: {sold_status} | Qtd vendida: {sold_qty}"
                )
                write_wrapped(line)
                write_wrapped(line2)
                pdf.ln(1)

            pdf.ln(2)

    try:
        output = pdf.output(dest="S")
        return output.encode("latin-1", "replace") if isinstance(output, str) else bytes(output)
    except Exception:
        return b""

def convert_df_to_csv(df):
    rows = df or []
    if not rows:
        return "".encode("utf-8")

    output = io.StringIO()
    fieldnames = list(rows[0].keys())
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for row in rows:
        cleaned = {}
        for key in fieldnames:
            value = row.get(key)
            if isinstance(value, bytes):
                cleaned[key] = base64.b64encode(value).decode("utf-8")
            else:
                cleaned[key] = value
        writer.writerow(cleaned)

    return output.getvalue().encode("utf-8")
