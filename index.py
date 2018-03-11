import bs4 as bs
import lxml
from nltk import word_tokenize
import time
import sys
from urlparse import urlparse
import json
import re
import math
from stop_words import get_stop_words

database = {}
title_index = {}
high_tier = {}
low_tier = {}
folder_num = 75
file_num =500
Count = 0
filter_list = ['body', 'title', 'h1', 'h2', 'h3', 'b', 'strong']
Length = {} #doc : doc length(used in vector cosine normalization)

#{"info":{file1:3, ...}}

def is_valid(url):
    parsed = urlparse(url)
    has_Calendar = re.match("^.*calendar.*$", parsed.path.lower())
    has_RepeatedDir = re.match("^.*?(/.+?/).*?\1$|^.*/(.+?/)\2.*$", parsed.path.lower())
    has_LongUrl = len(parsed.path.lower()) > 170

    boolean_ret = not re.match(".*\.(css|js|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4"\
            + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf" \
            + "|ps|eps|tex|ppt|pptx|doc|docx|txt|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" \
            + "|thmx|mso|arff|rtf|jar|csv"\
            + "|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())\
            and not has_Calendar and not has_RepeatedDir and not has_LongUrl and "txt" not in url[-3:]
    if boolean_ret == False:
        global Count
        Count+=1
    return boolean_ret

def collect(word_bag, file):
    squared_sum=0
    for term in set(word_bag):
        tf = word_bag.count(term)
        weighted_tf = 1 + math.log(tf,10)
        squared_sum += math.pow(weighted_tf,2)
        if term in database:
            database[term][file] = weighted_tf
        else:
            database[term] = {file:weighted_tf}
    Length[file] = math.sqrt(squared_sum)
    #used for cosine calculation

def build_title(title_bag,file):
    for term in set(title_bag):
        tf = title_bag.count(term)
        if term in title_index:
            title_index[term][file] = tf
        else:
            title_index[term] = {file:tf}


def tokenize(soup):
    word_bag = []
    for w in word_tokenize(soup.get_text().lower()):
        w = re.sub('[^a-zA-Z0-9]',' ',w)
        #substitute a white space for all non-alphanumeric characters 
        terms = w.split(  )#words is  a list of all words in a line
        for term in terms:
            if term not in get_stop_words('english'):
                word_bag.append(term)
    return word_bag

def tokenize_title(soup):
    title_bag = []
    for w in word_tokenize(soup.title.string.lower()):
        w = re.sub('[^a-zA-Z0-9]',' ',w)
        #substitute a white space for all non-alphanumeric characters 
        terms = w.split(  )#words is  a list of all words in a line
        for term in terms:
            if term not in get_stop_words('english'):
                title_bag.append(term)
    return title_bag

#def tokenize_bold(soup):
    
def tf_idf():
    N = len(database)
    for (word,posting) in database.iteritems():
        idf =  math.log(N/len(posting),10)
        for doc,tf in posting.iteritems():
            posting[doc] = (1 + math.log(tf,10)) * idf

def build_tier():
    for term,posting in database.iteritems():
        sorted_tf_posting = sorted(posting.items(),key = lambda v : -v[1])
        high_tier[term] = sorted_tf_posting[:20]
        low_tier[term] = sorted_tf_posting[20:]

def handle_json_file():
    with open("high_tier.json", "w") as file:
        json.dump(high_tier, file, indent=4)
    file.close()
    with open("low_tier.json", "w") as file:
        json.dump(low_tier, file, indent=4)
    file.close()

    with open("title_index.json","w") as file:
        json.dump(title_index, file, indent=4)
    file.close()
    with open("length.json", "w") as file:
        json.dump(Length, file, indent=4)
    file.close()

def main():
    with open("WEBPAGES_RAW/bookkeeping.json", "r") as op2:
        urls = json.load(op2)
    
    for i in range(folder_num):
        #print("-------- Folder ", i, "--------")
        if i == 74:
            global file_num
            file_num = 497
        for j in range(file_num):
            p_file_path = str(i)+"/"+str(j)
            
            if is_valid(urls[p_file_path]):
                file_path = "WEBPAGES_RAW/"+p_file_path
                fop = open(file_path, 'r')
                soup = bs.BeautifulSoup(fop, 'lxml')
                print("Working on ", file_path)
                word_bag= tokenize(soup)
                collect(word_bag, p_file_path)

                print("Working on metadata")
                if soup.title != None and soup.title.string != None:
                    title_bag = tokenize_title(soup)
                    build_title(title_bag,p_file_path)
                    
                fop.close()
        
        tf_idf()
        build_tier()
        handle_json_file()

start = time.time()
main()
end = time.time()





print("Time: ", end - start)
print('Count: ',Count)
print(len(database))
print(sys.getsizeof(database))

##with open("output.json", "r") as op:
##    readfile = json.load(op)
##with open("WEBPAGES_RAW/bookkeeping.json", "r") as op2:
##    urls = json.load(op2)
##count = 1
##for path in readfile["Irvine"]:
##    print(count, ". ", urls[path])
##    count += 1
##
##
##op.close()
##op2.close()
