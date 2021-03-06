import normalizer
import CMUTweetTagger
import graph
#use tweets
#db.copyDatabase("tweets","tweets_current","localhost")
def update_edges_tag(database):
    tweets = [u"someone is cold game nd he needs to follow me",
          u"only 3mths left in school . i wil always mis my skull , frnds and my teachrs"]


    lot = CMUTweetTagger.runtagger_parse(tweets)

    norm = normalizer.Normalizer(lot,database)
#    tags = norm.nodes.distinct('tag')
    tags = [u'A',
            u'N',
            u'^',
            u'V',
            u'!',
            u'O',
            u'G',
            u'S',
            u'R',
            u',',
            u'P',
            u'Z',
            u'L',
            u'D',
            u'&',
            u'T',
            u'X',
            u'Y',
            u'M']
    for tag in tags:
        nouns = [node['node'] for node in filter(lambda x: x['freq']> 8, norm.nodes.find({'tag':tag}))]
        norm.edges.update({'from': { '$in' : nouns}},{'$set' : {u'from_tag':tag } },multi=True)
        norm.edges.update({'to': { '$in' : nouns}},{'$set' : {u'to_tag':tag } },multi=True)

def setDegrees(database):
    query = graph.db_tweets.nodes.find()
    for node in query:
        indegree = graph.db_tweets.edges.find({'to': node['node'], 'to_tag': node['tag']}).count()
        outdegree = graph.db_tweets.edges.find({'from': node['node'], 'from_tag': node['tag']}).count()
        graph.db_tweets.nodes.update({'node':node['node'], 'tag': node['tag']},
                                     {'$set' : {u'indegree':indegree, u'outdegree':outdegree }}, multi=False)
        #print(node)

def ensure_indexes(database):
    from pymongo import MongoClient
    client = MongoClient('localhost', 27017)
    db = client[database]

    db.edges.ensure_index([ ('to', 1) , ('from_tag', 1), ('to_tag', 1)] )
    db.edges.ensure_index([ ('from', 1) , ('from_tag', 1), ('to_tag', 1)] )
    db.edges.ensure_index('from_tag', 1)
    db.edges.ensure_index('to_tag', 1)
    # db.nodes.ensureIndex( { "to": 1, "to_tag": 1 ,"from_tag": 1 })
    # db.nodes.ensureIndex( { "from": 1, "from_tag": 1 ,"to_tag": 1 })
    # db.nodes.ensureIndex( { "from_tag": 1 })
    # db.nodes.ensureIndex( { "to_tag": 1 })

    db.nodes.ensure_index([ ('node', 1), ('tag', 1)], unique=True)
    # db.nodes.ensureIndex( { "node": 1, "tag": 1 }, { unique: true } )

if __name__ == "__main__":
    update_edges_tag()
