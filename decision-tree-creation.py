#créer un arbre de décision à partir d'une base de données (fichier txt (.data))

#désolé, des fois y'a de l'anglais, des fois du français

import libs.libAnnexe as lib



treePrintingMod = "tab" #"tab" or "block", mode d'affichage de l'arbre dans le terminal
createGraph:bool = False #permet un formatage adapté à un fichier .dot (graph) (s'affiche dans le terminal)


#data base informations

name = "agaricus-lepiota" #nom de la BdD (purement décoratif)
filePath = "data_base/agaricus-lepiota.data" #fichier de la BdD
classPos = 0 #position de la classe dans les données (0 = 1er élément)
attributsName = ["Class", "cap-shape", "cap-surface", "cap-color", "bruises?", "odor", "gill-attachment", "gill-spacing", "gill-size", "gill-color", "stalk-shape", "stalk-root", "stalk-surface-above-ring", "stalk-surface-below-ring", "stalk-color-above-ring", "stalk-color-below-ring", "veil-type",  "veil-color", "ring-number", "ring-type", "spore-print-color", "population", "habitat"] #!!! doivent obligatoirement être ordonnés de la même manière que les données
modalitiesToIgnore:list[str] = ['?'] #tout attributs confondu, afin de ne pas créer de branches inutiles





class Tree():
    def __init__(self, classe:tuple[str|list[str]], attributs:dict[list[str]], datas:list[list[str]], modality, profondeur):
        self.attribut = ("ROOT", []) #nom, modalités
        self.modality = modality #une des modalités du parent
        self.subTrees = {} #il doit y avoir autant de subTrees que de modalité à "self.attribut"


        self.profondeur = profondeur #used in self.printTree()

        self.fillTree(classe, attributs, datas)








    #retourne le nombre de noeuds de l'arbre
    def nbNodes(self) -> int:
        if len(self.subTrees) == 0:
            return 1
        
        res = 0

        for subT in self.subTrees.values():
            res += subT.nbNodes()
        
        return 1 + res


    #retourne la hauteur de l'arbre
    def height(self) -> int:
        if len(self.subTrees) == 0:
            return 0
        
        subTreesHeight:list[int] = []
        for subT in self.subTrees.values():
            subTreesHeight.append(1 + subT.height())

        return lib.greater(subTreesHeight)


    #retourne le nombre de feuilles de l'arbre
    def nbLeaves(self):
        if len(self.subTrees) == 0:
            return 1
        
        res = 0
        for subT in self.subTrees.values():
            res += subT.nbLeaves()

        return res







    def printTreeForPdfContent(self):
        for name, subT in self.subTrees.items():
            print(f"\t{self.modality} -> {self.attribut[0]}_{name}")
            subT.printTreeForPdfContent()

    #affiche l'arbre (parcours préfixe), formaté pour un fichier .dot
    def printTreeForPDF(self):
        print("digraph G {")
        self.printTreeForPdfContent()
        print("}")



    #affiche l'arbre (parcours préfixe) "joliment" formaté dans le terminal
    def printTreeWithTab(self):
        print()
        lib.printTab(self.profondeur)

        print(f"{self.modality} : {self.attribut[0]}", end="")

        #si le neoud à des sous arbres...
        if len(self.subTrees) > 0:
            for subT in self.subTrees.values():
                subT.printTreeWithTab()



    #affiche l'arbre (parcours préfixe) sans (peu) formatage dans le terminal
    def printTreeOneBlock(self):
        if self.profondeur % 3 == 0:
            print("(", end="")
        elif self.profondeur % 2 == 0:
            print("{", end="")
        else:
            print("[", end="")

        print(f"{self.modality}:{self.attribut[0]}", end="")

        #si le neoud à des sous arbres...
        if len(self.subTrees) > 0:
            print(", ", end="")
            pass
            
            for i, subT in enumerate(self.subTrees.values(), start=1):
                subT.printTreeOneBlock()

                if i < len(self.subTrees):
                    print(", ", end="")
                    pass
                
        if self.profondeur % 3 == 0:
            print(")", end="")
        elif self.profondeur % 2 == 0:
            print("}", end="")
        else:
            print("]", end="")



    def printTree(self, mod):
        if mod == "tab":
            self.printTreeWithTab()
        elif mod == "block":
            self.printTreeOneBlock()
        else:
            print(f'ERROR: in printTree\n\tprinting mod "{mod}" doesn\'t exists (except: tab, block)\n')












    def fillTree(self, classe:tuple[str|list[str]], attributs:dict[list[str]], datas:list[list[str]]) -> None:
        #s'il ne reste qu'une seule donnée à traiter
        if len(datas) == 1:
            self.attribut = ("LEAF", [])
            return

        #si tous les attributs on été traité, ou qu'il n'y a plus de données
        if len(attributs) == 0 or len(datas) == 0:
            return


        #=== SMALLEST ENTROPIE =========================
        #trouver l'attribut ayant la plus faible entropie

        smallestEntropie:float = 1.0 #greatest possible value

        for i, (att, modalities) in enumerate(attributs.items()):
            #si on trouve un attribut avec une entropie null (donc la plus petit valeur possible)
            # if (smallestEntropie == 0):
            #     break

            #si c'est la première boucle du for
            if not i:
                smallestEntropie = entropy(classe, modalities, datas, 0)
                self.attribut = (att, modalities)

            else:
                tempEnt = entropy(classe, modalities, datas, i)
                
                if (smallestEntropie > tempEnt):
                    smallestEntropie = tempEnt
                    self.attribut = (att, modalities)


        #on va chercher la position de l'att ayant la plus faible entropie, dans attributs
        index = 0 #index d'un attribut dans "attributs"
        for att_name in attributs.keys():
            if att_name == self.attribut[0]: #rappel, attribut est un tuple ("name", modalities:list)
                break
            index += 1
                
        #=== END SMALLEST ENTROPIE =====================


        self.createSubTrees(classe, attributs, datas, index)




    def createSubTrees(self, classe, attributs, datas, index) -> None:
        #append autant de Tree() à "self.subTrees" qu'il y'a de modalités à "self.attribut"

        #pour chaque modalité de "self.attribut"
        for modality in self.attribut[1]:
            if modality in modalitiesToIgnore:
                continue

            newAtts = attributs.copy()
            newDatas = [] #on va append une copy de chaques n de "datas" (sinon, les éléments de "datas" seront modifiés, et on ne veux pas)

            for n in datas:
                newDatas.append(n.copy())


            #on retire les datas qui n'ont pas la bonne modalité
            #ou la valeur à la position correspondant à l'attribut
            j = 0 #index dans la liste des états (newDatas)
            #rappel : index = index d'un attribut dans le dico des attributs (attributs)
            
            while j < len(newDatas):

                #on retire l'état de la liste
                if not newDatas[j][index] == modality:
                    newDatas.pop(j)
                
                else:
                    j += 1
                

            #on retire la valeur de chaque état à l'indice correspondant à la position de l'attribut dans "attributs"
            for e in newDatas:
                e.pop(index)

            #on retire l'attribut de la liste
            newAtts.pop(self.attribut[0])

            #on ajoute un subTree, en lui donnant les attributs et états restants
            if (len(newDatas) > 0 and len(newAtts) > 0):
                subTreeModality = self.attribut[0] + "=" + modality
                self.subTrees[subTreeModality] = Tree(classe, newAtts, newDatas, subTreeModality, self.profondeur + 1)
                
            else:
                return




