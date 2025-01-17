import os.path

import pandas as pd
from flask import Flask, render_template, redirect, request, url_for, make_response

from functions import ReturnWeatherVerdict, FinalVerdict, ReturnHighestPercentage

app = Flask(__name__, template_folder="templates")

if not os.path.exists("polls.csv"):
    structure = {
        "id": [],
        "area": [],
        "location": [],
        "verdict": [],

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

polls_df = pd.read_csv("polls.csv").set_index("id")

@app.route("/")
def index():
    return render_template("index.html", polls=polls_df)

@app.route("/polls/<pollId>")
def polls(pollId):
    poll = polls_df.loc[int(pollId)]
    return render_template("show_poll.html", poll=poll)

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