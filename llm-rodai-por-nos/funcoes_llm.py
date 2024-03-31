# PROCESSA TRANSCRIÇÃO
# Recupera as informações essenciais e possíveis leads da entrevista usando LLM
# Retorna duas strings (infos, pontos) com as informações essenciais e os possíveis leads

def processa_transcricao(partes_transcricao, instrucao_infos, instrucao_pontos):
    from openai import OpenAI
    import os
    from dotenv import load_dotenv
    load_dotenv()  # Carrega as variáveis de ambiente do arquivo .env
    openai_api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key = openai_api_key)

    infos = ''
    pontos = ''
    parte1 = True  # Flag para sinalizar a primeira iteração
    for parte in partes_transcricao:
        if parte1:
            # Envia uma primeira mensagem para obter as informações essenciais da entrevista
            chat = client.chat.completions.create(
                model="gpt-3.5-turbo", 
                temperature = 0,
                messages=[
                    {"role": "system", "content": instrucao_infos},
                    {"role": "user", "content": parte}])
            print(f'Bloco enviado para recuperação de informações essenciais.')
            infos = infos + '\n' + chat.choices[0].message.content

            # Envia uma segunda conversa para obter os pontos importantes da primeira parte        
            chat = client.chat.completions.create(
                model="gpt-3.5-turbo", 
                temperature = 0,
                messages=[
                    {"role": "system", "content": instrucao_pontos},
                    {"role": "user", "content": parte}])
            print(f'Bloco reenviado para recuperação de pontos de interesse.')
            pontos = pontos + '\n' + chat.choices[0].message.content

            # Muda a flag após a primeira iteração para evitar repetir a primeira parte
            parte1 = False 

        else:
            chat = client.chat.completions.create(
                model="gpt-3.5-turbo",
                temperature = 0,
                messages=[
                    {"role": "system", "content": instrucao_pontos},
                    {"role": "user", "content": parte}])
            print(f'Bloco enviado para recuperação de pontos de interesse.')
            pontos = pontos + '\n' + chat.choices[0].message.content
    return infos, pontos



# DIVIDE TRANSCRIÇÃO
# Divide a transcrição em partes para processar no LLM evitando o limite de tokens
# Cada item da lista 'transcricao' corresponde a aproximadamente 1 minuto de áudio
# Cada bloco a ser enviado ao GPT deve corresponder a aproximadamente 60 blocos
# Retorna uma lista com as partes da transcrição divididas

def divide_transcricao(transcricao):
    num_total_itens = len(transcricao)
    tamanho_bloco_ideal = 60

    # Calcula o número ideal de blocos, arredondando para cima
    num_blocos = -(-num_total_itens // tamanho_bloco_ideal)  # Truque para arredondamento para cima

    # Calcula o novo tamanho de bloco para distribuir os itens de forma mais uniforme
    novo_tamanho_bloco = -(-num_total_itens // num_blocos)  # Truque para arredondamento para cima

    partes_transcricao = []
    for i in range(0, num_total_itens, novo_tamanho_bloco):
        # Extrai um subconjunto de 'transcricao' para formar o bloco atual
        bloco = '\n'.join(transcricao[i:i+novo_tamanho_bloco])
        partes_transcricao.append(bloco)

    # Isso resultará em blocos que são mais uniformemente distribuídos
    print(f'A transcrição foi dividida em {num_blocos} blocos')
    return partes_transcricao



# EXTRAI DADOS
# Função que extrai as informações essenciais e os pontos de interesse da resposta do LLM
# Recebe como argumentos duas strings (infos, pontos) com as informações essenciais e os possíveis leads
# Retorna um dicionário com as informações extraídas e estruturadas para serem inseridas no banco de dados

def extrai_dados(infos, pontos):

    import re

    # Extrair informações básicas
    nome_entrevistado = re.search(r"Nome do entrevistado: (.*)", infos).group(1)
    cargo = re.search(r"Cargo ou função do entrevistado: (.*)", infos).group(1)
    entrevistadores = re.search(r"Nome dos entrevistadores: (.*)", infos).group(1).split(", ")
    editorias = re.search(r"Editorias prováveis: (.*)", infos).group(1).split(", ")

    # Expressão regular ajustada para capturar apenas o tempo de início e a descrição
    regex = r"(?:\[)?(\d{1,2}:\d{2}(?::\d{2})?)(?:\])?\s-\s(.*?)(?=(?:\[?\d{1,2}:\d{2}|\Z)(?!^\s-\s))"

    pontos_dicio = []

    for match in re.finditer(regex, pontos, re.DOTALL):
        tempo_inicio = match.group(1)
        descricao = match.group(2).strip()
        
        # Verificar se o tempo final está presente
        if len(descricao) > 10:
            pontos_dicio.append({
                "tempo_inicio": tempo_inicio,
                "descricao": descricao
            })

    informacoes = {
        "cargo_funcao": cargo,
        "nome_entrevistadores": entrevistadores,
        "editorias_provaveis": editorias,
        "pontos": pontos_dicio
    }
    print(f'Informações da entrevista com {nome_entrevistado} extraídas com sucesso.')
    return informacoes


# NOME DO ENTREVISTADO
# Extrai o nome do entrevistado a partir do título do vídeo
# Retorna o nome do entrevistado como uma string
def nome_entrevistado(titulo):
    # Divide a string pelo caractere '|'
    partes = titulo.split('|')
    
    # O nome do entrevistado está na segunda parte da lista (índice 1)
    nome_entrevistado = partes[1].strip()  # Usa strip() para remover espaços em branco extras
    
    return nome_entrevistado