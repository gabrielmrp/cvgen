from flask import Flask, render_template, make_response, redirect, url_for, request
from flask_cors import CORS
import pandas as pd
import numpy as np
import io
import os
import shutil
#import pdfkit
from xhtml2pdf import pisa
import xlsxwriter
#config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
import json 
from datetime import datetime
pd.options.mode.chained_assignment = None
from collections import OrderedDict

#input_file_path = 'modelos/exemplo_pt.txt'
#output_file_path = 'modelos/exemplo_pt.json'
#INPUT_JSON = 'exemplo_pt.json'
#data_source = 'dados_exemplo'

data_source = 'dados'#_exemplo
input_file_path = 'modelos/cd_pt.txt'
output_file_path = 'modelos/cd_pt.json'  
INPUT_JSON = 'cd_pt.json'

app = Flask(__name__)
CORS(app)

def convert_html_to_pdf(html):
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), dest=result)
    if not pdf.err:
        return result.getvalue()
    return None

@app.route('/para_planilha', methods=['POST'])
def para_planilha(): 
    if request.method == 'POST':
        print(request.form.get('cabecalho_perfil_pt'))

        data = request.form.to_dict()
        # Exemplos de DataFrames vazios
        

         

        # Função para preencher os DataFrames
        # Função para preencher os DataFrames
        def populate_dataframes(data):
            cabecalho = pd.DataFrame(columns=['rotulo_pt','rotulo_en','valor_pt','valor_en'])
            resumo = pd.DataFrame(columns=['id','alias', 'texto_pt', 'texto_en'])

            secoes = pd.DataFrame(columns=['id','alias', 'nome_pt', 'nome_en'])

            experiencia = pd.DataFrame(columns=['id', 'alias', 'cargo_pt', 'empresa_pt', 'duracao_pt', 'descricao_pt', 'detalhe1_pt', 'detalhe2_pt', 'detalhe3_pt', 'detalhe4_pt', 'detalhe5_pt', 'cargo_en', 'empresa_en', 'duracao_en', 'descricao_en', 'detalhe1_en', 'detalhe2_en', 'detalhe3_en', 'detalhe4_en', 'detalhe5_en'])
            formacao = pd.DataFrame(columns=['id', 'alias', 'curso_pt', 'instituicao_pt', 'duracao_pt', 'descricao_pt', 'detalhe1_pt', 'detalhe2_pt', 'detalhe3_pt', 'detalhe4_pt', 'detalhe5_pt', 'curso_en', 'instituicao_en', 'duracao_en', 'descricao_en', 'detalhe1_en', 'detalhe2_en', 'detalhe3_en', 'detalhe4_en', 'detalhe5_en'])

            habilidade = pd.DataFrame(columns=['id','classe_pt','classe_en','tipo','nome_pt','nome_en'])

            habilidade_tecnica = pd.DataFrame(columns=['id','classe_pt','classe_en','tipo','nome_pt','nome_en'])
            habilidade_comportamental = pd.DataFrame(columns=['id','classe_pt','classe_en','tipo','nome_pt','nome_en'])
            habilidade_idioma = pd.DataFrame(columns=['id','classe_pt','classe_en','tipo','nome_pt','nome_en'])

            outros = pd.DataFrame(columns=['id','alias','descricao_en','descricao_pt','duracao'])

             

            for key, value in data.items():
                print(key)
                if key!='Enviar':
                    parts = key.split('_')

                    if len(parts) == 3:
                        dataframe, coluna, idioma = parts
                        id_val = None
                    elif len(parts) == 4:
                        dataframe, tipo, coluna, idioma = parts 
                        id_val = None
                    elif len(parts) == 5:
                        dataframe, tipo, coluna, idioma, id_val = parts
                    else:
                        raise ValueError(f"Unexpected key format: {key}")

                    if dataframe == 'cabecalho': 
                        cabecalho.loc[tipo,f'{coluna}_{idioma}'] = value 


                    elif dataframe == 'secoes':

                        if coluna == 'alias' or coluna == 'id':
                            id_val = parts[-1]
                            secoes.at[id_val, f'{coluna}'] = value
                        else: 
                            dataframe, coluna, idioma, id_val = parts 
                            secoes.at[id_val, f'{coluna}_{idioma}'] = value

                    elif dataframe == 'resumo':
                        if coluna == 'alias' or coluna == 'id':
                            id_val = parts[-1]
                            resumo.at[id_val, f'{coluna}'] = value
                        else: 
                            dataframe, coluna, idioma, id_val = parts 
                            resumo.at[id_val, f'{coluna}_{idioma}'] = value


                    elif dataframe == 'experiencia' : 
                        if len(parts) == 3: 
                            dataframe, coluna,id_val  = parts
                            experiencia.at[id_val, coluna] = value
                            
                        elif len(parts) == 4: 
                            dataframe, coluna, idioma,id_val  = parts
                            experiencia.at[id_val, f'{coluna}_{idioma}'] = value 
                        else:
                            pass
  

                    elif dataframe == 'formacao': 
                        if len(parts) == 3: 
                            dataframe, coluna,id_val  = parts
                            formacao.at[id_val, coluna] = value
                            
                        elif len(parts) == 4: 
                            dataframe, coluna, idioma,id_val  = parts
                            formacao.at[id_val, f'{coluna}_{idioma}'] = value 
                        else:
                            pass

                    elif dataframe == 'outros': 
                        if len(parts) == 3: 
                            dataframe, coluna,id_val  = parts
                            outros.at[id_val, coluna] = value
                            
                        elif len(parts) == 4: 
                            dataframe, coluna, idioma,id_val  = parts
                            outros.at[id_val, f'{coluna}_{idioma}'] = value 
                        else:
                            pass


                    
                    elif dataframe == 'habilidade':  
                        simple = False
                        if len(parts) == 4:
                            if parts[-2] not in ['en','pt']: 
                                simple=True
                                dataframe, tipo, coluna,id_val  = parts 
                            else:
                                dataframe, coluna, idioma,id_val  = parts
                        elif len(parts) == 5:
                            if parts[-2] not in ['en','pt']: 
                                simple=True
                                print(dw)
                            else:
                                dataframe, tipo, coluna, idioma, id_val  = parts  
                        id_val = int(parts[-1]) - 1  

                        if tipo in ['tecnica', 'comportamental', 'idioma']: 
                            if tipo == 'tecnica':
                                df = habilidade_tecnica
                            elif tipo == 'comportamental':
                                df = habilidade_comportamental
                            elif tipo == 'idioma':
                                df = habilidade_idioma
 
                            df.at[id_val, 'tipo'] = tipo 
                            if simple:
                                col_atualizar = coluna
                            else:
                                col_atualizar = f'{coluna}_{idioma}'
 
                            df.at[id_val, col_atualizar] = value

 
            habilidade = pd.concat([habilidade_tecnica,habilidade_comportamental,habilidade_idioma]).reset_index(drop = True) 

            classes = habilidade[[ 'alias', 'classe_pt', 'classe_en','tipo']].drop_duplicates()
            classes.index = range(1, len(classes) + 1)

            #

            for i in range(habilidade.shape[0]):
                row = habilidade.iloc[i]
                matched_index = classes[(classes['alias'] == row['alias']) & 
                                        (classes['classe_pt'] == row['classe_pt']) & 
                                        (classes['classe_en'] == row['classe_en'])].index[0]
                habilidade.loc[i,'classe'] = str(matched_index)

            classes.reset_index(inplace=True)
            classes.rename(columns={'index':'classe'},inplace=True)
            habilidade=habilidade[['id','classe','nome_pt','nome_en']]  

            return cabecalho,resumo,experiencia,formacao,habilidade,classes,outros,secoes

                 
        # Preencher os DataFrames com os dados do dicionário
        cabecalho,resumo,experiencia,formacao,habilidade,classes,outros,secoes  = populate_dataframes(data)

        #cabecalho.set_index('alias', inplace=True)
        cabecalho.reset_index(inplace=True) 
        cabecalho.rename(columns={'index':'alias'},inplace=True)

        #return cabecalho.to_html()+"<br>"+resumo.to_html()+"<br>"+experiencia.to_html()+formacao.to_html()+ habilidade.to_html()#+ idioma.to_html()

        nome_arquivo = 'dados_planilha.xlsx'
        with pd.ExcelWriter(nome_arquivo, engine='openpyxl') as writer:
            # Salvar cada DataFrame em uma aba diferente
            cabecalho.to_excel(writer, sheet_name='Cabeçalho', index=False)
            resumo.to_excel(writer, sheet_name='Resumo', index=False)
            experiencia.to_excel(writer, sheet_name='Experiência', index=False)
            formacao.to_excel(writer, sheet_name='Formação', index=False)
            outros.to_excel(writer, sheet_name='Outros', index=False)
            secoes.to_excel(writer, sheet_name='Seções', index=False)
            habilidade.to_excel(writer, sheet_name='Habilidade', index=False)
            classes.to_excel(writer, sheet_name='Classes', index=False)




        return resumo.to_html() 
        # Exibir os DataFrames preenchidos
        
