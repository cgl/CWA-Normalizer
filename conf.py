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

OOVFUNC = is_oov
wo_tag=False
with_degree=False
window_size = 7
