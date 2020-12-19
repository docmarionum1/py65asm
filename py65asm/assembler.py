from .ops import ops
import re


# Handle file check for python 3
import sys
if sys.version_info[0] == 3:
    from io import IOBase
    file = IOBase

num_formats = [
    '\$([\dabcdefABCDEF]{1,4})',
    '%([01]{1,16})',
    '0([01234567]{1,6})',
    '(-*\d{1,5})',
    '(\w[\w\d]*)'
]

num_bases = [16, 2, 8, 10, None]

arg_regex = [
    ('im', ''.join([
        '^#', '(?:', '|'.join(num_formats), ')$'
    ])),
    ('z', ''.join([
        '^(?:', '|'.join(num_formats), ')$'
    ])),
    ('zx', ''.join([
        '^(?:', '|'.join(num_formats), ')', ',[xX]$'
    ])),
    ('zy', ''.join([
        '^(?:', '|'.join(num_formats), ')', ',[yY]$'
    ])),
    ('ix', ''.join([
        '^\(', '(?:',
        '|'.join(num_formats),
        ')', ',[xX]\)$',
    ])),
    ('iy', ''.join([
        '^\(', '(?:',
        '|'.join(num_formats),
        ')', '\),[yY]$',
    ])),
    ('i', ''.join([
        '^\(', '(?:',
        '|'.join(num_formats),
        ')', '\)$',
    ])),
]


class Assembler:

    def __init__(self, org=None):
        self.symbols = {}
        self.out = []
        if org is not None:
            self.org = org
            self.start = self.org
        else:
            self.org = 0
            self.start = self.org

    def assemble(self, asm, output_dest=None):
        self.out = []

        if isinstance(asm, str):
            lines = asm.split('\n')
        elif isinstance(asm, file):
            lines = list(asm.readlines())

        for l in lines:
            l = l.strip()
            if l:
                if l[0] == ";": #Comment
                    continue

                if ";" in l: #Strip trailing comment
                    l = l[:l.index(";")]

                tokens = l.split()

                self.assembleTokens(tokens)

        self.resolveLabels()

        if output_dest:
            with open(output_dest, 'wb') as f:
                f.write(bytearray(self.out))



        return self.out

    def assembleTokens(self, tokens):
        op = tokens[0].upper()
        if op in ops:
            if len(tokens) == 1: #Implied
                self.out.append(ops[op]['im'])
                return

            t, n = self.getArgument(tokens[1])
            if n is not None:
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
                if op not in ["BCC", "BCS", "BEQ", "BMI", "BNE", "BPL", "BVC"]:
                    self.out.append("") #Create a blank space to make sure that the length is correct.
        elif op == ".BYTE":
            n = self.getNumber(tokens[1])
            if n:
                self.out.append(n)
            else:
                self.out.append(tokens[1])
        elif op == ".WORD":
            n = self.getNumber(tokens[1])
            if n:
                self.out.append(n & 0xff)
                self.out.append(n >> 8)
            else:
                self.out.append("WORD")
                self.out.append(tokens[1])
        elif op == ".ORG":
            n = self.getNumber(tokens[1])
            #Is this before any code has been generated?  Set the start to this
            if len(self.out) == 0 or not [i for i in self.out if type(i) != str]:
                self.start = n
            else:
                #self.out.extend([0]**n - len)
                self.out.append("ORG")
                self.out.append(str(n))
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

            if type(self.out[i]) == str and self.out[i] == "ORG":
                self.out = self.out[:i] + [0]*(int(self.out[i+1])-i - self.start) + self.out[i+2:]
            elif type(self.out[i]) == str and self.out[i] == "LABEL":
                self.out.pop(i) #Remove the "LABEL" tag
                self.symbols[self.out[i]] = i + self.start #Add the label to the symbols
                #Resolve this label
                j = 0
                l = len(self.out)

                # Keep track of the number of 'LABEL' tags that are still in self.out because
                # we need to compensate for them in branch instructions that go backwards
                num_labels = 0

                while j < len(self.out):
                    if type(self.out[j]) == str and self.out[j] == "LABEL":
                        num_labels += 1
                    elif type(self.out[j]) == str and j != i and \
                        re.search("^[\(#]*%s([\),]|$)" % self.out[i], self.out[j]):

                        if type(self.out[j-1]) == int: #BYTE
                            self.out[j] = self.getNumber(self.out[j])
                            continue
                        elif self.out[j-1] == "WORD":
                            n = self.getNumber(self.out[j])
                            self.out[j-1] = n & 0xff
                            self.out[j] = n >> 8
                            continue

                        new = []
                        t, n = self.getArgument(self.out[j])
                        op = self.out[j-1].upper()

                        if op in ["BCC", "BCS", "BEQ", "BMI", "BNE", "BPL", "BVC"]:
                            new.append(ops[op]['z'])
                            c = j + self.start - num_labels*2
                            if n < c:
                                d = n - c
                            else:
                                d = n - c - 1

                            if d > 127 or d < -128:
                                    raise Exception("Branch target too far")

                            new.append(d & 0xff)

                            self.out = self.out[:j-1] + new + self.out[j+1:]

                        else:
                            if 'z' in t:
                                t = t.replace("z", "a")
                            new.append(ops[op][t])

                            new.append(n & 0xff)
                            new.append(n >> 8)

                            self.out = self.out[:j-1] + new + self.out[j+2:]

                    j += 1

                self.out.pop(i)

            i += 1


    def getNumber(self, arg):
        for i in range(len(num_bases)):
            if num_bases[i]:
                s = re.match(num_formats[i], arg)
                if s and s.group(1):
                    return int(s.group(1), num_bases[i])
            else:
                return self.symbols.get(arg, None)


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

        if t[0] == "z" and n and (n > 0xff or len(v) == 4):
            t = t.replace("z", "a")

        if n is not None and n < 0:
            n = n & 0xff

        return t, n
