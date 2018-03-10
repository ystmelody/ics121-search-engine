#print(sys.getsizeof(database))
import json
import math
#N is the unique words in the dictionary
#tf_idf calculates the tf-idf score for each document in posting
def tf_idf(N):
    for (word,posting) in database.iteritems():
        idf =  math.log(N/len(posting),10)
        for doc,tf in posting.iteritems():
            posting[doc] = (1 + math.log(tf,10)) * idf
#Normalize the document length

def cosine_score(query,database,K):
    #query list or dict?
    score = {}
    qdict = {}
    for w in query:
        if w not in qdict:
            qdict[w] =1
        else:
            qdict[w] +=1
    for w,tf in qdict.iteritems():
            qdict[w] = (1+math.log(tf,10))* math.log(N/len(database[w]))  
    squared_sum = 0
    for w in qdict:
        squared_sum+= math.pow(qdict[w],2)
        query_length = math.sqrt(squared_sum)
     for w,tf in qdict:
         qdict[w] = tf/query_length
         for doc,tf_d in database[w].iteritems():
                if doc not in score:
                    score[doc] = qdict[w]*tf_d
                else:
                    score[doc] += qdict[w]*tf_d
    for doc,sc in score.iteritems():
        score[doc] = sc/Length[doc]
    sorted_score = sorted(score.items(),key = lambda v: v[1],reverse = True)
    doc_list = []
    for i in range(K):
        doc_list.append(sorted_score[i][0])
    return doc_list
        
def main():
    with open("output.json", "r") as op:
        readfile = json.load(op)
    with open("WEBPAGES_RAW/bookkeeping.json", "r") as op2:
        urls = json.load(op2)
    count = 1
    for path in readfile["Irvine"]:
        print(count, ". ", urls[path])
       count += 1

    op.close()
    op2.close()

main()
