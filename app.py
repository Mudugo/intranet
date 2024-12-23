from flask import Flask, render_template
from docx import Document
import os

app = Flask(__name__)

cargos = [
"AJUDANTE GERAL",
"ANALISTA ADMINISTRATIVO PLENO",
"ANALISTA ADMINISTRATIVO SENIOR",
"ANALISTA DE RH PLENO",
"ANALISTA DE RH SENIOR",
"ANALISTA JURIDICO SENIOR",
"ANALISTA OPERACIONAL JUNIOR",
"ASSISTENTE ADMINISTRATIVO JUNIORPLENO",
"ASSISTENTE DE DP PLENO",
"ASSISTENTE DE ESTOQUE SENIOR",
"ASSISTENTE DE RH JUNIORPLENO",
"ASSISTENTE OPERACIONAL JUNIOR",
"AUXILIAR ADMINISTRATIVO MENSAGEIRO",
"AUXILIAR DE LIMPEZA",
"AUXILIAR DE MANUTENCAO",
"CONTROLADOR DE ACESSO",
"ENCARREGADO DE LIMPEZA",
"GERENTE PREDIAL",
"LIDER CONTROLADOR DE ACESSO",
"LIDER DE LIMPEZA",
"MANOBRISTA",
"OPERADOR DE MONITORAMENTO",
"RECEPCIONISTA",
"SUPERVISOR OPERACIONAL PLENOSENIOR",
"TECNICO DE MANUTENCAO",
"ZELADOR",
]

def read_docx_content(cargo):
    file_path = os.path.join('documentos', cargo.lower().replace(' ', '_'), f"{cargo.lower().replace(' ', '_')}.docx")
    
    if not os.path.exists(file_path):
        return {
            "organograma": "N/A",
            "missao": "N/A",
            "experiencia": "N/A",
            "atividades": "N/A",
            "formacao": "N/A",
            "competencias": "N/A"
        }

    doc = Document(file_path)
    content_dict = {
        "organograma": "",
        "missao": "",
        "experiencia": "",
        "atividades": [],
        "formacao": "",
        "competencias": []
    }
    current_section = None

    # Mapeamento das palavras-chave com ":" como parte da detecção
    section_keywords = {
        "ORGANOGRAMA:": "organograma",
        "MISSÃO:": "missao",
        "EXPERIÊNCIA:": "experiencia",
        "ATIVIDADES:": "atividades",
        "FORMAÇÃO:": "formacao",
        "COMPETÊNCIAS:": "competencias"
    }

    for para in doc.paragraphs:
        text = para.text.strip()

        # Remove espaços em branco extras ao redor do texto
        text = text.replace(" :", ":").strip()  # Remove espaço antes do ':'

        # Verifica se a palavra-chave com ":" está no parágrafo
        for keyword, section in section_keywords.items():
            if keyword in text.upper():  # Verifica a palavra-chave em maiúsculas
                current_section = section
                break
        else:
            # Adiciona o texto à seção atual se houver uma seção ativa e o texto não for vazio
            if current_section and text:
                # Se a seção atual for atividades ou competências
                if current_section in ["atividades", "competencias"]:
                    if text.startswith("•"):  # Se a linha começa com "•"
                        content_dict[current_section].append(text[1:].strip())  # Adiciona sem o "•"
                    else:
                        content_dict[current_section].append(text)  # Adiciona normalmente
                else:
                    content_dict[current_section] += text + "\n"  # Adiciona normalmente

    # Formata as seções de lista como strings, garantindo uma linha por item
    for key in ["atividades", "competencias"]:
        content_dict[key] = "\n".join(content_dict[key]).strip() or "Conteúdo não disponível."

    # Remove espaços extras das seções, mas não para listas
    for key in content_dict:
        if key not in ["atividades", "competencias"]:  # Não remove para listas
            content_dict[key] = content_dict[key].strip() or "Conteúdo não disponível."

    return content_dict

# Passa a lista de cargos para todos os templates
@app.context_processor
def inject_cargos():
    return dict(cargos=cargos)

# Página inicial
@app.route('/')
def index():
    return render_template('base.html')

# Rota dinâmica para cada cargo
@app.route('/cargo/<cargo_nome>')
def cargo_page(cargo_nome):
    cargo_nome = cargo_nome.replace('_', ' ').upper()
    if cargo_nome in cargos:
        content = read_docx_content(cargo_nome)
        return render_template(f"{cargo_nome.lower().replace(' ', '_')}.html", cargo=cargo_nome, content=content)
    else:
        return "Cargo não encontrado", 404

@app.route('/')
def home():
    return render_template('base.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
