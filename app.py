from flask import Flask, render_template, make_response, redirect, url_for
import pandas as pd
import numpy as np
import io
#import pdfkit
from xhtml2pdf import pisa
#config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
import json 


app = Flask(__name__)
def convert_html_to_pdf(html):
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), dest=result)
    if not pdf.err:
        return result.getvalue()
    return None

def carregar_dados(data_source, sheet_name, idioma, colunas):
    df = pd.read_excel(f'{data_source}.xlsx', sheet_name=sheet_name)
    for col in colunas:
        df[col] = df[f'{col}_{idioma}']
    return df

def processar_cabecalho(df):
    df = df[['chave', 'valor', 'rotulo']]
    df.set_index('chave', inplace=True)
    return df.apply(lambda row: {'valor': row['valor'], 'rotulo': row['rotulo']}, axis=1).to_dict()

def processar_historico(df,selecion_ordered,campos):
    df = df[df['alias'].isin(selecion_ordered)]
    df['selecion_ordered'] = pd.Categorical(df['alias'], categories=selecion_ordered, ordered=True)
    df = df.sort_values('selecion_ordered')
    return df[campos].to_dict('records') 

def processar_experiencias(df,selecion_ordered,secundario=False):
    df.loc['tipo'] = 'principal'
    if secundario:
        df.loc['tipo'] = 'complementar'
    return processar_historico(df,selecion_ordered,['empresa', 'cargo', 'duracao', 'descricao', 'tipo'])

def processar_experiencias_adicionais(df,selecion_ordered):
    return processar_experiencias(df,selecion_ordered,True)

def processar_formacoes(df,selecion_ordered,secundario=False):
    df.loc['tipo'] = 'principal'
    if secundario:
        df.loc['tipo'] = 'secundária'
    return processar_historico(df,selecion_ordered,['curso', 'instituicao', 'duracao', 'descricao', 'tipo'])

def processar_formacoes_complementares(df,selecion_ordered): 
    return processar_formacoes(df,selecion_ordered,True)
 

def processar_habilidades(df_habilidades_simples, df_classes, idioma):
    df_habilidades = pd.merge(df_habilidades_simples, df_classes, on='classe')
    df_habilidades['nome'] = df_habilidades[f'nome_{idioma}']
    df_habilidades['classe'] = df_habilidades[f'classe_{idioma}']
    return df_habilidades.groupby(['classe', 'tipo'])['nome'].apply(' / '.join).reset_index().to_dict('records')

def processar_sessoes(df, idioma):
    return df.set_index(df.columns[1]).to_dict()[f'nome_{idioma}']

 
#@app.route('/transform')
def transform():
    def parse_txt(file_path):

        with open(file_path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
        lines = [line for line in lines if line.strip()]

        lists = []
        for line in lines:
          count = line.count('\t')
          lists.append(f"{count}/{line.strip()}")
         
        array_tabs = [l for l in lists if l!='0/'][::-1]

        def associate_children_to_parents(array_tabs):
            result = []
            parent_key = None
            j=0

            for item in array_tabs:
                num, key = item.split('/')
                num = int(num)

                if num == 0:
                    # Nível raiz, não há pai
                    parent_key = None
                else:
                    # Encontrar o pai com número num-1
                    for i in range(j+1,len(array_tabs)):
                        
                        if int(array_tabs[i][0]) + 1 ==  num:
                            parent_key = array_tabs[i]
                            break
                j=j+1
                if parent_key is not None: 
                    result.append({key:parent_key.split('/')[1]})
                    
                else:
                    result.append({key: None})  # Or any other suitable default value

            return result[::-1]
         
        associations = associate_children_to_parents(array_tabs)

        primeiro_nivel = [d for d in associations if None in d.values()]
        segundo_nivel = [d for d in associations if  d in [p.keys() for p in primeiro_nivel]]

        primeiro_nivel = [list(d.keys())[0] for d in primeiro_nivel]

        result = { p:None for p in primeiro_nivel}

        for item in primeiro_nivel: 
            if item == 'estrutura': 
               result[item] = {}
               for item_segundo_nivel in [list(d.keys())[0] for d in associations if item in d.values()]:
                   result[item][item_segundo_nivel] =  [] 
                   for item_terceiro_nivel in [list(d.keys())[0] for d in associations if item_segundo_nivel in d.values()]:
                        result[item][item_segundo_nivel].append(item_terceiro_nivel) 
            else:
              result[item] = [list(d.keys())[0]  for d in associations if item in d.values()][0]
        return result

    def save_as_json(data, json_file_path):
        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)

    # Teste do algoritmo
    input_file_path = 'modelos/exemplo_pt.txt'
    output_file_path = 'modelos/exemplo_pt.json'

    parsed_data = parse_txt(input_file_path)
    save_as_json(parsed_data, output_file_path) 
    return parsed_data 
 


