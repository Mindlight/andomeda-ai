import mysql.connector
from mysql.connector import errorcode
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import sys

# nlp.pipeline = [nlp.tagger, nlp.parser, SentimentAnalyser.load("./", nlp, max_length=100)]

def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()
    

config = {
    'user': 'ckd',
    'password': 'n0dr1gal',
    'host': '127.0.0.1',
    'database': 'gilead'
}

cnx = cur = None
try:
    cnx = mysql.connector.connect(**config)
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print('Something is wrong with your user name or password')
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
else:
    cur = cnx.cursor()
#     cur.execute('show databases;')
#     for row in cur.fetchall():
#         print(row)

    print("Selecting corpus ...")

    lst = []
    query = ("SELECT text FROM src WHERE Country='United Kingdom'")
    cur.execute(query)
    for item in cur.fetchall():
        lst.append(item[0])

    print ("Articles in queue: "+str(len(lst)))

    print("Building feature weights ...")
	
    tfidf = TfidfVectorizer(lowercase=False, )
    tfidf.fit_transform(lst)
    word2tfidf = dict(zip(tfidf.get_feature_names(), tfidf.idf_))
	
    print("Loading NLP utilities ... ")

    import spacy
    nlp = spacy.load('en_core_web_lg')

    vecs1 = []
    idx = 0
    for excerpt in lst:
        idx = idx + 1
        progress(idx, len(lst), "vectorizing")
        doc = nlp(excerpt) 
        for sent in doc.sents:
            mean_vec = np.zeros([len(doc), 300])
            for word in sent:
                # word2vec
                vec = word.vector
                # fetch df score
                try:
                    idf = word2tfidf[str(word)]
                except:
                    #print word
                    idf = 0
                # compute final vec
                mean_vec += vec * idf
            mean_vec = mean_vec.mean(axis=0)
            vecs1.append(mean_vec)
        
        
    print("")
    
    features = list(vecs1)
    print ("Featurecount: "+str(len(features)))





#     query = ("SELECT text FROM src WHERE Coverage1=1 AND Country='United Kingdom'")
#     cur.execute(query)
#     for (item) in cur.fetchall():
#         print("##################")
#         doc = nlp(item[0])
#         
#         for sent in doc.sents:
# 	        print("-->")
# 	        print (sent)
# 	        print sent.vector
# 	        print("<--")
# 	        
#         
#         for ent in doc.ents:
#             print(ent.text, ent.start_char, ent.end_char, ent.label_, doc.sentiment)

finally:
    if cur:
        cur.close()
    if cnx:
        cnx.close()


    