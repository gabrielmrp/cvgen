from flask import Flask, send_from_directory, session, render_template, make_response, redirect, url_for, request
import pandas as pd
import numpy as np
import io
import os
import shutil  
import json 
from datetime import datetime
from collections import OrderedDict 
import hashlib
from dotenv import load_dotenv 
from flask_cors import CORS
from werkzeug.debug import get_pin_and_cookie_name
import threading
from bs4 import BeautifulSoup
import sys 
from PyQt5.QtWidgets import QApplication, QPushButton, QWidget, QVBoxLayout
from PyQt5.QtCore import QProcess
  
app = Flask(__name__)

app.secret_key = os.getenv('FLASK_SESSION_SECRET_KEY')
CORS(app)

pd.options.mode.chained_assignment = None

@app.route('/')
def index():
    return redirect(url_for('usuarios'))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/move-pdf', methods=['POST','GET'])
def move_pdf():
    file_name =  request.json.get('file_name')
    download_path = os.getenv("DOWNLOAD_FOLDER")
    destination_path = os.getenv("DESTINATION_FOLDER") 

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

    
def transform_idented_txt_to_json(cv_name):
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
            if item in ['estrutura']:#,'renomear']: 
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

    INPUT_FILE_PATH = 'modelos/'+cv_name+'.txt' 
    OUTPUT_FILE_PATH = 'modelos/'+cv_name+'.json'
   
    parsed_data = parse_txt(INPUT_FILE_PATH) 
    save_as_json(parsed_data, OUTPUT_FILE_PATH) 
    return parsed_data 


def create_filename_hashed_suffix(username,filename): 

    def convert_to_fixed_hash(s):
        """Convert a string to a fixed hash with characters between 0 and Z."""
        # Define the possible characters (0-9, A-Z)
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        max_index = len(chars) - 1

        # Create a simple hash by summing the ASCII values of the characters in the string
        if len(s)<5:

            hash_value = sum([ord(s[i]) ** (i+1)  for i in range(len(s))]) % max_index
        else:
            hash_value = sum([ord(s[i]) * (i+1)  for i in range(len(s))]) % max_index
     
        #print(wd)
        # Convert the hash value to two characters from the chars string
        return chars[hash_value]

    part0 = filename.split('_')[0]
    part1 =  filename.split('_')[1]

    # Get current date
    date_str = datetime.now().strftime("%Y%m%d")
    
    # Generate identifier

    def split_string(s):
        midpoint = (len(s) + 1) // 2  # Ensures the second part is larger if the length is odd
        return s[:midpoint], s[midpoint:]

    part0 = split_string(part0)
 
    zz1 = convert_to_fixed_hash(part0[0])
    zz2 = convert_to_fixed_hash(part0[1])
    kk = convert_to_fixed_hash(part1)
    
    # Construct the filename
    filename = f"{username}_{date_str}{zz1}{zz2}{kk}.pdf"
    
    return filename

def process_cabecalho(df_cabecalho,df_titulos,alias_selecionados_ordenados): 
    df_cabecalho = df_cabecalho[['alias', 'valor', 'rotulo']]
 
    df_titulos = df_titulos[['alias', 'valor']]  
        
    if alias_selecionados_ordenados !=  '*' :
       df_cabecalho.loc[:,'alias_selecionados_ordenados'] = pd.Categorical(df_cabecalho['alias'], categories=alias_selecionados_ordenados, ordered=True) 
       df_cabecalho = df_cabecalho.sort_values('alias_selecionados_ordenados').dropna(subset=['alias_selecionados_ordenados'])
       #df_cabecalho.set_index('alias', inplace=True)

       df_titulos.loc[:,'alias_selecionados_ordenados'] = pd.Categorical(df_titulos['alias'], categories=alias_selecionados_ordenados, ordered=True) 
       df_titulos = df_titulos.sort_values('alias_selecionados_ordenados').dropna(subset=['alias_selecionados_ordenados'])  
       df_titulos.loc[df_titulos.head(1).index,'alias'] = 'titulo' 
       df_titulos = df_titulos.head(1) 

    df = pd.concat([df_titulos,df_cabecalho]).reset_index(drop=True)
    df.set_index('alias', inplace=True)
     
    return df.apply(lambda row: {'valor': row['valor'], 'rotulo': row['rotulo']}, axis=1).to_dict()

