from ops import ops
import re
class Assembler:

    def __init__(self):
        pass

    def assemble(self, asm, output=None):
        if type(asm) == str:
            lines = str.split('\n')
        elif type(asm) == file:
            lines = list(asm.readlines())


        for l in lines:

            if l[0] == ";":
                continue


    def getArgument(self, arg): 
        regex = [
            ('iy', ''.join([
                '\((',
                '(\$)([\dabcdefABCDEF]{2})','|',
                '(%)([01]{1,8})'
                ')\)',
            ]), ['hex', 'bin'])
        ]

        re.search(regex[0][1], arg).groups()