import conf,constants, standalone, time, analysis

annotated = standalone.construct_annotated(constants.pos_tagged, constants.results, conf.OOVFUNC)
annotated01 = standalone.construct_annotated(constants.pos_tagged[0:1], constants.results[0:1], conf.OOVFUNC)
#annotated05 = standalone.construct_annotated(constants.pos_tagged[0:5],
#                                             constants.results[0:5], conf.OOVFUNC)
#annotated010 = standalone.construct_annotated(constants.pos_tagged[0:10],
#                                             constants.results[0:10], conf.OOVFUNC)
#annotated0100 = standalone.construct_annotated(constants.pos_tagged[0:100],
#                                              constants.results[0:100], conf.OOVFUNC)
#annotated0200 = standalone.construct_annotated(constants.pos_tagged[0:200],
#                                              constants.results[0:200], conf.OOVFUNC)

def all_ordered():
    return all_un_ordered(ordered=True)

def all_un_ordered(ordered=False):
    start = time.time()
    a,e = standalone.norm_all(annotated,ordered)
    end = time.time()
    print("Time: %d" %(end - start))
    return a,e

def ordered(i,j):
    a,e = standalone.norm_all(annotated[i:j],True)
    return a,e

def un_ordered(i,j):
    a,e = standalone.norm_all(annotated[i:j],False)
    return a,e

def run(i,j):
    start = time.time()
    if i == 9 and j == 9:
        setcurrent = analysis.run([],[],[],None)
    else:
        setcurrent = analysis.run([],[],[],None,
                                  pos_tagged=constants.pos_tagged[i:j],
                                  results = constants.results[i:j])
    end = time.time()
    print("Time: %d" %(end - start))
    return setcurrent
