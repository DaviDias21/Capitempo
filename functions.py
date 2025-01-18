def ReturnHighest(numbersList=[]):
    # Recebe uma lista de números e retorna o maior
    # Função auxiliar para as outras

    highestNumber=numbersList[0]
    for i in numbersList:
        if i > highestNumber:
            highestNumber = i
    
    return highestNumber

def ReturnWeatherVerdict(noOption : str, lowOption : str, avgOption : str, highOption : str,
                          votesNo : int, votesLow : int, votesAvg : int, votesHigh : int, votesTotal : int):
    # Conta os votos em cada opção e retorna uma string que descreve o evento mais votado
    # Em caso de empate, as opções são pesadas
    # com as seguintes prioridades (em ordem decrescente):
    # 1 - Evento com intensidade moderada
    # 2 - Evento com intensidade alta
    # 3 - Evento com intensidade baixa
    # 4 - Evento não está acontecendo

    highestVoteCount = ReturnHighest([votesNo,votesLow,votesAvg,votesHigh])
    
    if votesTotal == 0:
        return "Sem informações"
    else:
        if highestVoteCount == votesAvg:
            return avgOption
        elif highestVoteCount == votesHigh:
            return highOption
        elif highestVoteCount == votesLow:
            return lowOption
        elif highestVoteCount == votesNo:
            return noOption

def FinalVerdict(cloudVerdict : str, rainVerdict : str):
    
    if rainVerdict == "Sem informações":
        return cloudVerdict
    elif cloudVerdict == "Sem informações":
        return rainVerdict
    elif rainVerdict != "Sem chuva":
        return rainVerdict
    else:
        return cloudVerdict
    
def ReturnHighestPercentage(votesNo : int, votesLow : int, votesAvg : int, votesHigh : int, votesTotal : int):
    # Divide o número de votos da opção mais votada pelo total de votos e transforma-o em uma string
    # que contém o resultado até duas casas decimais seguido da
    highestVoteCount = ReturnHighest([votesNo, votesLow, votesAvg, votesHigh])

    if highestVoteCount <= 0: # No caso em que a opção mais votada tem zero votos (ou menos, no caso de algum erro),
                              # essa condição evita uma possível divisão por zero,
                              # assim como uma porcentagem negativa como resultado final.
        votingPercentage = 0
    else:
        votingPercentage = (float(highestVoteCount)/float(votesTotal))*100

    roundedPercentage=round(votingPercentage,2)
    return str(roundedPercentage)+"%"
    