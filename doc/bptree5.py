from latextool_basic import *
from latexcircuit import *

def f(M): return tuple(r'{{\scriptsize\texttt{%s}}}' % _ for _ in M)


p = Plot()
widths = [0.1, 0.4]
height = 0.4
node_sep = 0.1
vsep = 1.5 # vertical separation -- from bottom of root to top of child


keyss = [(10, 30, 65, 80), (1, 5, 7, 9), (10, 14, 15, 28), (35, 42, 45, 57),
         (68, 72, 75, 79), (80, 89, 90, 92)] 
Ms = [f(keys) for keys in keyss]

Y = -(height + vsep)
children = bptree_get_siblings(0, Y, Ms[1:], widths, height, node_sep)
root = bptree_get_root(0, keyss[0], children, widths, height)

for _ in [root] + children: p += _

arcs = bptree_get_arcs(root, children, vsep, height)
for _ in arcs: p += _

labels = bptree_get_labels(keyss, arcs)
for label in labels:
    p += label



"""
            A
      B   C   D   E
     H I     F G
              J K
"""
edges = {'A':['B','C','D','E'],
         'D':['F','G'],
         'B':['H','I'],
         'G':['J','K'],
         }
nodes = {'A':f([0,1,2,3]),
         'B':f([4,'','','']),
         'C':f([8,9,10,11]),
         'D':f([12,'','','']),
         'E':f([16,17,18,19]),
         'F':f([20,21,22,23]),
         'G':f([24,24,24,'']),
         'H':f([28,29,30,31]),
         'I':f([32,33,34,35]),
         'J':f([36,37,38,39]),
         'K':f([40,41,42,43]),
         }
bptree(p, edges=edges, nodes=nodes)    

print p