def get_user_data(idioma):
    data_source = 'dados_exemplo'

    with open('modelos/exemplo_pt.json', 'r') as f:
        model = json.load(f)

    df_cabecalho = carregar_dados(data_source, 'Cabeçalho', idioma, ['rotulo', 'valor'])
    cabecalho = processar_cabecalho(df_cabecalho)
    
    df_experiencias = carregar_dados(data_source, 'Experiências', idioma, ['empresa', 'cargo', 'duracao', 'descricao'])
    experiencias = processar_experiencias(df_experiencias,model['estrutura']['experiencias'])
    experiencias_adicionais = processar_experiencias_adicionais(df_experiencias,model['estrutura']['experiencias_adicionais'])


    df_formacoes = carregar_dados(data_source, 'Formações', idioma, ['curso', 'instituicao', 'duracao', 'descricao'])
    formacoes = processar_formacoes(df_formacoes,model['estrutura']['formacao'])
    formacoes_complementares = processar_formacoes_complementares(df_formacoes,model['estrutura']['formacao_complementar'])
    
    df_habilidades_simples = pd.read_excel(f'{data_source}.xlsx', sheet_name='Habilidades').fillna('')
    df_classes = pd.read_excel(f'{data_source}.xlsx', sheet_name='Classes').fillna('')
    habilidades = processar_habilidades(df_habilidades_simples, df_classes, idioma)
    
    df_sessoes = pd.read_excel(f'{data_source}.xlsx', sheet_name='Seções').fillna('')
    sessoes = processar_sessoes(df_sessoes, idioma)

    return cabecalho, experiencias,experiencias_adicionais, formacoes,formacoes_complementares, habilidades, sessoes


@app.route('/')
def home(idioma='pt'): 
    model_data = transform()

    idioma = model_data['idioma']
 
 
    cabecalho, experiencias,experiencias_adicionais, formacoes,formacoes_complementares, habilidades, sessoes  = get_user_data(idioma)

    # Convert HTML file to PDF
    #pdfkit.from_file('/templates/curriculo.html', 'output.pdf') 
    print(experiencias_adicionais)

    
    html_content =  render_template('curriculo.html', 
        user_data=cabecalho,  
        sessoes=sessoes,
        experiencias=experiencias, 
        formacoes=formacoes,
        habilidades=habilidades,
        experiencias_adicionais=experiencias_adicionais,
        formacoes_complementares=formacoes_complementares,
        margem=model_data['margem'],
        ordem_sessoes =  [
                            'formacao',
                            'experiencias',
                            'experiencias_adicionais',
                            'formacao_complementar',
                            'habilidades_tecnicas',
                            'habilidades_comportamentais',
                            'idiomas'
                            ]
        #classes_habilidades_tecnicas = np.unique([i['classe'] for i in habilidades if i['tipo'] == 'técnica']),
        #classes_habilidades_comportamentais = np.unique([i['classe'] for i in habilidades if i['tipo'] == 'comportamental'])
        )
    return html_content
   
@app.route('/en')
def index_en():
    IDIOMA = 'en'
    return home(IDIOMA)

@app.route('/pt')
def index_pt():
    IDIOMA = 'pt'
    return home(IDIOMA)

def create_app():
    app = Flask(__name__)
    # Configurações e registros de extensões aqui, se houver
    return app

if __name__ == '__main__':
    app.run(debug=True, port=9970)


# pdf = convert_html_to_pdf(html_content)
#
#    if pdf:
#        response = make_response(pdf)
#        response.headers['Content-Type'] = 'application/pdf'
#        response.headers['Content-Disposition'] = 'inline; filename=output.pdf'
#        return response
#    return "Error generating PDF"