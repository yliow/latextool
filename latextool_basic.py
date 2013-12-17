"""
All measures in cm by default!!!

linewidth  default=''
linecolor  default=black
linestyle  default=solid
"""

import math, random, os, string, re
from subprocess import Popen
from subprocess import PIPE
from math import *
import traceback

random.seed()
#==============================================================================
# Constants
#==============================================================================
L = 0.04 # default line width
DOUBLE_LINKED_LIST_LINEWIDTH = 0.03
POINTER_LINEWIDTH = 0.03

#==============================================================================
# Basic utilities
#==============================================================================
def IFELSE(b, x, y):
    if b: return x
    else: return y

def RANGE(a, b=None, c=None):
    if b==None and c==None:
        a, b, c = 0, a, 1
    elif b!=None and c==None:
        c = 1
    ret = []
    x = a
    while x < b:
        ret.append(x)
        x += c
    return ret

def ceiling(x):
    return IFELSE(int(x) == x, int(x), int(x) + 1)

def floor(x):
    if int(x) == x: return int(x)
    else: return IFELSE(x >= 0, int(x), int(x) - 1)

def readfile(filename): return file(filename, 'r').read()
def writefile(filename, s): return file(filename, 'w').write(s)

#==============================================================================
# The following function will remove extraneous character in the stdout
# when you execute scons
#==============================================================================
def clean_scons_output(s):
    return s.replace(chr(27)+"[?1034h", "") # remove garbage char

#==============================================================================
# beamer
#==============================================================================
def beamerframe(title='SOME TITLE',
                fragile=True,
                allowframebreaks=False,
                s='SOME CONTENT',
          ):
    options = []
    if fragile:
        options.append('fragile')
    if allowframebreaks:
        options.append('allowframebreaks')
    if options != []:
        options = '[%s]' % (','.join(options))
    else:
        options = ''
    return r'''
\begin{frame}%(options)s
\frametitle{%(title)s}
%(s)s
\end{frame}

''' % {'title':title, 's': s, 'options':options}
    
#==============================================================================
# Basic latex utilities
#==============================================================================
def console(s='',
            filename='', # TODO: read file a file instead
            xs=[],       # DEPRECATED: Use commands
            commands=[],
            command=[],
            numbers='',
            frame='single', # TODO
            width=75, wrapmarker=''):
    return verbatim(s=s,
                    filename=filename,
                    commands=commands,
                    command=command,
                    numbers=numbers,
                    frame=frame,
                    width=width,
                    wrapmarker=wrapmarker)


def tikzpicture(s):
    return r"""\begin{tikzpicture}
%s
\end{tikzpicture}
""" % s


def center(s):
    return r"""\begin{center}
%s
\end{center}""" % s


def do_latex_example(s, center=True):
    print console(s.strip())
    if center:
        print r"""\begin{center}
%s
\end{center}""" % s
    else:
        print r"""\begin{center}
%s
\end{center}""" % s
        


def do_tikz_example(s):
    print console(s.strip())
    print r"""\begin{center}
\begin{tikzpicture}
%s
\end{tikzpicture}
\end{center}
""" % s

#==============================================================================
# verbatim
# It's annoying when executing latex commands that we have to choose 3 chars
# that does not appear in the text. Furthermore, hand coding the tex commands
# in the verbatim text shifts the text. This function allows you to write the
# text and then spell out what substrings should have tex command applied to.
# The function will find the 3 commandchars for you.
#
# WARNING: Note that the characters in the environment name cannot be used.
# For instance if you uses \begin{console}...\end{console}, then
# c, o, n, s, l, e
# cannot be used.
#
# WARNING: The following characters cannot use: <>-,
#
# Note that the charactes in extrachars are those that requires \ in the
# commandchars line.
#
# Example:
#   verbatim(s, [['underline', ['hello', 'world']],
#                ['redtext',   ['abc', 'def']],
#               ]
#           )
#==============================================================================
def verbatim(s='',
             filename='', # TODO: read file a file instead
             xs=[],       # DEPRECATED: Use commands
             commands=[],
             command=[],
             numbers='',
             frame='single', # TODO
             width=75, wrapmarker=''
             ):
    if xs != []: commands = xs
    if command != []: commands = [command]
    #--------------------------------------------------------------------------
    # Get file contents if necessary
    #--------------------------------------------------------------------------
    if filename != '':
        try:
            s = readfile(filename)
        except:
            return verbatim('verbatim error: Cannot read file %s' % filename)
    #--------------------------------------------------------------------------
    # Format according to width
    #--------------------------------------------------------------------------
    lines = s.split('\n')
    newlines = []
    ret = ''
    for line in lines:
        pre, line = line[:width], line[width:]
        newlines.append(pre)
        while line != '':
            pre, line = line[:width], line[width:]
            pre = wrapmarker + pre
            newlines.append(pre)
    ret += '\n'.join(newlines)
    s = ret
    #--------------------------------------------------------------------------
    # Line numbering on the left
    #--------------------------------------------------------------------------
    numbers = IFELSE(numbers in ['', None, False], '', 'numbers=%s' % numbers)
    #--------------------------------------------------------------------------
    # Frame
    #--------------------------------------------------------------------------
    frame = IFELSE(frame in ['', None, False], '', 'frame=%s' % frame)
    #--------------------------------------------------------------------------
    # Compute commandchars
    #--------------------------------------------------------------------------
    from string import ascii_letters, digits, punctuation
    #chars = list(digits + "~!@$()*_+|:;./?") # FOR SOME REASON digits HAS
                                              # PROBLEMS
    chars = list("~!@$()*_+|:;./?")
    chars = [c for c in chars if c not in "console"]
    extrachars = ['\\', '{', '}', '#', '^', '&', '[', ']']
    commandchars = {}
    for c in chars: commandchars[c] = c
    for c in extrachars: commandchars[c] = '\\' + c
    chars = chars + extrachars
    c = [x for x in chars if x not in s][:3] # 3 characters in char, not in s
    commandchars = 'commandchars=%s%s%s' % \
                   (commandchars[c[0]], commandchars[c[1]],commandchars[c[2]])
    #--------------------------------------------------------------------------
    # Perform replacement
    #--------------------------------------------------------------------------
    for item in commands:
        func, substrings = item

        if isinstance(substrings, str):
            # CASE: item looks like ['textcolor', 'hello world']
            substrings = [substrings]

        if isinstance(substrings[0], str):
            # CASE: item looks like ['textcolor', ['hello', ...]]
            for substring in substrings:
                import re
                p = re.compile('(%s)' % substring)
                done = ''
                while s != '':
                    parts = p.split(s, 1)
                    #print "parts:", parts
                    if len(parts) == 1:
                        done += s
                        s = ''
                    else:
                        left, mid, right = parts
                        done += left
                        done += r"%s%s%s%s%s" % (c[0], func, c[1], mid, c[2])
                        s = right
                s = done
        elif isinstance(substrings[0], int):
            # CASE: item looks like ['textcolor', [42,....]]
            # Two subcases:
            # SUBCASE 1: item looks like ['textcolor', [42,5,10]]
            #            This means that substring is a list of 3 numbers
            #            line number, starting column number, ending
            #            column number
            # SUBCASE 2: item looks like ['textcolor', [42, 'hello']]
            if isinstance(substrings[1], int):
                lines = s.split('\n')
                i,j,k = substrings # all ints
                substring = lines[i][j:k]
                new_substring = r"%s%s%s%s%s" % (c[0], func, c[1], substring, c[2])
                lines[i] = lines[i][:j] + new_substring + lines[i][k:] 
                s = '\n'.join(lines)
            else:
                linenumber, substring = substrings
                lines = s.split('\n')
                import re
                p = re.compile('(%s)' % substring)
                done = ''
                s = lines[linenumber]
                while s != '':
                    parts = p.split(s, 1)
                    #print "parts:", parts
                    if len(parts) == 1:
                        done += s
                        s = ''
                    else:
                        left, mid, right = parts
                        done += left
                        done += r"%s%s%s%s%s" % (c[0], func, c[1], mid, c[2])
                        s = right
                s = done
                lines[linenumber] = s
                s = '\n'.join(lines)
    return r"""\begin{console}[%s, %s, %s]
%s
\end{console}
""" % (frame, numbers, commandchars, s)

#==============================================================================
# table
#==============================================================================
def table(data,
          style=None,
          col_headings=None,
          row_headings=None,
          topleft_heading=None,
          col_width=None):
    # data is a dictionary or a list of list/tuples
    if style == None and isinstance(data, dict):
        s = ''
        for k,v in data.items():
            s += r'%s & %s \\' % (k,v) + '\n'
        return r'''
\begin{longtable}{|r|r|}
\hline
%s
\hline
\end{longtable}
        ''' % s

    # Change rows of data from tuples/lists to lists and all data to string
    data = [[str(_) for _ in row] for row in data]
    
    # compute num_cols
    if col_headings == None: col_headings = []
    col_headings = [str(_) for _ in col_headings]
    num_cols = max([len(x) for x in data] + [len(col_headings)])
    if col_headings:
        col_headings = col_headings + ['' for i in range(num_cols - len(col_headings))] # add '' to col headings if nec


    # compute num_rows
    if row_headings == None: row_headings = []
    row_headings = [str(_) for _ in row_headings]
    num_rows = max([len(row_headings), len(data)])
    if row_headings:
        row_headings = row_headings + ['' for i in range(num_rows - len(row_headings))] # add '' to row headings if nec

    # add '' so that data is (num_rows)-by-(num_cols)
    data = data + [[''] for i in range(num_rows - len(data))]
    data = [row + ['' for i in range(num_cols - len(row))] for row in data]
    
    # Put row heading entries into data
    if row_headings:
        data = [[x] + row for x,row in zip(row_headings, data)]

    # Add col_headings and topleft_heading to data:
    # NOTE:
    # -- If col_headings is empty, then topleft_heading will not appear
    # -- If row_headings is empty, then topleft_heading will not appear
    if col_headings:
        if topleft_heading == None: topleft_heading = ''
        if row_headings:
            data.insert(0, [str(topleft_heading)] + col_headings)
        else:
            data.insert(0, col_headings)
    num_cols = len(data[0])

    #for i,row in enumerate(data):
    #    print i, row

    # Change all entries in data to strings of the same width
    widths = [0 for i in range(num_cols)]
    #print "widths:", widths
    for row in data:
        for i in range(num_cols):
            widths[i] = max([widths[i],len(row[i])])
    
    data = [[str(x).ljust(width) for x,width in zip(row,widths)] for row in data]
    
    s = ''

    for row in data:
        row = row + ['' for _ in range(num_cols - len(row))]
        row = ' & '.join([str(x) for x in row]) + r'\\ \hline' + '\n'
        s += row

    s = ''
    for i,row in enumerate(data):
        t = ' & '.join(row) + r' \\ \hline '
        if i == 0 and col_headings: # col header
            t += r'\hline '
        t += '\n'
        s += t
    if s.endswith('\n'): s = s[:-1]
    if row_headings:
        if col_width:
            align = '|'.join(['p{%s}|' % col_width] + ['p{%s}' % col_width for _ in range(num_cols - 1)])
        else:
            align = '|'.join(['r|'] + ['r' for _ in range(num_cols - 1)])
    else:
        align = '|'.join(['r' for _ in range(num_cols)])
    align = '|%s|' % align
    #if row_headings:
    #    align = '|r|' + align
        
    return r'''
\begin{longtable}{%s}
\hline 
%s
\end{longtable}
        ''' % (align, s)
    
#==============================================================================
# execute(source, print_source=False, debug)
# source = python code string
#
# 1. Saves source as a file with random filename of the form [rand].tmp.py
# 2. Execute the python program and retrieves stdout, stderr, return code
# 3.
#
# Return case:
#    return stdout, stderr, return code?
#==============================================================================
def execute(source,
            print_source=False,
            debug=False,
            print_result=True, # True: print result. False: return result
            ):
    """
    source is a python program.
    1. Print s in a latex console environment.
    2. Print traceback (etc) if there are errors
    3. Insert stdout
    """
    source = source.strip()

    # Get source filename
    randstr = ''.join([random.choice(string.lowercase) for _ in range(8)])
    filename = '%s.tmp.py' % randstr

    # Save source and execute
    writefile(filename, source) # Note: source does not have filename
    cmd = 'python %s' % filename
    stdout, stderr, returncode = myexec(cmd)
    os.system('rm -f %s' % filename) # delete source file

    if debug or stderr != '':
        s = r"""PYTHON ERROR. See source, stderr, stdout below
%s\vspace{-.1\baselineskip}
%s\vspace{-.1\baselineskip}
%s""" % (verbatim(source), verbatim(stdout), verbatim(stderr))
    else:
        # debug == false or stderr == ''
        s = ''
        if print_source:
            s = console(source) + r'\vspace{0.5\baselineskip}' + stdout
        else:
            s = stdout
        
    if print_result:
        print s
    else:
        return s


def error():
    s = readfile('main.py.err').strip()
    if s == '': return ''
    return r"""
\begin{console}
ERROR FROM main.py.err:

    %s
\end{console}
    """



