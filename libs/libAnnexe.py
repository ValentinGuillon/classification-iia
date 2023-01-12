

#lit un fichier de données, puis retourne chacune d'elle dans une liste
def extractDatas(path:str, separator:str) -> list[list[str]]:
    datas:list[list[str]] = []

    with open(path, 'r') as file:
        for line in file:
            datas.append(line[:-1].split(separator))

    return datas






#on retourne un dictionnaire contenant chaque attribut de la classe avec leurs modalités
def determineAttributs(datas:list[list[str]], attsName) -> dict[list[str]]:

    # test = 0
    nbAtt = len(datas[0])
    tempAtt = {}

    #on initialise des emplacement vide dans le dict
    for i in range(nbAtt):
        tempAtt[i] = []


    #on remplis le dico
    for data in datas:
        for i, modality in enumerate(data):
            if not modality in tempAtt[i]:
                tempAtt[i].append(modality)


    #on renomme les clés du dict
    attributs = {}
    i = 0
    for key in tempAtt.keys():
        attributs[attsName[i]] = tempAtt[key].copy()
        i += 1

    return attributs
    





def printTab(x):
    if x == 0:
        return
    print("|   ", end="")
    printTab(x-1)



#retourne la plus grande valeur de la liste
def greater(numbers:list[int]):
    res = numbers[0]

    for n in numbers:
        if n > res:
            res = n

    return res



