import sys
import json
import math
from stop_words import get_stop_words
N = 257355
#N is the unique words in the dictionary
K = 10
#K is the number of ranked results returned for each query

def preprocess(query):
    q = []
    for term in query:
        if term not in get_stop_words('english'):
            q.append(term.lower())
    return q

def print_final_result(docs,urls):
    for i in docs:
        print(urls[i])

def query_tf_idf(query,high_tier,low_tier):
#tf_idf calculates the tf-idf score for each term in query.
    qdict = {}
    for w in query:
        if w not in qdict:
            qdict[w] =1
        else:
            qdict[w] +=1
    for w,tf in qdict.iteritems():
            df = len(high_tier[w]) + len(low_tier[w])
            qdict[w] = (1+math.log(tf,10))* math.log(N/df,10)  
    squared_sum = 0
    for w in qdict:
        squared_sum+= math.pow(qdict[w],2)
    query_length = math.sqrt(squared_sum)
    #Normalize the query length, used for cosine_score calculation.
    return (qdict,query_length)

def cosine_score(pool,q_tf,query_length,high_tier,Length):
    score = {}
    for w,tf in q_tf:
 #        qdict[w] = tf/query_length
        for doc,tf_d in high_tier[w]:
            if doc in pool:
                if doc not in score:
                    score[doc] = q_tf[w]*tf_d
                else:
                    score[doc] += q_tf[w]*tf_d
    for doc,sc in score.iteritems():
        score[doc] = sc/Length[doc]/query_length
    sorted_score = sorted(score.items(),key = lambda v: v[1],reverse = True)
    doc_list = []
    for i in range(K):
        doc_list.append(sorted_score[i][0])
    return doc_list

def single_term_retrieval(high_tier,title_index,query,urls):
    #single term retrieval,return the K docuents with the highest tf-idf in high_tier
    #combined with the appearance of the term in metadata "title"
    results = high_tier[query[0]]
    count = 0
    left_out = []
    for i in range(len(results)):
        if results[i][0] in title_index[query[0]]:
            count +=1
            print(urls[results[i][0]])
            if count == K:
                return
        else:
            left_out.append(results[i][0])
    for i in range(K-count):
        print(urls[leftout[i]])

def muliple_terms_retrieval(high_tier,low_tier,title_index,query,Length,urls):
        q_tf,query_length = query_tf_idf(query,high_tier,low_tier)
        #calculate the tf-idf score for all terms in query.
        q_tf = sorted(q_tf,key = lambda v:v[1],reverse=True)
        #sort tf-idf for query terms, so we consider the most important (rare) term first in
        #determining whether or not that document should be into the pool.
        pool = []
        pool_intersect = []
        eliminated =[ [] for i in len(q_tf)]
        #pool of the candidates for K documents
        i = 0
        for term,tf in q_tf:               
            ht = high_tier[term]
            ti = title_index[term]
            pool[i] = set([ht[i][0] for i in len(ht)] )| set([ti[i][0] for i in len(ti)])
            i+=1
            
        for doc in pool[0]:
            in_the_pool = True
            for i in range(1,len(q_tf)):
                in_the_pool = in_the_pool and doc in pool[i]
                if in_the_pool == False:
                    eliminated[i-1].append(doc)
                    break
            if in_the_pool:
                pool_intersect.append(doc)
        if len(pool_interesect) >= K:
            doc_list = cosine_score(pool_intersect,q_tf,query_length,high_tier,Length)
            print_final_result(doc_list,urls)
        else:
            for i in range(len(eliminated)-1,-1,-1):
                pool_intersect += eliminated[i] 
            pool_intersect = pool_intersect[:K]
            doc_list = cosine_score(pool_intersect,q_tf,query_length,high_tier,Length)
            print_final_result(doc_list,urls)

def ask_for_continue():
    print("Continue? y/n")
    if sys.argv[0] == "n" or sys.argv[0] == "no":
        return False
    else:
        return True

def main():
    with open("high_tier.json", "r") as fh:
        high_tier = json.load(fh)
    with open("low_tier.json", "r") as fl:
        low_tier = json.load(fl)
    with open("title_index.json", "r") as tit:
        title_index = json.load(tit)
    with open("length.json", "r") as flen:
        Length = json.load(flen)
    with open("WEBPAGES_RAW/bookkeeping.json", "r") as op2:
        urls = json.load(op2)

    Continue = True
    while (Continue):
        print("Please enter the search query: ")
        query = sys.argv[1:]
        print(query)
        query = preprocess(query)
        print(query)
        #lowercase all query terms, eliminate all stop words,
        if len(query) == 1:
            single_term_retrieval(high_tier,title_index,query,urls)           
        else:
            muliple_terms_retrieval(high_tier,low_tier,title_index,query,Length,urls)
        Continue = ask_for_continue()
    fh.close()
    fl.close()
    tit.close()
    flen.close()
    op2.close()

main()
