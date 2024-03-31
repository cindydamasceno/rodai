# RodAI por nós (LLM)
# Script para processar via LLM uma transcrição recuperada do MongoDB
# A transcrição é feita utilizando Whisper no GPU do Kaggle
# Referência: https://www.kaggle.com/code/paulofehlauer/rodai-por-n-s-gpu 


# BIBLIOTECAS EXTERNAS
from dotenv import load_dotenv
import os
from pymongo import MongoClient
from bson import ObjectId


# FUNÇÕES LOCAIS
from funcoes_llm import processa_transcricao, divide_transcricao, extrai_dados, nome_entrevistado


# VARIÁVEIS DE AMBIENTE
load_dotenv()  # Carrega as variáveis de ambiente do arquivo .env
uri = os.getenv("MONGODB_URI")


# PROMPTS PARA LLM
instrucao_infos = '''
Você é um editor de textos jornalísticos.
Sua tarefa é ler transcrições de entrevistas e recuperar as informações essenciais para a futura elaboração de uma reportagem.
A partir da transcrição fornecida, preencha o formulário a seguir:
Nome do entrevistado:
Cargo ou função do entrevistado:
Nome dos entrevistadores:
Editorias prováveis (selecione até 2 editorias entre as seguintes opções: Política, Economia, Internacional, Cultura, Esportes, Ciência, Tecnologia, Saúde, Educação, Meio Ambiente, Segurança, Justiça, Direitos Humanos, Outra):
'''
instrucao_pontos = '''
Você é um editor de textos jornalísticos.
Sua tarefa é ler transcrições de entrevistas e recuperar as informações essenciais.
A partir da transcrição fornecida, selecione 5 pontos da entrevista que mereçam destaque.
Para cada um desses pontos, preencha o formulário a seguir:
[Tempo em que ocorre a citação] - [Breve descrição do ponto importante]
Lembre-se de incluir o tempo exato em que cada citação ocorre para referência futura.
Certifique-se de capturar as informações essenciais, bem como os principais pontos discutidos durante a entrevista.
Considere sempre o interesse público e a relevância jornalística dos pontos selecionados.
Leve em conta também possíveis pontos polêmicos que tenham gerado discussão durante a entrevista.
'''


# EXECUÇÃO DO SCRIPT

# Conecta ao MongoDB
db = MongoClient(uri, ssl=True, tlsAllowInvalidCertificates=True)['mjd_2024']
db_rodai = db.tri3_grupo2
docs = db_rodai.find()

# Filtra os documentos que ainda não foram processados pelo LLM
nao_processados = db_rodai.find({'nome_entrevistado': {'$exists': False}})
    
# Itera sobre cada documento no MongoDB
for doc in nao_processados:
    # Recupera somente a transcrição
    transcricao = doc['transcricao']

    # Divide a transcrição em partes para processar no LLM
    transcricao_partes = divide_transcricao(transcricao)

    # Processa a transcrição usando LLM
    infos, pontos = processa_transcricao(transcricao_partes, instrucao_infos, instrucao_pontos)

    # Extrai os dados essenciais
    dados = extrai_dados(infos, pontos)
    dados["nome_entrevistado"] = nome_entrevistado(doc['titulo'])

    # Atualiza o documento no MongoDB
    db_rodai.update_one({'_id': ObjectId(doc['_id'])}, {'$set': dados})
    print(f'Documento {doc["_id"]} atualizado com sucesso!')