def minipage(s='',
             align='t',
             h=0, w=0):
    h = round(h,3)
    w = round(w,3)
    if h < 0.1: h = 0.1
    if w < 0.1: w = 0.1
    if s=='': s = r'\mbox{}' + '\n'
    return r'''
\begin{minipage}[%(align)s][%(h)scm]{%(w)scm}
%(s)s
\end{minipage}
''' % {'align':align, 'h':h, 'w':w, 's':s}


    
class Plot:
    """
    Goal
    - maintains a list of object to draw
    - maintains a tight bounding rect of all objects
    - provides debug/error window at the bottom

    This basically spits out a tikz environment in a centered
    environment.
    
    TODO:
    - Plot(pdf=True, filename='a', dir='tmp/')
    """
    def __init__(self,
                 verbose=False,
                 center=True,
                 scale=1,
                 extra=0, # extra added to the minimal grid
                 **karg   # things like linewidth, ...
                 ):      
        # named shapes (see add method)
        # is an object is added without name,
        # a name will be give ('0', '1', ...)
        # see self.auto_inc
        self.auto_inc = 0
        self.xs = {}
        self.verbose = verbose
        self.center = center
        self.extra = extra
        self.scale = scale
        self.debug = '' # a debug/status minipage?
        self.font = '' # not used yet
        self.env = karg
        self.grid = None
    def add(self, shape, *arg, **karg):
        """ Note that if shape is a string, then it's just a latex
        fragment.

        TODO: Add objects instead
        """            
        if karg.has_key('name'):
            name = karg['name']
        else:
            name = self.auto_inc; self.auto_inc += 1

        if isinstance(shape, BaseNode):
            self.xs[name] = shape
        else:
            self.xs[name] = [shape, arg, karg]
    def __iadd__(self, x):
        if isinstance(x, Grid):
            self.grid = x
        else:
            self.add(x)
        return self
    def __str__(self):
        draw_grid = False
        min_x0 = None
        min_y0 = None
        max_x1 = None
        max_y1 = None
        s = ''

        def f(): pass
        
        for value in self.xs.values():
            try:
                shape, arg, karg = value
                if type(shape) == type('') and arg == () and karg == {}:
                    s += shape
                else:
                    s += apply(shape, arg, karg)
            except:
                try:
                    s += str(value)
                except:
                    raise ValueError("str method in Plot error: %s, type:%s" % (value, type(value)))

        # The rest computes parameters for the grid
        # Either grid params were passed in or computed.
        if self.grid:
            # If Grid() created with x0,y0,x1,y1 need to compute bounding rect.
            if self.grid.x0==0 and \
               self.grid.y0==0 and \
               self.grid.x1==0 and \
               self.grid.y1==0:
                # Compute bounding rec for grid
                min_x0 = min_y0 = max_x1 = max_y1 = None
                for value in self.xs.values():
                    if isinstance(value, BaseNode):
                        x0,y0,x1,y1 = value.leftx(), value.bottomy(), value.rightx(), value.topy()
                    else:
                        # This should be deprecated
                        x0 = y0 = x1 = y1 = 0
                        shape, arg, karg = value
                        if shape in [circle]:
                            radius = karg.get('radius', None)
                            r = karg.get('r', None)
                            if radius == None and r != None: radius = r
                            x0 = karg['x'] - radius
                            y0 = karg['y'] - radius
                            x1 = karg['x'] + radius
                            y1 = karg['y'] + radius
                        else:
                            try:
                                x0 = karg['x0']
                                y0 = karg['y0']
                                x1 = karg['x1']
                                y1 = karg['y1']
                            except:
                                pass
                    if min_x0 == None or x0 < min_x0: min_x0 = x0
                    if min_y0 == None or y0 < min_y0: min_y0 = y0
                    if max_x1 == None or x1 > max_x1: max_x1 = x1
                    if max_y1 == None or y1 > max_y1: max_y1 = y1
                if min_x0 == None: min_x0 = 0 # PROBABLY ... or max_x1 is it's not none? 
                if min_y0 == None: min_y0 = 0
                if max_x1 == None: max_x1 = 0
                if max_y1 == None: max_y1 = 0
                # adjust to integers
                min_x0 = floor(min_x0)
                min_y0 = floor(min_y0)
                max_x1 = ceiling(max_x1)
                max_y1 = ceiling(max_y1)
                s += str(Grid(x0=min_x0, y0=min_y0, x1=max_x1, y1=max_y1))
            else:
                s += str(self.grid)
            
        s = s.rstrip()
        # \begin{tikzpicture}[...]
        options = ''
        if self.scale != 1:
            options = "[scale=%s]" % self.scale
        latex = r"""\begin{tikzpicture}%s
%s
\end{tikzpicture}""" % (options, s)
        latex += '\n'
        if self.center:
            latex = r"""\begin{center}
%s
\end{center}""" % latex
            latex += '\n'
        if self.verbose:
            latex = r"""\begin{console}
%s
\end{console}
%s""" % (latex, latex)
        return latex


    
def get_style(**arg):
    """Form  a string s to be used in latex
    \draw[s]
    """
    
    linewidth = str(arg.get('linewidth', '')).strip()
    if linewidth in ['', None]:
        linewidth = ''
    else:
        if linewidth == 'very thin':
            pass # DON'T DO ANYTHING
        else:
            if not linewidth.endswith('cm'):
                linewidth = '%scm' % linewidth
        linewidth = 'line width=%s' % linewidth

    #--------------------------------------------------------------------------
    # Color: only color, linecolor used
    #--------------------------------------------------------------------------
    color = arg.get('color', '')
    linecolor = arg.get('linecolor', '')
    if color=='' and linecolor!='': color=linecolor

    startstyle = arg.get('startstyle','')
    endstyle = arg.get('endstyle','')
    # Get rid of "dot"
    startstyle = startstyle.replace('dot', '')
    endstyle = endstyle.replace('dot', '')
    
    #--------------------------------------------------------------------------
    # Add arrow tips to linestyle
    #--------------------------------------------------------------------------
    linestyle = ''
    if startstyle.startswith('-'): startstyle = startstyle[1:]
    if startstyle == '>': startstyle = '<'
    if startstyle == '>>': startstyle = '<<'
    if startstyle == '>|': startstyle = '|<'
    if startstyle == '>>|': startstyle = '|<<'
    
    
    if endstyle.startswith('-'): endstyle = endstyle[1:]

    if startstyle or endstyle:
        linestyle = '%s-%s' % (startstyle, endstyle)
    else:
        linestyle = ''

    """
    if startstyle in ['>','->']:
        startstyle = '<'
        if endstyle in ['>','->']:
            linestyle = '<->'
        else:
            linestyle = '<-'
    else:
        if endstyle in ['>','->']:
            linestyle = '->'
        else:
            linestyle = ''
    """
    #--------------------------------------------------------------------------
    # arrow (tip) style
    #--------------------------------------------------------------------------
    if arg.get('arrowstyle', '') != '':
        linestyle = ','.join([linestyle, ">=triangle 60"])

    #-------------------------------------------------------------------------- 
    # Add 'dashed', etc to linestyle
    #--------------------------------------------------------------------------
    if arg.get('linestyle', '') != '':
        linestyle = ','.join([linestyle, arg.get('linestyle', '')])

    xs = [str(linewidth), str(color), linestyle]
    xs = [_.strip() for _ in xs if _.strip() != '']
    return ','.join(xs)





#==============================================================================
# BaseNode: parent of all shapes
#==============================================================================
class BaseNode:
    # Note that the width,height or x0,y0,x1,y1 specified is the
    # the boundary box. The actual content area is smaller.
    #
    # TODO: Remove x, y, w, h as computed fields
    def __init__(self,
                 x=None, y=None, # center
                 w=None, h=None, # width, height
                 #
                 x0=None, y0=None, x1=None, y1=None, # bounding box
                 # Note that either w,h or x0,y0,x1,y1 is specified
                 debug=True):
        if x != None:
            self.x0 = x - w/2.0
            self.x1 = x + w/2.0
            self.y0 = y - h/2.0
            self.y1 = y + h/2.0
        elif x0 != None:
            self.x0 = x0
            self.x1 = x1
            self.y0 = y0
            self.y1 = y1
        self.debug = False # debug
    def move(self, dx=0.0, dy=0.0):
        self.x0 += dx
        self.y0 += dy
        self.x1 += dx
        self.y1 += dy
    def centerx(self): return (self.x0 + self.x1)/2.0
    def centery(self): return (self.y0 + self.y1)/2.0
    def topy(self): return self.y1
    def bottomy(self): return self.y0
    def leftx(self): return self.x0
    def rightx(self): return self.x1
    def height(self): return self.y1 - self.y0
    def width(self): return self.x1 - self.x0
    def top(self): return self.centerx(), self.y1
    def bottom(self): return self.centerx(), self.y0
    def left(self): return self.x0, self.centery()
    def right(self): return self.x1, self.centery()
    def center(self): return self.centerx(), self.centery()
    def topleft(self): return self.x0, self.y1
    def topright(self): return self.x1, self.y1
    def bottomleft(self): return self.x0, self.y0
    def bottomright(self): return self.x1, self.y0
    def __str__(self):
        x0 = self.x0
        y0 = self.y0
        x1 = self.x1
        y1 = self.y1
        s = ''
        if self.debug: # add bounding box
            s += rect(x0=x0, y0=y0, x1=x1, y1=y1, color='red') # 
        return s

    def get_edge(self, node, style=""):
        """ return list of points describing edge joining self to node.
        assume down
        """
        y = (self.y0 + self.y1)/2.0
        x = (self.x0 + self.x1)/2.0
        node_y = (node.y0 + node.y1) / 2.0
        node_x = (node.x0 + node.x1) / 2.0
        if y == node_y: # CASE: same level
            if self.x1 <= node.x0:
                x0,y0 = self.right()
                x1,y1 = node.left()
            else:
                x0,y0 = self.left()
                x1,y1 = node.right()
            return [(x0,y0),(x1,y1)]
        
        if style == "":
            if y > node_y: # CASE: downward
                x0,y0 = self.bottom()
                x1,y1 = node.top()
            elif y < node_y: # CASE: up
                x0,y0 = self.top()
                x1,y1 = node.bottom()  
            return [(x0,y0),(x1,y1)]
        elif style == "ES":
            x0,y0 = self.right()
            x2,y2 = node.top()
            x1,y1 = x2,y0
            return (x0,y0),(x1,y1),(x2,y2)
        elif style == "SW":
            x0,y0 = self.bottom()
            x2,y2 = node.right()
            x1,y1 = x0,y2
            return (x0,y0),(x1,y1),(x2,y2)
        elif style == "WS":
            x0,y0 = self.left()
            x2,y2 = node.top()
            x1,y1 = x2,y0
            return (x0,y0),(x1,y1),(x2,y2)
        elif style == "broom": # leg of a broom downward
            x0,y0 = self.bottom()
            x3,y3 = node.top()
            x1,y1 = x0,(y0+y3)/2.0
            x2,y2 = x3,y1
            return (x0,y0),(x1,y1),(x2,y2),(x3,y3)

#==============================================================================
# Grid
#==============================================================================
def grid(x0=0, y0=0, x1=5, y1=5,
         color='gray',
         linewidth='very thin',
         dx=1, dy=1,
         label_axes=True):
    s = ''
    for x in RANGE(x0, x1+0.00001, dx):
        s += line(x0=x,y0=y0,x1=x,y1=y1,color=color, linewidth='')
    for y in RANGE(y0, y1+0.00001, dy):
        s += line(x0=x0,y0=y,x1=x1,y1=y,color=color, linewidth='')

    if label_axes:
        for x in RANGE(x0, x1+0.00001, dx):
            if x == int(x): x = int(x)
            if x0 == int(x0): x0 = int(x0)
            if y == int(y): y = int(y)
            if y0 == int(y0): y0 = int(y0)
            s += r"\draw(%s, %s) node [font=\ttfamily, label=below:{\texttt{%s}}] {};" % (x, y0, x)
            s += '\n'
        for y in RANGE(y0, y1+0.00001, dy):
            s += r"\draw(%s, %s) node [font=\ttfamily, label=left:{\texttt{%s}}] {};" % (x0, y, y)
            s += '\n'
    return s

class Grid(BaseNode):
    def __init__(self,
                 x0=0, y0=0, x1=0, y1=0,
                 linecolor='gray',
                 linewidth='very thin',
                 linestyle='',
                 dx=1, dy=1,
                 label_axes=True,
                 debug=True):
        BaseNode.__init__(self,
                          x0=x0, y0=y0, x1=x1, y1=y1,
                          debug=debug)
        self.linewidth = linewidth
        self.linestyle = linestyle
        self.linecolor = linecolor
        self.dx = dx
        self.dy = dy
        self.label_axes = label_axes
        
    def __str__(self):
        linewidth = self.linewidth
        linestyle = self.linestyle
        linecolor = self.linecolor
        x0, y0 = self.x0, self.y0
        x1, y1 = self.x1, self.y1
        dx, dy = self.dx, self.dy
        label_axes = self.label_axes
        return grid(x0=x0, y0=y0, x1=x1, y1=y1,
                    color=linecolor, linewidth=linewidth,
                    dx=dx, dy=dy, label_axes=label_axes)
        
#==============================================================================
# Circle
#==============================================================================
def circle(x=0, y=0, center=None, r=0,
           linewidth='', linestyle='', linecolor='black',
           background = '', foreground = 'black',
           innersep=0,
           align='t', font='',
           label='', s='',
           rotate=0,
           ):

    if center != None: x, y = center
    x0 = x - r
    x1 = x + r
    y0 = y - r
    y1 = y + r

    # Parameters for minipage
    radius = 0 # this is the radius for the rounded corner used in rect
               # NOT used in circle.
               
    def floatlinewidth(linewidth):
        if isinstance(linewidth, str): return 0
        else: return linewidth

    h = 2 * r - 2 * floatlinewidth(linewidth)
    w = 2 * r - 2 * floatlinewidth(linewidth)
    
    # WARNING: the x,y is the center and not the bounding rect

    s = s.strip()
    label = label.strip()

    d = {'x':x, 'y':y, 'h':h, 'w':w,
         'background':background, 'foreground':foreground,
         'linewidth':linewidth, 'linecolor':linecolor, 'linestyle':linestyle,
         'r':r,
         'radius':radius, 'innersep':innersep, 'align':align, 's':s}

    # CHECK: d is not used later.
    # To account for thickness of border
    import copy
    d1 = copy.deepcopy(d)
    d1['w'] = d['w'] - floatlinewidth(linewidth)
    d1['h'] = d['h'] - floatlinewidth(linewidth)
    emptypage = minipage(s='', align=d1['align'], h=d1['h'], w=d1['w'])
    d1.update({'minipage':emptypage})

    ret = ''

    # Draw boundary and interior with background color
    if background != '':
        ret += r"""\fill[%s] (%s, %s) circle (%s);
""" % (background, x, y, r)


    # change line width
    if d1['linewidth'] == '':
        pass
    else:
        d1['linewidth'] == 'line width=%scm' % d1['linewidth']

    #print "d1 ...:", d1['linewidth']

    style = get_style(linewidth=linewidth,
                      linecolor=linecolor,
                      linestyle=linestyle)
    d1['style'] = style
    # Draw boundary with boundary color
    if linecolor != '' and linewidth != 0:
        if linestyle == 'double':
            d1['r'] = r - floatlinewidth(linewidth)
        else:
            d1['r'] = r - floatlinewidth(linewidth) / 2.0
        ret += r"""
\draw[%(style)s] (%(x)s, %(y)s)
circle (%(r)s);
""" % d1

    # content
    if s != '':
        length = (r - floatlinewidth(linewidth)) / 1.414 * 2.0
        d1.update({'minipage':minipage(s=s,
                                       align=d1['align'],
                                       h=length-2*innersep, w=length-2*innersep)})
        ret += r'''
\draw (%(x)s,%(y)s) node[color=%(foreground)s, inner sep=%(innersep)scm] {
 %(minipage)s
};''' % d1
    elif label != '':
        d1['label'] = label
        ret += r'\draw (%(x)s, %(y)s) node[color=%(foreground)s] {%(label)s};' % d1

    #print "circle .. ret:", ret
    return ret