def process_historico(df,alias_selecionados_ordenados,campos):  
 
    if not alias_selecionados_ordenados:
        return

    df['tem_detalhe'] = df['alias'].apply(lambda x: any(alias.startswith(x) for alias in alias_selecionados_ordenados if ' ...' in alias)) 
    alias_selecionados_ordenados = new_array = [item.replace(" ...", "") if item[-4:] == ' ...' else item for item in alias_selecionados_ordenados]
    df = df[df['alias'].isin(alias_selecionados_ordenados)] 

    df.loc[:,'alias_selecionados_ordenados'] = pd.Categorical(df['alias'], categories=alias_selecionados_ordenados, ordered=True) 
    df = df.sort_values('alias_selecionados_ordenados')
    return df[campos].fillna('').to_dict('records') 

def process_resumo(df,alias_selecionados_ordenados):  

    df = df[df['alias'].isin(alias_selecionados_ordenados)]  
    df.loc[:,'alias_selecionados_ordenados'] = pd.Categorical(df['alias'], categories=alias_selecionados_ordenados, ordered=True) 
    
    if df.empty:
        return None   

    return df.head(1)['texto'].values[0]
 
def process_experiencias(df,alias_selecionados_ordenados,secundario=False):
    df['tipo'] = 'principal'
    if secundario:
        df['tipo'] = 'complementar' 
    return process_historico(df,alias_selecionados_ordenados,['empresa', 'cargo', 'duracao','tipo', 'descricao', 'detalhe1','detalhe2','detalhe3','detalhe4','detalhe5','tem_detalhe'])

def process_experiencias_adicionais(df,alias_selecionados_ordenados):
    return process_experiencias(df,alias_selecionados_ordenados,True)

def process_formacoes(df,alias_selecionados_ordenados,secundario=False):
    df['tipo'] = 'principal'
    if secundario:
        df['tipo'] = 'secundária' 
    return process_historico(df,alias_selecionados_ordenados,['curso', 'instituicao', 'duracao','tipo', 'descricao',  'detalhe1','detalhe2','detalhe3','detalhe4','detalhe5','tem_detalhe'])

def process_formacoes_complementares(df,alias_selecionados_ordenados): 
    return process_formacoes(df,alias_selecionados_ordenados,True)
 

def process_habilidades(df_habilidades_simples, df_classes, idioma, grupos_selecionados_ordenados): 
    df_habilidades = pd.merge(df_habilidades_simples, df_classes,left_on='classe' , right_on='id',suffixes=('_left','_right')).fillna('')

    #print(dw)
    df_partes = []
    for key in df_habilidades.tipo.unique(): 
        if grupos_selecionados_ordenados[key] != ['*']:

            aux_df = df_habilidades[df_habilidades.tipo == key]

            #print(wd)
            aux_df.loc[:,'grupos_selecionados_ordenados'] =  pd.Categorical(aux_df['grupo'], categories=grupos_selecionados_ordenados[key], ordered=True)
                    
            df_partes.append(aux_df.sort_values('grupos_selecionados_ordenados').dropna(subset=['grupos_selecionados_ordenados']))
        else:
            df_partes.append(df_habilidades[df_habilidades.tipo == key])

    df_habilidades_concatenadas = pd.concat(df_partes) 

    df_habilidades_concatenadas['nome'] = df_habilidades_concatenadas[f'nome_{idioma}']
    df_habilidades_concatenadas['classe'] = df_habilidades_concatenadas[f'classe_{idioma}']
 
    return df_habilidades_concatenadas.groupby(['classe', 'tipo'])['nome'].apply(' / '.join).reset_index().to_dict('records')

