from leitura_de_arquivos import processamento_dos_dados
import gurobipy as gp
from gurobipy import GRB

def main():

    rj,dj,pj,wj = processamento_dos_dados('random_instance.txt')
    
    m = gp.Model("mip1")

    print(rj)
    print(dj)
    print(pj)
    print(wj)

    var_atrasos = []
    var_terminos = []
    ordem = []
    infinity = GRB.INFINITY

    
    #CRIAÇÃO DAS VARIÁVEIS BINÁRIAS QUE DEFINEM A ORDEM DOS PEDIDOS
    i=0
    aux = 1
    while(aux <=len(rj)): #Criação do nó fantasma
        decisao_ordem = m.addVar(vtype=GRB.BINARY, name='x'+str(0)+str(aux))
        ordem.append(decisao_ordem)
        aux+=1
    LinExpr = gp.LinExpr()
    while(i < len(rj)):
        LinExpr.add(ordem[-len(rj):][i], 1)
        i+=1
    m.addConstr(LinExpr == 1, 'Rs0') #Restrição do somatório das saídas em um nó fantasma == 1
    del LinExpr

    i = 1
    j = 1
    while(i <= len(rj)): #Criação dos nós das tarefas
        while(j <= len(rj)):
            if(i != j):
                decisao_ordem = m.addVar(vtype=GRB.BINARY, name='x'+str(i)+str(j))
                ordem.append(decisao_ordem)
            j+=1
        aux=0
        LinExpr = gp.LinExpr()
        while(aux < len(rj)-1):
            LinExpr.add(ordem[-(len(rj)-1):][aux], 1)
            aux+=1
        m.addConstr(LinExpr == 1, 'Rs'+str(i)) #Restrição do somatório das saídas em um nó de tarefas == 1
        del LinExpr
        j=1
        i+=1
    
    i = 1                     
    j = 1
    aux=1
    while(i <= len(rj)):
        cont = 0
        arrayProvisorio = []
        LinExpr = gp.LinExpr()
        while(j <= len(ordem[-(len(ordem)-len(rj)):])):
            arrayProvisorio.append(ordem[-(len(ordem)-len(rj)):][j-1])
            if(aux==len(arrayProvisorio)):
                j+=(2*(len(rj)))-1
            else:
                j=j+len(rj)-1
        while(cont < len(arrayProvisorio)):
            LinExpr.add(arrayProvisorio[cont], 1)
            cont+=1
        if(i==len(rj)):
            LinExpr.add(ordem[0], 1)
            m.addConstr(LinExpr == 1, 'Re'+str(i))
        else:
            LinExpr.add(ordem[i], 1)
            m.addConstr(LinExpr == 1, 'Re'+str(i))

        i+=1
        j=i
        aux=i
        del arrayProvisorio
        del LinExpr
    
        
    #CRIAÇÃO DAS VARIÁVEIS INTEIRAS QUE DEFINEM AS RESTRIÇÕES DE TÉRMINO 
    i = 1
    var_terminos.append(m.addVar(ub=0, name='vy0')) #Término do nó fantasma (y0)
    while(i <= len(rj)):
        termino = m.addVar(ub=infinity, name ='vy'+str(i))
        termino.vType = GRB.INTEGER
        var_terminos.append(termino)
        i+=1
    
    #CRIAÇÃO DAS VARIÁVEIS INTEIRAS QUE DEFINEM AS RESTRIÇÕES DE ATRASO
    i = 1
    var_atrasos.append(m.addVar(ub=0, name='va0')) #atraso do nó fantasma (y0)
    while(i <= len(rj)):
        atraso = m.addVar(ub=infinity, name ='va'+str(i))
        atraso.vType = GRB.INTEGER
        var_atrasos.append(atraso)
        i+=1

    #CRIAÇÃO DAS RESTRIÇÕES DE TÉRMINO
    i = 1
    m.addConstr(var_terminos[0] == 0, 'y0')
    while(i <= len(rj)):
        m.addConstr(var_terminos[i] >= dj[i-1] + rj[i-1], 'y'+str(i))
        i+=1
    
    #CRIAÇÃO DAS RESTRIÇÕES DE ATRASO
    i = 1
    m.addConstr(var_atrasos[0] == 0, 'a0')

    while(i <= len(rj)):
        m.addConstr(var_atrasos[i] >= var_terminos[i] - pj[i-1], 'a'+str(i))
        m.addConstr(var_atrasos[i] >= 0, 'ca'+str(i))
        i+=1

    #CRIAÇÃO DAS RESTRIÇÕES DE TÉRMINOS Yj >= Yi + dj - ((1 - Xij)M)
    i = 1
    j = 0
    cont = 0
    bigM = 1e10
    
    


    while(i <= len(rj)):
        aux = i-1
        j=0
        while(j < len(rj)+1):
            m.addConstr(var_terminos[i] >= var_terminos[j] + dj[i-1] - (1 - ordem[aux])*bigM, 'Y'+str(i))
            if(j+1==i):
                aux+=(2*(len(rj))-1) 
                j+=2 
            else:
                aux+=len(rj)-1
                j+=1
        i+=1
    
    i = 1
    el = gp.LinExpr()
    while(i <= len(rj)):
        el.add(var_atrasos[i], wj[i-1])
        i+=1
    m.setObjective(el, GRB.MINIMIZE)
    m.optimize()
    print(m.display())
    




    
if __name__ == "__main__": 
    main()
