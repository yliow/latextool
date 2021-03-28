from latextool_basic import *
p = Plot()
ER.attrib_width=0.9
ER.attrib_height=0.5
ER.attrib_dist=0.4
ER.attrib_sep=0.4
ER.entity_width=1.8
ER.entity_height=0.5
ER.relation_width=1.8
ER.relation_height=0.5

p += ER.entity(center=(0,0), name='A', attribs=[], keys=[])
p += ER.relation(center=(3,0), name='R', attribs=[], label=r'{\scriptsize R}')
p += ER.entity(center=(6,0), name='B', attribs=[], keys=[])
p += ER.line(names=['B', 'R'])
p += ER.line(names=['A', 'R'])
crowfoot(p, x=3 + 0.9, y=0, kind="0..1", direction="west")
crowfoot(p, x=6 - 0.9, y=0, kind="1", direction="east")


# Test "west"
p += Line(points=[(0,-1),(2, -1)])
crowfoot(p, x=0, y=-1, kind="1", direction="west")

p += Line(points=[(0,-1.5),(2, -1.5)])
crowfoot(p, x=0, y=-1.5, kind="0..1", direction="west")

p += Line(points=[(0,-2),(2, -2)])
crowfoot(p, x=0, y=-2, kind="*", direction="west")

p += Line(points=[(0,-2.5),(2, -2.5)])
crowfoot(p, x=0, y=-2.5, kind="1..*", direction="west")

# Test "east"
p += Line(points=[(3,-1),(5, -1)])
crowfoot(p, x=5, y=-1, kind="1", direction="east")

p += Line(points=[(3,-1.5),(5, -1.5)])
crowfoot(p, x=5, y=-1.5, kind="0..1", direction="east")

p += Line(points=[(3,-2),(5, -2)])
crowfoot(p, x=5, y=-2, kind="*", direction="east")

p += Line(points=[(3,-2.5),(5, -2.5)])
crowfoot(p, x=5, y=-2.5, kind="1..*", direction="east")

# Test changing dx
x = 0
y = -4
p += Line(points=[(x,-5),(x + 2, -5)])
crowfoot(p, x=x+2, y=y, dx=0.25, kind="1", direction="east")
x += 3
p += Line(points=[(x, y),(x + 2, y)])
crowfoot(p, x=x+2, y=y, dx=0.25, kind="0..1", direction="east")
x += 3
p += Line(points=[(x, y),(x + 2, y)])
crowfoot(p, x=x+2, y=y, dx=0.25, kind="*", direction="east")
x += 3
p += Line(points=[(x, y),(x + 2, y)])
crowfoot(p, x=x+2, y=y, dx=0.25, kind="1..*", direction="east")

print(p)