class Circle(BaseNode):
    def __init__(self,
                 x=0, y=0, center=None, r=0,
                 linewidth='', linestyle='', linecolor='black',
                 background='', foreground='black',
                 innersep=0,
                 font='', s='', label='',
                 debug=True):
        if center != None: x, y = center
        BaseNode.__init__(self,
                          x=x, y=y,
                          w=2*r, h=2*r,
                          x0=x-r, y0=y-r, x1=x+r, y1=y+r,
                          debug=debug)
        self.r = r
        self.linewidth = linewidth
        self.linestyle = linestyle
        self.linecolor = linecolor
        self.background = background
        self.foreground = foreground
        self.innersep = innersep
        self.font = font
        self.s = s
        self.label = str(label)
        
    def __str__(self):
        x, y = self.center()
        r = self.r
        s = self.s # TODO: REMOVE textsf
        label = self.label
        linewidth = self.linewidth
        linestyle = self.linestyle
        linecolor = self.linecolor
        foreground = self.foreground
        background = self.background
        innersep = self.innersep
        font = self.font
        label = self.label
        ret = ''
        ret += BaseNode.__str__(self)
        ret += circle(x=x, y=y, r=r,
                      linewidth=linewidth,
                      linestyle=linestyle,
                      linecolor=linecolor,
                      background=background,
                      foreground=foreground,
                      innersep=innersep,
                      font=font,
                      s=s,
                      label=label,
                      )
        return ret


#==============================================================================

def tabrect(x0=0, y0=0, x1=1, y1=1,
            linewidth=L, linecolor='black', linestyle='',
            background='white', foreground='black',
            innersep=0, radius=0,
            align='t', 
            s='',
            #
            #tab data
            ):
    ret = ''
    h = 0.8
    w = 2.5
    ret += r"""
    \draw (%s,%s) node[style=rounded corners, draw, line width=1, fill=blue!40, rotate=90] {
\begin{minipage}[t][%scm]{%scm}
\begin{flushleft}
\textsf{\scriptsize INTERMEDIATE}
\end{flushleft}
\end{minipage}
};""" % (x0, y0 + w/2.0 + 1, h, w)
    ret += rect(x0=x0, y0=y0, x1=x1, y1=y1,
             linewidth=linewidth, linecolor=linecolor, linestyle=linestyle,
             background=background, foreground=foreground,
             innersep=0.2, radius=0.5,
             align=align, 
             s=s)
    return ret

#==============================================================================
# Rect
#==============================================================================
def rect(x0=None, y0=None, x1=None, y1=None,
         x=None, y=None, w=None, h=None,
         linewidth='', linecolor='black', linestyle='',
         background='', foreground='black',
         innersep=0.0, radius=0.0,
         align='t', font='',
         label='',
         s=' ',
         rotate=0,
         ):
        
    if x0 != None:
        x = (x0 + x1) / 2.0
        y = (y0 + y1) / 2.0
        w = (x1 - x0) - 2 * innersep
        h = (y1 - y0) - 2 * innersep

    s = str(s).strip()
    label = str(label).strip()
    
    d = {'x':x, 'y':y, 'h':h, 'w':w,
         'background':background, 'foreground':foreground,
         'linewidth':linewidth, 'linecolor':linecolor, 'linestyle':linestyle,
         'radius':radius, 'innersep':innersep, 'align':align, 's':s}

    # To account for thickness of border
    import copy
    d1 = copy.deepcopy(d)
    d1['w'] = d['w'] - IFELSE(isinstance(linewidth,str), 0, linewidth)
    d1['h'] = d['h'] - IFELSE(isinstance(linewidth,str), 0, linewidth)
    emptypage = minipage(s='', align=d1['align'], h=d1['h'], w=d1['w'])
    d1.update({'minipage':emptypage})

    ret = ''

    if background != '':
        ret += r'''
\draw (%(x)s, %(y)s)
  node[fill=%(background)s,rounded corners=%(radius)scm,inner sep=%(innersep)scm] {
%(minipage)s
};''' % d1

    if d1['linewidth']=='': pass
    else: d1['linewidth'] = 'line width=%scm' % d1['linewidth']
    # border
    if linewidth != 0:
        ret += r'''
\draw (%(x)s, %(y)s)
  node[draw, %(linewidth)s, %(linestyle)s, color=%(linecolor)s,
       rounded corners=%(radius)scm, inner sep=%(innersep)scm] {
%(minipage)s
};''' % d1
    
    # content
    if s != '':
        d1.update({'minipage':minipage(s=s,
                                       align=d1['align'],
                                       h=d1['h'], w=d1['w'])})
        ret += r'''
\draw (%(x)s, %(y)s) node[color=%(foreground)s,
 inner sep=%(innersep)scm] {
 %(minipage)s
};''' % d1
    elif label != '':
        d1['label'] = label
        ret += r'\draw (%(x)s, %(y)s) node[color=%(foreground)s] {%(label)s};' % d1

    return ret



class Rect(BaseNode):
    def __init__(self,
                 x0=0, y0=0, x1=0, y1=0,
                 linewidth='', linestyle='', linecolor='black',
                 background='', foreground='black',
                 innersep=0, radius=0,
                 align='t', font='', s='', label='',
                 rotate=0,
                 debug=True):
        BaseNode.__init__(self,
                          x0=x0, y0=y0, x1=x1, y1=y1,
                          debug=debug)
        self.linewidth = linewidth
        self.linestyle = linestyle
        self.linecolor = linecolor
        self.background = background        
        self.foreground = foreground
        self.font = font
        self.s = str(s)
        self.label = str(label)
        self.innersep = innersep
        self.radius = radius
        self.align = align
        self.rotate=rotate
    def __str__(self):
        x0 = self.x0
        y0 = self.y0
        x1 = self.x1
        y1 = self.y1
        align = self.align
        font = self.font
        s = self.s
        label = self.label
        linewidth = self.linewidth
        linestyle = self.linestyle
        linecolor = self.linecolor
        background, foreground = self.background, self.foreground
        innersep, radius = self.innersep, self.radius
        rotate = self.rotate
        ret = ''
        ret += BaseNode.__str__(self)
        ret += rect(x0=x0, y0=y0, x1=x1, y1=y1,
                    linewidth=linewidth, linestyle=linestyle, linecolor=linecolor,
                    background=background, foreground=foreground,
                    innersep=innersep, radius=radius,
                    align=align, font=font, s=s, label=label,
                    rotate=rotate)
        return ret

class BlankRect(Rect):
    # blank rect that acts as a spacing
    def __init__(self, x0=0, y0=0, x1=0, y1=0):
        Rect.__init__(self,
                      x0=x0, y0=y0, x1=x1, y1=y1,
                      linewidth=0.0, linestyle='', linecolor='',
                      background='', foreground='',
                      innersep=0, radius=0,
                      align='t', font='', s='', label='',
                      rotate=0)
    
class Rect2(Rect):
    # This is really the same as Rect except that the boundary line
    # is 1/2 in the rect and 1/2 out.
    # This is used for arrays (for instance) or anything that
    # requires overlapping boundary.
    def __init__(self,
                 x0=0, y0=0, x1=0, y1=0,
                 linewidth=L, linestyle='', linecolor='black',
                 background='', foreground='black',
                 innersep=0, radius=0,
                 align='t', font='', s='', label='',
                 rotate=0,
                 debug=True):
        Rect.__init__(self, x0=x0, y0=y0, x1=x1, y1=y1,
                      linewidth=linewidth,
                      linestyle=linestyle,
                      linecolor=linecolor,
                      background=background,
                      foreground=foreground,
                      innersep=innersep, radius=radius,
                      align=align, font=font, s=s, label=label,
                     rotate=rotate,
                      debug=debug)
    def floatlinewidth(self):
        if isinstance(self.linewidth, str): return 0
        else: return self.linewidth
    def height(self): return (self.x1 - self.x0)  + self.floatlinewidth()
    def width(self): return (self.y1 - self.y0)  + self.floatlinewidth()
    def topy(self): return self.y1 + self.floatlinewidth()/2.0
    def top(self): return self.centerx(), self.topy()
    def bottomy(self): return self.y0 - self.floatlinewidth()/2.0
    def bottom(self): return self.centerx(), self.bottomy()
    def leftx(self): return self.x0 - self.floatlinewidth()/2.0
    def left(self): return self.leftx(), self.centery()
    def rightx(self): return self.x1 + self.floatlinewidth()/2.0
    def right(self): return self.x1 + self.floatlinewidth()/2.0, self.centery()
    def topleft(self): return self.leftx(), self.topy()
    def topright(self): return self.rightx(), self.topy()
    def bottomleft(self): return self.leftx(), self.bottomy()
    def bottomright(self): return self.rightx(), self.bottomy()
    def __str__(self):
        x0, y0 = self.x0, self.y0
        x1, y1 = self.x1, self.y1
        linestyle = self.linestyle
        linecolor = self.linecolor
        background = self.background
        foreground = self.foreground
        innersep = self.innersep
        radius = self.radius
        align = self.align
        font = self.font
        s = self.s
        label = self.label
        rotate = self.rotate
        debug = self.debug
        L = self.floatlinewidth() / 2.0
        r = Rect(x0=x0-L, y0=y0-L, x1=x1+L, y1=y1+L,
                 linewidth=self.linewidth,
                 linestyle=linestyle,
                 linecolor=linecolor,
                 background=background,
                 foreground=foreground,
                 innersep=innersep, radius=radius,
                 align=align, font=font, s=s, label=label,
                 rotate=rotate,
                 debug=debug)
        return str(r)

class Rect2NoLeftRight(Rect2):
    def __init__(self,
                 x0=0, y0=0, x1=0, y1=0,
                 linewidth='', linestyle='', linecolor='black',
                 background='', foreground='black',
                 innersep=0, radius=0,
                 align='t', font='', s='', label='',
                 rotate=0,
                 debug=True):
    
        Rect2.__init__(self, x0=x0, y0=y0, x1=x1, y1=y1,
                       linewidth=linewidth, linestyle=linestyle,
                       linecolor=linecolor,
                       background=background, foreground=foreground,
                       innersep=innersep, radius=radius,
                       align=align, font=font, s=s, label=label,
                       rotate=rotate,
                       debug=debug)
    def __str__(self):
        x0, y0 = self.x0, self.y0
        x1, y1 = self.x1, self.y1
        linestyle = self.linestyle
        linewidth= self.linewidth
        linecolor = self.linecolor
        background = self.background
        foreground = self.foreground
        innersep = self.innersep
        radius = self.radius
        align = self.align
        font = self.font
        s = self.s
        label = self.label
        rotate = self.rotate
        debug = self.debug
        L = self.floatlinewidth() / 2.0
        ret = str(Line(x0=x0-L, y0=y1, x1=x1+L, y1=y1,
                     linewidth=linewidth, linestyle=linestyle,
                     linecolor=linecolor))
        ret += str(Line(x0=x0-L, y0=y0, x1=x1+L, y1=y0,
                     linewidth=linewidth, linestyle=linestyle,
                     linecolor=linecolor))
        ret += str(Rect2(x0=x0, y0=y0, x1=x1, y1=y1,
                       linewidth=0, 
                       background=background, foreground=foreground,
                       innersep=innersep, radius=radius,
                       align=align, font=font, s=s, label=label,
                       rotate=rotate,
                       debug=debug))
        return ret
        
# Containers:
#   - can have bounding box and all objects placed in box
#   - can be no bounding box (no limit) but still need to specify starting
#     x0,y0
# x,y = a reference point for drawing the collection
# rects = list of rects
# direction and align = for drawing
#
# Rects' drawn positions are with respect to (x,y)
#
# Adding to container:
#   - left-to-right, top-to-bottom (for bounding box case)
#   - left-to-right (no bounding box case)
#   - for the time being ignore right-to-left or bottom-to-top
#   - can align rects by their bottoms, middles, tops
#   - default is align by bottom
class RectContainer(BaseNode):
    def __init__(self,
                 x=0, y=0,
                 debug=False,
                 align='bottom',
                 direction='left-to-right',
                 ):
        # x0,y0,x1,y1 is the rect area of this container
        BaseNode.__init__(self,
                          x0=x, y0=y, x1=x, y1=y,
                          debug=debug)
        self.rects = []
        self.x = x
        self.y = y
        self.direction = direction
        self.align = align
    def layout(self):
        # First layout the rects using x,y and direction and align.
        direction = self.direction
        align = self.align
        x, y = self.x, self.y
        self.x0 = self.x1 = x
        self.y0 = self.y1 = y
        
        for r in self.rects:
            w = r.x1 - r.x0
            h = r.y1 - r.y0
        
            if direction == 'left-to-right':
                r.x0 = x
                r.x1 = x + w
                self.x1 = x = r.x1
                if self.align == 'bottom':
                    r.y0 = y
                    r.y1 = y + h
                    self.y1 = max(self.y1, r.y1)
                elif self.align == 'top':
                    r.y1 = y
                    r.y0 = y - h
                    self.y0 = min(self.y0, r.y0)
            elif direction == 'top-to-bottom':
                r.y1 = y
                r.y0 = y - h
                y = r.y0
                if self.align == 'left':
                    r.x0 = x
                    r.x1 = r.x0 + w
                    self.x1 = max(self.x1, r.x1)
                    self.y0 = r.y0
                elif self.align == 'right':
                    r.x1 = x
                    r.x0 = r.x1 - w
                    self.x0 = min(self.x0, r.x0)
                    self.y0 = r.y0
        self.x0 = min([r.x0 for r in self.rects])
        self.y0 = min([r.y0 for r in self.rects])
        self.x1 = max([r.x1 for r in self.rects])
        self.y1 = max([r.y1 for r in self.rects])
    def __iadd__(self, r):
        self.rects.append(r)
        self.layout()
        return self
    def __getitem__(self, i):
        return self.rects[i]
    def __setitem__(self, i, r):
        self.rects[i] = r
    def __str__(self):
        s = ''
        for rect in self.rects:
            s += str(rect)
        return s


def RectAdaptor(**karg):
    env = karg.get('env', {})
    env.update(karg)
    x0 = env.get('x0', 0)
    y0 = env.get('y0', 0)
    x1 = env.get('x1', 0)
    y1 = env.get('y1', 0)
    linewidth = env.get('linewidth', L)
    linestyle = env.get('linestyle', '')
    linecolor = env.get('linecolor', 'black')
    background = env.get('background', '')
    foreground = env.get('foreground', 'black')
    innersep = env.get('innersep', 0)
    radius = env.get('radius', 0)
    align = env.get('align', 't')
    font = env.get('font', '')
    s = env.get('s', '')
    rotate = env.get('rotate', 0)
    debug = env.get('debug', True)
    return Rect(x0=x0, y0=y0, x1=x1, y1=y1,
                linewidth=linewidth, linestyle=linestyle, linecolor=linecolor,
                background=background, foreground=foreground,
                innersep=innersep, radius=radius,
                align=align, font=font, s=s,
                rotate=rotate,
                debug=debug)

