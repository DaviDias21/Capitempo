import os.path

import pandas as pd
from flask import Flask, render_template, redirect, request, url_for, make_response
from flask_apscheduler import APScheduler

from functions import ReturnWeatherVerdict, FinalVerdict, ReturnHighestPercentage

app = Flask(__name__, template_folder="templates")

sched = APScheduler()

# Inicializa o arquivo .csv que contém as informações das enquetes da aplicação.
# Quaisquer mudanças nos valores da aplicação são registrados no arquivo,
# o que garante a persistência dos dados.

if not os.path.exists("polls.csv"):
    # A estrutura 'structure' definida contém todos os dados necessários para as operações com as enquetes
    # e para a exibição das informações
    structure = {
        # 'id': único para uma determinada parte de Brasília (Esplanada, Rodoviária, etc.)
        # 'area': é a região do Plano Piloto à qual o lugar pertence (Norte, Sul, Central)
        # 'location': o nome do lugar
        # 'verdict': um breve resumo do tempo no lugar. Se está chovendo, mostra o nível da chuva. Se não, mostra o status das nuvens

        "id": [],
        "area": [],
        "location": [],
        "verdict": [],
        
        # Temos também as informações das enquetes. Cada lugar tem duas. Uma para as nuvens, uma para a chuva.
        # Estruturalmente, ambas são idênticas, com um resultado (opção mais votada), quatro estágios de evento climático,
        # (evento não acontecendo, evento pouco intenso, evento moderado, evento intenso), a contagem de votos para cada opção,
        # o número total de votos da enquete e uma porcentagem para a opção vencedora (a divisão dos votos da opção mais votada
        # com o total de votos) convertida em string

        # As enquetes recebem um prefixo para serem diferenciadas pelo script: 'c_' para clouds, ou nuvens; e 'r_' para rain, ou chuva

        "c_pollResult": [],
        "c_noOption": [],
        "c_lowOption": [],
        "c_avgOption": [],
        "c_highOption": [],
        "c_votesNo": [],
        "c_votesLow": [],
        "c_votesAvg": [],
        "c_votesHigh": [],
        "c_votesTotal": [],
        "c_highestPercentage" : [],

        "r_pollResult": [],
        "r_noOption": [],
        "r_lowOption": [],
        "r_avgOption": [],
        "r_highOption": [],
        "r_votesNo": [],
        "r_votesLow": [],
        "r_votesAvg": [],
        "r_votesHigh": [],
        "r_votesTotal": [],
        "r_highestPercentage" : []
    }
    pd.DataFrame(structure).set_index("id").to_csv("polls.csv")
    # Inicializa um Data Frame com a estrutura descrita acima e transfere os dados para o arquivo .csv

polls_df = pd.read_csv("polls.csv").set_index("id")
# cria um Data Frame a ser usado no script para acessar e mudar valores

cloudList = []
rainList = []

def downvoteAll():
    print("Votos diminuídos")
    for pollId in range(19):
        downvote(pollId+1, 'c_', 'No')
        downvote(pollId+1, 'c_', 'Low')
        downvote(pollId+1, 'c_', 'Avg')
        downvote(pollId+1, 'c_', 'High')
        
        downvote(pollId+1, 'r_', 'No')
        downvote(pollId+1, 'r_', 'Low')
        downvote(pollId+1, 'r_', 'Avg')
        downvote(pollId+1, 'r_', 'High')
        
        polls_df.to_csv("polls.csv")

@app.route("/")
# O index recebe um Data Frame e imprime os seus índices (lugares de Brasília) um por um na tela da aplicação
def index():
    return render_template("index.html", polls=polls_df)

@app.route("/polls/<pollId>", methods=["GET","POST"])
# Mostra as informações de um lugar específico (enquetes e resultados)
def polls(pollId):
    if request.method =="GET":
        poll = polls_df.loc[int(pollId)]
        return render_template("show_location_info.html", poll=poll)

    elif request.method=="POST":
        cloudList = request.form.getlist("cloudList")
        rainList = request.form.getlist("rainList")

        print(cloudList)
        print(rainList)

        if cloudList:
            for option in cloudList:
                upvote(pollId, "c_", option)

        if rainList:
            for option in rainList:
                upvote(pollId, "r_", option)
        
        cloudList.clear()
        rainList.clear()

        polls_df.to_csv("polls.csv")
        # Atualiza o arquivo .csv com as informações do Data Frame

        return redirect(url_for("polls", pollId=pollId))
        # Retorna para o endereço da enquete, com as informações atualizadas

@app.route("/polls", methods=["GET", "POST"])
# Nesse link ficam as informações da função de criar uma nova enquete: o link para a página de criação
# e os comandos executados após a submissão das informações necessárias (nome da área e nome do lugar)
def create_poll():
    if request.method == "GET":
        return render_template("new_poll.html")
    elif request.method == "POST":
        area = request.form['area']
        location = request.form['location']
        
        polls_df.loc[max(polls_df.index.values) + 1] = [area,location,"Sem informações",
                                                        "Sem informações","Céu limpo","Pouco nublado","Nublado","Muito nublado",0,0,0,0,0,0,
                                                        "Sem informações","Sem chuva","Chuva leve","Chuva moderada","Chuva forte",0,0,0,0,0,0]
        # Preenche a enquete recém-criada com os dados de inicialização
        # (nenhuma informação de tempo e nenhum voto registrado)
        
        polls_df.to_csv("polls.csv")
        return redirect(url_for("index"))

# Abaixo temos as funções de voto positivo e negativo.

# No Data Frame e no arquivo .csv, as variáveis de contagem de voto de ambas as enquetes
# recebem um prefixo e um sufixo, correspondentes: 1) à enquete a qual a opção pertence e
# 2) à intensidade do evento climático, respectivamente. Isso garante a reutilização das funções de voto
# para todas as opções das duas enquetes.

