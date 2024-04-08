# RodAI por Nós
O RodAI por Nós é a versão beta de uma ferramenta que prepara o resumo do programa semanal Roda Viva, da TV Cultura, com Inteligência Artificial. A ideia original foi transformar o conteúdo do programa Roda Viva em um banco de dados de futuras pautas em razão de sua relevância jornalística e qualidade das fontes entrevistadas. Semanalmente, o Rodai por Nós recupera o conteúdo na íntegra destes episódios a partir do canal na web, transcrevendo-os e interpretando-os com auxílio de LLM. O produto foi desenvolvido por Christina Souza, Cindy Damasceno, João Barbosa, Paulo Fehlauer e Sumaia Villela como projeto final da disciplina de Machine Learning do Master em Jornalismo de Dados, Automação e Storytelling do Insper. Por se tratar de uma primeira versão, os resultados devem ser avaliados com cautela pois pode trazer ainda alguma incongruência.

<hr>

## De ponto em ponto
A ferramenta roda em um notebook do Kaggle para tirar proveito do processamento em GPU e da possibilidade de agendamento semanal. Na sequência, visita a playlist do Roda Viva e encontra o episódio mais recente. Depois, converte o áudio do episódio para o formato MP3, recupera informações essenciais, tais como: data de publicação, nome do entrevistado, duração do episódio, ID do vídeo e caminho do arquivo MP3 no ambiente de processamento. 

Feito isso, carrega o modelo LLM do Whisper (utilizando whisper-large-v3), transcreve o episódio utilizando o Whisper, trata os blocos de transcrição resultantes e concatena em blocos maiores para otimizar o processamento, já que cada bloco original corresponde a uma frase bastante curta, incluindo timestamps de início e fim, o que aumenta consideravelmente o tamanho das strings. Por fim, converte os timestamps originais (fornecidos em segundos) para um formato mais amigável (hh:mm:ss), transforma os blocos resultantes em uma lista de strings, adiciona as informações essenciais mais a transcrição a uma coleção no MongoDB para processamento posterior e envia mensagem no Telegram confirmando a operação.


## Como usar
O uso é bastante simples. Basta filtrar os episódios por assunto. De toda forma, a opção com todos os episódios está ativada por padrão. É possível também buscar os episódios diretamente pelas pessoas entrevistadas ou por editorias de interesse.

[![ACESSE O CÓDIGO COMPLETO](https://img.shields.io/badge/Installation-EF2D5E?style=for-the-badge&logoColor=white&logo=DocuSign)](https://github.com/cindydamasceno/rodai/tree/main/llm-rodai-por-nos)


## Metodologia
A metodologia aplicada para desenvolver o RodAI busca por automação e processamento de dados. Foi utilizado um notebook do Kaggle e modelo LLM do Whisper para transcrever o episódio. Os dados são armazenados em uma coleção no MongoDB para processamento posterior, enquanto uma mensagem é enviada via Telegram para confirmar a operação.


## Limitações
Em razão das inserções comerciais do próprio programa Roda Viva, em comemoração aos 55 anos no ar, o processamento não conseguiu diferenciar o que eram os episódios atuais do conteúdo publicitário. Por isso, as transcrições, em alguns casos, acabaram incorporando frases de convidados de programas antigos ao programa recente que estava sendo processado. Talvez haja a necessidade de pré-processar o conteúdo no MongoDB.