@app.route('/compare')
def compare(): 
    df1 = pd.read_excel('dados_planilha.xlsx')
    df2 = pd.read_excel('dados.xlsx')
    if df1.equals(df2):
        return "Os arquivos são idênticos."
    else:
        diff = df1.compare(df2, align_axis=0, keep_shape=True)
        return diff.to_html()


@app.route('/profiler')
def profiler(): 
    sheets = ['Outros', 'Experiências', 'Habilidades', 'Formações','Resumo','Seções']  # Nomes das abas
    data = read_excel_data(data_source, sheets)
    cabecalho = read_cabecalho_data(data_source)
    habilidades = read_habilidades_data(data_source)
    #print(dw)
     
    return render_template('profiler.html', data=data , cabecalho=cabecalho, habilidades=habilidades  )

# Função para ler o CSV e retornar os dados
def read_excel_data(data_source, sheets):
    try:
        data = {}
        for sheet_name in sheets:
            df = pd.read_excel(f'{data_source}.xlsx', sheet_name=sheet_name).fillna('')
            data[sheet_name] = df.to_dict(orient='records')  # Converte o DataFrame para lista de dicionários.head(np.infinity)
        return data
    except Exception as e:
        print(f"Erro ao ler o arquivo Excel: {str(e)}")
        return None

