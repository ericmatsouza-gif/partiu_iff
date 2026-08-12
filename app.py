# ══════════════════════════════════════════════════════════════════════════════
# PREPARATÓRIO ESCOLAS TÉCNICAS — v2
# Abas: Questões por Prova | Simulados | Tirar Dúvidas | Lista de Exercícios
# Modelo: gemini-3.5-flash-lite
# ══════════════════════════════════════════════════════════════════════════════
import os, re, io, random, requests, tempfile
import streamlit as st
from google import genai
from google.genai import types
from google.genai.errors import APIError
from fpdf import FPDF, XPos, YPos

MODELO = "gemini-3.5-flash-lite"

# ── CONFIGURAÇÃO DA PÁGINA ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Prep. Escolas Técnicas | Prof. Eric",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
.stButton>button {
    width: 100%;
    background-color: #2980b9;
    color: white;
    font-weight: bold;
    height: 3.2em;
    border-radius: 8px;
    border: none;
    font-size: 16px;
}
.stButton>button:hover { background-color: #1f6391; color: white; }
.badge-prova {
    display: inline-block;
    background: #2980b9;
    color: white;
    border-radius: 12px;
    padding: 2px 10px;
    font-size: 0.78rem;
    font-weight: bold;
    margin-right: 4px;
}
.footer {
    margin-top: 50px;
    padding-top: 20px;
    border-top: 1px solid #e0e0e0;
    text-align: center;
    font-size: 0.85rem;
    color: #7f8c8d;
}
.author-name-sidebar { margin-top: -0.8rem; }

@media (min-width: 768px) {
    section[data-testid="stSidebar"] {
        min-width: 320px !important; max-width: 320px !important;
    }
}
@media (max-width: 767px) {
    section[data-testid="stSidebar"] {
        transform: translateX(-110%) !important;
        position: fixed !important; top: 0 !important; left: 0 !important;
        height: 100vh !important; width: 80vw !important;
        min-width: unset !important; max-width: 85vw !important;
        z-index: 9999 !important; transition: transform 0.3s ease !important;
    }
    section[data-testid="stSidebar"][aria-expanded="true"] {
        transform: translateX(0%) !important;
    }
    .main { margin-left: 0 !important; width: 100vw !important; }
    .main .block-container {
        padding-left: 1rem !important; padding-right: 1rem !important;
        padding-top: 1rem !important; max-width: 100% !important; width: 100% !important;
    }
    div[data-testid="column"] {
        width: 100% !important; flex: 1 1 100% !important; min-width: 100% !important;
    }
    .stButton>button { height: 3.6em !important; font-size: 1rem !important; }
    .stTabs [data-baseweb="tab"] { font-size: 0.85rem !important; padding: 0.4rem 0.6rem !important; }
    h1 { font-size: 1.4rem !important; }
}
div[data-testid="stSidebarUserContent"] { padding-top: 1rem !important; }
section[data-testid="stSidebar"] h1:first-of-type { margin-top: 0 !important; padding-top: 0 !important; }
button[data-testid="stSidebarCollapseButton"],
div[data-testid="stSidebarHeader"] { z-index: 999999 !important; position: relative !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# DADOS: PROVAS E CONTEÚDOS
# ══════════════════════════════════════════════════════════════════════════════

PROVAS = {
    "IFF (Instituto Federal Fluminense)": {
        "emoji": "🏛️",
        "disciplinas": {
            "Matemática": [
                "Números e operações (inteiros, racionais, irracionais)",
                "Potenciação e radiciação",
                "Frações e porcentagem",
                "Razão, proporção e regra de três",
                "Equação do 1º grau",
                "Equação do 2º grau",
                "Sistemas de equações",
                "Geometria plana (áreas e perímetros)",
                "Geometria espacial (volume e área de sólidos)",
                "Trigonometria básica",
                "Estatística e probabilidade",
                "Progressão aritmética (PA)",
                "Progressão geométrica (PG)",
                "Funções (1º e 2º graus)",
            ],
            "Português": [
                "Interpretação de texto",
                "Gêneros textuais",
                "Ortografia e acentuação",
                "Classes de palavras",
                "Análise sintática básica",
                "Concordância verbal e nominal",
                "Regência verbal e nominal",
                "Crase",
                "Pontuação",
                "Figuras de linguagem",
                "Coesão e coerência textual",
                "Produção textual (dissertação e narrativa)",
            ],
            "Ciências": [
                "Célula e tecidos",
                "Genética básica",
                "Ecologia e ecossistemas",
                "Química: reações e substâncias",
                "Física: grandezas e medidas",
                "Física: força e movimento",
                "Corpo humano: sistemas",
                "Biotecnologia básica",
            ],
            "Geografia": [
                "Cartografia e leitura de mapas",
                "Geomorfologia brasileira",
                "Clima e vegetação do Brasil",
                "Regiões brasileiras",
                "Urbanização e industrialização",
                "Globalização e geopolítica",
                "Problemas ambientais",
                "Energia e recursos naturais",
            ],
            "História": [
                "Brasil Colônia",
                "Brasil Império",
                "República Velha",
                "Era Vargas",
                "Ditadura Militar",
                "Redemocratização",
                "Primeira e Segunda Guerras Mundiais",
                "Revolução Industrial",
                "Revolução Francesa",
                "Movimentos sociais no Brasil",
            ],
        },
    },
    "IFRJ (Instituto Federal do Rio de Janeiro)": {
        "emoji": "🔬",
        "disciplinas": {
            "Matemática": [
                "Conjuntos numéricos",
                "Operações com frações",
                "Equações e inequações",
                "Funções do 1º e 2º graus",
                "Geometria analítica básica",
                "Grandezas proporcionais",
                "Estatística descritiva",
                "Combinatória e probabilidade",
                "Polígonos e círculos",
                "Volumes de sólidos geométricos",
                "Expressões algébricas",
                "Sequências e padrões numéricos",
            ],
            "Português": [
                "Compreensão e interpretação textual",
                "Variação linguística",
                "Formação de palavras",
                "Sintaxe da oração",
                "Semântica e figuras de linguagem",
                "Tipologia textual",
                "Ortografia (novo acordo ortográfico)",
                "Uso da vírgula e demais pontuações",
            ],
            "Ciências": [
                "Matéria e energia",
                "Seres vivos e classificação",
                "Evolução e hereditariedade",
                "Sistema solar e astronomia básica",
                "Química: mistura e substâncias puras",
                "Física: luz e som",
                "Saúde e prevenção de doenças",
            ],
            "História": [
                "Civilizações antigas",
                "Idade Média",
                "Colonização da América",
                "Independência do Brasil",
                "Brasil República",
                "Conflitos mundiais do século XX",
                "Direitos humanos e cidadania",
            ],
            "Geografia": [
                "Territorialidade e espaço geográfico",
                "Clima e biomas mundiais",
                "Hidrografia e relevo",
                "Geopolítica mundial",
                "Brasil no contexto global",
                "Questões ambientais contemporâneas",
            ],
        },
    },
    "CEFET-RJ": {
        "emoji": "⚙️",
        "disciplinas": {
            "Matemática": [
                "Operações fundamentais e propriedades",
                "Sistemas de numeração",
                "Divisibilidade e números primos",
                "Frações, decimais e porcentagem",
                "Razão, proporção e grandezas proporcionais",
                "Regra de três simples e composta",
                "Equações do 1º e 2º grau",
                "Sistemas de equações do 1º grau",
                "Funções: conceito, domínio e imagem",
                "Função afim e quadrática",
                "Geometria plana: polígonos e círculo",
                "Geometria espacial: prismas, pirâmides, cone, cilindro, esfera",
                "Trigonometria: razões no triângulo retângulo",
                "Estatística: média, mediana e moda",
                "Combinatória: fatorial, arranjos, combinações",
                "Probabilidade",
            ],
            "Português": [
                "Leitura e interpretação de textos variados",
                "Intertextualidade",
                "Funções da linguagem",
                "Morfologia completa",
                "Sintaxe: oração e período",
                "Concordância verbal e nominal",
                "Regência e crase",
                "Ortografia e acentuação gráfica",
                "Pontuação",
                "Redação: dissertação argumentativa",
                "Literatura brasileira (noções básicas)",
            ],
            "Ciências (Física e Química)": [
                "Introdução à Física: grandezas e unidades",
                "Cinemática: movimento uniforme e variado",
                "Dinâmica: força e 2ª Lei de Newton",
                "Trabalho e energia",
                "Termologia: temperatura e calor",
                "Óptica geométrica",
                "Eletricidade básica",
                "Substâncias e misturas",
                "Transformações físicas e químicas",
                "Ácidos, bases, sais e óxidos",
                "Tabela periódica básica",
                "Reações químicas",
            ],
            "História e Geografia": [
                "Formação do Estado moderno",
                "Brasil: período colonial ao imperial",
                "República brasileira: fases e transformações",
                "Geopolítica: blocos econômicos e conflitos",
                "Urbanização e industrialização brasileira",
                "Questões ambientais globais",
                "Direitos humanos e movimentos sociais",
                "Globalização e desigualdades",
            ],
        },
    },
    "SESI-SENAI RJ": {
        "emoji": "🏭",
        "disciplinas": {
            "Matemática": [
                "Operações e propriedades dos números",
                "Porcentagem e juros simples",
                "Regra de três aplicada ao cotidiano",
                "Equações do 1º grau",
                "Geometria: formas e medidas práticas",
                "Estatística: leitura de gráficos e tabelas",
                "Noções de probabilidade",
                "Proporcionalidade direta e inversa",
            ],
            "Português": [
                "Leitura e compreensão de textos do dia a dia",
                "Textos instrucionais e informativos",
                "Ortografia básica",
                "Gramática aplicada: sujeito e predicado",
                "Pontuação em textos",
                "Escrita de textos curtos (carta, bilhete, aviso)",
                "Vocabulário e sinonímia",
            ],
            "Ciências e Tecnologia": [
                "Meio ambiente e sustentabilidade",
                "Saúde e qualidade de vida",
                "Tecnologia e trabalho",
                "Materiais e suas propriedades",
                "Energia: tipos e fontes renováveis",
                "Segurança no trabalho (noções)",
                "Raciocínio lógico aplicado",
            ],
            "Atualidades e Cidadania": [
                "Cidadania e direitos do trabalhador",
                "Ética e trabalho em equipe",
                "Mercado de trabalho atual",
                "Noções de empreendedorismo",
                "Questões ambientais e responsabilidade social",
                "Brasil e mundo: atualidades",
            ],
        },
    },
}

CONTEUDOS_SIMULADO = {
    "Português": [
        "Interpretação de texto",
        "Gramática e sintaxe",
        "Ortografia e acentuação",
        "Figuras de linguagem",
        "Gêneros textuais",
        "Coesão e coerência",
        "Concordância e regência",
        "Tipologia textual",
    ],
    "Matemática": [
        "Equações e funções",
        "Geometria plana e espacial",
        "Porcentagem e proporcionalidade",
        "Estatística e probabilidade",
        "Álgebra e expressões",
        "Grandezas e medidas",
        "Razão e proporção",
        "Números e operações",
    ],
    "Ciências": [
        "Biologia celular e genética",
        "Ecologia e meio ambiente",
        "Corpo humano",
        "Química básica",
        "Física básica",
        "Saúde e prevenção",
    ],
    "História": [
        "Brasil República",
        "Era Vargas e Ditadura Militar",
        "Guerras Mundiais",
        "Independência do Brasil",
        "Movimentos sociais",
    ],
    "Geografia": [
        "Regiões brasileiras",
        "Geopolítica e globalização",
        "Clima e biomas",
        "Urbanização",
        "Problemas ambientais",
    ],
}

TIPOS_SIMULADO = {
    "IFF — Modelo Oficial":           {"Português": 10, "Matemática": 10, "Ciências": 5, "Geografia": 5, "História": 5},
    "IFRJ — Modelo Oficial":          {"Português": 10, "Matemática": 10, "Ciências": 5, "Geografia": 5, "História": 5},
    "CEFET — Modelo Completo":        {"Português": 10, "Matemática": 10, "Ciências": 5, "Geografia": 5, "História": 5},
    "SESI-SENAI — Modelo Prático":    {"Português": 10, "Matemática": 10, "Ciências": 5, "Geografia": 3, "História": 2},
    "Simulado Geral (misturado)":     {"Português": 10, "Matemática": 10, "Ciências": 5, "Geografia": 5, "História": 5},
}


# ══════════════════════════════════════════════════════════════════════════════
# PDF — helpers (inalterados do original)
# ══════════════════════════════════════════════════════════════════════════════

def _localizar_fontes_dejavu() -> str:
    for p in ["/usr/share/fonts/truetype/dejavu/", "/usr/share/fonts/dejavu/", "/usr/local/share/fonts/"]:
        if os.path.isfile(os.path.join(p, "DejaVuSans.ttf")):
            return p
    return ""

FONT_DIR = _localizar_fontes_dejavu()
CODECOGS_URL = "https://latex.codecogs.com/png.image?"


def latex_para_png(expr: str, dpi: int = 110) -> bytes | None:
    params = f"\\dpi{{{dpi}}}\\bg{{white}}{expr}"
    try:
        resp = requests.get(CODECOGS_URL + requests.utils.quote(params), timeout=8)
        if resp.status_code == 200 and resp.content:
            return resp.content
    except Exception:
        pass
    return None


def inserir_imagem_latex(pdf: FPDF, png_bytes: bytes, is_display: bool):
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp.write(png_bytes); tmp_path = tmp.name
    try:
        from PIL import Image as PILImage
        with PILImage.open(io.BytesIO(png_bytes)) as img:
            w_px, h_px = img.size
        px_to_mm = 0.22
        if is_display:
            h = min(h_px * px_to_mm, 12.0); w = h * (w_px / h_px)
            pdf.ln(6.5); pdf.set_x(pdf.l_margin)
            x_centro = pdf.l_margin + (pdf.epw - w) / 2
            pdf.image(tmp_path, x=x_centro, y=pdf.get_y(), h=h, w=w)
            pdf.set_y(pdf.get_y() + h + 3); pdf.set_x(pdf.l_margin)
        else:
            y_base = pdf.get_y(); pdf.set_x(pdf.get_x() + 0.8)
            h = min(h_px * px_to_mm, 4.0); w = h * (w_px / h_px)
            if pdf.get_x() + w > pdf.w - pdf.r_margin:
                pdf.ln(6.5); pdf.set_x(pdf.l_margin); y_base = pdf.get_y()
            y_img = y_base + (6.5 - h) / 2; x_img = pdf.get_x()
            pdf.image(tmp_path, x=x_img, y=y_img, h=h, w=w)
            pdf.set_xy(x_img + w + 1.2, y_base)
    finally:
        os.unlink(tmp_path)


def tokenizar_linha(texto: str) -> list[dict]:
    tokens = []; i = 0; buf = ""; n = len(texto)
    while i < n:
        if texto.startswith("$$", i):
            if buf: tokens.append({"tipo": "texto", "conteudo": buf}); buf = ""
            j = texto.find("$$", i + 2)
            if j != -1:
                tokens.append({"tipo": "display", "conteudo": texto[i + 2:j]}); i = j + 2
            else:
                buf += texto[i]; i += 1
            continue
        if texto[i] == "$":
            precedido = i > 0 and (texto[i - 1].isalpha() or texto[i - 1].isdigit())
            seguido_valido = (i + 1 < n) and texto[i + 1] not in (" ", "\t", "")
            if not precedido and seguido_valido:
                j = i + 1; fechamento = -1
                while j < n:
                    if texto[j] == "$":
                        prec_ok = texto[j - 1] != " "
                        segu = texto[j + 1] if j + 1 < n else ""
                        segu_ok = segu == "" or not segu.isalnum()
                        if prec_ok and segu_ok: fechamento = j; break
                    j += 1
                if fechamento != -1:
                    if buf: tokens.append({"tipo": "texto", "conteudo": buf}); buf = ""
                    tokens.append({"tipo": "inline", "conteudo": texto[i + 1:fechamento]}); i = fechamento + 1
                    continue
        buf += texto[i]; i += 1
    if buf: tokens.append({"tipo": "texto", "conteudo": buf})
    return tokens


class TextRenderer:
    def __init__(self, pdf: FPDF, font_name: str = "DejaVu", base_size: float = 10):
        self.pdf = pdf; self.font_name = font_name; self.base_size = base_size; self.lh = 6.5

    def _set(self, style: str = ""):
        try: self.pdf.set_font(self.font_name, style, self.base_size)
        except Exception: self.pdf.set_font("helvetica", style, self.base_size)

    def _encode(self, t: str) -> str:
        t = t.replace("—", "-").replace("–", "-")
        if self.pdf.font_family.lower() == "helvetica":
            return t.encode("latin-1", "replace").decode("latin-1")
        return t

    def write_span(self, text: str):
        partes = re.split(r'(\*\*|\*)', text); bold = False; italic = False
        for p in partes:
            if p == "**": bold = not bold; continue
            elif p == "*": italic = not italic; continue
            if not p: continue
            style = ("B" if bold else "") + ("I" if italic else "")
            self._set(style)
            limpo = p.replace("*", "")
            if limpo: self.pdf.write(self.lh, self._encode(limpo))
        self._set("")


def _renderizar_tokens(pdf, renderer, texto):
    for tok in tokenizar_linha(texto):
        if tok["tipo"] == "texto": renderer.write_span(tok["conteudo"])
        elif tok["tipo"] in ("inline", "display"):
            png = latex_para_png(tok["conteudo"])
            if png: inserir_imagem_latex(pdf, png, tok["tipo"] == "display")
            else: renderer.write_span(tok["conteudo"])


class PDFBase(FPDF):
    def __init__(self, titulo_cabecalho: str, subtitulo_cabecalho: str):
        super().__init__(); self._titulo_cab = titulo_cabecalho; self._subtitulo_cab = subtitulo_cabecalho
        if FONT_DIR:
            self.add_font("DejaVu", style="", fname=os.path.join(FONT_DIR, "DejaVuSans.ttf"))
            self.add_font("DejaVu", style="B", fname=os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf"))
            self.add_font("DejaVu", style="I", fname=os.path.join(FONT_DIR, "DejaVuSans-Oblique.ttf"))

    def header(self):
        if self.page_no() == 1:
            fonte = "DejaVu" if FONT_DIR else "helvetica"
            self.set_font(fonte, "B", 12); self.set_text_color(26, 42, 58)
            self.cell(0, 10, self._titulo_cab, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_font(fonte, "B", 9); self.set_text_color(41, 128, 185)
            self.cell(0, 5, self._subtitulo_cab, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(2); self.set_draw_color(41, 128, 185); self.set_line_width(0.5)
            self.line(15, self.get_y(), 195, self.get_y()); self.ln(5)

    def footer(self):
        self.set_y(-15); fonte = "DejaVu" if FONT_DIR else "helvetica"
        self.set_font(fonte, "", 8); self.set_text_color(130, 130, 130)
        self.cell(0, 10, f"Página {self.page_no()}/{{nb}}", align="R")


def _compilar_pdf_generico(texto_md: str, titulo_cab: str, subtitulo_cab: str,
                            marcador_nova_pagina: str = "GABARITO") -> bytes:
    pdf = PDFBase(titulo_cab, subtitulo_cab)
    pdf.alias_nb_pages(); pdf.set_margins(15, 20, 15); pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    fonte = "DejaVu" if FONT_DIR else "helvetica"
    renderer = TextRenderer(pdf, font_name=fonte, base_size=10)
    W = pdf.epw

    def set_fonte(bold=False, size=10):
        try: pdf.set_font(fonte, "B" if bold else "", size)
        except Exception: pdf.set_font("helvetica", "B" if bold else "", size)

    for linha_raw in texto_md.split("\n"):
        linha = linha_raw.rstrip(); s = linha.strip()
        if not s: pdf.ln(3); continue
        if s.startswith("# "):
            if marcador_nova_pagina and marcador_nova_pagina.upper() in s.upper():
                pdf.add_page()
            else:
                pdf.ln(4)
            pdf.set_fill_color(41, 128, 185); set_fonte(bold=True, size=11)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(W, 8, f"  {s[2:]}", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_text_color(44, 62, 80); pdf.ln(3); continue
        if s.startswith("## "):
            pdf.ln(3); set_fonte(bold=True, size=10.5); pdf.set_text_color(26, 42, 58)
            pdf.cell(W, 7, s[3:], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_draw_color(41, 128, 185); pdf.line(15, pdf.get_y(), 195, pdf.get_y())
            pdf.ln(2); continue
        if re.match(r'^#{3,4}\s+', s):
            conteudo = re.sub(r'^#{3,4}\s+', '', s); pdf.ln(2)
            set_fonte(bold=True, size=10); pdf.set_text_color(44, 62, 80)
            pdf.cell(W, 6, conteudo, new_x=XPos.LMARGIN, new_y=YPos.NEXT); pdf.ln(1); continue
        if re.match(r'^-{3,}$', s):
            pdf.ln(2); pdf.set_draw_color(200, 200, 200)
            pdf.line(15, pdf.get_y(), 195, pdf.get_y()); pdf.ln(2); continue
        match_list = re.match(r'^(\s*)([-•]|\d+\.|\w\))\s+', linha)
        if match_list:
            bullet = match_list.group(2); indent = len(match_list.group(1)) * 2 + 5
            conteudo = linha[len(match_list.group(0)):]
            pdf.set_x(pdf.l_margin + indent - 3); set_fonte(bold=False, size=10)
            pdf.set_text_color(44, 62, 80); pdf.write(renderer.lh, bullet + " ")
            _renderizar_tokens(pdf, renderer, conteudo); pdf.ln(renderer.lh + 1); continue
        pdf.set_x(pdf.l_margin); pdf.set_text_color(44, 62, 80); set_fonte(bold=False, size=10)
        _renderizar_tokens(pdf, renderer, s); pdf.ln(renderer.lh + 1)

    return bytes(pdf.output())


def compilar_pdf_questoes(texto_md, prova, disciplina, conteudo):
    return _compilar_pdf_generico(texto_md, f"QUESTÕES — MODELO {prova.upper()}",
                                   f"{disciplina.upper()} | {conteudo}", "GABARITO")

def compilar_pdf_simulado(texto_md, tipo):
    return _compilar_pdf_generico(texto_md, "SIMULADO — PREPARATÓRIO ESCOLAS TÉCNICAS",
                                   tipo.upper(), "GABARITO")

def compilar_pdf_aula(texto_md, disciplina, assunto):
    return _compilar_pdf_generico(texto_md, "AULA PERSONALIZADA — 9º ANO",
                                   f"{disciplina.upper()} | {assunto}", "")

def compilar_pdf_exercicios(texto_md, disciplina, assunto):
    sep = re.split(r'(?mi)^#{1,2}\s+.*GABARITO.*$', texto_md)
    return _compilar_pdf_generico(sep[0].strip(), "LISTA DE EXERCÍCIOS",
                                   f"{disciplina.upper()} | {assunto}", "")

def compilar_pdf_gabarito(texto_md, disciplina, assunto):
    match = re.search(r'(?mi)^#{1,2}\s+.*GABARITO.*$', texto_md)
    conteudo = texto_md[match.start():].strip() if match else texto_md
    return _compilar_pdf_generico(conteudo, "GABARITO COMENTADO",
                                   f"{disciplina.upper()} | {assunto}", "")


# ══════════════════════════════════════════════════════════════════════════════
# GEMINI
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_resource
def get_client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)


def _tratar_erro(e: Exception):
    s = str(e)
    if "429" in s or "RESOURCE_EXHAUSTED" in s:
        st.warning("⏳ Cota atingida! Aguarde ~15 segundos e tente novamente.")
    elif "503" in s or "unavailable" in s.lower():
        st.error("⚠️ Servidor temporariamente indisponível. Tente em instantes.")
    else:
        st.error(f"❌ Erro: {e}")


def _gerar(client, prompt: str, tokens: int = 8192, temp: float = 0.7) -> str:
    cfg = types.GenerateContentConfig(max_output_tokens=tokens, temperature=temp)
    resp = client.models.generate_content(model=MODELO, contents=prompt, config=cfg)
    return resp.text


REGRAS_LATEX = """
REGRAS DE FORMATAÇÃO:
- NUNCA use blocos de código (```) para texto ou matemática.
- Use LaTeX ($...$) para toda expressão ou fórmula matemática.
- Expressões em destaque: $$expressão$$
- Notação: \\frac, \\sqrt, x^{2}, \\cdot, \\pm, \\leq, \\geq
- NÃO use $ para moeda — escreva "R$" com espaço, ou "reais".
- Negrito para termos-chave: **termo**.
"""

ORIENTACAO = """
ORIENTAÇÃO PEDAGÓGICA:
- Questões no estilo das provas de ingresso em escolas técnicas federais.
- Linguagem acessível para aluno do 9º ano da rede pública.
- Contextualize em situações reais do cotidiano (trabalho, tecnologia, saúde, ambiente).
"""


# ── Geradores ─────────────────────────────────────────────────────────────────

def gerar_questoes_prova(client, prova, disciplina, conteudo, quantidade, tipo_questao):
    mapa = {
        "Múltipla escolha (A–E)": "múltipla escolha com 4 alternativas (A, B, C, D, E)",
        "Dissertativa": "dissertativa com resolução passo a passo",
        "Misto (múltipla + dissertativa)": "misto: metade múltipla escolha e metade dissertativa",
    }
    tipo_str = mapa.get(tipo_questao, "múltipla escolha com 4 alternativas")
    prompt = f"""
Você é professor especialista em elaborar questões para provas de ingresso em escolas técnicas ({prova}).

Elabore {quantidade} questões de {disciplina} para alunos do 9º ano, sobre: **{conteudo}**.
Tipo: {tipo_str}

- Estilo fiel ao modelo {prova}. Nível: ~40% fáceis, 40% médias, 20% difíceis.
- Indique: [Conteúdo: ...] e nível (Fácil/Médio/Difícil) em cada questão.
- Múltipla escolha: alternativas A), B), C), D) em linhas separadas, uma correta.
- Use LaTeX para toda matemática.

# QUESTÕES — {prova}
## {disciplina} | 9º Ano | {conteudo}
[Questões 1 a {quantidade}, marcador: **Questão N.**]

# GABARITO E RESOLUÇÕES
**Questão N.** — Resposta: [letra/resposta]
- **Resolução:** [passo a passo]
- **Dica:** [orientação em linguagem acessível]

{REGRAS_LATEX}
{ORIENTACAO}
"""
    return _gerar(client, prompt)


def gerar_simulado(client, tipo, distribuicao, conteudos_escolhidos):
    secoes = []
    for mat, qtd in distribuicao.items():
        conts = conteudos_escolhidos.get(mat, [])
        cont_str = ", ".join(conts) if conts else "conteúdos variados do 9º ano"
        secoes.append(f"- {mat}: {qtd} questões | Conteúdos: {cont_str}")
    total = sum(distribuicao.values())
    prompt = f"""
Você é professor especialista em simulados para ingresso em escolas técnicas (IFF, IFRJ, CEFET, SESI-SENAI).

Elabore um simulado com {total} questões de múltipla escolha (A, B, C, D, E) para 9º ano — estilo: **{tipo}**.

DISTRIBUIÇÃO:
{chr(10).join(secoes)}

- Questões numeradas de 1 a {total} em sequência contínua.
- Antes de cada questão: **[DISCIPLINA]** e [Conteúdo: ...].
- Alternativas A), B), C), D), E) em linhas separadas, uma correta.
- Níveis: ~40% fáceis (F), 40% médias (M), 20% difíceis (D).
- Use LaTeX para matemática.
- Ao final das questões, inclua folha de respostas vazia.

# SIMULADO — {tipo}
## Preparatório Escolas Técnicas | 9º Ano | {total} Questões

[Questões 1 a {total}]

---
## FOLHA DE RESPOSTAS
[Tabela: Questão | Resposta — {total} linhas]

# GABARITO OFICIAL
[1-X | 2-X | ... até {total}]

## RESOLUÇÕES SELECIONADAS
[Resolva detalhadamente pelo menos 6 questões das mais difíceis]

{REGRAS_LATEX}
{ORIENTACAO}
"""
    return _gerar(client, prompt)


def gerar_aula_aluno(client, disciplina, assunto, duvida):
    prompt = f"""
Você é um professor tutor paciente, especializado em alunos do 9º ano de escolas públicas brasileiras.

Disciplina: {disciplina} | Assunto: **{assunto}**
Dúvida do aluno: "{duvida if duvida.strip() else 'Explicar o assunto desde o início'}"

Elabore uma AULA EXPLICATIVA COMPLETA, falando diretamente com o aluno:
- Linguagem acessível e próxima do cotidiano.
- Exemplos concretos (cidade, trabalho, tecnologia, esporte).
- Passo a passo detalhado.
- Analogias e comparações.
- Resumo ao final (mapa mental em texto ou tabela).
- 3 a 5 exercícios resolvidos com comentários.
- Dica de como esse conteúdo cai nas provas IFF, IFRJ, CEFET e SESI-SENAI.

# 📚 AULA: {assunto} — {disciplina}
## Para o 9º Ano

### 🎯 O que você vai aprender
### 🌍 Por que isso importa?
### 📖 Explicação Principal
### 💡 Exemplos Resolvidos
### 🗺️ Resumo / Mapa de Ideias
### ✏️ Praticando: Exercícios com Gabarito
### 🔑 Dica de Prova

{REGRAS_LATEX}
"""
    return _gerar(client, prompt, temp=0.65)


def gerar_exercicios(client, disciplina, ano, assunto, nivel, quantidade, tipos):
    mapa_tipos = {
        "Dissertativos / resolução passo a passo": "dissertativos (resolução passo a passo)",
        "Múltipla escolha": "múltipla escolha (4 alternativas, A a D)",
        "Verdadeiro ou Falso": "verdadeiro ou falso (com justificativa)",
    }
    tipos_str = ", ".join(mapa_tipos[t] for t in tipos if t in mapa_tipos) or "variados"
    prompt = f"""
Você é professor especialista em elaborar listas de exercícios para o 9º ano.

Disciplina: {disciplina} | Ano: {ano} | Assunto: {assunto}
Nível: {nivel} | Quantidade: {quantidade} | Tipos: {tipos_str}

# LISTA DE EXERCÍCIOS
## {disciplina} | {ano} | {assunto}
[Exercícios 1 a {quantidade}, marcador: **Exercício N.**]

# GABARITO COMENTADO
**Exercício N.**
- **Resposta:** [resposta]
- **Resolução:** [passo a passo]
- **Comentário:** [dica pedagógica]

{REGRAS_LATEX}
"""
    return _gerar(client, prompt)


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
for _k, _v in [
    ("questoes_md", None), ("qp_prova", ""), ("qp_disc", ""), ("qp_cont", ""),
    ("simulado_md", None), ("sim_tipo", ""),
    ("aula_md", None), ("dv_disc", ""), ("dv_assunto", ""),
    ("exercicios_md", None), ("ex_disc", ""), ("ex_ano", ""), ("ex_assunto", ""),
]:
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.title("Sobre o Autor")
    st.markdown('<div class="author-name-sidebar"><strong>Prof. Me. Eric Souza da Silva</strong></div>',
                unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align:justify;font-size:0.8rem;line-height:1.5;color:rgba(250,250,250,0.65)">
        Licenciado em Matemática (UERJ), Mestre em Matemática pelo PROFMAT/UERJ e especialista em
        Tecnologias Digitais Aplicadas ao Ensino (IFRJ).<br><br>
        Professor de Matemática da Prefeitura de Macaé (Matrícula nº 48.836) e da Prefeitura de
        Casimiro de Abreu (Matrícula nº 15.035).<br><br>
        Atua em Educação Matemática, Tecnologias Digitais no Ensino, História da Educação
        Matemática, Políticas Públicas, Educação Ambiental e Esquemas Colaborativos na Educação.
        </div>""", unsafe_allow_html=True)
    st.divider()
    st.markdown("### 📞 Contato & Suporte")
    st.markdown("📧 **E-mail:** [eric@educacao.casimirodeabreu.rj.gov.br](mailto:eric@educacao.casimirodeabreu.rj.gov.br)")
    st.info("💡 **Dica do Prof:** Caso não conseguiu compreender, me mande um e-mail que eu tenho ajudar da melhor maneira possível.")


# ══════════════════════════════════════════════════════════════════════════════
# CABEÇALHO
# ══════════════════════════════════════════════════════════════════════════════
st.title("🎓 Preparatório Escolas Técnicas")
st.markdown("**Prof. Me. Eric Souza da Silva**")
st.markdown("""
<div style="background:rgba(128,128,128,0.12);padding:15px;border-radius:10px;
text-align:justify;line-height:1.6;margin:10px 0 15px 0;">
Plataforma de preparação para as provas de ingresso no Ensino Médio Técnico:
<strong>IFF, IFRJ, CEFET-RJ e SESI-SENAI</strong>.
Questões, simulados e aulas no estilo das provas reais, para alunos do 9º ano da rede pública.
</div>""", unsafe_allow_html=True)

# API KEY
api_key = os.getenv("GEMINI_API_KEY", "")
if not api_key:
    api_key = st.text_input("🔑 Chave API Gemini:", type="password")


# ══════════════════════════════════════════════════════════════════════════════
# ABAS
# ══════════════════════════════════════════════════════════════════════════════
aba_prova, aba_simulado, aba_duvidas, aba_exercicios = st.tabs([
    "📝 Questões por Prova",
    "🏆 Simulados",
    "🙋 Tirar Dúvidas",
    "✏️ Lista de Exercícios",
])


# ════════════════════════════════════════════════════════════════════════════════
# ABA 1 — QUESTÕES POR PROVA
# ════════════════════════════════════════════════════════════════════════════════
with aba_prova:
    st.markdown("#### Questões no Estilo das Provas de Ingresso")
    st.caption("Escolha a escola, a disciplina, o conteúdo e gere questões no padrão oficial.")

    prova_sel = st.selectbox("🏛️ Escola / Prova", list(PROVAS.keys()), key="qp_prova_sel")
    prova_info = PROVAS[prova_sel]

    disc_opcoes = list(prova_info["disciplinas"].keys())
    disc_sel = st.selectbox("📚 Disciplina", disc_opcoes, key="qp_disc_sel")

    conteudos_disp = prova_info["disciplinas"][disc_sel]
    conts_sel = st.multiselect("📌 Conteúdo(s)", conteudos_disp,
                                default=[conteudos_disp[0]], key="qp_cont_sel",
                                help="Selecione um ou mais conteúdos.")

    col1, col2 = st.columns(2)
    with col1:
        qp_qtd = st.slider("Nº de Questões", 5, 30, 10, key="qp_qtd")
    with col2:
        qp_tipo = st.selectbox("Tipo", ["Múltipla escolha (A–D)", "Dissertativa",
                                         "Misto (múltipla + dissertativa)"], key="qp_tipo")

    if st.button("✨ Gerar Questões", key="btn_qp"):
        if not api_key:
            st.warning("Informe a chave API Gemini.")
        elif not conts_sel:
            st.warning("Selecione ao menos um conteúdo.")
        else:
            try:
                with st.spinner(f"Gerando {qp_qtd} questões estilo {prova_sel}..."):
                    client = get_client(api_key)
                    cont_str = ", ".join(conts_sel)
                    st.session_state.questoes_md = gerar_questoes_prova(
                        client, prova_sel, disc_sel, cont_str, qp_qtd, qp_tipo)
                    st.session_state.qp_prova = prova_sel
                    st.session_state.qp_disc = disc_sel
                    st.session_state.qp_cont = cont_str
                st.success("✅ Questões geradas!")
            except (APIError, Exception) as e:
                _tratar_erro(e)

    if st.session_state.questoes_md:
        st.divider()
        with st.expander("📄 Visualizar", expanded=True):
            st.markdown(st.session_state.questoes_md)
        st.divider()
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🖨️ PDF Aluno (sem gabarito)", key="btn_pdf_qp_aluno"):
                with st.spinner("Gerando PDF..."):
                    try:
                        sep = re.split(r'(?mi)^#{1,2}\s+.*GABARITO.*$', st.session_state.questoes_md)
                        pdf = compilar_pdf_questoes(sep[0].strip(), st.session_state.qp_prova,
                                                    st.session_state.qp_disc, st.session_state.qp_cont)
                        st.download_button("⬇️ Baixar PDF Questões", pdf,
                                           f"Questoes_{st.session_state.qp_prova[:10]}_{st.session_state.qp_disc}.pdf",
                                           "application/pdf", key="dl_qp_aluno")
                    except Exception as e:
                        st.error(f"❌ {e}")
        with col_b:
            if st.button("🖨️ PDF (com gabarito)", key="btn_pdf_qp_prof"):
                with st.spinner("Gerando PDF..."):
                    try:
                        pdf = compilar_pdf_questoes(st.session_state.questoes_md,
                                                    st.session_state.qp_prova,
                                                    st.session_state.qp_disc,
                                                    st.session_state.qp_cont)
                        st.download_button("⬇️ Baixar Gabarito PDF", pdf,
                                           f"Gabarito_{st.session_state.qp_prova[:10]}_{st.session_state.qp_disc}.pdf",
                                           "application/pdf", key="dl_qp_prof")
                    except Exception as e:
                        st.error(f"❌ {e}")


# ════════════════════════════════════════════════════════════════════════════════
# ABA 2 — SIMULADOS
# ════════════════════════════════════════════════════════════════════════════════
with aba_simulado:
    st.markdown("#### 🏆 Simulado Completo — Estilo Prova Real")
    st.markdown("10 questões de Português + 10 de Matemática + 5 de Ciências, História e Geografia, como nas provas reais.")

    tipo_sim = st.selectbox("🎯 Modelo de Simulado", list(TIPOS_SIMULADO.keys()), key="sim_tipo_sel")
    distrib = TIPOS_SIMULADO[tipo_sim]
    total_sim = sum(distrib.values())

    st.markdown(f"**Distribuição:** {' | '.join(f'{m}: {q}q' for m, q in distrib.items())} = **{total_sim} questões**")
    st.divider()

    st.markdown("##### 🎲 Personalize os conteúdos (opcional)")
    st.caption("Se não selecionar, os conteúdos são sorteados automaticamente.")

    conteudos_sim = {}
    for mat, qtd in distrib.items():
        if qtd == 0:
            continue
        with st.expander(f"📚 {mat} ({qtd} questões)", expanded=False):
            opts = CONTEUDOS_SIMULADO.get(mat, [])
            if opts:
                padrao = random.sample(opts, min(2, len(opts)))
                sel = st.multiselect(f"Conteúdos de {mat}", opts, default=padrao,
                                     key=f"sim_cont_{mat}")
                conteudos_sim[mat] = sel

    st.divider()
    if st.button("🚀 Gerar Simulado Completo", key="btn_sim"):
        if not api_key:
            st.warning("Informe a chave API Gemini.")
        else:
            try:
                with st.spinner(f"Gerando simulado com {total_sim} questões — pode levar até 1 minuto..."):
                    client = get_client(api_key)
                    st.session_state.simulado_md = gerar_simulado(
                        client, tipo_sim, distrib, conteudos_sim)
                    st.session_state.sim_tipo = tipo_sim
                st.success(f"✅ Simulado com {total_sim} questões pronto!")
            except (APIError, Exception) as e:
                _tratar_erro(e)

    if st.session_state.simulado_md:
        st.divider()
        with st.expander("📄 Visualizar Simulado", expanded=True):
            st.markdown(st.session_state.simulado_md)
        st.divider()
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if st.button("🖨️ PDF Aluno (sem gabarito)", key="btn_pdf_sim_aluno"):
                with st.spinner("Gerando PDF..."):
                    try:
                        sep = re.split(r'(?mi)^#{1,2}\s+.*GABARITO.*$', st.session_state.simulado_md)
                        pdf = compilar_pdf_simulado(sep[0].strip(), st.session_state.sim_tipo)
                        st.download_button("⬇️ Baixar Simulado PDF", pdf,
                                           f"Simulado_{st.session_state.sim_tipo[:20].replace(' ','_')}.pdf",
                                           "application/pdf", key="dl_sim_aluno")
                    except Exception as e:
                        st.error(f"❌ {e}")
        with col_s2:
            if st.button("🖨️ PDF Gabarito Simulado", key="btn_pdf_sim_gab"):
                with st.spinner("Gerando PDF..."):
                    try:
                        pdf = compilar_pdf_simulado(st.session_state.simulado_md,
                                                    st.session_state.sim_tipo)
                        st.download_button("⬇️ Baixar Gabarito PDF", pdf,
                                           f"Gabarito_Simulado_{st.session_state.sim_tipo[:15].replace(' ','_')}.pdf",
                                           "application/pdf", key="dl_sim_gab")
                    except Exception as e:
                        st.error(f"❌ {e}")


# ════════════════════════════════════════════════════════════════════════════════
# ABA 3 — TIRAR DÚVIDAS
# ════════════════════════════════════════════════════════════════════════════════
with aba_duvidas:
    st.markdown("#### 🙋 Tirar Dúvidas — Aula Personalizada para Você")
    st.markdown("Escolha a matéria e o assunto e receba uma aula completa em linguagem de 9º ano, com exemplos, passo a passo e dicas de prova!")

    disc_lista = [
        "Matemática", "Português", "Ciências", "Física", "Química", "Biologia",
        "História", "Geografia", "Inglês", "Artes", "Educação Física (teoria)",
        "Outra (digitar abaixo)",
    ]
    col_d1, col_d2 = st.columns([1, 2])
    with col_d1:
        disc_escolha = st.selectbox("📚 Disciplina", disc_lista, key="dv_disc_lista")
    with col_d2:
        if disc_escolha == "Outra (digitar abaixo)":
            disc_duvida = st.text_input("Digite a disciplina", placeholder="Ex: Filosofia", key="dv_disc_texto")
        else:
            disc_duvida = disc_escolha
            st.text_input("Disciplina", value=disc_duvida, disabled=True, key="dv_disc_fix")

    assunto_duvida = st.text_input("📌 Assunto / Tema",
                                    placeholder="Ex: Equação do 2º grau, Fotossíntese, Revolução Francesa...",
                                    key="dv_assunto_field")
    duvida_esp = st.text_area("❓ Qual é a sua dúvida? (opcional)",
                               placeholder="Ex: Não entendo como usar a fórmula de Bhaskara.",
                               height=90, key="dv_duvida_field")

    st.info("💡 Quanto mais específica a dúvida, mais direcionada será a explicação!")

    if st.button("🎓 Quero Aprender!", key="btn_duvida"):
        if not api_key:
            st.warning("Informe a chave API Gemini.")
        elif not assunto_duvida.strip():
            st.warning("Informe o assunto que quer estudar.")
        elif not disc_duvida.strip():
            st.warning("Informe a disciplina.")
        else:
            try:
                with st.spinner("Preparando sua aula personalizada..."):
                    client = get_client(api_key)
                    st.session_state.aula_md = gerar_aula_aluno(
                        client, disc_duvida, assunto_duvida, duvida_esp)
                    st.session_state.dv_disc = disc_duvida
                    st.session_state.dv_assunto = assunto_duvida
                st.success("✅ Aula pronta!")
            except (APIError, Exception) as e:
                _tratar_erro(e)

    if st.session_state.aula_md:
        st.divider()
        with st.expander("📖 Sua Aula", expanded=True):
            st.markdown(st.session_state.aula_md)
        st.divider()
        if st.button("🖨️ Gerar PDF da Aula", key="btn_pdf_duvida"):
            with st.spinner("Gerando PDF..."):
                try:
                    pdf = compilar_pdf_aula(st.session_state.aula_md,
                                            st.session_state.dv_disc,
                                            st.session_state.dv_assunto)
                    st.download_button("⬇️ Baixar Aula PDF", pdf,
                                       f"Aula_{st.session_state.dv_assunto.replace(' ','_')[:30]}.pdf",
                                       "application/pdf", key="dl_pdf_duvida")
                except Exception as e:
                    st.error(f"❌ {e}")


# ════════════════════════════════════════════════════════════════════════════════
# ABA 4 — LISTA DE EXERCÍCIOS
# ════════════════════════════════════════════════════════════════════════════════
with aba_exercicios:
    st.markdown("#### ✏️ Lista de Exercícios")

    col_e1, col_e2 = st.columns(2)
    with col_e1:
        ex_disc = st.text_input("Disciplina", placeholder="Ex: Matemática", key="ex_disc_field")
    with col_e2:
        ex_ano = st.text_input("Ano / Série", placeholder="Ex: 9º ano", key="ex_ano_field")

    ex_assunto = st.text_input("Assunto", placeholder="Ex: Potenciação", key="ex_assunto_field")
    ex_nivel = st.selectbox("Nível", ["Básico", "Intermediário", "Avançado"], key="ex_nivel_field")
    ex_qtd = st.slider("Quantidade de exercícios", 5, 20, 10, key="ex_qtd")
    ex_tipos = st.multiselect("Tipos de exercício",
                               ["Dissertativos / resolução passo a passo", "Múltipla escolha", "Verdadeiro ou Falso"],
                               default=["Dissertativos / resolução passo a passo", "Múltipla escolha"],
                               key="ex_tipos_field")

    if st.button("✨ Gerar Lista de Exercícios", key="btn_ex"):
        if not api_key or not ex_disc or not ex_ano or not ex_assunto:
            st.warning("Preencha todos os campos obrigatórios.")
        elif not ex_tipos:
            st.warning("Selecione ao menos um tipo de exercício.")
        else:
            try:
                with st.spinner(f"Gerando {ex_qtd} exercícios..."):
                    client = get_client(api_key)
                    st.session_state.exercicios_md = gerar_exercicios(
                        client, ex_disc, ex_ano, ex_assunto, ex_nivel, ex_qtd, ex_tipos)
                    st.session_state.ex_disc = ex_disc
                    st.session_state.ex_ano = ex_ano
                    st.session_state.ex_assunto = ex_assunto
                st.success("✅ Lista gerada!")
            except (APIError, Exception) as e:
                _tratar_erro(e)

    if st.session_state.exercicios_md:
        st.divider()
        with st.expander("📄 Visualizar exercícios", expanded=True):
            st.markdown(st.session_state.exercicios_md)
        st.divider()
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            if st.button("🖨️ PDF Exercícios (aluno)", key="btn_pdf_ex"):
                with st.spinner("Gerando PDF..."):
                    try:
                        pdf = compilar_pdf_exercicios(st.session_state.exercicios_md,
                                                       st.session_state.ex_disc,
                                                       st.session_state.ex_assunto)
                        st.download_button("⬇️ Baixar Exercícios PDF", pdf,
                                           f"Exercicios_{st.session_state.ex_assunto.replace(' ','_')}.pdf",
                                           "application/pdf", key="dl_ex_aluno")
                    except Exception as e:
                        st.error(f"❌ {e}")
        with col_p2:
            if st.button("🖨️ PDF Gabarito (professor)", key="btn_pdf_gab"):
                with st.spinner("Gerando PDF..."):
                    try:
                        pdf = compilar_pdf_gabarito(st.session_state.exercicios_md,
                                                     st.session_state.ex_disc,
                                                     st.session_state.ex_assunto)
                        st.download_button("⬇️ Baixar Gabarito PDF", pdf,
                                           f"Gabarito_{st.session_state.ex_assunto.replace(' ','_')}.pdf",
                                           "application/pdf", key="dl_ex_gab")
                    except Exception as e:
                        st.error(f"❌ {e}")


# ── RODAPÉ ────────────────────────────────────────────────────────────────────
st.markdown('<div class="footer">© Prof. Eric Souza da Silva | Preparatório Escolas Técnicas RJ</div>',
            unsafe_allow_html=True)
