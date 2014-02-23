from ops import ops
import re

num_formats = [
    '\$([\dabcdefABCDEF]{1,4})',
    '%([01]{1,16})',
    '0([01234567]{1,6})',
    '(\d{1,5})',
    '(\w[\w\d]*)'
]

arg_regex = [
    ('im', ''.join([
        '^#', '(?:', '|'.join(num_formats), ')$'
    ])),
    ('z', ''.join([
        '^(?:', '|'.join(num_formats), ')$'
    ])),
    ('zx', ''.join([
        '^(?:', '|'.join(num_formats), ')', ',X$'
    ])),
    ('zy', ''.join([
        '^(?:', '|'.join(num_formats), ')', ',Y$'
    ])),
    ('ix', ''.join([
        '^\(', '(?:',
        '|'.join(num_formats),
        ')', ',X\)$',
    ])),
    ('iy', ''.join([
        '^\(', '(?:',
        '|'.join(num_formats),
        ')', '\),Y$',
    ])),
    ('i', ''.join([
        '^\(', '(?:',
        '|'.join(num_formats),
        ')', '\)$',
    ])),
]


class Assembler:

    def __init__(self):
        self.symbols = {}

    def assemble(self, asm, output_dest=None):
        out = []

        if type(asm) == str:
            lines = asm.split('\n')
        elif type(asm) == file:
            lines = list(asm.readlines())

        for l in lines:
            if l[0] == ";": #Comment
                continue

            tokens = l.split()

            if tokens[0] in ops:
                t, n = self.getArgument(tokens[1])
                out.append(ops[tokens[0]][t])
                out.append(n)

        return out


    def getArgument(self, arg):
        if re.match('A', arg):
            return ('im', 'A')

        for r in arg_regex:
            s = re.match(r[1], arg)
            if s:
                if s.group(1):
                    t, n, v  = (r[0], int(s.group(1), 16), s.group(1))
                    break
                elif s.group(2):
                    t, n, v  = (r[0], int(s.group(2), 2), s.group(2))
                    break
                elif s.group(3):    
                    t, n, v  = (r[0], int(s.group(3), 8), s.group(3))
                    break
                elif s.group(4):    
                    t, n, v  = (r[0], int(s.group(4), 10), s.group(4))
                    break
                elif s.group(5):    
                    t, n, v  = (r[0], self.symbols.get(s.group(5), None), s.group(5))
                    break


        if t[0] == "z" and (n > 0xff or len(v) == 4):
            t = t.replace("z", "a")

        return t, n