def read_cabecalho_data(data_source):
    # Carregar o arquivo Excel
    df = pd.read_excel(data_source+".xlsx", sheet_name='Cabeçalho') 
    return df.set_index('alias').T.to_dict()

def read_habilidades_data(data_source):
    array_dfs = {}
    df_habilidades_simples = pd.read_excel(data_source+".xlsx", sheet_name='Habilidades') 
    df_classes = pd.read_excel(data_source+".xlsx", sheet_name='Classes') 
    df = pd.merge(df_habilidades_simples, df_classes, on='classe').fillna('')

    for u in df.tipo.unique():
        array_dfs[u] = df[df.tipo == u].to_dict(orient='records') 
    return array_dfs

@app.route('/move-pdf', methods=['POST'])
def move_pdf():
    download_path = request.json.get('download_path')
    destination_path = request.json.get('destination_path')
    file_name = request.json.get('file_name')

    # Verifica o caminho completo do arquivo a ser movido
    file_path = os.path.join(download_path, file_name)

    if os.path.exists(file_path):
        # Verifica se o arquivo com mesmo nome já existe no destino
        if os.path.exists(os.path.join(destination_path, file_name)):
            # Gera um timestamp para acrescentar ao nome do arquivo
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            
            # Renomeia o arquivo antigo adicionando o timestamp
            deprecated_file_name = f"{os.path.splitext(file_name)[0]}_versao_{timestamp}{os.path.splitext(file_name)[1]}"
            
            # Move o arquivo antigo para a pasta 'versoes' dentro do destino
            shutil.move(os.path.join(destination_path, file_name), os.path.join(destination_path, 'versoes', deprecated_file_name))
        
        # Move o novo arquivo para o destino principal
        shutil.move(file_path, os.path.join(destination_path, file_name))
        
        return f'{file_name} movido para {destination_path}\\versoes', 200
    else:
        return f'{file_name} - Arquivo não encontrado', 404


