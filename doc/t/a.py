from latextool_basic import *
d = positions(r"""
    B  
  C D E
G H I Z
J   L  
K     
""", xscale=0.7)
edges = {'B':['C', 'D', 'E'], 'C':[],
         'C':['G','H','I'],  'G':['J'],           'J':['K'],
         'I':['L'],
         'E':['Z'],
        }
p = Plot()
labels = {'A':r'\texttt{<expr>}',   'B':r'\texttt{<expr>}',
          'C':r'\texttt{<expr>}',   'D':r'\texttt{+}',
          'E':r'\texttt{<term>}',   'F':r'\texttt{term}',
          'G':r'\texttt{<expr>}',   'H':r'\texttt{+}',
          'I':r'\texttt{<term>}',   'J':r'\texttt{<term>}',
          'K':r'\texttt{1}',        'L':r'\texttt{1}',
          'Z':r'\texttt{1}',
        }
rects = {}
for k,(x,y) in d.items():
    rects[k] = Rect(x0=x, y0=y-0.3, x1=x, y1=y+0.3, label=labels[k],
                    name=k, linecolor='white')
    p += rects[k]
for k,v in edges.items():
    for _ in v:
        p += Line(points=[rects[k].bottom(), rects[_].top()])
print(p)
