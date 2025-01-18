import os.path

import pandas as pd
from flask import Flask, render_template, redirect, request, url_for, make_response

from functions import ReturnWeatherVerdict, FinalVerdict, ReturnHighestPercentage

app = Flask(__name__, template_folder="templates")

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
        # com o total de votos) convertido em string

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
    # Inicializa um Data Frame com a estrutura descrita acima e transfere os dados para o arquivo .csv
    pd.DataFrame(structure).set_index("id").to_csv("polls.csv")

# cria um Data Frame a ser usado no script para acessar e mudar valores

polls_df = pd.read_csv("polls.csv").set_index("id")

# O index recebe um Data Frame e imprime os seus índices (lugares de Brasília) um por um na tela da aplicação
@app.route("/")
def index():
    return render_template("index.html", polls=polls_df)

# Mostra as informações de um lugar específico (enquetes e resultados)
@app.route("/polls/<pollId>")
def polls(pollId):
    poll = polls_df.loc[int(pollId)]
    return render_template("show_location_info.html", poll=poll)

@app.route("/polls", methods=["GET", "POST"])
def create_poll():
    if request.method == "GET":
        return render_template("new_poll.html")
    elif request.method == "POST":
        area = request.form['area']
        location = request.form['location']
        polls_df.loc[max(polls_df.index.values) + 1] = [area,location,"Sem informações",
                                                        "Sem informações","Céu limpo","Pouco nublado","Nublado","Muito nublado",0,0,0,0,0,0,
                                                        "Sem informações","Sem chuva","Chuva leve","Chuva moderada","Chuva forte",0,0,0,0,0,0]
        
        polls_df.to_csv("polls.csv")
        return redirect(url_for("index"))

@app.route("/upvote/<pollId>/<pollPrefix>/<option>")
def upvote(pollId, pollPrefix ,option):
    polls_df.at[int(pollId), str(pollPrefix)+"votes"+str(option)] += 1
    polls_df.at[int(pollId), str(pollPrefix)+"votesTotal"] += 1
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
    response = make_response(redirect(url_for("polls", pollId=pollId)))
    return response

@app.route("/downvote/<pollId>/<pollPrefix>/<option>")
def downvote(pollId, pollPrefix, option):
    if(polls_df.at[int(pollId), str(pollPrefix)+"votes"+str(option)]) > 0:
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
    response = make_response(redirect(url_for("polls", pollId=pollId)))
    return response

if __name__ == "__main__":
    app.run(debug=True)