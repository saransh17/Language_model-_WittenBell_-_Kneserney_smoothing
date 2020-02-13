import os
import re
import sys
from itertools import chain
from glob import glob

unigrams={}
bigrams={}
trigrams={}

def clean(data,num):
    data = data.lower()
    if num ==1:
        data = re.sub("\d","",data)
        data = re.sub("[()~@#$%&*}{/=_"''"]"," ",data)
        data = re.sub("[?,!;:]\n",".\n",data)
        data = re.sub('\n+','\n',data)
        data = re.sub('[*]','', data)
    return data


def grams(data,num):
    i = 0
    count=0
    if num == 1:
        for line in data.split("."):
            tokens = line.split(" ")
            while i <= len(tokens)-1:
                if tokens[i] not in unigrams:
                    unigrams[tokens[i]] = 1
                else:
                    unigrams[tokens[i]] += 1
                i += 1
        return unigrams


    if num == 2:
        for line in data.split("."):
            tokens = line.split(" ")
            while i <= len(tokens)-2:
                if tokens[i] in bigrams:
                    if tokens[i+1] in bigrams[tokens[i]]:
                        bigrams[tokens[i]][tokens[i+1]] += 1 
                    else:
                        count+=1
                        bigrams[tokens[i]][tokens[i+1]] = 1

                else:
                    bigrams[tokens[i]] = {}
                    if tokens[i+1] in bigrams[tokens[i]]:
                        bigrams[tokens[i]][tokens[i+1]] += 1 
                    else:
                        bigrams[tokens[i]][tokens[i+1]] = 1
                i += 1                
        return bigrams

    if num == 3:
        for line in data.split("."):
            tokens = line.split(" ")
            while i <= len(tokens)-3:
                if tokens[i] in trigrams:
                    #print("was")
                    count+=1
                else:
                    trigrams[tokens[i]] = {}
                
                if tokens[i+1] in trigrams[tokens[i]]:
                    count+=1
                else:
                    trigrams[tokens[i]][tokens[i+1]] = {}

                if tokens[i+2] in trigrams[tokens[i]][tokens[i+1]]:
                    count+=1
                    trigrams[tokens[i]][tokens[i+1]][tokens[i+2]] += 1 
                else:
                    trigrams[tokens[i]][tokens[i+1]][tokens[i+2]] = 1
                i += 1
        return trigrams
def k_n1(w1, w2):
    flag1=0
    flag2=0
    bi_count = 0
    context = []
    tri_count = 0
    para = 2
    if w1 in unigrams:
        flag1=1
    if w2 in unigrams:
        flag2=1

    if flag1==0:
        unigrams[w1] = float(1/2)
    if w1 not in bigrams:
        bigrams[w1] = {}

    if flag2==0:
        unigrams[w2] = float(1/2)
    if w2 not in bigrams[w1]:
        bigrams[w1][w2] = float(1/4)
    
    for w in bigrams:
        if w1 in bigrams[w]:
            bi_count +=1
    
    for w in trigrams:
        if w1 in trigrams[w]:
            if w2 in trigrams[w][w1]:
                tri_count += 1
    
    prob = (tri_count-para)/float(bi_count)
    if prob<=0:
        prob=0
    return prob+(para/unigrams[w1])*(len(bigrams[w1]))*(unigrams[w2]/sum(unigrams.values()))

def lp(w):
    prob = 1/(sum(unigrams.values())+len(unigrams))
    if w in unigrams:
        prob += unigrams[w]/(sum(unigrams.values())+len(unigrams))
    return prob

def k_n2(w1, w2, w3):

    if w1 in bigrams:
        context=[]
    else:
        bigrams[w1] = {}
    if w1 not in trigrams:
        trigrams[w1] = {}

    if w2 in bigrams:
        context.append(w2)
    else:
        bigrams[w2] = {}
    if w2 not in bigrams[w1]:
        bigrams[w1][w2] = float(1/2)
    if w2 not in trigrams[w1]:
        trigrams[w1][w2] = {}

    if w3 not in bigrams[w2]:
        bigrams[w2][w3] = float(1/2)
    if w3 not in trigrams[w1][w2]:
        trigrams[w1][w2][w3] = float(1/4)

    d = 0.75#as in slides
    prob = (trigrams[w1][w2][w3]-d)/float(bigrams[w2][w3])
    if prob <=0:
        prob=0
    
    prob += (d/bigrams[w1][w2])*(len(trigrams[w1][w2]))*k_n1(w2,w3)
    return prob

