from latextool_basic import *
p = Plot()

def rect(index, p, x0, y0, no_draw=False):
    data = [(r'$q_0$',
             ['0','b','a','a'],
             0),
            (r'$q_1$',
             ['1','b','a','a',r'\SPACE',r'\SPACE',r'\SPACE'],
             1),
            (r'$q_2$',
             ['2','b','a','a',r'\SPACE',r'\SPACE',r'\SPACE'],
             2),
            (r'$q_3$',
             ['3','b','a','a',r'\SPACE',r'\SPACE',r'\SPACE'],
             3),
            (r'$q_4$',
             ['4','b','a','a',r'\SPACE',r'\SPACE',r'\SPACE'],
             2),
            (r'$q_5$',
             ['5','b','a','a',r'\SPACE',r'\SPACE',r'\SPACE'],
             2),
            (r'$q_6$',
             ['6','b','a','a',r'\SPACE',r'\SPACE',r'\SPACE'],
             2),
            (r'$q_7$',
             ['7','b','a','a',r'\SPACE',r'\SPACE',r'\SPACE'],
             2),
            ]
    if index < len(data):
        state, tape, head_index = data[index]    
        return dfa(p,
               x0=x0,y0=y0,
               #stackvalues = stackvalues,
               tape= tape,
               state = state,
               head_index = head_index,
               vsep=0.5, hsep=0.25,
               body_w=1, body_h=0.7, w=0.4,
               no_draw=no_draw,
               )
    else:
        return None

sequence(p, rect=rect)
print p