#==============================================================================
# Snipped Array
# TODO: Add width, height [DONE]
#==============================================================================
class SnippedArray(RectContainer):

    def __init__(self, x=0, y=0,
                 xs=[],
                 linewidth=L,
                 width=1, height=1,
                 snippedstring='...'):
        RectContainer.__init__(self, x=x, y=y)
        for i,x in enumerate(xs):
            if x != snippedstring:
                self += Rect2(x0=0, y0=0, x1=width, y1=height,
                              linewidth=linewidth,
                              label=r'{\texttt{%s}}' % x)
            else:
                if i < len(xs) - 1:
                    self += Rect2(x0=0, y0=0, x1=width*1.5, y1=height,
                                  linewidth=linewidth, label=x)
                else:
                    self += Rect2NoLeftRight(x0=0, y0=0, x1=width*1.5,
                                             y1=height, label=x,
                                             linewidth=linewidth)
        self.layout()
        
#==============================================================================
# Cross
#==============================================================================

def cross(x0, y0, x1, y1, color='', linewidth="2mm"):
    style = get_style(linewidth=linewidth, color=color)
    return r"""
\draw[%(style)s] (%(x0)s, %(y0)s) -- (%(x1)s, %(y1)s);
\draw[%(style)s] (%(x0)s, %(y1)s) -- (%(x1)s, %(y0)s);
""" % {'x0':x0, 'y0':y0, 'x1':x1, 'y1':y1, 'style':style}

def crossed_rect(x0, y0, x1, y1, linewidth='', color=''):
    s = rect(x0, y0, x1, y1, linewidth=linewidth, color=color)
    s += line(x0, y0, x1, y1, linewidth=linewidth, color=color)
    s += line(x0, y1, x1, y0, linewidth=linewidth, color=color)
    return s

class CrossedRect2(Rect2):
    def __init__(self,
                 x0=0, y0=0, x1=0, y1=0,
                 linewidth='', linestyle='', linecolor='black',
                 background='', foreground='black',
                 innersep=0, radius=0,
                 align='t', font='', s='', label='',
                 rotate=0,
                 debug=True):
        Rect2.__init__(self,
                       x0=x0, y0=y0, x1=x1, y1=y1,
                       linewidth=linewidth, linestyle=linestyle, linecolor=linecolor,
                       background=background, foreground=foreground,
                       innersep=innersep, radius=radius,
                       align=align, font=font, s=s, label=label,
                       rotate=rotate,
                       debug=debug)
    def __str__(self):
        s = Rect2.__str__(self)
        linecolor = self.linecolor
        linewidth = self.linewidth
        (x0, y0), (x1, y1) = self.topleft(), self.bottomright()
        s += str(Line(x0, y0, x1, y1, linecolor=linecolor, linewidth=linewidth))
        (x0, y0), (x1, y1) = self.topright(), self.bottomleft()
        s += str(Line(x0, y0, x1, y1, linecolor=linecolor, linewidth=linewidth))
        return s
#==============================================================================
# Line
#==============================================================================
def line(x0=0, y0=0, x1=0, y1=0,
         points=None,
         linecolor='black',
         linewidth='',
         linestyle = '', # solid, dash, etc
         color='', # DEPRECATED
         startstyle = '', # "->", ".", etc.
         arrowstyle = '',
         endstyle = '',
         r=0):
    if color != '': linecolor = color
    if color == '' and linecolor != '': color=linecolor
    style = get_style(linewidth=linewidth,
                      color=color,
                      startstyle=startstyle,
                      linestyle=linestyle,
                      arrowstyle=arrowstyle,
                      endstyle=endstyle)
    if points == None:
        points = [(x0,y0),(x1,y1)]
    s = ["(%s,%s)" % (x,y) for x,y in points ]
    s = ' -- '.join(s)
    s = r"\draw[%s] %s;" % (style, s)
    s += '\n'

    if isinstance(linewidth, (int, float)):
        if linewidth != 0:
            if r <= 0:
                r = 0
            elif r <= 0.5 * linewidth:
                r = 1.5 * linewidth
                #print ">>>>>> 0"        
            else:
                #print ">>>>>> 1"
                pass
        else:
            #print ">>>>>> 2"
            r = 0.05 # hardcoded
    else:
        #print ">>>>>> 3"
        r = 0.05 # hardcoded
    #print "r:", r
    if startstyle in ['.', 'dot']:
        x, y = points[0]
        s += circle(x=x, y=y, r=r,
                    linecolor=linecolor, background=linecolor)
    if endstyle in ['.', 'dot']:
        x, y = points[-1]
        s += circle(x=x, y=y, r=r,
                    linecolor=linecolor, background=linecolor)
    return s

def midpoint(p0, p1, ratio=0.5):
    if ratio < 0: ratio = 0.0
    if ratio > 1: ratio = 1.0
    #print "midpoint ... p0:", p0
    #print "midpoint ... p1:", p1
    v = [p1[0] - p0[0], p1[1] - p0[1]]
    #print "v:", v
    #l = length(p0, p1)
    v = [v[0] * ratio, v[1] * ratio]
    p2 = [p0[0] + v[0], p0[1]+ v[1]]
    return p2

def length(p0, p1):
    from math import sqrt
    x0, y0 = p0
    x1, y1 = p1
    return sqrt((x1 - x0)**2 + (y1 - y0)**2)

class Line(BaseNode):
    """Line(
    x0=0, y0=0, x1=0, y1=0,
    points=None,
    linecolor='black',
    linewidth='',
    linestyle='',
    startstyle='',
    endstyle='',
    r=0,                    # radius of dot at start or end of line
)

    TODO: Path class

    """
    def __init__(self,
                 x0=0, y0=0, x1=0, y1=0,
                 points=None,
                 startstyle = '', # "->", ".", etc.
                 arrowstyle = '',
                 endstyle = '',
                 linestyle = '', # solid, dash, etc
                 linecolor='black',
                 linewidth=L,
                 r=0,
                 debug=False):
        if points != None:
            x0 = min([i for i,j in points])
            x1 = max([i for i,j in points])
            y0 = min([j for i,j in points])
            y1 = max([j for i,j in points])
        BaseNode.__init__(self,
                          x0=x0, y0=y0, x1=x1, y1=y1,
                          x=(x0+x1)/2.0, y=(y0+y1)/2.0,
                          w=(x1-x0), h=(y1-y0),
                          debug=debug)
        self.points = points
        self.startstyle=startstyle
        self.endstyle=endstyle
        self.arrowstyle=arrowstyle
        self.linewidth = linewidth
        self.linestyle = linestyle
        self.linecolor = linecolor
        self.r = float(r)
        
    def __length(self):
        startpoints = self.points[:-1]
        endpoints = self.points[1:]
        return sum([length(p,q) for p,q in zip(startpoints, endpoints)])
    
    def midpoint(self, ratio=0.5):
        """
                a         b
        <--------------><--->
        p---q----r-----s----------t----------u
                       <---------->
                             c
        <------------------------------------>
            l
            
        r = (a + b) / l    (l = total length)
        r * l = a + b
        r * l - a = b
        b/c = (r * l - a)/c
        """
        totallength = float(self.__length())
        startpoints = self.points[:-1]
        endpoints = self.points[1:]

        if ratio < 0: ratio = 0.0
        if ratio > 1: ratio = 1.0
        if ratio==0.0: return self.points[0]
        if ratio==1.0: return self.points[-1]
        prevsum = 0.0
        prevp = self.points[0]
        prevq = self.points[1]
        s = 0.0
        #print "totallength:", totallength
        for p,q in zip(startpoints, endpoints):
            #print 
            #print "p:", p
            #print "q:", q
            prevsum = s
            #print "prevsum:", prevsum
            s += length(p,q)
            #print "s:", s
            if s / totallength > ratio:
                #print "break"
                break
            prevp = p
            prevq = q
        #print "p:", p
        #print "q:", q
        #print "ratio:", ratio
        #print "totallength:", totallength
        #print "prevsum:", prevsum
        #print "length(p,q):", length(p, q)
        #print "new ratio:", (ratio*totallength - prevsum) / length(p,q)
        return midpoint(p, q,
                        ratio=(ratio*totallength - prevsum) / length(p,q)
                        )
        
    def __str__(self):
        x0 = self.x0
        y0 = self.y0
        x1 = self.x1
        y1 = self.y1
        points = self.points
        startstyle = self.startstyle
        endstyle = self.endstyle
        arrowstyle = self.arrowstyle
        linewidth = self.linewidth
        linestyle = self.linestyle
        linecolor = self.linecolor
        r = self.r
        ret = ''
        ret += BaseNode.__str__(self)
        ret += line(x0=x0, y0=y0, x1=x1, y1=y1,
                    points=points,
                    startstyle=startstyle,
                    arrowstyle=arrowstyle,
                    endstyle=endstyle,
                    linestyle=linestyle,
                    linecolor=linecolor,
                    linewidth=linewidth,
                    r=r)
        return ret
    
#==============================================================================
# Arc
#==============================================================================
def arc(x=0, y=0, r=0, angle0=0, angle1=0,
        linewidth='', color='', linecolor='', linestyle=''):
    # TODO: add linewidth an color
    if linecolor!='': color=linecolor
    style = get_style(linewidth=linewidth, color=color, linestyle=linestyle)
    return r"\draw[%s] (%s,%s) arc (%s:%s:%s);" % \
           (style, x, y, angle0, angle1, r)

def text(x=0, y=0, s='', color='', font=r'\ttfamily'):
    return r"""\draw[%s, font=%s] (%s, %s) node {%s};
""" % (color, font, x, y, s)

def boxed_text(x0, y0, x1, y1, label):
    # DEPRECATED: Use rect and Rect instead
    s = rect(x0, y0, x1, y1)
    x2, y2 = (x0+x1)/2.0, (y0+y1)/2.0
    s += text(x2, y2, label)
    return s

#==============================================================================
# Pointer
#==============================================================================
def pointer(points, color=''):
    # points is a list of (x,y).
    # This draws a line with endpoints from points.
    # A filled circle of radius of radius 0.1cm.
    s = circle(points[0][0], points[0][1], radius=0.1)
    
    if color != '': color = ',' + color
    s += r"\draw[-> %s] (%s, %s)" %  (color, points[0][0], points[0][1])
    for point in points[1:]:
        s += " -- (%s, %s)" % (point[0], point[1])
        s += ";\n"
    return s

class Pointer(Line):
    def __init__(self,
                 x0=0, y0=0, x1=0, y1=0,
                 points=None,
                 linestyle = '', # solid, dash, etc
                 linecolor='black',
                 linewidth=POINTER_LINEWIDTH,
                 debug=False):
        Line.__init__(self,
                      x0=x0, y0=y0, x1=x1, y1=y1,
                      points=points,
                      startstyle='dot', 
                      endstyle='->',
                      linestyle=linestyle,
                      linecolor=linecolor,
                      linewidth=linewidth,
                      r=1.5*linewidth,
                      debug=False)


    
def get_points(x0=0, y0=0, x1=0, y1=0, style='hbroom'):
    """
    style:
        'vbroom':
                     |
                     +-----+
                           |
        'hbroom'
    """
    if style == 'hbroom':
        x3,y3 = x1,y1
        x1,y1 = (x0+x3)/2.0,y0
        x2,y2 = x1,y3
        return [[x0,y0],[x1,y1],[x2,y2],[x3,y3]]
    elif style == 'vbroom':
        x3,y3 = x1,y1
        x1,y1 = x0,(y0+y3)/2.0
        x2,y2 = x3,y1
        return [[x0,y0],[x1,y1],[x2,y2],[x3,y3]]
    return points

#==============================================================================
# attach points
# the following computes starting/ending points of edges
# the points are on the boundary of the shapes
# any point on the boundary can be returned.
# however there are special points: top, bottom, left, right, topright, etc.
#==============================================================================
def get_edge(x0=0, y0=0, x1=0, y1=0, 
             width=0, height=0, radius=0,
             node_shape='rect'):
    # returns a,b,c,d where (a,b), (c,d) are points of the edge
    # joining the two nodes with given data
    if node_shape == 'rect':
        if y0 - height/2.0 > y1 + height / 2.0:
            # pointing down
            return x0, y0 - height/2.0, x1, y1 + height/2.0
        elif y0 + height/2.0 < y1 - height / 2.0:
            # pointing up
            return x0, y0 + height / 2.0, x1, y1 - height / 2.0
        else:
            # sideways
            return x0 + width / 2.0, y0, x1 - width / 2.0, y1
    elif node_shape == 'circle':
        source = x0, y0
        target = x1, y1
        # compute intersection of line st and circle about s
        st = [target[0] - source[0], target[1] - source[1]]
        length = math.sqrt(st[0]**2 + st[1]**2)
        u = [st[0]/length, st[1]/length]
        s1 = [source[0] + radius * u[0], source[1] + radius * u[1]]
        # compute intersection of line ts and circle about t
        ts = [-st[0], -st[1]]
        u = [-u[0], -u[1]]
        t1 = [target[0] + radius * u[0], target[1] + radius * u[1]]
        return s1[0], s1[1], t1[0], t1[1]

def tree2(edges=[],
          label={},
          node_constructor=None):
    """
    Want to take tree of edges and let the function position the
    nodes.

    edges = {'A':['B','C','D'],
             'B':['E','F','G'],
            }

    label = {'A':'$a$'}

    Note: the graph might be a forest.
    
    1. Find all leaves
    
    """

    # vertices
    vertices = []
    for k, v in edges.items():
        if k not in vertices: vertices.append(k)
        for x in v:
            if x not in vertices: vertices.append(x)
        
    print "vertices:", vertices

    for v in vertices:
        if v not in edges.keys():
            edges[v] = []
    
    label_keys = label.keys()
    for k in v:
        if k not in label_keys: label[k] = k
    
    s = ''
    return s

