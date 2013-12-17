"""
Note that
Plot class from this file is moved to FunctionPlot class in latextool_basic.py
graph and graph_color_label functions from this file to latextool_basic.py
"""

"""
The input is a string.
"""

def automata(
    xscale=1,
    yscale=1,
    layout="",
    separator="|",
    edges="",
    **args
    ):
    """
automata(layout='''
A B C D
''',
edges='A,$a$,A|A,$a,b$,B|A,$a,\epsilon$,C'
A='initial|accept|label=$q_0$',
B='accept|label=$q_1$',
"""
    pos = positions(layout,xscale,yscale)
    node = {}
    #print "pos:", pos
    for k,v in pos.items():
        node[k] = {'pos':v}
        node[k]['initial'] = ""
        node[k]['accept'] = ""
        node[k]['label'] = k

    e = {}
    for v in [_ for _ in edges.split(separator) if _ != '']:
        #print "v:", v
        q1,v = v.split(',',1)
        v,q2 = v.rsplit(',',1)
        e[(q1,q2)] = v

    for k in node.keys():
        for v in [_ for _ in args.get(k,'').split(separator) if _ != '']:
            if v == 'initial':
                node[k]['initial'] = ",initial"
            elif v == 'accept':
                node[k]['accept'] = ",accepting"
            elif v.startswith('label='):
                node[k]['label'] = v.replace('label=', '').strip()
            else:
                raise ValueError("unknown option for node [%s]" % v)

    # form node string
    node_str = ""
    #print "node:", node
    for k,v in node.items():
        d = {}
        d['name'] = k
        d['label'] = v['label']
        d['initial'] = v['initial']
        d['accept']= v['accept']
        d['pos'] = "(%3s,%3s)" % v['pos']
        node_str += r"\node[state%(initial)s%(accept)s] (%(name)s) at %(pos)s {%(label)s};" % d
        node_str += '\n'

    # form edge string
    # q1==q2: loop above (default)
    #
    # if q1 same row as q2:
    #     if no node between q1 and q2:
    #         if only q1 to q2 but no q2 to q1
    #             straight line
    #         else:
    #             bend left=15
    #     else:
    #         bend left=angle where angle = 30 + 15* num nodes between   
    # else if q1 same column as q2
    #     not possible
    # else
    #     straight line
    #
    # p0,p1 when is p in between p0,p1?
    # u=p0,p same dir as v=p,p1
    def edge_shape(q0,q1,node,e):
        def between(p0,p,p1):
            #print "p0,p,p1:",p0,p,p1
            u = p[0]-p0[0], p[1]-p0[1]
            v = p1[0]-p[0], p1[1]-p[1]
            #print "u,v:",u,v
            # u[0]=c*v[0], u[1]=c*v[1]
            if u[0] == 0 and v[0] == 0:
                return u[1] * v[1] > 0
            elif u[1] == 0 and v[1] == 0:
                return u[0] * v[0] > 0
            return u[0]*v[1] == u[1]*v[0]
        if q0==q1:
            return "[loop above]" # have to decide on which loop
        p0,p1 = node[q0]['pos'],node[q1]['pos']
        # count num of nodes between
        count = 0
        #print "check between for",q0,q1
        for p in node.keys():
            if p not in [q0,q1]:
                if between(p0,node[p]['pos'],p1):
                    #print "between found:",p
                    count += 1
        #print "q0,q1,count:", q0,q1,count
        if count == 0:
            if (q1,q0) in e.keys(): angle = 10
            else: angle = 0
        else: angle = 30 + 10*count
        
        return "[bend left=%s]" % angle
            
    edge_str = ""
    #print "e:", e
    e2 = e.items()
    e2.sort()
    for k, v in e2:
        q1,q2 = k
        if q1 not in node.keys():
            raise ValueError("state [%s] in edges param not found in layout" % q1)
        if q2 not in node.keys():
            raise ValueError("state [%s] in edges param not found in layout" % q2)

        d = {'q1':q1, 'q2':q2, 'label':v, 'edge':edge_shape(q1,q2,node,e)}
        if q1==q2:
            edge_str += r"(%(q1)s) edge %(edge)s node {%(label)s} ()" % d
        else:
            edge_str += r"(%(q1)s) edge %(edge)s node {%(label)s} (%(q2)s)" % d
        edge_str += '\n'
    return r'''
\begin{center}
\begin{tikzpicture}[shorten >=1pt,node distance=2cm,auto,initial text=]
%s

\path[->]
%s
;
\end{tikzpicture}
\end{center}
    ''' % (node_str, edge_str)