def carregar_dados(data_source, sheet_name, idioma, colunas):
    df = pd.read_excel(f'{data_source}.xlsx', sheet_name=sheet_name)
    for col in colunas:
        df[col] = df[f'{col}_{idioma}']
    return df

def processar_cabecalho(df,alias_selecionados_ordenados): 
    df = df[['alias', 'valor', 'rotulo']]
    #print(ge)
    if alias_selecionados_ordenados !=  '*' :
       df.loc[:,'alias_selecionados_ordenados'] = pd.Categorical(df['alias'], categories=alias_selecionados_ordenados, ordered=True) 
       df = df.sort_values('alias_selecionados_ordenados').dropna(subset=['alias_selecionados_ordenados'])
    
    df.set_index('alias', inplace=True)
    return df.apply(lambda row: {'valor': row['valor'], 'rotulo': row['rotulo']}, axis=1).to_dict()

def processar_historico(df,alias_selecionados_ordenados,campos):  
    #print(dw)
    df['tem_detalhe'] = df['alias'].apply(lambda x: any(alias.startswith(x) for alias in alias_selecionados_ordenados if ' ...' in alias)) 
    alias_selecionados_ordenados = new_array = [item.replace(" ...", "") if item[-4:] == ' ...' else item for item in alias_selecionados_ordenados]
    df = df[df['alias'].isin(alias_selecionados_ordenados)] 

    df.loc[:,'alias_selecionados_ordenados'] = pd.Categorical(df['alias'], categories=alias_selecionados_ordenados, ordered=True) 
    df = df.sort_values('alias_selecionados_ordenados')
    return df[campos].fillna('').to_dict('records') 

def processar_resumo(df,alias_selecionados_ordenados):

    #print(wd)
    df = df[df['alias'].isin(alias_selecionados_ordenados)] 

    df.loc[:,'alias_selecionados_ordenados'] = pd.Categorical(df['alias'], categories=alias_selecionados_ordenados, ordered=True) 
    
    return df.head(1)['texto'].values[0]



def processar_experiencias(df,alias_selecionados_ordenados,secundario=False):
    df['tipo'] = 'principal'
    if secundario:
        df['tipo'] = 'complementar' 
    return processar_historico(df,alias_selecionados_ordenados,['empresa', 'cargo', 'duracao','tipo', 'descricao', 'detalhe1','detalhe2','detalhe3','detalhe4','detalhe5','tem_detalhe'])

def processar_experiencias_adicionais(df,alias_selecionados_ordenados):
    return processar_experiencias(df,alias_selecionados_ordenados,True)

def processar_formacoes(df,alias_selecionados_ordenados,secundario=False):
    df['tipo'] = 'principal'
    if secundario:
        df['tipo'] = 'secundária' 
    return processar_historico(df,alias_selecionados_ordenados,['curso', 'instituicao', 'duracao','tipo', 'descricao',  'detalhe1','detalhe2','detalhe3','detalhe4','detalhe5','tem_detalhe'])

def processar_formacoes_complementares(df,alias_selecionados_ordenados): 
    return processar_formacoes(df,alias_selecionados_ordenados,True)
 

def processar_habilidades(df_habilidades_simples, df_classes, idioma, grupos_selecionados_ordenados):
    df_habilidades = pd.merge(df_habilidades_simples, df_classes, on='classe').fillna('')

    #print(dw)
    df_partes = []
    for key in df_habilidades.tipo.unique(): 
        if grupos_selecionados_ordenados[key] != ['*']:

            aux_df = df_habilidades
            aux_df.loc[:,'grupos_selecionados_ordenados'] =  pd.Categorical(df_habilidades['grupo'], categories=grupos_selecionados_ordenados[key], ordered=True)
                    
            df_partes.append(aux_df.sort_values('grupos_selecionados_ordenados').dropna(subset=['grupos_selecionados_ordenados']))
        else:
            df_partes.append(df_habilidades[df_habilidades.tipo == key])

    df_habilidades_concatenadas = pd.concat(df_partes) 

    df_habilidades_concatenadas['nome'] = df_habilidades_concatenadas[f'nome_{idioma}']
    df_habilidades_concatenadas['classe'] = df_habilidades_concatenadas[f'classe_{idioma}']
    

    return df_habilidades_concatenadas.groupby(['classe', 'tipo'])['nome'].apply(' / '.join).reset_index().to_dict('records')