def w_b(w1,w2):#witten Bell
    flag1=0
    flag2=0
    if w1 in unigrams:
        flag1=1
    if w2 in unigrams:
        flag2 = 1

    if flag1==0:
        unigrams[w1] = float(1/2)
    if w1 not in bigrams:
        bigrams[w1] = {}

    if flag2==0:
        unigrams[w2] = float(1/2)
    if w2 not in bigrams[w1]:
        bigrams[w1][w2] = float(1/4)
    den=unigrams[w1]+ len(bigrams[w1])
    lenb=len(bigrams[w1])
        
    if bigrams[w1][w2] > 0:
        prob = float(bigrams[w1][w2]/den)

    else:
        prob = float(lenb/((len(bigrams)-lenb)*den))
    
    wb=float(bigrams[w1][w2]/(bigrams[w1][w2]+sum((bigrams[w1].values()))))
    return ((wb)*prob+(1-wb)*unigrams[w2]/float(sum(unigrams.values())))

def w_b2(w1,w2,w3):
    flag1=0
    flag2=0
    flag3=0
    if w1 in bigrams:
        flag1=1
    if w2 in bigrams:
        flag2=1
    if w3 in bigrams:
        flag3=1

    if flag1 !=1:
        bigrams[w1] = {}
    if w1 not in trigrams:
        trigrams[w1] = {}

    if flag2!=1:
        bigrams[w1][w2] = float(1/4)
    if w2 not in trigrams[w1]:
        trigrams[w1][w2] = {}

    if flag3!=1:
        trigrams[w1][w2][w3] = float(1/4)

    dent=float(bigrams[w1][w2]+len(trigrams[w1][w2]))
    t_flag=trigrams[w1][w2][w3]
    if trigrams[w1][w2][w3] > 0:
        prob = float(trigrams[w1][w2][w3])/dent
    else:
        prob = float(len(trigrams[w1][w2]))/float(dent*(len(trigrams) -len(trigrams[w1][w2])))
    
    wb=1-t_flag/float(t_flag+sum((trigrams[w1][w2]).values()))
    return((wb)*prob+(1-wb)*w_b(w2, w3))    

if __name__ == '__main__':
    
    n_type = sys.argv[1]
    s_type = sys.argv[2]
    f = sys.argv[3]
    data = open(f)
    train_data = data.read()
    train_data = clean(train_data,1)

    inp = input("input sentence: ")
    inp = clean(inp,2)
    tokens = inp.split(' ')
    ans = 1
    i = 0
    inp_length = len(tokens)
    
    unigrams = grams(train_data,1)
    bigrams = grams(train_data,2)
    trigrams = grams(train_data,3)
    
    if s_type == 'k':
        
        if n_type == '1':
            while i <= inp_length - 2:
                prob = lp(tokens[i])
                ans *= prob
                i += 1
            print(ans)

        elif n_type == '2':
            while i < inp_length - 1:
                prob = k_n1(tokens[i], tokens[i+1])
                ans *= prob
                i += 1
            print(ans)

        elif n_type == '3':
            while i < inp_length - 2:
                prob = k_n2(tokens[i], tokens[i+1], tokens[i+2])
                ans *= prob
                i += 1
            print(ans)
        else:
            print("Invalid")

    elif s_type == 'w':
        
        if n_type == '1':
            while i < inp_length - 1:
                prob = lp(tokens[i])
                ans *= prob
                i += 1
            print(ans)

        elif n_type == '2':
            while i < inp_length - 1:
                prob = w_b(tokens[i], tokens[i+1])
                ans *= prob
                i += 1
            print(ans)

        elif n_type == '3':
            while i < inp_length - 2:
                prob = w_b2(tokens[i],tokens[i+1],tokens[i+2])
                ans *= prob
                i +=1
            print(ans)

        else:
            print("Invalid")
    else:
        print("Invalid")
    