# Os prefixos são: 'c_' para a enquete de nuvens e 'r_' para a enquete de chuva
# Os sufixos são: 'No', o evento não está acontecendo, 'Low', evento com baixa intensidade,
# 'Avg', evento com intensidade moderada, 'High', evento com intensiade alta

@app.route("/upvote/<pollId>/<pollPrefix>/<option>")
def upvote(pollId, pollPrefix ,option): # Pega o id único do lugar,
                                        # o prefixo que indica a enquete e o sufixo que indica a opção votada
    
    polls_df.at[int(pollId), str(pollPrefix)+"votes"+str(option)] += 1 # incrementa 1 na opção do Data Frame

    polls_df.at[int(pollId), str(pollPrefix)+"votesTotal"] += 1 # incrementa 1 no total de votos

    polls_df.at[int(pollId), str(pollPrefix)+"pollResult"] = ReturnWeatherVerdict(polls_df.at[int(pollId), str(pollPrefix)+"noOption"],
                                                                                  polls_df.at[int(pollId), str(pollPrefix)+"lowOption"],
                                                                                  polls_df.at[int(pollId), str(pollPrefix)+"avgOption"],
                                                                                  polls_df.at[int(pollId), str(pollPrefix)+"highOption"],
                                                                                  polls_df.at[int(pollId), str(pollPrefix)+"votesNo"],
                                                                                  polls_df.at[int(pollId), str(pollPrefix)+"votesLow"],
                                                                                  polls_df.at[int(pollId), str(pollPrefix)+"votesAvg"],
                                                                                  polls_df.at[int(pollId), str(pollPrefix)+"votesHigh"],
                                                                                  polls_df.at[int(pollId), str(pollPrefix)+"votesTotal"])
    # A função acima recebe todas as opções de uma enquete com 
    # os seus votos e retorna a opção mais votada

    polls_df.at[int(pollId), str(pollPrefix)+"highestPercentage"] = ReturnHighestPercentage(polls_df.at[int(pollId), str(pollPrefix)+"votesNo"],
                                                                                            polls_df.at[int(pollId), str(pollPrefix)+"votesLow"],
                                                                                            polls_df.at[int(pollId), str(pollPrefix)+"votesAvg"],
                                                                                            polls_df.at[int(pollId), str(pollPrefix)+"votesHigh"],
                                                                                            polls_df.at[int(pollId), str(pollPrefix)+"votesTotal"],)
    # Retorna a porcentagem do resultado vencedor em relação ao total de votos

    polls_df.at[int(pollId), "verdict"] = FinalVerdict(polls_df.at[int(pollId), "c_pollResult"],
                                                       polls_df.at[int(pollId), "r_pollResult"])
    # Recebe os vereditos das duas enquetes e os pesa
    # pra mostrar o resultado mais relevante na página inicial
    
    return

@app.route("/downvote/<pollId>/<pollPrefix>/<option>")
def downvote(pollId, pollPrefix, option):
    if(polls_df.at[int(pollId), str(pollPrefix)+"votes"+str(option)]) > 0:
        # Realiza as mesmas ações que a função de voto positivo, só que subtraindo
        # um dos votos da opção e dos votos totais. A condição assegura que essa subtração só será feita
        # se o número atual de votos for positivo, ou seja,
        # ela evita que o número de votos seja um número negativo.

        polls_df.at[int(pollId), str(pollPrefix)+"votes"+str(option)] -= 1
        polls_df.at[int(pollId), str(pollPrefix)+"votesTotal"] -= 1
        polls_df.at[int(pollId), str(pollPrefix)+"pollResult"] = ReturnWeatherVerdict(polls_df.at[int(pollId), str(pollPrefix)+"noOption"],
                                                                                      polls_df.at[int(pollId), str(pollPrefix)+"lowOption"],
                                                                                      polls_df.at[int(pollId), str(pollPrefix)+"avgOption"],
                                                                                      polls_df.at[int(pollId), str(pollPrefix)+"highOption"],
                                                                                      polls_df.at[int(pollId), str(pollPrefix)+"votesNo"],
                                                                                      polls_df.at[int(pollId), str(pollPrefix)+"votesLow"],
                                                                                      polls_df.at[int(pollId), str(pollPrefix)+"votesAvg"],
                                                                                      polls_df.at[int(pollId), str(pollPrefix)+"votesHigh"],
                                                                                      polls_df.at[int(pollId), str(pollPrefix)+"votesTotal"])
        polls_df.at[int(pollId), str(pollPrefix)+"highestPercentage"] = ReturnHighestPercentage(polls_df.at[int(pollId), str(pollPrefix)+"votesNo"],
                                                                                                polls_df.at[int(pollId), str(pollPrefix)+"votesLow"],
                                                                                                polls_df.at[int(pollId), str(pollPrefix)+"votesAvg"],
                                                                                                polls_df.at[int(pollId), str(pollPrefix)+"votesHigh"],
                                                                                                polls_df.at[int(pollId), str(pollPrefix)+"votesTotal"],)
        polls_df.at[int(pollId), "verdict"] = FinalVerdict(polls_df.at[int(pollId), "c_pollResult"],
                                                           polls_df.at[int(pollId), "r_pollResult"])
        polls_df.to_csv("polls.csv")
    else:
        polls_df.at[int(pollId), str(pollPrefix)+"votes"+str(option)] = 0
    
    return

if __name__ == "__main__":
    sched.add_job(id='downvoteAll', func=downvoteAll, trigger='interval', minutes = 5)
    sched.start()
    app.run(debug=True, use_reloader=False)