import mysql.connector
from mysql.connector import errorcode
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import sys
import collections

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
    'database': 'rm'
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
    d = {}
    query = ("SELECT id, strval FROM src_sents")
    cur.execute(query)
    for item in cur.fetchall():
        lst.append(item)
        d[item[0]] = item[1]

    print ("Sentences in queue: "+str(len(lst)))

    clusters = []
    clusters_boundries = {}
	
    print("Pre-populate clusters from cache ... ")
    query = ("SELECT id FROM src_sent_cluster WHERE parent_id = 0")
    cur.execute(query)
    for item in cur.fetchall():
        clusters.append(item[0])

    print("Pre-populate clusters-boundries from cache ... ")
    query = ("SELECT id, cluster_id, sent_id FROM src_sent_cluster_boundry_nodes")
    cur.execute(query)
    for item in cur.fetchall():
        clusters_boundries[item[0]] = [item[1], item[2]]
        
    
    print("Starting analysis ... ")


    import spacy
    nlp = spacy.load('en_core_web_lg')


    idx = 0
    for excerpt in lst:
        idx = idx + 1
        progress(idx, len(lst), "Clusters: {0}, Boundaries: {1}".format(str(len(clusters)), str(len(clusters_boundries))))
        src_doc_id = excerpt[0]
        doc = nlp(d[src_doc_id]) 
        connected = 0
        
        cluster_id = 0
        cluster_boundry_id = 0;
        
        # find cluster boundry, if not found, you are the boundry
        for key, boundry_node in clusters_boundries.iteritems():
            boundry_node_list = list(boundry_node)
#             print boundry_node
#             print boundry_node_list
            dst_doc_id = boundry_node_list[1]
            cluster_id = boundry_node_list[0]
            doc2 = nlp(d[dst_doc_id])
            simvalue = doc.similarity(doc2)
            if simvalue > 0.95:
                query = ("INSERT INTO src_sent_distances(src_sent_id, dst_sent_id, distance) VALUES (%s,%s,%s)")
                cur.execute(query, (str(src_doc_id), str(dst_doc_id), str(simvalue)))
                cnx.commit()
                connected = connected + 1

        if connected == 0:
        	# create a new cluster
            try:
                query = ("INSERT INTO src_sent_cluster(parent_id, description) VALUES (0, 'Untitled')")
                cur.execute(query)
                cnx.commit()
                cluster_id = cur.lastrowid
                clusters.append(cluster_id)
                query = ("INSERT INTO src_sent_cluster_boundry_nodes(cluster_id, sent_id) VALUES (%s,%s)")
                cur.execute(query, (str(cluster_id), str(src_doc_id)))
                cnx.commit()
                cluster_boundry_id = cur.lastrowid
                clusters_boundries[cluster_boundry_id] = [cluster_id, src_doc_id]
            except mysql.connector.Error as err:
                try:
                    print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
                except IndexError:
                    print "MySQL Error: %s" % str(e)
                    
        if connected > 1:
        	# create a new boundry node and 
#             print "Connected to another node"
#             print ""
            query = ("INSERT INTO src_sent_cluster_boundry_nodes(cluster_id, sent_id) VALUES (%s,%s)")
            cur.execute(query, (str(cluster_id), str(src_doc_id)))
            cnx.commit()
            cluster_boundry_id = cur.lastrowid
            clusters_boundries[cluster_boundry_id] = [cluster_id, src_doc_id]
            
    	connected = 0

        
    print("")

# 
#     print("Building feature weights ...")
# 	
#     tfidf = TfidfVectorizer(lowercase=False, )
#     tfidf.fit_transform(lst)
#     word2tfidf = dict(zip(tfidf.get_feature_names(), tfidf.idf_))
# 	
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
        cur.close()
    if cnx:
        cnx.commit()
        cnx.close()


    