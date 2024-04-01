from flask import Flask, render_template, request, redirect, url_for, send_file
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import os, json

######### ENCONTRA URI ###############
from dotenv import load_dotenv, find_dotenv 
load_dotenv(find_dotenv()) 
##########################################

app = Flask(__name__, template_folder='templates')

# Conecta ao MongoDB
uri = os.environ.get('MONGODB_URI') # CHAMA AS CREDENCIAIS

client = MongoClient(uri, ssl=True, tlsAllowInvalidCertificates=True)
db = MongoClient(uri, ssl=True, tlsAllowInvalidCertificates=True)['mjd_2024']
collection = db['tri3_grupo2']

# Função para obter os valores únicos de uma determinada chave
def get_unique_values(key):
    return collection.distinct(key)

# Define a rota da página principal
@app.route('/', methods=['GET'])
def home():
    nomes = get_unique_values('nome_entrevistado')
    editorias_duplas = get_unique_values('editorias_provaveis')
    datas = get_unique_values('data_publicacao')
   
    # Separa os dois termos da lista editorias_provaveis
    editorias = []
    for dupla in editorias_duplas:
        palavras=dupla.split(",")
        editorias.extend(palavras)

    ## TRABALHA EDITORIAS ##           
   
    # Remove duplicatas
    editorias = list(set(editorias))

    # DROPDOWN 
    relacao_editorias={}

    # GUARDA TODOS OS EPISÓDIOS EM UM DICIONÁRIO
    todos_episodios=[]
    for episodio in collection.find():
        todos_episodios.append(episodio["nome_entrevistado"])
        relacao_editorias["Todos os episódios"]=todos_episodios

    for editoria in editorias:
        entrevistado_editoria=[]
        for episodio in collection.find({'editorias_provaveis':{'$regex':editoria}}): # $REGEX (MONGODB) FACILITA O QUERY DE EDITORIA
            entrevistado_editoria.append(episodio["nome_entrevistado"])
        relacao_editorias[editoria]=entrevistado_editoria

    #Capturar a entrevista mais recente adicionada à collection do MongoDB
    ultima_entrevista = collection.find_one(sort=[('data_publicacao', -1)])

    # Buscar as últimas 3 entrevistas excluindo a última, ordenadas por data de publicação
    historico_entrevistas = collection.find(sort=[('data_publicacao', -1)]).skip(1).limit(3)
    
    print(relacao_editorias)
    return render_template('index.html', relacao_editorias=relacao_editorias,nomes=nomes, editorias=editorias, datas=datas, ultima_entrevista=ultima_entrevista, historico_entrevistas=historico_entrevistas)

# Rota para lidar com a pesquisa e exibir os resultados
@app.route('/resultado', methods=['POST'])
def resultados():
    nome = request.form['entrevistado']
    resultados = collection.find({'nome_entrevistado': nome})

    # Obtendo informações adicionais da entrevista
    for resultado in resultados:
        editorias = resultado['editorias_provaveis']
        cargo = resultado['cargo_funcao']
        entrevistadores = resultado['nome_entrevistadores']
        data=resultado['data_publicacao'].strftime('%d/%m/%Y')
        pontos = resultado['pontos']
        url = resultado['url']
        transcricao = resultado['transcricao']
    
    # Preparar dados para a página de resultados
    dados_entrevista = {
        'nome': nome.upper(),
        'editorias': editorias,
        'cargo': cargo,
        'entrevistadores': ",".join(entrevistadores), # TIRA VALOR DAS LISTAS. BOM FAZER UMA CONFERÊNCIA DOS ENTREVISTADORES COM PALAVRAS NADA A VER. 
        'pontos': pontos,
        'data': data,
        'url': url,
        'texto': pontos,
        'transcricao': transcricao,
    }

    # Escrever a transcrição em um arquivo .txt
    with open('transcricao.txt', 'w') as file:
        file.write(str(transcricao))

    # Retornar os resultados e o link para download da transcrição
    return render_template('resultado.html', dados_entrevista=dados_entrevista)

# Rota para fazer o download da transcrição completa da entrevista
@app.route('/download_transcricao')
def download_transcricao():
    return send_file('transcricao.txt', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
