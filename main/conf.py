import tools
is_ill = lambda x,y,z : True if x != z else False
is_oov = lambda x,y,z : True if y == 'OOV' else False
spell = lambda x,y,z : not tools.spell_check(x)

SLANG = tools.get_slangs()

threshold=1.5
slang_threshold=1
max_val = [1., 1., 0.5, 0.0, 1.0, 0.5]
verbose=False
distance = 2

database='tweets2'

OOVFUNC = is_ill
wo_tag=False
with_degree=False
window_size = 7
NA_TAGS = ['#', ',', 'E', '~', 'U', '@'] # not available in db was ',','@'

#EMNLP setting
mydict20 = tools.db_tweets.nodes.find({'freq' : {"$gt": 20}}).distinct("node")
mydict20_filtered = filter(tools.spell_check,mydict20)

ovv_fun_20_filtered_extended = lambda x,y,z: not (x.lower() in mydict20_filtered) if tools.isvalid(x) and not tools.isHashtag(x) and not tools.isMention(x) and not tools.isURL(x) else False

mydict60 = tools.db_tweets.nodes.find({'freq' : {"$gt": 60}}).distinct("node")
mydict60_filtered = filter(tools.spell_check,mydict60)

ovv_fun_60_filtered_extended = lambda x,y,z: not (x.lower() in mydict60_filtered) if tools.isvalid(x) and not tools.isHashtag(x) and not tools.isMention(x) and not tools.isURL(x) else False

clean_words = tools.get_clean_words()
met_map = {}

# NAACL
FILTERCONTEXTUALCANDS = 1
