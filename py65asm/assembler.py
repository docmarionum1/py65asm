from ops import ops
import re

num_formats = [
    '\$([\dabcdefABCDEF]{1,4})',
    '%([01]{1,16})',
    '0([01234567]{1,6})',
    '(\d{1,5})',
    '(\w[\w\d]*)'
]

num_bases = [16, 2, 8, 10]

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
        self.out = []

    def assemble(self, asm, output_dest=None):
        self.out = []

        if type(asm) == str:
            lines = asm.split('\n')
        elif type(asm) == file:
            lines = list(asm.readlines())

        for l in lines:
            if l[0] == ";": #Comment
                continue

            if ";" in l: #Strip trailing comment
                l = l[:l.index(";")]

            tokens = l.split()

            self.assembleTokens(tokens)

        self.resolveLabels()

            
        return self.out

    def assembleTokens(self, tokens):
        op = tokens[0].upper()
        if op in ops:
            if len(tokens) == 1: #Implied
                self.out.append(ops[op]['im'])
                return

            t, n = self.getArgument(tokens[1])
            if n:
                # If zero page is not available switch to absolute
                if t not in ops[op] and t == 'z': 
                    t = 'a'

                self.out.append(ops[op][t])
                if t in ['a', 'ax', 'ay', 'i']:
                    self.out.append(n & 0xff)
                    self.out.append(n >> 8)
                else:
                    self.out.append(n)
            else: #Unresolved variable
                self.out.append(tokens[0])
                self.out.append(tokens[1])
        else: #Label or variable
            if len(tokens) > 1 and tokens[1] == "=": #variable
                if tokens[2] == "*": #label = * is equal to lable:
                    self.out.append("LABEL")
                    self.out.append(tokens[0])
                else:
                    n  = self.getNumber(tokens[2])
                    self.symbols[tokens[0]] = n
            else:
                self.out.append("LABEL")
                self.out.append(tokens[0].rstrip(":"))
                if len(tokens) > 1: #Label on same line as code
                    self.assembleTokens(tokens[1:])

    def resolveLabels(self):
        i = 0
        while i < len(self.out):
            if type(self.out[i]) == str and self.out[i] == "LABEL":
                self.out.pop(i) #Remove the "LABEL" tag
                self.symbols[self.out[i]] = i #Add the label to the symbols

                #Resolve this label
                j = 0
                l = len(self.out)

                while j < len(self.out):
                    if type(self.out[j]) == str and j != i and self.out[i] in self.out[j]:
                        new = []
                        t, n = self.getArgument(self.out[j])
                        op = self.out[j-1].upper()
                        # If zero page is not available switch to absolute
                        if t not in ops[op] and t == 'z': 
                            t = 'a'

                        new.append(ops[op][t])

                        if op in ["BCC", "BCS", "BEQ", "BMI", "BNE", "BPL", "BVC"]:
                            if n < j:
                                d = n - j
                            else:
                                d = n - j - 1

                            if d > 127 or d < -128:
                                    raise Exception("Branch target too far")

                            new.append(d & 0xff)
                        elif t in ['a', 'ax', 'ay', 'i']:
                            if j < n:  #Adjust the labels position for the extra byte
                                self.symbols[self.out[i]] += 1
                                n += 1
                                i += 1
                            new.append(n & 0xff)
                            new.append(n >> 8)
                        else:
                            new.append(n)

                        self.out = self.out[:j-1] + new + self.out[j+1:]

                    j += 1
                self.out.pop(i)
                continue

            i += 1


    def getNumber(self, arg):
        for i in range(len(num_bases)):
            s = re.match(num_formats[i], arg)
            if s.group(1):
                return int(s.group(1), num_bases[i])


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

