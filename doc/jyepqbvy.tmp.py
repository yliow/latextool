from latextool_basic import *
print automata(layout="""
A B C D
""",
edges="A,1,B|B,1,C|C,1,D|A,$0,1$,A|D,$0,1$,D|B,0,B|C,0,C",
A="initial|label=$q'_0$",
B="label=$q'_1$",
C="label=$q'_2$",
D="accept|label=$q'_3$",
)