import sys
import json
import math
from stop_words import get_stop_words
N = 128678
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

def cosine_score(pool,q_tf,query_length,high_tier,low_tier,Length):
    score = {}
    print(q_tf)
    for term in q_tf:
        w =term[0]
        tf_q = term[1]
        #print(w)
        if low_tier[w][0][1] < 2:
            low =[]
        else:
            low= low_tier[w]
        for dtf in high_tier[w]+low:
            doc = dtf[0]
            tf_d = dtf[1]
            if doc in pool:
                if doc not in score:
                    score[doc] = tf_q * tf_d
                else:
                    score[doc] += tf_q*tf_d
    for doc,sc in score.iteritems():
        score[doc] = sc/Length[doc]/query_length
    sorted_score = sorted(score.items(),key = lambda v: v[1],reverse = True)
    return sorted_score

def retrieve_k_doc(score):
    doc_list = []
    if len(score) >= K:
        for i in range(K):
            doc_list.append(score[i][0])
    else:
        doc_list = [score[i][0] for i in range(len(score))]
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
        print(urls[left_out[i]])

def muliple_terms_retrieval(high_tier,low_tier,title_index,query,Length,urls):
        q_tf,query_length = query_tf_idf(query,high_tier,low_tier)
        #calculate the tf-idf score for all terms in query.
        q_tf = sorted(q_tf.items(),key = lambda v:-v[1])
        #sort tf-idf for query terms, so we consider the most important (rare) term first in
        #determining whether or not that document should be into the pool.
        pool = []
        pool_intersect = []
        eliminated =[ [] for i in range(len(q_tf))]
        #pool of the candidates for K documents
        #i=0
        for term in q_tf:               
            ht = high_tier[term[0]]
            ti = title_index[term[0]]
            #print(ti)
            pool_ht = set([ht[j][0] for j in range(len(ht))] )
            pool_ti = set([doc for doc in ti])
            pool.append(pool_ht.union(pool_ti))
            #i+=1

        for doc in pool[0]:
            in_the_pool = True
            for i in range(1,len(q_tf)):
                in_the_pool = in_the_pool and doc in pool[i]
                if in_the_pool == False:
                    eliminated[i-1].append(doc)
                    break
            if in_the_pool:
                pool_intersect.append(doc)
        if len(pool_intersect) >= K:
            #print("pool_intersect",pool_intersect)
            score = cosine_score(pool_intersect,q_tf,query_length,high_tier,low_tier,Length)
            doc_list = retrieve_k_doc(score)
            print_final_result(doc_list,urls)
        else:
            for i in range(len(eliminated)-1,-1,-1):
                pool_intersect += eliminated[i]
            #print("pool_intersect",pool_intersect)
            #pool_intersect = pool_intersect[:K]
            #print("pool_intersect",pool_intersect)
            score = cosine_score(pool_intersect[:30],q_tf,query_length,high_tier,low_tier,Length)
            doc_list = retrieve_k_doc(score)
            if len(doc_list) < 10:
                doc_set = set(doc_list).union(set(pool_intersect[:10]))
                doc_list = list(doc_set)
            print_final_result(doc_list,urls)

def ask_for_continue():
    ans = raw_input("Continue? y/n")
    if ans == "n" or ans == "no":
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
        try:
            query = raw_input("Please enter the search query: ").split()
            query = preprocess(query)
            #print(query)
            #lowercase all query terms, eliminate all stop words,
            if len(query) == 1:
                single_term_retrieval(high_tier,title_index,query,urls)           
            else:
                muliple_terms_retrieval(high_tier,low_tier,title_index,query,Length,urls)
        except:
            print("Invalid query")
            
        Continue = ask_for_continue()
    fh.close()
    fl.close()
    tit.close()
    flen.close()
    op2.close()

main()