def processar_sessoes(df, idioma):
    return df.set_index(df.columns[1]).to_dict()[f'nome_{idioma}']

 
#@app.route('/transform')
def transform():
    def parse_txt(file_path):

        with open(file_path, 'r', encoding='utf-8') as file:
                    lines = []
                    for line in file:
                        if " --" in line:
                            line = line.split(" --")[0]
                        lines.append(line)

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
   
    parsed_data = parse_txt(input_file_path) 
    save_as_json(parsed_data, output_file_path) 
    return parsed_data 
 


def get_user_data(idioma):
    
   
    with open('modelos/'+INPUT_JSON, 'r') as f:
        model = json.load(f)

    df_resumo = carregar_dados(data_source, 'Resumo', idioma, ['texto'])
    
    resumo = processar_resumo(df_resumo,model['estrutura']['resumo'])
    
    df_cabecalho = carregar_dados(data_source, 'Cabeçalho', idioma, ['rotulo', 'valor']) 
    cabecalho = processar_cabecalho(df_cabecalho,model['estrutura']['cabecalho'])
    
    df_experiencias = carregar_dados(data_source, 'Experiências', idioma, ['empresa', 'cargo', 'duracao', 'descricao','detalhe1','detalhe2','detalhe3','detalhe4','detalhe5'])
    experiencias = processar_experiencias(df_experiencias,model['estrutura']['experiencias'])
    experiencias_adicionais = processar_experiencias_adicionais(df_experiencias,model['estrutura']['experiencias_adicionais'])

    df_outros = carregar_dados(data_source, 'Outros', idioma, ['descricao'])
    outros = processar_historico(df_outros,model['estrutura']['outros'],['duracao', 'descricao'])
 
    df_formacoes = carregar_dados(data_source, 'Formações', idioma, ['curso', 'instituicao', 'duracao', 'descricao','detalhe1','detalhe2','detalhe3','detalhe4','detalhe5'])
    formacoes = processar_formacoes(df_formacoes,model['estrutura']['formacao'])
    formacoes_complementares = processar_formacoes_complementares(df_formacoes,model['estrutura']['formacao_complementar'])


    
    df_habilidades_simples = pd.read_excel(f'{data_source}.xlsx', sheet_name='Habilidades')
    df_classes = pd.read_excel(f'{data_source}.xlsx', sheet_name='Classes')
    habilidades = processar_habilidades(df_habilidades_simples, df_classes, idioma,
        {
        'técnica' : model['estrutura']['habilidades_tecnicas'],
        'comportamental' : model['estrutura']['habilidades_comportamentais'],
        'idioma' : model['estrutura']['idiomas'],
        }
        )
 
    
    df_sessoes = pd.read_excel(f'{data_source}.xlsx', sheet_name='Seções')
    sessoes = processar_sessoes(df_sessoes, idioma)

    return cabecalho, resumo, experiencias,experiencias_adicionais, formacoes,formacoes_complementares, outros, habilidades, sessoes


@app.route('/')
def home(idioma='pt'): 
    model_data = transform()
 

    idioma = model_data['idioma']

    cabecalho, resumo, experiencias,experiencias_adicionais, formacoes,formacoes_complementares, outros, habilidades, sessoes  = get_user_data(idioma)
  
    html_content =  render_template('curriculo.html', 
        user_data=cabecalho,  
        resumo=resumo,
        sessoes={ key : sessoes[key]  for key in model_data['estrutura'].keys() if key in sessoes.keys() },
        experiencias=experiencias, 
        formacoes=formacoes,
        habilidades=habilidades,
        experiencias_adicionais=experiencias_adicionais,
        formacoes_complementares=formacoes_complementares,
        outros=outros,
        margem=model_data['margem'], 
        file_name=model_data['arquivo'],
        download_path=model_data['pasta_downloads'],
        destination_path=model_data['pasta_curriculos'] 
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
 