def tree(pos, # return value from function positions
         width = 0.5,
         height = 0.5, # assume rect
         edges = [], # list of [name1, name2] where name1, name2 are keys in
                # positions or [name1:[name2,name3,name4]
         hor_sep = 0.25, # min horizontal separation between rect boundaries
         node_shape = 'circle',
         node_label = None,
         radius = 0.25,
         autoadjust=False,
         ):
    keys = pos.keys()
    if node_label == None:
        node_label = {}
    for key in keys:
        if key not in node_label.keys():
            node_label[key] = key

    for key in pos.keys():
        if key not in edges.keys():
            edges[key] = []
            
    if autoadjust:
        height_nodes = {}
        for key in keys:
            y = pos[key][1]
            if y not in height_nodes.keys(): height_nodes[y] = []
            height_nodes[y].append(key)
        heights = height_nodes.keys()
        heights.sort()
        for i,h in enumerate(heights):
            if i == 0:
                nodes = height_nodes[h]
                x_nodes = [(pos[node][0], node) for node in nodes]
                x_nodes.sort()
                for j,x_node in enumerate(x_nodes):
                    if j == 0:
                        pos[node][0] = 0
                    else:
                        x,node = x_node
                        pos[node][0] = j * (width + hor_sep)
            else:
                # not leaves case
                nodes = height_nodes[h]
                # order nodes by x-coord
                nodes = [(pos[node][0], node) for node in nodes]
                nodes.sort()
                nodes = [node for _,node in nodes]
                for j,node in enumerate(nodes):
                    # find children and set x of node to be the middle
                    # if a node does not have children, then
                    # set it to the middle between siblings [FIXIT]
                    children = edges[node]
                    if children != []:
                        minx = min([pos[child][0] for child in children])
                        maxx = max([pos[child][0] for child in children])
                        pos[node][0] = (minx + maxx)/2.0
                    else:
                        # no children
                        if j == 0: # leftmost sibling
                            pos[node][0] = 0
                        else: # fix
                            leftsibling = nodes[j - 1]
                            pos[node][0] = pos[leftsibling][0]+width+hor_sep
                        
    s= ""
    for key in keys:
        center_x, center_y = pos[key]
        x0 = center_x - width / 2.0
        y0 = center_y - height / 2.0
        x1 = center_x + width / 2.0
        y1 = center_y + height / 2.0
        if node_shape == 'rect':
            s += rect(x0=x0, y0=y0, x1=x1, y1=y1,
                      align='c',
                      s=node_label[key])
        elif node_shape == 'circle':
            s += circle(x=center_x, y=center_y, r=radius,
                        s=node_label[key])
                
    if node_shape == 'rect':
        for key in keys:
            source_x, source_y = pos[key]
            for target in edges.get(key, []):
                target_x, target_y = pos[target]

                if source_y - height/2.0 > target_y + height / 2.0:
                    # pointing down
                    s += line(source_x, source_y - height/2.0,
                              target_x, target_y + height/2.0)
                elif source_y + height/2.0 < target_y - height / 2.0:
                    s += line(source_x, source_y + height / 2.0,
                              target_x, target_y - height / 2.0)
                else:
                    # sideways
                    s += line(source_x + width / 2.0, source_y,
                              target_x - width / 2.0, target_y)
    elif node_shape == 'circle':
        for key in keys:
            source_x, source_y = pos[key]
            for target in edges.get(key, []):
                target_x, target_y = pos[target]
                source = source_x, source_y
                target = target_x, target_y
                # compute intersection of line st and circle about s
                st = [target[0] - source[0], target[1] - source[1]]
                length = math.sqrt(st[0]**2 + st[1]**2)
                u = [st[0]/length, st[1]/length]
                s1 = [source[0] + radius * u[0], source[1] + radius * u[1]]
                # compute intersection of line ts and circle about t
                ts = [-st[0], -st[1]]
                u = [-u[0], -u[1]]
                t1 = [target[0] + radius * u[0], target[1] + radius * u[1]]
                s += line(s1[0], s1[1], t1[0], t1[1])
    return s

#==============================================================================
# For drawing arrays
# array - 1d array drawn horizontally
#==============================================================================
def array(x0, y0, width, height,
          xs,
          linewidth=L,
          arraylinewidth=L, celllinewidth='',
          color=''):
    if arraylinewidth==0 and linewidth!=0: arraylinewidth=linewidth
    if celllinewidth==0 and linewidth!=0: celllinewidth=linewidth

    s = ''    
    s += rect(x0=x0, y0=y0,
              x1=x0+len(xs)*width, y1=y0+height,
              linewidth=arraylinewidth)
    textx = x0 + width / 2.0
    texty = y0 + height / 2.0
    linex = x0 + width
    liney = y0
    for i, x in enumerate(xs):
        s += text(textx, texty, x, color=color)
        textx += width
        if i != len(xs) - 1:
            s += line(linex, liney, linex, liney+height,
                      color=color, linewidth=celllinewidth)
            linex += width
    return s

#==============================================================================
# 2d array
#==============================================================================
def array2(x0=0, y0=0, width=1.0, height=1.0,
           vs=[],
           linewidth=0,
           arraylinewidth=L, celllinewidth=L,
           color='',
           ):
    ret = ''
    x = x0
    for v in vs:
        r = Rect(x0=x, y0=y0, x1=x+width, y1=y0+height, label=v,
                 linewidth=celllinewidth)
        ret += str(r)
        x += width - celllinewidth
    return ret

class Array2d(RectContainer):
    def __init__(self, x=0, y=0, xs=[],
                 linewidth=L, width=1, height=1, linecolor='black'):
        RectContainer.__init__(self, x=x, y=y, align='left', direction='top-to-bottom')
        for row in xs:
            c = RectContainer(x=0, y=0, align='bottom', direction='left-to-right')
            for x in row:
                c += Rect2(x0=0, y0=0, x1=width, y1=height,
                           linewidth=linewidth, linecolor=linecolor,
                           label=r'{\texttt{%s}}' % x)
            self += c
        for c in self:
            c.x = c.x0; c.y = c.y0; c.layout()


"""
class Array2d: # (RectContainer): # Maybe subclass RectContainer??
    def __init__(self, x=0, y=0, xs=[],
                 width=1, height=1,
                 linewidth=0.04,
                 linecolor='black'):
        
        self.arr = RectContainer(x=0, y=0, align='left', direction='top-to-bottom')
        for rows in xs:
            c = RectContainer(x=0, y=0,
                              align='bottom', direction='left-to-right')
            for x in rows:
                c += Rect2(x0=0, y0=0, x1=width, y1=height,
                           linecolor=linecolor, linewidth=linewidth,
                           label=r'{\texttt{%s}}' % x)
            self.arr += c
        for c in self.arr:
            c.x = c.x0
            c.y = c.y0
            c.layout()
        
    def __str__(self):
        return str(self.arr)
"""

#==============================================================================
# draw swaps
#
# swaps is a list of (index1, index2, dy)
#     p4     p5
#     --------
#    /        \  <---- 90 degree arc
# p1 |        | p2     with radius = cellwidth/2
# p0 v        v p3
#
# general function bend: specify
#     --------       ^
#    /        \      | dy=1   radius of arc (default=min(|dy|, |p0[0], p1[0]|))
#    |        |      |
# p0 v        v p3   v
#
# default radius computation
# CASE:
#     --       
#    /  \      
#    |  |      
# p0 v  v p3 
# radius = (x distance of p0-p3)/2
#
# CASE:
#     --------------       
#    /              \      
#    |              |      
# p0 v              v p3 
# radius = dy
# for now assume p0,p3 parallel to x axis
def bend(p0, p3, dy=1, radius=None,
         linewidth=L, linecolor='black', linestyle=''):
    if radius == None: radius=min(abs(dy), abs(p0[0] - p3[0])/2.0)
    dx = p3[0] - p0[0]
    if dy > 0:
        p1 = [p0[0], max(p0[1], p3[1]) + dy - radius]
        if p0[1] >= p1[1]: # something's funny here
            p1[1] = p0[1] + 0.0001
    else:
        p1 = (p0[0], min(p0[1], p3[1]) + dy + radius)
    p2 = (p0[0] + dx, p1[1])
    p4 = (p0[0] + radius, p0[1] + dy)
    p5 = (p3[0] - radius, p0[1] + dy)
    s = ''
    # left vertical arrow
    s += line(p1[0], p1[1], p0[0], p0[1],
              linewidth=linewidth, linecolor=linecolor, linestyle=linestyle,
              endstyle='->', arrowstyle='triangle')
    # right vertical arrow
    s += line(p2[0], p2[1], p3[0], p3[1], endstyle='->',
              linewidth=linewidth, linecolor=linecolor, linestyle=linestyle,
              arrowstyle='triangle')
    # hroizontal line
    s += line(p4[0], p4[1], p5[0], p5[1],
              linewidth=linewidth, linecolor=linecolor, linestyle=linestyle)
    # draw arcs
    if dy > 0:
        s += arc(x=p2[0], y=p2[1], r=radius, angle0=0, angle1=90,
                 linewidth=linewidth, linecolor=linecolor, linestyle=linestyle)
        s += arc(x=p1[0], y=p1[1], r=radius, angle0=180, angle1=90,
                 linewidth=linewidth, linecolor=linecolor, linestyle=linestyle)
    else:
        s += arc(x=p2[0], y=p2[1], r=radius, angle0=0, angle1=-90,
                 linewidth=linewidth, linecolor=linecolor, linestyle=linestyle)
        s += arc(x=p1[0], y=p1[1], r=radius, angle0=180, angle1=270,
                 linewidth=linewidth, linecolor=linecolor, linestyle=linestyle)
    return s