def process_sessoes(df, idioma,renomear=None):
 
    if renomear: 
        renomear_partes = renomear.split(': ')
        df.loc[df.alias== renomear_partes[0],[f'nome_{idioma}']]=renomear_partes[1]

    return df.set_index(df.columns[1]).to_dict()[f'nome_{idioma}']
 
def get_model_data(model,campo,parent='estrutura'):

    if parent=='base':
        if campo in model:
            return model[campo]
        else:
            return []
    else: 
        if campo in model[parent]:
            return model[parent][campo]
        else:
            return []

def read_from_user_data_source(data_source, sheet_name, idioma, colunas):
    df = pd.read_excel(f'{data_source}.xlsx', sheet_name=sheet_name)
    for col in colunas:
        df[col] = df[f'{col}_{idioma}']
    return df

def get_user_data(idioma,model):


    data_source = 'dados_exemplo' if mostra_usuario()=='exemplo' else 'dados'
     
    df_titulos = read_from_user_data_source(data_source, 'Títulos', idioma, ['valor'])
    df_cabecalho = read_from_user_data_source(data_source, 'Cabeçalho', idioma, ['rotulo', 'valor'])  
    df_resumo = read_from_user_data_source(data_source, 'Resumo', idioma, ['texto'])
    df_experiencias = read_from_user_data_source(data_source, 'Experiências', idioma, ['empresa', 'cargo', 'duracao', 'descricao','detalhe1','detalhe2','detalhe3','detalhe4','detalhe5'])
    df_outros = read_from_user_data_source(data_source, 'Outros', idioma, ['descricao'])
    df_formacoes = read_from_user_data_source(data_source, 'Formações', idioma, ['curso', 'instituicao', 'duracao', 'descricao','detalhe1','detalhe2','detalhe3','detalhe4','detalhe5'])    
    df_habilidades_simples = read_from_user_data_source(data_source, 'Habilidades', idioma, ['nome'])
    df_classes = read_from_user_data_source(data_source, 'Classes', idioma, ['classe'])
    df_sessoes = pd.read_excel(f'{data_source}.xlsx', sheet_name='Seções')
    model_cabecalho_titulo = get_model_data(model,'cabecalho') + get_model_data(model,'titulo')
 
    
    cabecalho = process_cabecalho(df_cabecalho,df_titulos, model_cabecalho_titulo)
    resumo = process_resumo(df_resumo,get_model_data(model,'resumo'))

    sessoes = process_sessoes(df_sessoes, idioma, get_model_data(model,'renomear','base'))

    experiencias = process_experiencias(df_experiencias,get_model_data(model,'experiencias'))
    experiencias_adicionais = process_experiencias_adicionais(df_experiencias,get_model_data(model,'experiencias_adicionais'))  
    outros = process_historico(df_outros,get_model_data(model,'outros'),['duracao', 'descricao']) 
    formacoes = process_formacoes(df_formacoes,get_model_data(model,'formacao'))
    formacoes_complementares = process_formacoes_complementares(df_formacoes,get_model_data(model,'formacao_complementar')) 
    habilidades = process_habilidades(df_habilidades_simples, df_classes, idioma,
            {
                'técnica' : get_model_data(model,'habilidades_tecnicas'),
                'comportamental' : get_model_data(model,'habilidades_comportamentais'),
                'idioma' : get_model_data(model,'idiomas'),
            }
        ) 

    return cabecalho, resumo, experiencias,experiencias_adicionais, formacoes,formacoes_complementares, outros, habilidades, sessoes



@app.route('/pasta')
def pasta():
    # Executa a GUI PyQt em um thread separado para abrir uma pasta
    thread = threading.Thread(target=run_pyqt_app)
    thread.start()
    return redirect(url_for('usuarios'))