#=== FIN DE LA CLASSE Tree() ==============

















#la somme, pour chaque modalité (k) de la classe (C), de la proba de Ai sachant Ck au carré
def giniSommeCSachantAi(classe, Ai, datas, index, numerateurAi): #name ici juste pour le débug, à retirer
    somme = 0


    for k in classe[1]:
        nbAiCk = 0 #nb d'apparition d'une modalité, sachant la modalité de la classe
        for e in datas:
            if e[-1] == k and e[index] == Ai:
                nbAiCk += 1


        somme += (nbAiCk / numerateurAi) ** 2
    
    return somme
    


#attribut:list des mod d'un attribut, index = position de l'attribut dans "attributs"
def entropy(classe, attribut, datas, index):
    res = 0
    denomi = len(datas)

    for i in attribut: #i est une modalité de l'attribut
        #on compte dans combien d'états est "i"
        nbAi = 0 #proba d'une modalité
        for e in datas:
            if e[index] == i:
                nbAi += 1

        if nbAi == 0:
            pass
        else:
            res += (nbAi / denomi) * (1 - giniSommeCSachantAi(classe, i, datas, index, nbAi))

    return res

    








 


def main():
    #datas informations
    datas     :list[list[str]]      = [] #liste des données (une donnée étant une liste de str)
    attributs :dict[list[str]]      = {} #attributs de la classe ("name": [modalities])
    classe    :tuple[str|list[str]] = () #classe of datas ("name", [modalities])


    if not createGraph:
        print("Préparation des données...")
    #=== RÉCUPÉRATION ET FORMATAGE DES DONNÉES ==========================
    datas = lib.extractDatas(filePath, ',')


    attributs = lib.determineAttributs(datas, attributsName)

    

    #on retire la classe de la liste, qu'on va isoler
    for key, val in attributs.items():
        if key == attributsName[classPos]:
            classe = (key, val)
            attributs.pop(key)
            break


    #on retire les modalités interdites
    for key, val in attributs.items():
        i = 0
        while 1:
            if i == len(val):
                break

            if val[i] in modalitiesToIgnore:
                val.pop(i)
                continue

            i += 1


    #pour chaque données, on place la valeur correspondant à la classe en fin de liste
    if not classPos >= len(datas[0]) - 1:
        for n in datas:
            x = n.pop(classPos)
            n.append(x)

    #=== FIN === RÉCUPÉRATION ET FORMATAGE DES DONNÉES =================
    if not createGraph:
        print("Données prêtes !")


    if not createGraph:
        print("Création de l'arbre...")
    tree = Tree(classe, attributs, datas, "ROOT", 0)
    if not createGraph:
        print("Arbre créé !")



    if createGraph:
        tree.printTreeForPDF()
        return

    else:
        tree.printTree(treePrintingMod)
        print("\n\nArbre affichée !\n")
        print("Nombre de noeuds :", tree.nbNodes())
        print("Nombre de feuilles :", tree.nbLeaves())
        print(f"\nDatabase : {name} (https://archive.ics.uci.edu/ml/datasets/Mushroom)\n")





if __name__=="__main__":
    main()