#==============================================================================
# The function shell executes a linux shell command and returns the stdout
# and stderr.
#==============================================================================
def myexec(cmd, timeout=None):
    """
    execute a shell command with timeout.
    TODO: timeout not done yet
    """
    from subprocess import Popen, PIPE

    p = Popen(cmd, shell=True, bufsize=0,
              stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    p.wait() # can be a problem ...
    (stdin,
     stdout,
     stderr) = (p.stdin, p.stdout, p.stderr)
    stdout = stdout.read().strip()
    stderr = stderr.read().strip()
    returncode = p.returncode
    return stdout, stderr, returncode

def exec_python(s):
    pass

def pdflatex(filename):
    if not filename.endswith('.tex'): filename += '.tex'
    d = {'filename':filename}
    cmd = 'pdflatex -halt-on-error --shell-escape %(filename)s' % d
    stdout, stderr, returncode = myexec(cmd)
    if os.path.exists('%s.pdf' % filename):
        # second pass ... how to check if this is necessary?
        stdout, stderr, returncode = myexec(cmd)
    return stdout, stderr, returncode

def pdfcrop(filename):
    if not filename.endswith('.pdf'): filename += '.pdf'
    d = {'filename':filename}
    cmd = 'pdfcrop %(filename)s %(filename)s' % d
    stdout, stderr, returncode = myexec(cmd)
    
#==============================================================================
# The function shell executes a linux shell command and returns the stdout
# and stderr.
#==============================================================================

def getprompt(hostname='localhost'):
    import getpass
    user = getpass.getuser()
    cwd = os.getcwd()
    a,b = os.path.split(cwd)
    if b == user: b = '~'
    return "[%s@%s %s]" % (user, hostname, b)

def postprocess(s): return s

def shell2(cmd,
          CWD='home/student',
          TESTDIR='',
          dir='', # a better name for TESTDIR
          postprocess=None,
          latex=True,
          execute=True,
          ):
    # Same as shell() except that this version has cache
    ahash = hash(str(cmd))
    filename = 'tmp/%s.tex' % ahash 
    if os.path.exists(filename):
        s = readfile(filename)
    else:
        s = shell(cmd=cmd,
                  CWD=CWD,
                  TESTDIR=TESTDIR,
                  dir=dir,
                  postprocess=postprocess,
                  latex=latex,
                  execute=execute,
                  )
        writefile(filename, s)
    # add hash filename to s
    if latex:
        s += r'''
\begin{center}
{\scriptsize \verb!%s!}
\end{center}
''' % filename
    return s
    
def shell(cmd,
          CWD='home/student',
          TESTDIR='',
          dir='', # a better name for TESTDIR
          postprocess=None,
          latex=True,
          execute=True,
          prompt=None,
          ):
    if isinstance(cmd, str): cmd = [cmd]
    cwd = os.getcwd()
    if dir != '': TESTDIR = dir
    
    if TESTDIR: os.chdir(TESTDIR)
    if not prompt:
        prompt = getprompt()
    s = ''
    for c in cmd:
        if execute:
            p = Popen(c, shell=True, bufsize=2048,
                      stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
            p.wait() # can be a problem ...
            (stdin,
             stdout,
             stderr) = (p.stdin, p.stdout, p.stderr)
            stdout = stdout.read()
            stderr = stderr.read()
        else:
            stdout = stderr = ''
        
        t = "%s %s\n%s%s" % (prompt, c, stdout, stderr)
        t = t.replace(cwd, CWD)
        if postprocess:
            t = postprocess(t)
        s += t
        
    s = s.rstrip()
    if latex:
        """
        s = r'''\begin{consoleone}
%s
\end{consoleone}''' % s
        """
        s = verbatim(s)
    os.chdir(cwd)


    
    return s


#==============================================================================
# The function positions a dictionary of k,v where k is the string and v
# is the position of k.
#==============================================================================
def positions(layout="", xscale=1, yscale=1):
    """ If layout is 
  A
B C
    Then this returns {'A':(2,0), 'B':(0,-1), 'C':(2,-1)}
"""
    layout = [_ for _ in layout.split('\n')]
    # removing pre-pended blank lines
    while 1:
        if layout[0].strip() == '':
            layout = layout[1:]
        else:
            break

    d = {}
    for row,line in enumerate(layout):
        s = line
        symbols = [_ for _ in s.split(' ') if _ != '']
        for symbol in symbols:
            col = line.index(symbol)
            if d.has_key(symbol):
                raise ValueError("repeat symbols %s" % symbols)
            d[symbol] = [col*xscale, -row*yscale]
    return d








def pipes(center=[0,0],
          numpipes=1, pipeheight=1, pipewidth=0.3, dx=0.2,
          color=''):
    # draws a bunch of | 
    pass
    s = ''
    s += line(pipex, pipey, 
              pipex, pipey + pipeheight,
              linewidth=pipewidth, color=color)


def chunkedarray(x=0, y=0, cellwidth=1, cellheight=1,
                 arr=[],
                 linewidth=L,
                 color='',
                 pipewidth=0.1,
                 spacing=0.1,
                 pipeheight=None,
                 chunklabels=[],
                 celllabels=[],
                 swaps=[],
                 labels=[], # new
                 dividers=[]): # new
 
    # labels is a list of
    # s, index, description
    #
    # Example: s='pivot', index=0, description='<->', dy = 1
    # Example: s='pivot', index=0, description='--', dy = 1
    # Example: s='kill', index=[0,5,6], description='->', dy = -1
    # Example: s='kill', index=[0,5,6], description='->', dy = -1
    # Example: s='left', index=[0,5], description='{', dy=-1

    def celltop(index):
        # compute the (x,y) of the cell at index
        pass
    
    def cellbottom(index):
        pass
    
    xss = arr
    if pipeheight==None:
        pipeheight = cellheight * 1.4

    s = ''

    # draw cells
    ys = []
    for xs in xss:
        ys += xs
    s += array(x, y, width=cellwidth, height=cellheight, xs=ys,
               linewidth=linewidth, arraylinewidth=linewidth, celllinewidth=linewidth)

    # Draw the bend for swaps
    for swap in swaps:
        if len(swap) == 2:
            index1, index2 = swap
            dy = -cellwidth
        else:
            index1, index2, dy = swap
        if index1 > index2: index1, index2 = index2, index1
        x0 = x + (index1 + 0.5) * cellwidth
        x1 = x + (index2 + 0.5) * cellwidth
        if dy > 0:
            y0 = y1 = y + cellheight
        else:
            y0 = y1 = y
        s += bend([x0,y0], [x1,y1], dy, cellwidth/2.0) # , cellwidth / 2.0)
         
    # draw cell labels
    # distinguish between label above or below
    for nodetext, index, dy in celllabels:
        celllabelx = x + (index + 0.5) * cellwidth
        # NOTE: dy is the displacement from the bottom or the
        # top of the cell
        if dy < 0:
            celllabely = y + dy
        else:
            celllabely = y + (dy + cellheight)
        s += text(celllabelx, celllabely, nodetext)
        arrowheadx = celllabelx
        arrowtailx = celllabelx
        if dy < 0:
            arrowtaily = y + dy + 0.3
            length = -dy - 0.3
        else: # dy >= 0
            arrowtaily = y + cellheight + dy - 0.3
            length = -dy + 0.3
        s += "%s" % Path(x=arrowtailx, y=arrowtaily, start='',
                         points=[(0,0), (0, length)], linewidth='1')

    # draw chunk labels
    for i,chunklabel in enumerate(chunklabels):
        if isinstance(chunklabel, (list, tuple)):
            label, dy = chunklabel
        else:
            label = chunklabel
            dy = 0.7
        # compute center of label
        x0 = x + cellwidth * sum([len(xs) for xs in xss[:i]])
        x1 = x0 + cellwidth * len(xss[i])
        labelx = (x0 + x1)/2.0
        if dy > 0:
            labely = y + cellheight + dy
        else:
            labely = y + dy
        s += text(labelx, labely, label)
        # draw 'brace'
        if label != '':
            if dy > 0:
                if abs(x0 - x1) >= 0.5:
                    s += '\draw (%s,%s) -- (%s,%s) -- (%s,%s);\n' % \
                     (x0+0.1, y+cellheight+0.1,
                      labelx, labely - 0.6 * dy,
                      x1-0.1, y+cellheight+0.1)
                    s += '\draw (%s,%s) -- (%s,%s);\n' % \
                     (labelx, labely - 0.6 * dy,
                      labelx, labely - 0.3)
                else:
                    s += '\draw (%s,%s) -- (%s,%s);\n' % \
                     (labelx, y+cellheight+0.1, labelx, labely - 0.3)
            else:
                if abs(x0 - labelx) >= 0.3:
                    s += '\draw (%s,%s) -- (%s,%s) -- (%s,%s);\n' % \
                         (x0+0.1, y-0.1, labelx, y-cellwidth/2, x1-0.1, -0.1)
                    s += '\draw (%s,%s) -- (%s,%s);\n' % \
                         (labelx, y-cellwidth/2, labelx, labely + 0.3)
                else:
                    s += '\draw (%s,%s) -- (%s,%s);\n' % \
                         (labelx, y-0.1, labelx, labely + 0.3)
    # draw pipes
    # correct case of multiple consecutive empty lists (can be a problem is there are too many ...)

    # new pipe drawing
    i = 0
    runlen = 0
    pipey = y - (pipeheight - cellheight) / 2.0
    while i < len(xss):
        runlen += len(xss[i])
        
        # count number of empty lists after xss[i]
        j = i + 1 # have to keep i so as to compute drawing position
        numempty = 0
        while j < len(xss) and xss[j] == []:
            numempty += 1
            j += 1
            
        # draw pipes at index i
        count = numempty + 1 # number of pipes to draw

        if j == len(xss): count -= 1
        
        x0 = x + runlen * cellwidth # pipes about this x-coord
        #
        #             # # # # # #
        #             # # # # # # 
        #             # # # # # #
        # -----------------+--------------------
        #                  x0
        # Total width of pipes = numpipes * (pipewidth) + (numpipes - 1) * spacing
        totalwidth = count * pipewidth + (count - 1) * spacing 
        pipex = x0 - totalwidth/2.0 + pipewidth/2.0
        if i == 0 and xss[0] == []:
            pipex = x + spacing
        elif j == len(xss):
            pipex = pipex - totalwidth / 2.0 - spacing/2.0
        for k in range(count):
            s += line(pipex, pipey, 
                      pipex, pipey + pipeheight,
                      linewidth='%scm' % pipewidth, color=color)
            pipex += pipewidth + spacing
        i = j

    return s



#==============================================================================
# Draws a frame/record.
#==============================================================================
def frame(env, top='', W=1.2, H=0.6):
    # TODO: string
    # TODO: pointer
    # TODO: heap
    # TODO: frame stack
    
    # W - width of int value box
    # H - height of value box

    s = ''
    y = 0
    h = H
    space = 0.2 # between boxes
    s = rect(x0=-1, y0= -(h + space) * (len(env) - 1) - h, x1=3, y1=1, linewidth=0.1)

    if top != '':
        s += rect(x0=-1, y0=1, x1=3, y1=1.5, s=r'{\verb!%s!}' % top, linewidth=0)
    for k,v in env:
        if isinstance(v, int): w = W
        elif isinstance(v, float): w = W * 2
        elif isinstance(v, str) and len(v) == 1: w = W / 2
        else: w = W

        s += text(x=-0.5, y=y+h/2.0, s=k)
        s += rect(x0=0, y0=y, x1=w, y1=y+h)
        
        if isinstance(v, str) and len(v) == 1:
            s += text(x=w/2.0, y=y+h/2.0, s=r"{\verb!'%s'!}" % v)
        else:
            s += text(x=w/2.0, y=y+h/2.0, s="%s" % v)
        y -= h + space
        
    return s


#==============================================================================
# Save pdf image and do pdfcrop
# makepdf(latex) will create a cropped pdf with the latex fragment.
# This is saved in tmp/[filename] where filename is the md5 hash digest of
# the latex string.
#
# Handle 2 cases:
# - latex is a latex fragment
# - latex is a python program that generates a latex fragment
#==============================================================================
def makepdf(latex,
            ahash=None,
            ):
    if ahash==None: ahash = hash(latex)
    latex = latex.strip()
    TMP = 'tmp'
    s = r"""
\documentclass[a4paper,12pt]{scrbook}
\usepackage{amsmath,amssymb,amsthm}
\usepackage{fancyvrb}
\usepackage{parskip}
\usepackage{lastpage}
\usepackage{verbatim,boxedminipage,enumitem}
\usepackage{ifthen}
\usepackage{color,graphicx}
\usepackage{pgf}
\usepackage{longtable}
\usepackage{upquote}
%\usepackage[all]{xy}
\usepackage{tobiShell}
\usepackage{tikz}
\usetikzlibrary{automata}
\usetikzlibrary{arrows}
\usepackage{pgf,pgfarrows,pgfnodes}
\usepackage{pgfplots}
\usepackage{circuitikz}
\usetikzlibrary{circuits}
\usetikzlibrary{circuits.logic.US}
\usepackage{mymath}
\usepackage{python}
%------------------------------------------------------------------
% Verbatim for console window - single line frame, no line numbers
%------------------------------------------------------------------
\DefineVerbatimEnvironment%
 {console}{Verbatim}
 {frame=single}

%--------------------------------------------------------
% Remove the vertical spacing before and after Verbatim.
%--------------------------------------------------------
\usepackage{atbeginend}
\BeforeBegin{console}{\mbox{}\\ \begin{minipage}{\textwidth}\vspace{3pt}}
\AfterEnd{console}{\vspace{4pt} \end{minipage} \\ }

\begin{document}
\thispagestyle{empty}

""" + latex + r"""

\end{document}
"""
    
    import os
    cwd = os.getcwd()
    if not os.path.exists(TMP):
        os.makedirs(TMP)
    os.chdir(TMP)

    filename = ahash
    writefile("%s.tex" % filename, s)

    stdout, stderr, returncode = pdflatex(filename)
    
    if os.path.exists("%s.pdf" % filename):
        stdout, stderr, returncode = pdfcrop(filename)
    else:
        pass
    os.chdir(cwd)
    return stdout, stderr, returncode

def hash(s):
    import hashlib
    return hashlib.md5(s).hexdigest()

    
def includegraphics(filename, include_filename=False):
    #print "includegraphics ..."
    if include_filename:
        return r"""\begin{center}
\includegraphics{%s}
\\
{\scriptsize \verb!%s!}
\end{center}
""" % (filename, filename)
    else:
        return r"""\begin{center}
\includegraphics{%s}
\end{center}
""" % filename
    



def makeandincludegraphics(latex='',
                           python='',
                           filename=None,
                           include_filename=True,
                           ):
    if filename!=None:
        ahash = filename
    else:
        ahash = IFELSE(python!='', hash(python), hash(latex))

    #--------------------------------------------------------------------------
    # Execute python source to get latex string. If there's an error,
    # execute_error is True.
    # If python source is '', just use the parameter latex.
    #--------------------------------------------------------------------------
    execute_error = False
    if python!='':
        latex = execute(python, print_result=False)
        # WARNING: latex can be stdout or console of source,stdout,stderr.
        # The following hack disambiguates
        if latex.count(r'\begin{console}') == 3: execute_error = True
    else:
        # in this case the parameter latex is used directly
        pass

    if execute_error:
        # The above python source has an error. 
        return latex
    else:
        # Use latex directly or python was executed without error.
        hash_latex_pdf = "tmp/%s.pdf" % ahash
    
        if not os.path.exists(hash_latex_pdf):
            stdout, stderr, returncode = makepdf(latex, ahash)

        if not os.path.exists(hash_latex_pdf):
            return r"""
***** ERROR IN makeandincludegraphics: no pdf file.

See tmp/%s.tex.

See stdout and stderr below:
%s
%s
""" % (ahash, console(stdout[-600:]), console(stderr[-600:]))
        else:
            return includegraphics(hash_latex_pdf, include_filename=include_filename)







class Node(BaseNode):
    def __init__(self,
                 x=None, y=None, # center
                 w=None, h=None, # width, height
                 x0=None, y0=None, x1=None, y1=None, # bounding box
                 # Note that either w,h or x0,y0,x1,y1 is specified
                 s='',
                 align='t',
                 innersep=0.07,
                 radius=0.1,
                 background='blue!5!white',
                 linewidth=0,
                 linestyle='',
                 debug=True):
        BaseNode.__init__(self,
                          x=x, y=y, w=w, h=h,
                          x0=x0, y0=y0, x1=x1, y1=y1,
                          debug=debug)
        self.s = s
        self.align = align
        self.innersep = innersep
        self.radius = radius
        self.background = background
        self.linewidth = linewidth
        self.linestyle = linestyle
        
    def __str__(self):
        x0 = self.x0
        x1 = self.x1
        y0 = self.y0
        y1 = self.y1
        s = r'{\textsf{\scriptsize %s}}' % self.s
        background = self.background
        innersep = self.innersep
        radius = self.innersep
        align = self.align
        linewidth = self.linewidth
        linestyle = self.linestyle
        ret = rect(x0=x0, y0=y0, x1=x1, y1=y1,
                 innersep=innersep, radius=radius,
                 align=align, s=s, background=background, linewidth=linewidth,
                 linestyle=linestyle)
        ret += BaseNode.__str__(self)
        return ret




#==============================================================================
# This is used by cs-prog.py
#==============================================================================
class Container(Node):
    # Extra boundary spacing for component nodes 
    BORDERX = 0.1
    BORDERY = 0.15

    def __init__(self, nodes=[], s=''):
        if nodes == []:
            raise "Container.__init__: nodes is empty"
        # compute rect data and place in d
        minx = min([n.x0 for n in nodes])
        maxx = max([n.x1 for n in nodes])
        miny = min([n.y0 for n in nodes])
        maxy = max([n.y1 for n in nodes])
        if s=='':
            align = 'c'
        else:
            align = 't'

        # WARNING: hardcode
        if s in ['INTERMEDIATE', 'ADVANCED']:
            s = ''
        else:
            maxy += 0.4 # Hardcoded
            s = r'''\begin{center}
            %s
            \end{center}
            ''' % s
        Node.__init__(self,
                      x0=minx - Container.BORDERX,
                      y0=miny - Container.BORDERY,
                      x1=maxx + Container.BORDERX,
                      y1=maxy + Container.BORDERY,
                      s=s,
                      linewidth=0.01, # ADDED
                      align=align)




class Path:

    """
    suppose points = [p0, p1]

    points is a sequence of (x,y) or [x,y] and strings
    the strings are
    "left 0.5", "right 2", "up 5", "down 2"
    "flush left", "flush right", "flush up", "flush down"

    flush is toward the bounding box of p0, p1
    flush left: point is from current point in path to the left of bounding box
    flush right: ... to the left of bounding box
    """
        
    def __init__(self,
                 x=0, y=0, # offset of the points
                 points=[],
                 description=None,
                 start='dot', end='->',
                 color='', linewidth='', moves=''):
        self.x = x
        self.y = y
        self.color = color
        self.linewidth = linewidth
        self.start = start
        self.end = end

        # CHECK THIS FIX FOR OTHER CASES
        if self.start == '<-' and self.end == '->':
            self.end = '<->'
        
        self.points = []
        if description in [None, '']:
            self.points = points
        elif description.startswith('down'):
            # Example: description = "down 0.5"
            down = description.split(' ')[1].strip()
            down = float(down)
            # draws a "U" shape path of one of the following shapes:
            #              P
            # S            |     or     |
            # ^            |            |             ^
            # |            |            |             |
            # +------------+            +-------------+
            # R             Q
            # points is the starting point and ending point
            P = [x + points[0][0], y + points[0][1]]
            Q = [P[0], P[1] - down]
            R = [points[1][0], Q[1]]
            S = [x + points[1][0], y + points[1][1]]
            self.points = [P, Q, R, S]
        elif description.startswith('up'):
            # Example: description = "up 0.5"
            up = description.split(' ')[1].strip()
            up = float(up)
            # R            Q
            # +----------- +
            # |            |     
            # |            |     
            # V            |     
            # S            |     
            #              P
            P = [x + points[0][0], y + points[0][1]]
            Q = [P[0], P[1] + up]
            R = [points[1][0], Q[1]]
            S = [x + points[1][0], y + points[1][1]]
            self.points = [P, Q, R, S]
        elif description == '???':
            # CASE: 90 degree turn (i.e. something like L shape or
            # rotation or reflection)
            pass

        # ALTERNATIVE TO description
        if moves!="" and len(self.points) > 0:
            pass
            
    def __str__(self):
        if self.points in [[], None] : return ''

        if self.linewidth not in ['', None]:
            linewidth = "line width=%s" % self.linewidth
        else:
            linewidth = ''
        s = r"\draw[%s] " % ','.join([self.end, self.color, linewidth])
        
        points = self.points
        
        #x, y = self.center() ?????
        x, y = self.x, self.y
        
        s += "(%s, %s)" %  (x + points[0][0], y + points[0][1])
        for point in points[1:]:
            s += " -- (%s, %s)" % (x + point[0], y + point[1])
        s += ";\n"
            
        # draw start if it's a dot
        if self.start == 'dot':
            s += circle(x+points[0][0], y+points[0][1],
                        filled=True, color=self.color)
        return s
        
#==============================================================================
# Doubly Linked List Node
#==============================================================================
class DoublyLinkedListNode(RectContainer):
    def __init__(self, x=0, y=0, prev='', label='', next='', linewidth=DOUBLE_LINKED_LIST_LINEWIDTH):
        RectContainer.__init__(self, x=x, y=y)
        if prev == None:
            self += CrossedRect2(0, 0, 0.5, 0.5, linewidth=linewidth)
        else:
            self += Rect2(0, 0, 0.5, 0.5, linewidth=linewidth)
        self += Rect2(x0=0, y0=0, x1=1, y1=0.5, linewidth=linewidth, label=r'\texttt{%s}' % label)
        if next == None:
            self += CrossedRect2(0, 0, 0.5, 0.5, linewidth=linewidth)
        else:
            self += Rect2(0, 0, 0.5, 0.5, linewidth=linewidth)

#==============================================================================
# consolegrid
#==============================================================================
def consolegrid(numrows=1, numcols=21, s=''):
    if isinstance(s, str):
        lines = s.split('\n')
        if len(lines) > numrows: numrows = len(lines)
        lines = [list(line) for line in lines]
        tnumcols = max([len(line) for line in lines] + [-1])
        numcols = max(numcols, tnumcols)
        lines = [line + ['' for i in range(numcols - len(line))] \
                 for line in lines]
        lines = lines + [ ['' for k in range(numcols)] \
                          for i in range(numrows - len(lines))]
    elif isinstance(s, list):
        lines = [['' for i in range(numcols)] for j in range(numrows)]
        for i, row in enumerate(s):
            for j, col in enumerate(row):
                lines[i][j] = col
    s = '|'.join(['p{0.35cm}' for _ in range(numcols)])
    s = '|%s|' % s + '}\n'
    s += r'\hline' + '\n'
    for line in lines:
        s += ' & '.join(line)
        s += r' \\ \hline'  + '\n'
    s = s[:-1]
    return r"""
{\Large\texttt{
\begin{longtable}{
%s
\end{longtable}
}}""" % s










#==============================================================================
# This is from the ciss362-automata/r/dfa/graph/graph.py and is the latest
# version
#==============================================================================

def automata(
    xscale=1,
    yscale=2,
    layout="",
    separator="|",
    edges="",
    initial_bend=28,
    delta_bend=8,
    **args
    ):
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
    node_items = node.items()
    node_items.sort()
    for k,v in node.items():
        d = {}
        d['name'] = k
        d['label'] = v['label']
        d['initial'] = v['initial']
        d['accept']= v['accept']
        try:
            d['pos'] = "(%3s,%3s)" % (v['pos'][0], v['pos'][1])
        except:
            print "v[pos]:", v['pos']
            raise
        node_str += r"\node[state%(initial)s%(accept)s] (%(name)s) at %(pos)s {%(label)s};" % d
        node_str += '\n'

    def edge_shape(q0,q1,node,e):

        # edges going right: label above
        # edges going left: label below
        #
        
        def between(p0,p,p1):
            u = p[0]-p0[0], p[1]-p0[1]
            v = p1[0]-p[0], p1[1]-p[1]
            dot = u[0]*v[0] + u[1]*v[1] # dot product
            len_u = math.sqrt(u[0]*u[0] + u[1]*u[1])
            len_v = math.sqrt(v[0]*v[0] + v[1]*v[1])
            return abs(dot - len_u * len_v) < 0.01
        
        if q0==q1:
            return "[loop above]" # have to decide on which loop
        
        p0, p1 = node[q0]['pos'],node[q1]['pos']
        # count num of nodes between
        count = 0
        for p in node.keys():
            if p not in [q0,q1]:
                if between(p0,node[p]['pos'],p1):
                    count += 1
	#print "p0,p1,count:", p0,p1,count
        if count == 0:
            if (q1,q0) in e.keys(): angle = 10
            else: angle = 0
        else:
            if count == 1:
                angle = initial_bend + delta_bend*count - 5
            else:
                angle = initial_bend + delta_bend*count
        
        if p0[0] < p1[0]:
            return "[bend left=%s,pos=0.5,above]" % angle
        else:
            # the two nodes are on above each other
            # THIS IS WRONG WHEN TARGET NODE IS BELOW SOURCE 
            return "[bend left=%s,pos=0.5]" % angle
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




if __name__ == '__main__':

    '''
    from latextool_basic import *

    bline = Line(points=[(0,-1), (5,-1), (5,-6)], 
                 linecolor='blue', linewidth=0.1, 
                 startstyle='dot', arrowstyle='triangle', endstyle='->')
    
    print bline.midpoint(ratio=0.2)
    '''

    '''
    print table([('',  2, 5,  8),
             ('', '', 3,  6),
            ],
            col_headings = ['0', '2', '5', '8'],
            row_headings = ['0', '2', '5', '8'],
            topleft_heading = r'$\Delta X$',
           )
    '''

    print consolegrid(2)

#==============================================================================
# This is from CISS380 graphics class
#==============================================================================
class vec:
    def __init__(self, x, y=None):
        if y == None:
            self.x = x
        else:
            self.x = []
            for a,b in zip(x, y):
                self.x.append(b - a) 

    def latex(self):
        s = ", ".join([str(_) for _ in self.x])
        return r"\langle %s \rangle" % s

    
    
def plot(vectors=[],
         vector=[]):

    #print "vector:", vector
    #print "vectors:", vectors
    
    if vector != []:
        vectors.append(vector)
        #print "vectors:", vectors
        
    vs = []
    for v in vectors:
        start,end = v
        #print start
        #print end
        a,b = start
        c,d = end
        vs.append(r"\addplot[->] coordinates {(%s,%s) (%s,%s)};" % (a,b,c,d))
    vs = '\n'.join(vs)
    vectors = vs

    return r"""
\begin{center}
\begin{tikzpicture}[>=triangle 60,scale=.6]
\begin{axis}[
width=5in, height=4in,
xmin=-5, xmax=5,
ymin=-3, ymax=5,
axis x line=middle,
axis y line=middle,
grid=major
]
%(vectors)s
\end{axis}
\end{tikzpicture}
\end{center}
""" % {'vectors':vectors}




def answer(width=3, height=1.2, answer=''):

    x0 = 1.25
    x1 = width + x0
    y0 = -height/2
    y1 = height + y0
    
    return r"""
\begin{tikzpicture}
\draw ( %(x0)s, %(y0)s ) rectangle ( %(x1)s, %(y1)s );
\draw (2.6, 0) node { %(answer)s };
\draw (0, 0) node {ANSWER:};
\end{tikzpicture}
""" % {'x0':x0, 'x1':x1, 'y0':y0, 'y1':y1, 'answer':answer}


import sys, copy
from fractions import Fraction

def xxx(v):
    if v < 0: return "(%s)" % v 
    else: return "%s" % v
    

def augmatrix(aug):
    colsize = (aug.colsize)/2
    option = ("c"*colsize) + "|" + ("c"*colsize)
    str_matrix = (r"\begin{bmatrix}[%s]" + '\n') % option
    for row in aug.xs:
        row0 = ["%5s" % _ for _ in row]
        row0 = " & ".join(row0)
        row0 += r" \\" + "\n"
        str_matrix += row0
    str_matrix += r"""\end{bmatrix}
"""
    return str_matrix


def latex_inverse(m):

    n, computations = m.inv()

    s = ""
    for i,computation in enumerate(computations):
        if i != 0: s += r" \displaybreak[0]\\ "
        s += latex(computation)

    x = augmatrix(m.augment())
    return r"""\begin{align*}
%s %s\end{align*}
""" % (x, s)


def latex_bmatrix(xs):

    if isinstance(xs, Matrix): return latex_bmatrix(xs.xs)
    
    s = (r"\begin{bmatrix}" + '\n')
    for row in xs:
        row0 = ["%5s" % _ for _ in row]
        row0 = " & ".join(row0)
        row0 += r" \\" + "\n"
        s += row0
    s += r"""\end{bmatrix}"""
    return s

def latex_mult(m, n):
    s = ""
    s += r"\begin{align*}"
    
    s += "& " + latex_bmatrix(m.xs)
    s += latex_bmatrix(n.xs)
    s += r" \\ " + '\n'

    xs = []
    for r in range(m.rowsize):
        row = []
        for c in range(n.colsize):
            entry = ["(%s)(%s)" % (m[r,k],n[k,c]) for k in range(m.colsize)]
            entry = " + ".join(entry)
            row.append(entry)
        xs.append(row)

    s += "& = "
    s += latex_bmatrix(xs)
    s += r" \\" + "\n"
    
    xs = []
    for r in range(m.rowsize):
        row = []
        for c in range(n.colsize):
            entry = []
            for k in range(m.colsize):
                x = m[r,k] * n[k,c]
                if x < 0: x = "(%s)" % x
                else: x = "%s" % x
                entry.append(x)
            entry = " + ".join(entry)
            row.append(entry)
        xs.append(row)

    s += "& = "
    s += latex_bmatrix(xs)
    s += r" \\ " + "\n"

    s += "& = "
    s += latex_bmatrix((m * n).xs)

    s += r"\end{align*}"
    
    return s
    

def latex(computation):
    name, params, aug = computation

    if name == 'swap':
        r0, r1 = params
        r0 += 1
        r1 += 1
        arrow = r"""\underrightarrow{\,\,\, R_%s \leftrightarrow R_%s \,\,\,} &
""" % (r0, r1)

    elif name == 'mult':
        r, k = params
        r += 1
        k = str(k)
        arrow = r"""\underrightarrow{\,\,\, R_%s \rightarrow \left( %s \right) R_%s \,\,\,}&
""" % (r, k, r)

    elif name == 'addmult':
        k, r0, r1 = params
        k = str(k)
        r0 += 1
        r1 += 1
        arrow = r"""\underrightarrow{\,\,\, R_%s \rightarrow R_%s + \left( %s \right) R_%s \,\,\,}&
""" % (r1, r1, k, r0)
        
    else:
        raise ValueError("unknown name:" + name)

    if arrow.startswith('\n'): sys.exit()
    str_matrix = augmatrix(aug)
    return arrow + str_matrix



    
class Matrix:

    latex = ""
    lookup = {}
    omit_zero = False # include 0 expansion for determinant
    
    def __init__(self, xs):
        self.xs = copy.deepcopy(xs)
        self.rowsize = len(self.xs)
        self.colsize = len(self.xs[0])
        if any([len(self.xs[r])!=self.colsize for r in range(self.rowsize)]):
            raise ValueError("column size not the same")

    def __str__(self):
        xs = self.xs
        width = []
        for c in range(self.colsize):
            col = [str(xs[r][c]) for r in range(self.rowsize)]
            lens = [len(_) for _ in col]
            width.append(max(lens))
        m = ''
        for r,row in enumerate(xs):
            m += '['
            for c,col in enumerate(row):
                m += str(col).rjust(width[c])
                if c < self.colsize - 1:
                    m += ", "
            m += ']\n'
        return m

    def samesize(self, m):
        return self.rowsize == m.rowsize and self.colsize == m.colsize

    def __isub__(self, m):
        if not self.samesize(m):
            raise ValueError("cannot add: incompatible sizes")
        for r in range(self.rowsize):
            for c in range(self.colsize):
                self[r, c] -= m[r, c]
        return self

    def __sub__(self, m):
        n = copy.deepcopy(self)
        n -= m
        return n
 
    def __mul__(self, m):
        if not isinstance(m ,Matrix):
            ret = copy.deepcopy(self)
            for r in range(self.rowsize):
                for c in range(self.colsize):
                    ret[r, c] *= m
            return ret
        else:
            if self.colsize != m.rowsize:
                raise ValueError("cannot mult: incompatible sizes")
            xs = []
            for r in range(self.rowsize):
                row = []
                for c in range(self.colsize):
                    s = 0
                    for k in range(self.colsize):
                        s += self[r, k] * m[k, c]
                    row.append(s)
                xs.append(row)
            return Matrix(xs)
            
    def __iadd__(self, m):
        if not self.samesize(m):
            raise ValueError("cannot add: incompatible sizes")
        for r in range(self.rowsize):
            for c in range(self.colsize):
                self[r, c] += m[r, c]
        return self
    
    def __add__(self, m):
        n = copy.deepcopy(self)
        n += m
        return n
    
    def rowswap(self, r0, r1):
        xs = self.xs
        for c in range(self.colsize):
            xs[r0][c], xs[r1][c] = xs[r1][c], xs[r0][c]

    def rowmult(self, r, k):
        # multiply row r with k
        for c in range(self.colsize):
            self.xs[r][c] *= k
            
    def rowaddmultiple(self, k, r0, r1):
        # add c*r0 to r1
        xs = self.xs
        for c in range(self.colsize):
            xs[r1][c] = xs[r1][c] + k * xs[r0][c]

    def __getitem__(self, k):
        r,c = k
        return self.xs[r][c]
    
    def __setitem__(self, k, v):
        r,c = k
        self.xs[r][c] = v
    
    def inv(self):
        # returns inverse and a list of computations of the
        # augmented matrix

        # Build augmented matrix
        augmat = self.augment()

        computations = []
        
        xs = self.xs
        for r in range(self.rowsize):

            # find and row to swap with
            r0 = r
            while r0 < augmat.rowsize and augmat[r0, r] == 0:
                r0 += 1
            if r0 == augmat.rowsize:
                raise ValueError("matrix has no inverse")

            # swap is necessary
            if r0 != r:
                augmat.rowswap(r0, r)
                computations.append(('swap', (r, r0), copy.deepcopy(augmat)))
            
            # force leading term of row to be 1
            k = augmat[r,r]**-1
            if k != 1:
                augmat.rowmult(r, k)
                computations.append(('mult', (r, k), copy.deepcopy(augmat)))

            # knock out all column values other than leading term
            for r1 in range(self.rowsize):
                if r1 == r: continue
                k = -augmat[r1, r]
                if k == 0: continue
                augmat.rowaddmultiple(k, r, r1)
                computations.append(('addmult', (k, r, r1), copy.deepcopy(augmat)))

            #print augmat

        # extract the inverse
        xs = []
        for r in range(self.rowsize):
            row = []
            for c in range(self.colsize):
                row.append(augmat[r, self.colsize + c])
            xs.append(row)
            
        return Matrix(xs), computations

    def augment(self):
        """ Add an identity matrix to the left of the given matrix
        """
        aug = []
        for i, row in enumerate(self.xs):
            extra = [0 for _ in range(self.colsize)]
            extra[i] = 1
            aug.append(row + extra)
        augmat = Matrix(aug)
        return augmat

    def delete_row(self, r):
        del self.xs[r]
        self.rowsize -= 1
        
    def delete_col(self, c):
        for row in self.xs:
            del row[c]
        self.colsize -= 1

    def minor(self, r, c):
        m = copy.deepcopy(self)
        m.delete_row(r)
        m.delete_col(c)
        return m
    
    def det(self):
        if self.rowsize != self.colsize:
            raise ValueError("det error: matrix not square")
            
        if self.rowsize == 1:
            # base
            return self[0,0]

        else:
            # recursion
            row = self.xs[0]
            computation0 = []
            computation1 = []
            computation2 = []
            computation3 = []
            computation4 = []
            computation5 = []
            for c, a in enumerate(row):
                if Matrix.omit_zero and a == 0:
                    computation0.append('0')
                else:
                    aminor = self.minor(0,c)
                    computation0.append(
                        "(-1)^{1+%s} (%s) \det %s" \
                        % (c+1, a, latex_bmatrix(aminor))
                        )
                    computation1.append(
                        "(%s) (%s) \det %s" \
                        % ((-1)**(1+c+1), a, latex_bmatrix(aminor))
                        )
                    computation2.append(
                        "(%s) \det %s" \
                        % ((-1)**(1+c+1) * a, latex_bmatrix(aminor))
                        )
                    if aminor.rowsize == 1:
                        computation3.append("(%s)(%s)" % \
                                            ((-1)**(1+c+1)*a,aminor[0,0]))
                        val = (-1)**(1+c+1)*a*aminor[0,0]
                        computation4.append(val)

            computation0 = " + ".join(computation0)
            computation1 = " + ".join(computation1)
            computation2 = " + ".join(computation2)
            computation3 = " + ".join(computation3)
            
            string = r"\det " + latex_bmatrix(self)
            string += "&= " + computation0 + "\\\\ \n" +\
                      "&= " + computation1 + "\displaybreak[0] \\\\ \n" +\
                      "&= " + computation2 + "\displaybreak[0] \\\\ \n"

            if computation3 != "":
                string += "&= " + computation3 + "\displaybreak[0] \\\\ \n"
            
            if len(computation4) > 0:
                s = sum(computation4)
                computation4 = " + ".join([xxx(_) for _ in (computation4)])
                computation5 = str(s)
                string += "&= " + computation4 + "\displaybreak[0] \\\\ \n"
                if computation4 != computation5:
                    string += "&= " + computation5 + "\displaybreak[0] \\\\ \n"
                
            Matrix.latex += string

            s = 0
            for c, a in enumerate(row):
                if Matrix.omit_zero and a == 0: continue
                aminor = self.minor(0,c)
                s += (-1)**(0 + c) * a * aminor.det()
            Matrix.lookup[str(self)] = s

            if self.rowsize > 2:
                Matrix.latex += r"\THEREFORE \det " + latex_bmatrix(self)

                yyy = []
                for c, a in enumerate(row):
                    if Matrix.omit_zero and a == 0: continue
                    aminor = self.minor(0,c)
                    v1 = (-1)**(0 + c) * a
                    v2 = Matrix.lookup[str(aminor)]
                    yyy.append("(%s)%s" % (v1, xxx(v2)))
                yyy = " + ".join(yyy)
                Matrix.latex += "&= " + yyy + "\displaybreak[0] \\\\ \n"
                Matrix.latex += "&= %s \\\\\n" % Matrix.lookup[str(self)]
                        
            return s






#==============================================================================
# Originally FunctionPlot = Plot from plot.py
#==============================================================================
from math import *
import traceback

# Use to be Plot from plot.py
class FunctionPlot:
    def __init__(self,
                 width="5in",
                 height="3in",
                 domain="0:10",
                 color="black",
                 line_width='1',
                 num_points = 100,
                 legend_pos = "outer north east",
                 vars=['x','y'] # independent and dependent vars
                 ):
        self.width = width
        self.height = height
        self.domain = domain
        self.color = color
        self.line_width = line_width
        self.num_points = num_points
        self.vars = vars
        if len(self.vars) == 1: self.vars.append('y')
        self.legend_pos = legend_pos
        "legend pos=outer north east,"
        self.pre = r"""
\begin{center}
\begin{tikzpicture}[line width=%(line_width)s]
\begin{axis}[width=%(width)s, height=%(height)s,
             xlabel={\mbox{}},
             xlabel style={name=xlabel}, 
             ylabel={\mbox{}},
             legend style={
                at={(xlabel.south)},
                yshift=-1ex,
                anchor=north,
                legend cell align=left
            }
        ]
]""" % {'height':self.height, 'width':self.width, 'line_width':line_width}
        self.body = ""
        self.post = r"""\end{axis}\end{tikzpicture}\end{center}"""
        self.exception = ''
        
    def add(self,
            *arglist,
            **argdict):
        """
        LINE GRAPH BY POINTS
        obj.add((1,1),(2,2),(3,3),line_width='1',color='black')

        LINE GRAPH BY LATEX FUNCTION
        obj.add("x**2 + 1",line_width='1',color='black')

        LINE GRAPH BY GENERATING POINTS BY PYTHON EXPRESSION
        obj.add("x**2 + 1", line_width='1', color='black', python=1)
        
        """
        try:
            d = {}
            d['color'] = argdict.get('color', self.color)
            d['line_width'] = argdict.get('line_width', self.line_width)
            d['domain'] = argdict.get('domain', self.domain)
            d['python'] = argdict.get('python', False)
            if d['python'] != False: d['python'] = True
            d['pin'] = argdict.get('pin', '')
            if d['pin'] in [1, '1', True]:
                d['pin'] = 'below right'
            d['style'] = argdict.get('style', '')
            d['num_points'] = argdict.get('num_points', self.num_points)
            if d['num_points'] <= 2: d['num_points'] = 3 # FIXIT
            d['vars'] = argdict.get('vars', self.vars)
            d['legend'] = argdict.get('legend', None)
                                      
            if isinstance(arglist[0], str):
                if not d['python']:
                    d['function'] = arglist[0]
                    d['expr'] = arglist[0]
                    partbody = r"""\addplot[draw=%(color)s, domain=%(domain)s, line width=%(line_width)s]{%(function)s};""" % d
                else: # python expr
                    d['expr'] = expr = arglist[0]
                    minx, maxx = d['domain'].split(':')
                    minx = float(minx.strip())
                    maxx = float(maxx.strip())
                    d['maxx'] = maxx
                    dx = (maxx - minx) / (d['num_points'] - 1)
                    x = minx; exec('%s = x' % d['vars'][0])
                    points = []
                    while x <= maxx:
                        try:
                            # in case for log function the x is not in domain
                            # can be a problem if the expression is written
                            # wrongly
                            #print "---> expr:", d['expr']
                            y = eval(d['expr'])
                            points.append("(%s,%s)" % (x,y))
                        except Exception, e1: # don't use e ... conflicts with math.e
                            pass
                            #print e
                        x += dx; exec('%s = x' % d['vars'][0])
                    
                    try:
                        # add last point just in case of fp errors
                        x = maxx; exec('%s = x' % d['vars'][0])
                        y = eval(d['expr'])
                        points.append("(%s,%s)" % (x,y))
                    except Exception, e1:
                        pass
                    
                    d['points'] = '\n'.join(points)
                            
            elif isinstance(arglist[0], (list, tuple)):
                d['points'] = "\n".join([str(_) for _ in arglist[0]]) 

            if d['style'] == '':
                partbody = r"""\addplot[draw=%(color)s, line width=%(line_width)s] coordinates {%(points)s};""" % d
                self.body += partbody
            elif d['style'] == 'step':
                partbody = r"""\addplot[const plot, draw=%(color)s, line width=%(line_width)s] coordinates {%(points)s};""" % d
                self.body += partbody

            # pin
            pin = ''
            if d['pin']:
                d['pin_message'] = "$y=%s$" % argdict.get('pin_message', d['expr'])
                d['pin_message'] = d['pin_message'].replace("**", "^") 
                d['pin_message'] = d['pin_message'].replace("*", " ")
                d['pin_message'] = d['pin_message'].replace("log(", "\log(")
                d['pin_message'] = d['pin_message'].replace("sin(", "\sin(")
                if d['pin_message'] == '$y=$': d['pin_message'] = ''
                d['pin_x'] = argdict.get('pin_x', d['maxx'] * 0.8) # depends on maxx
                x = d['pin_x']
                exec('%s = x' % d['vars'][0])
                if d['expr']:
                    d['pin_y'] = eval(expr) # depends on expr
                else:
                    d['pin_y'] = 0 # TODO

                if d['pin_message'] != '':
                    pin = r"""\node[pin=%(pin)s:{%(pin_message)s}] at (axis cs:%(pin_x)s,%(pin_y)s) {};""" % d
                
            self.body += pin

            # legend
            legend = ''
            if d['legend']:
                legend = r"\addlegendentry{%s}" % d['legend']

            self.body += legend

            
        except Exception, e:
            str_e = str(e)
            f = file('traceback.txt', 'w')
            traceback.print_exc(file=f)
            f.close()
            str_tb = file('traceback.txt', 'r').read()
            self.exception = '%s\n\n%s' % (str_tb, str_e)
    def __str__(self):
        if self.exception:
            return self.exception
        else:
            return "%s\n%s\n%s" % (self.pre, self.body, self.post)



#==============================================================================
# graph and graph_coloring_label from latextool.py
#==============================================================================
def graph_coloring_label(
    *args
    ):
    """ args is a list of (var,value,list) """

    args = args[0]
    #print
    #print "args:", args
    #print
    return args
    
    #domains = []
    domains = [(len(z),z) for x,y,z in args]
    domains.sort()
    longest_domain = domains[-1][1]

    # put mbox into arg which has [] list
    def f(z):
        if z == []: xs = longest_domain
        else: xs = z
        return r'\mbox{$\{%s\}$}' % (','.join(xs))
    
    args = [(x,y,f(z)) for x,y,z in args]
    
    lines = [r"$%s$ & \hskip-9pt $= %s$ & \mbox{$%s$}" % (x,y,z) \
             for x,y,z in args]

    return r'''\begin{tabular}{lll}
\end{tabular}'''


"""
Example:
  graph(shape='circle',
        minimumsize='14mm',
        layout='''
          A
         B C
        D E F G
        ''',
        edges='A-B,A>C',
        A='shape=rectangle, label=$A$, pos=(3,5)',
        B='label=B',
        )
The last keyword args A,B are kept in the dict args.
"""
def graph(shape='circle',
          minimum_size='14mm',
          layout=None,
          xscale=1,
          yscale=2,
          edges='',
          separator=',',
          **args
          ):
    """ For output of graphs for latex using the pgf library """

    # get all the nodes from layout
    nodes = [x for x in layout.replace('\n', ' ').split(' ') if x != '']

    # now get nodes from args
    for key in args.keys():
        if key not in nodes: nodes.append(key)

    # put all nodes into dict and fill with default values
    node_dict = {}
    for node in nodes:
        node_dict[node] = {'shape':shape,
                           'minimum_size':minimum_size,
                           'pos':None,
                           'label':'$%s$' % node}

    # now overwrite with args
    for key,value in args.items():
        if key != 'edge_label':
            parts = [_.strip() for _ in value.split(separator) \
                     if _.strip() != '']
            for part in parts:
                try:
                    k,v = part.split('=', 1)
                    k,v = k.strip(), v.strip()
                    node_dict[key][k] = v
                except:
                    pass

    # remove pre and post blank lines
    layout_lines = [line for line in layout.split('\n')]
    
    # make sure every line has the same number of chars by appending ' '
    max_len = max([len(line) for line in layout_lines])
    layout_lines = [line + (max_len - len(line)) * ' ' for line in layout_lines]
    # remove leftmost char from every line if it's ' '
    while 1:
        # check if every line begins with ' '
        if all([line[0] == ' ' for line in layout_lines]):
            layout_lines = [line[1:] for line in layout_lines]
        else:
            break

    # now place the nodes
    s = ''
    for line_index, line in enumerate(layout_lines):
        for node in nodes:
            p = re.compile('(^| )%s(\Z| )' % node)
            search = p.search(line)
            if search:
                ind = search.start()
                if search.group()[0] == ' ': ind += 1
                shape = node_dict[node]['shape']

                if node_dict[node].has_key('graph coloring'):
                    label = node_dict[node]['label']
                    label = graph_coloring_label(eval(label))
                else:
                    label = node_dict[node]['label']

                size = 'minimum size=%s' % node_dict[node]['minimum_size']
                if shape=='rectangle':
                    if node_dict[node].has_key('minimum width'):
                        size += ',minimum width=%s' % node_dict[node]['minimum width']
                    if node_dict[node].has_key('minimum height'):
                        size += ',minimum height=%s' % node_dict[node]['minimum height']
                if shape=='tree':
                    if node_dict[node].has_key('minimum height'):
                        size += ',minimum height=%s' % node_dict[node]['minimum height']
                if node_dict[node].has_key('text width'):
                    size += ',text width=%s' % node_dict[node]['text width']

                if shape=='tree':
                    # empty node
                    # the triangle
                    s += r'''\node at (%s,%s)
    [%s,
     draw,%s,
     anchor=north] (%s) {%s};''' % \
                         (ind*xscale, -line_index*yscale,
                          'isosceles triangle, shape border rotate=+90',
                          size,
                          node + 'triangle',
                          label)
                    s += '\n';
                    s += r'\coordinate (%s) at (%s,%s);' % \
                         (node, ind*xscale, -line_index*yscale)                    
                elif shape=='None':
                    s += r'\node at (%s,%s) [%s] (%s) {%s};' % \
                         (ind*xscale, -line_index*yscale, size, node, label)
                else:
                    s += r'\node at (%s,%s) [%s,draw,%s] (%s) {%s};' % \
                         (ind*xscale, -line_index*yscale, shape, size, node, label)
                    
                s += '\n'

    #print "s:",
    
    # now add edges
    for edge in [_.strip() for _ in edges.strip().split(',') if _.strip() != '']:
        start = None
        for node in nodes:
            if edge.startswith(node):
                start = node
                break
        if start == None:
            print "\nERROR: UNKNOWN START NODE IN", edge, "\n"
            continue
        
        end = None
        for node in nodes:
            if edge.endswith(node):
                end = node
                break
        if end == None:
            print "\nERROR: UNKNOWN START NODE IN", edge, "\n"
            continue

        linetype = edge[len(start):][:-len(end)]
        
        if linetype == '>': linetype = '->'
        elif linetype == '<': linetype = '<-'
        elif linetype == '-': pass
        elif linetype == '->': pass
        elif linetype == 'dashed': linetype='dashed' #????
        else:
            print
            print "ERROR: UNKNOWN LINE TYPE", linetype
            print
            continue

        if args.has_key('edge_label') \
               and args['edge_label'].has_key((start,end)):
            s += r'\draw [%s,thick] (%s) -- (%s) node[%s]{%s}  ;' % \
                 (linetype, start, end,
                  args['edge_label'][(start,end)].get('style','auto,pos=0.5'), 
                  args['edge_label'][(start,end)]['label'])
            s += '\n'            
        else:
            s += r'\draw [%s,thick] (%s) -- (%s);' % (linetype, start, end)
            s += '\n'

    return r'''
\begin{tikzpicture}
%s
;
\end{tikzpicture}
    ''' % s