@app.route('/planilha/<usuario>')
def planilha(usuario):
    # Executa a GUI PyQt em um thread separado para abrir um arquivo
    #thread = threading.Thread(target=run_pyqt_app, args=(False,))
    #thread.start()
    base_folder = os.getenv('BASE_FOLDER')
    data_source = 'dados_exemplo' if usuario.lower() == 'exemplo' else 'dados'
    file_path = os.path.join(base_folder, data_source + '.xlsx').replace('\\\\', '\\')
    os.startfile(file_path)
    return redirect(url_for('usuarios'))


def run_pyqt_app():
    app = QApplication([])  # Inicializa a aplicação Qt sem passar 'sys.argv'

    class PyQtApp(QWidget):
        def __init__(self):
            super().__init__() 
            self.open_folder()  

        def open_folder(self):
            path = os.getenv('MODEL_FOLDER').replace('\\\\', '\\')
            QProcess.startDetached('explorer', [path])
 
            

    ex = PyQtApp()
    ex.close()  # Fecha a janela imediatamente
    app.exec_()  # Executa o loop de eventos Qt


@app.route('/usuarios',methods=['GET'])
def usuarios(): 
    return render_template('usuarios.html',html_titulo="GENCV - Usuários")


@app.route('/define_usuario/<usuario>',methods=['GET'])
def define_usuario(usuario): 
    session['usuario'] = usuario
    return redirect(url_for('versoes'))

def mostra_usuario():
    # Recupera o valor de 'usuario' da sessão
    usuario = session.get('usuario', 'Nenhum usuário definido')
    return  usuario.lower()

@app.route('/versoes',methods=['GET'])
def versoes(): 
  
    # Lista os arquivos no diretório
    arquivos = os.listdir("modelos")   
   

    if session.get('usuario').lower() == 'exemplo':
        arquivos =  [arq for arq in arquivos if arq.startswith('exemplo')]

        
    arquivos = [arq[:-4] for arq in arquivos if arq[-4:]=='.txt']


    df_arquivos = pd.DataFrame([[arq,arq.split('_')[0],arq.split('_')[1]] for arq in arquivos])
 

    df_arquivos.columns = ['modelo_completo','modelo','idioma']

    dict_arquivos = df_arquivos.to_dict('records')

    return render_template('versoes.html',
        arquivos=dict_arquivos,
        usuario=session.get('usuario'),
        html_titulo="GENCV - Versões"
        )


@app.route('/cv/<cv_name>',methods=['GET'])
def home(cv_name): 
 
    global model_data
 
    model_data = transform_idented_txt_to_json(cv_name)

    with open('modelos/'+cv_name+'.json', 'r') as f:
        model = json.load(f) 


    user_data = get_user_data(model_data['idioma'],model)


    if os.getenv("NOME") is not None and mostra_usuario()!='exemplo':
        file_name = create_filename_hashed_suffix(os.getenv("NOME").replace(' ','_'), model_data['arquivo']) 
    else:
        file_name = create_filename_hashed_suffix("CURRICULO_FICTICIO_DE_EXEMPLO", model_data['arquivo'])  

    if len(user_data) == 2 and user_data[0]==None:
        return user_data[1]
    else: 
        cabecalho, resumo, experiencias,experiencias_adicionais, formacoes,formacoes_complementares, outros, habilidades, sessoes  = user_data
    
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
        file_name= file_name,
        download_path=model_data['pasta_downloads'],
        destination_path=model_data['pasta_curriculos'],
        usuario=mostra_usuario(),
        html_titulo="GENCV - CV"
        )

    file_path = os.path.join(os.getcwd(), 'curriculos', model_data['arquivo']+'.html')

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(html_content)
 
    return html_content
    

if __name__ == '__main__':  
    app.run(debug=True, port=9970)
 