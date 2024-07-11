from flask import Flask, render_template, make_response
import pandas as pd
import numpy as np
import io
#import pdfkit
from xhtml2pdf import pisa
#config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
 

def convert_html_to_pdf(html):
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), dest=result)
    if not pdf.err:
        return result.getvalue()
    return None

def get_user_data(idioma): 
    data_source = 'dados_exemplo'
    df = pd.read_excel(data_source+'.xlsx', sheet_name='Cabeçalho') 

    df['rotulo'] = df['rotulo_'+idioma]
    df['valor'] = df['valor_'+idioma]
    df = df[['chave','valor','rotulo']]

    df.set_index('chave', inplace=True)

    # Create the desired dictionary structure
    user_data = df.apply(lambda row: {'valor': row['valor'], 'rotulo': row['rotulo']}, axis=1).to_dict()


    df_experiencias = pd.read_excel(data_source+'.xlsx', sheet_name='Experiências')
    df_experiencias['empresa'] = df_experiencias['empresa_'+idioma]
    df_experiencias['cargo'] = df_experiencias['cargo_'+idioma]
    df_experiencias['duracao'] = df_experiencias['duracao_'+idioma]
    df_experiencias['descricao'] = df_experiencias['descricao_'+idioma]
    df_experiencias = df_experiencias[['empresa','cargo','duracao','descricao','tipo']] 

    # Transforme as experiências em uma lista de dicionários
    experiencias = df_experiencias.to_dict('records')

    df_formacoes = pd.read_excel(data_source+'.xlsx', sheet_name='Formações')
    df_formacoes['curso'] = df_formacoes['curso_'+idioma]
    df_formacoes['instituicao'] = df_formacoes['instituicao_'+idioma]
    df_formacoes['duracao'] = df_formacoes['duracao_'+idioma]
    df_formacoes['descricao'] = df_formacoes['descricao_'+idioma]
    df_formacoes = df_formacoes[['curso','instituicao','duracao','descricao','tipo']] 
    #print(df_formacoes)
    # Transforme as experiências em uma lista de dicionários
    formacoes = df_formacoes.to_dict('records')
    print(formacoes)

    df_habilidades = pd.read_excel(data_source+'.xlsx', sheet_name='Habilidades').fillna('')
    df_classes = pd.read_excel(data_source+'.xlsx', sheet_name='Classes').fillna('')
    # Transforme as experiências em uma lista de dicionários

    df_merged = pd.merge(df_habilidades, df_classes, on='classe')

    df_merged['nome'] = df_merged['nome_'+idioma]
    df_merged['classe'] = df_merged['classe_'+idioma]
    habilidades = df_merged.groupby(['classe','tipo'])['nome'].apply(' / '.join).reset_index().to_dict('records')
     
    df_secoes = pd.read_excel(data_source+'.xlsx', sheet_name='Seções').fillna('')
    # Transforme as experiências em uma lista de dicionários
    
    secoes = df_secoes.set_index([df_secoes.columns[1]]).to_dict()['nome_'+idioma]
    #print(secoes)
    return user_data, experiencias, formacoes, habilidades, secoes 

@app.route('/')
def home(idioma='pt'): 

    user_data, experiencias, formacoes, habilidades, secoes  = get_user_data(idioma)

    # Convert HTML file to PDF
    #pdfkit.from_file('/templates/curriculo.html', 'output.pdf')
    #print(secoes)
    print(habilidades)

    
    html_content =  render_template('curriculo.html', 
        user_data=user_data,  
        secoes=secoes,
        experiencias=experiencias, 
        formacoes=formacoes,
        habilidades=habilidades,
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