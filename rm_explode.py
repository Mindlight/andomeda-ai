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
    'database': 'rm',
    'charset': 'utf8',
    'use_unicode': True,
    'get_warnings': True,
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
    cur2 = cnx.cursor()
#     cur.execute('show databases;')
#     for row in cur.fetchall():
#         print(row)

    print("Selecting corpus ...")

    print("Loading NLP utilities ... ")

    import spacy
    nlp = spacy.load('en_core_web_lg')


    lst = []
    query = ("SELECT id, body FROM src")
    cur.execute(query)
    
    sources = cur.fetchall();


    print ("0) Recording sentences and entities")
    idx = 0
    total = len(sources)
    for item in sources:
        idx = idx + 1
        doc = nlp(item[1])
        progress(idx, total, "phase 0")
        for sent in doc.sents:
            query2 = ("INSERT INTO src_sents(src_id, strval) VALUES (%s,%s)")
            cur2.execute(query2, (str(item[0]), str(sent)) )
            sentenceid = cur2.lastrowid 
            sentdoc = sent.as_doc()           
            for ent in sentdoc.ents:
                query3 = ("INSERT INTO src_entities(src_id, src_sentence_id, entity, label) VALUES (%s,%s,%s,%s)")
                cur2.execute(query3, ((item[0]), str(sentenceid), (ent.text), (ent.label_) ) )
            for token in sentdoc:
                query3 = ("INSERT INTO src_postag(src_id, src_sentence_id, postext, lemma, pos, tag, dep, shape, alpha, stop) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
                cur2.execute(query3, ((item[0]), str(sentenceid), token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
          token.shape_, token.is_alpha, token.is_stop ) )
            

    cnx.commit()


#     print ("a) Recording article distance, only considering actor similarity")
#     print("")
#     
#     idx = 0
#     total = len(sources)*len(sources)
#     print(total)
#     for item in sources:
#         doc = nlp(item[1])
#         for item2 in sources:
#             doc2 = nlp(item2[1])
#             similarity = doc.similarity(doc2)
#             query = ("INSERT INTO src_doc_distance(src_id1, src_id2, distance) VALUES (%s,%s,%s)")
#             cur.execute(query, (str(item[0]), str(item2[0]), str(similarity)) )
#             idx = idx + 1
#             print(idx)            
# #             progress(idx, total, "calculating")
#             
#     cnx.commit()
    
    print("")
    
#     print ("b) Recording Sentences & Entities & Attributes")
#     for item in sources:
#         doc = nlp(item[1])
#         for sent in doc.sents:
#             print("---> " + str(item[0]))
#             query2 = ("INSERT INTO src_sents(src_id, strval) VALUES (%s,%s)")
#             cur2.execute(query2, (str(item[0]), str(sent)) )
# 
#     cnx.commit()


    ########################
    # Idea: when finding similarities, start with rough actor selection to limit scope and speed up relevancy
    ###

            
             
#     
#     
#         lst.append(item[0])
# 
#     print ("Articles in queue: "+str(len(lst)))
# 
#     print("Building feature weights ...")
# 	
#     tfidf = TfidfVectorizer(lowercase=False, )
#     tfidf.fit_transform(lst)
#     word2tfidf = dict(zip(tfidf.get_feature_names(), tfidf.idf_))
# 	
#     print("Loading NLP utilities ... ")
# 
#     import spacy
#     nlp = spacy.load('en_core_web_lg')
# 
#     vecs1 = []
#     idx = 0
#     for excerpt in lst:
#         idx = idx + 1
#         progress(idx, len(lst), "vectorizing")
#         doc = nlp(excerpt) 
#         for sent in doc.sents:
#             mean_vec = np.zeros([len(doc), 300])
#             for word in sent:
#                 # word2vec
#                 vec = word.vector
#                 # fetch df score
#                 try:
#                     idf = word2tfidf[str(word)]
#                 except:
#                     #print word
#                     idf = 0
#                 # compute final vec
#                 mean_vec += vec * idf
#             mean_vec = mean_vec.mean(axis=0)
#             vecs1.append(mean_vec)
#         
#         
#     print("")
#     
#     features = list(vecs1)
#     print ("Featurecount: "+str(len(features)))





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
        cur2.close()
        cur.close()
    if cnx:
        cnx.commit()
        cnx.close()


    