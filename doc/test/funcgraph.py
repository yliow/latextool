from latextool_basic import *
file('main.tex', 'w').write(r"""
\input{myblankpreamble}
\begin{document}
\begin{python}
from math import sin
domain = [x / 10.0 for x in range(-100, 101)]
y_sinx = [(x, 5 * sin(x)) for x in domain]
y_x = [(x, x) for x in domain]
from latextool_basic import *
plot = FunctionPlot(width="6in", height="3in")
plot.add(y_sinx, line_width='2', color='red', legend=r'$y = 5 \sin(x)$')
plot.add(y_x, line_width='2', color='green', legend='$y = x$')
print plot
\end{python}
\end{document}
""")
os.system('makemake')
os.system('make')
