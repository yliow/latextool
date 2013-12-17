from latextool_basic import *
from math import log

domain = [x / 10.0 for x in range(0, 101)]
f1 = [(x, x) for x in domain]
f2 = [(x, x**2) for x in domain]
f3 = [(x, log(x)) for x in [_ for _ in domain if _ > 0]]

from latextool_basic import *
plot = FunctionPlot(width="6in", height="7in")
plot.add(f1, line_width='2', color='red', legend=r'$y = x$')
plot.add(f2, line_width='2', color='green', legend=r'$y = x^2$')
plot.add(f3, line_width='2', color='blue', legend=r'$y = x \ln x$')
print plot

