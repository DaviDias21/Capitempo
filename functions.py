def ReturnHighest(numbersList=[]):
    highestNumber=numbersList[0]
    for i in numbersList:
        if i > highestNumber:
            highestNumber = i
    
    return highestNumber

def ReturnWeatherVerdict(noOption : str, lowOption : str, avgOption : str, highOption : str,
                          votesNo : int, votesLow : int, votesAvg : int, votesHigh : int, votesTotal : int):

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
    highestVoteCount = ReturnHighest([votesNo, votesLow, votesAvg, votesHigh])
    if highestVoteCount == 0:
        votingPercentage = 0
    else:
        votingPercentage = (float(highestVoteCount)/float(votesTotal))*100

    roundedPercentage=round(votingPercentage,2)
    return str(roundedPercentage)+"%"
    