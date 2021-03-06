from tools import max_values, min_values
from numpy import array
dims = ['weight', 'lcsr', 'distance', "com chars", "slang", "freq", "result"]
def pretty_top_n(res,ind_word,mapp,max_val,last=10):
    ind = ind_word
    ovv = mapp[ind_word][0]+"|"+mapp[ind_word][2]
    print "%10.10s %10.6s %10.6s %10.6s %10.6s %10.6s %10.6s %10.6s Current res" % (ovv, dims[0], dims[1], dims[2], dims[3], dims[4], dims[5],dims[6])
    for vec_pre in res[ind][:last]:
        vec = [round(a,4) for a in array(vec_pre[1:len(max_val)+1]) * array(max_val)]
        print "%10.10s %10.6f %10.6f %10.6f %10.6f %10.6f %10.6f %10.6f %10.6f"  % (vec_pre[0],vec[0],vec[1],vec[2],vec[3],vec[4],vec[5],vec_pre[-1],sum(vec))

def pretty_max_min(res,feat_mat1,mapp):
    maxes = max_values(res,mapp)
    mins = min_values(res)
    print "%8.8s %8.8s %8.8s %8.8s %8.8s %8.8s %8.8s " % (dims[0], dims[1], dims[2], dims[3], dims[4], dims[5],dims[6],)
    print "%8.6f %8.6f %8.6f %8.6f %8.6f %8.2f %8.6f" % (mins[0], mins[1], mins[2], mins[3], mins[4], mins[5], mins[6],)
    print "%8.6f %8.6f %8.6f %8.6f %8.6f %8.2f %8.6f" % (maxes[0], maxes[1], maxes[2], maxes[3], maxes[4], maxes[5],maxes[6],)

def pretty_incorrects(incor,mapp):
    for ind,ans in incor:
        print "%4d  %10s %10s %10s %s" %(ind, mapp[ind][0], mapp[ind][1], ans, mapp[ind][2] )

def show_nth_index(ind,index_list,res,mapp,max_val,last=4):
    for rr in index_list[ind][1]:
        print rr,mapp[rr]
        pretty_top_n(res,rr,mapp,max_val,last=last)
