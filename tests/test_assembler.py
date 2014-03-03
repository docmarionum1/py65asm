#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_assembler
----------------------------------

Tests for `py65asm` module.
"""

import unittest, os

from py65asm.assembler import Assembler


class TestAssembler(unittest.TestCase):

    def _asm(self):
        return Assembler()

    def setUp(self):
        pass

    def test_im_argument(self):
        a = self._asm()
        a.symbols['var'] = 0x55
        self.assertEqual(a.getArgument("#$FF"), ('im', 0xff))
        self.assertEqual(a.getArgument("#-1"), ('im', 0xff))
        self.assertEqual(a.getArgument("#%10101011"), ('im', 0b10101011))
        self.assertEqual(a.getArgument("#010"), ('im', 010))
        self.assertEqual(a.getArgument("#0"), ('im', 0))
        self.assertEqual(a.getArgument("#123"), ('im', 123))
        self.assertEqual(a.getArgument("#var"), ('im', a.symbols['var']))

    def test_z_argument(self):
        a = self._asm()
        a.symbols['var'] = 0x55
        self.assertEqual(a.getArgument("$FF"), ('z', 0xff))
        self.assertEqual(a.getArgument("%10101011"), ('z', 0b10101011))
        self.assertEqual(a.getArgument("010"), ('z', 010))
        self.assertEqual(a.getArgument("123"), ('z', 123))
        self.assertEqual(a.getArgument("var"), ('z', a.symbols['var']))

    def test_zx_argument(self):
        a = self._asm()
        a.symbols['var'] = 0x55
        self.assertEqual(a.getArgument("$FF,X"), ('zx', 0xff))
        self.assertEqual(a.getArgument("%10101011,X"), ('zx', 0b10101011))
        self.assertEqual(a.getArgument("010,X"), ('zx', 010))
        self.assertEqual(a.getArgument("123,X"), ('zx', 123))
        self.assertEqual(a.getArgument("var,X"), ('zx', a.symbols['var']))

    def test_zy_argument(self):
        a = self._asm()
        a.symbols['var'] = 0x55
        self.assertEqual(a.getArgument("$FF,Y"), ('zy', 0xff))
        self.assertEqual(a.getArgument("%10101011,Y"), ('zy', 0b10101011))
        self.assertEqual(a.getArgument("010,Y"), ('zy', 010))
        self.assertEqual(a.getArgument("123,Y"), ('zy', 123))
        self.assertEqual(a.getArgument("var,Y"), ('zy', a.symbols['var']))

    def test_a_argument(self):
        a = self._asm()
        a.symbols['var'] = 0x555
        self.assertEqual(a.getArgument("$FFFF"), ('a', 0xffff))
        self.assertEqual(a.getArgument("$00FF"), ('a', 0x00ff))
        self.assertEqual(a.getArgument("%1010101110101011"), ('a', 0b1010101110101011))
        self.assertEqual(a.getArgument("01110"), ('a', 01110))
        self.assertEqual(a.getArgument("1234"), ('a', 1234))
        self.assertEqual(a.getArgument("var"), ('a', a.symbols['var']))

    def test_ax_argument(self):
        a = self._asm()
        a.symbols['var'] = 0x555
        self.assertEqual(a.getArgument("$FFFF,X"), ('ax', 0xffff))
        self.assertEqual(a.getArgument("%1010101110101011,X"), ('ax', 0b1010101110101011))
        self.assertEqual(a.getArgument("01110,X"), ('ax', 01110))
        self.assertEqual(a.getArgument("1234,X"), ('ax', 1234))
        self.assertEqual(a.getArgument("var,X"), ('ax', a.symbols['var']))
        self.assertEqual(a.getArgument("$200,x"), ('ax', 0x200))

    def test_ay_argument(self):
        a = self._asm()
        a.symbols['var'] = 0x555
        self.assertEqual(a.getArgument("$FFFF,Y"), ('ay', 0xffff))
        self.assertEqual(a.getArgument("%1010101110101011,Y"), ('ay', 0b1010101110101011))
        self.assertEqual(a.getArgument("01110,Y"), ('ay', 01110))
        self.assertEqual(a.getArgument("1234,Y"), ('ay', 1234))
        self.assertEqual(a.getArgument("var,Y"), ('ay', a.symbols['var']))

    def test_ix_argument(self):
        a = self._asm()
        a.symbols['var'] = 0x55
        self.assertEqual(a.getArgument("($FF,X)"), ('ix', 0xff))
        self.assertEqual(a.getArgument("(%10101011,X)"), ('ix', 0b10101011))
        self.assertEqual(a.getArgument("(010,X)"), ('ix', 010))
        self.assertEqual(a.getArgument("(123,X)"), ('ix', 123))
        self.assertEqual(a.getArgument("(var,X)"), ('ix', a.symbols['var']))
        self.assertEqual(a.getArgument("($200,X)"), ('ix', 0x200))

    def test_iy_argument(self):
        a = self._asm()
        a.symbols['var'] = 0x55
        self.assertEqual(a.getArgument("($FF),Y"), ('iy', 0xff))
        self.assertEqual(a.getArgument("(%10101011),Y"), ('iy', 0b10101011))
        self.assertEqual(a.getArgument("(010),Y"), ('iy', 010))
        self.assertEqual(a.getArgument("(123),Y"), ('iy', 123))
        self.assertEqual(a.getArgument("(var),Y"), ('iy', a.symbols['var']))

    def test_i_argument(self):
        a = self._asm()
        a.symbols['var'] = 0x555
        self.assertEqual(a.getArgument("($FFFF)"), ('i', 0xffff))
        self.assertEqual(a.getArgument("(%1010101110101011)"), ('i', 0b1010101110101011))
        self.assertEqual(a.getArgument("(01110)"), ('i', 01110))
        self.assertEqual(a.getArgument("(1234)"), ('i', 1234))
        self.assertEqual(a.getArgument("(var)"), ('i', a.symbols['var']))



    def test_A_argument(self):
        a = self._asm()
        self.assertEqual(a.getArgument("A"), ('im', 'A'))

    def test_assemble_line(self):
        a = self._asm()
        self.assertEqual(a.assemble("LDA #55"), [169, 55])
        self.assertEqual(a.assemble("LDA #$55"), [169, 0x55])
        self.assertEqual(a.assemble("LDA $55"), [165, 0x55])
        self.assertEqual(a.assemble("LDA $555"), [173, 0x55, 0x5])

    def test_assemble_lines(self):
        a = self._asm()
        self.assertEqual(a.assemble("LDA #55\nSBC $33,X"), [169, 55, 245, 0x33])

    def test_labels(self):
        a = self._asm()
        self.assertEqual(a.assemble("loop: DEX\nJMP loop"), [202, 76, 0, 0])
        a = self._asm()
        self.assertEqual(
            a.assemble("JMP loop\nDEX\nDEX\nDEX\nloop"), 
            [76, 06, 00, 202, 202, 202]
        )
        a = self._asm()
        self.assertEqual(
            a.assemble("label1: JMP label1\nJMP label2\nlabel2: JMP label1\nJMP label2"),
            [76, 00, 00, 76, 06, 00, 76, 00, 00, 76, 06, 00]
        )

    def test_branch(self):
        a = self._asm()
        self.assertEqual(a.assemble("label: DEX\nDEX\nBNE label"),
            [202, 202, 208, 252]
        )
        a = self._asm()
        self.assertEqual(a.assemble("BNE label\nDEX\nDEX\nlabel"),
            [208, 2, 202, 202]
        )

    def test_variables(self):
        a = self._asm()
        self.assertEqual(a.assemble("var = $ff\nlda #var"),[169, 255])
        self.assertEqual(a.assemble("var = $ff\nlda var"),[165, 255])
        self.assertEqual(a.assemble("var = $ffff\nlda var"),[173, 255, 255])
        self.assertEqual(
            a.assemble("var1 = *\nlda #var1\nvar2 = *\nlda #var2"),
            [169, 0, 0, 169, 3, 0]
        )

    def test_byte(self):
        a = self._asm()
        self.assertEqual(a.assemble(".BYTE $0A"), [0xa])

    def test_word(self):
        a = self._asm()
        self.assertEqual(a.assemble(".WORD $0A"), [0xa, 0x00])
        self.assertEqual(a.assemble(".WORD $AAA"), [0xaa, 0xa])

    def test_org(self):
        a = self._asm()
        self.assertEqual(
            a.assemble(".BYTE 01\n.ORG 10\n.BYTE 02"), 
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2]
        )
        self.assertEqual(
            a.assemble(".ORG $8000\n.BYTE 1\nlabel: .BYTE 2\nJMP label"), 
            [1, 2, 76, 01, 0x80]
        )
        self.assertEqual(
            a.assemble("a = 5\n.ORG $8000\n.BYTE 1\nlabel: .BYTE 2\nJMP label"), 
            [1, 2, 76, 01, 0x80]
        )
        self.assertEqual(
            a.assemble(".ORG $8000\n.BYTE 1\n.ORG $8005\nlabel: .BYTE 2\nJMP label"), 
            [1, 0, 0, 0, 0, 2, 76, 01, 0x80]
        )

    def test_assemble_file(self):
        a = self._asm()

        f = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), 
            "files", "test.asm"
        )

        out = a.assemble(open(f))

        self.assertEqual(len(out), 0x4000)
        self.assertEqual(out[:5], [0xa9, 0xff, 0x4c, 0x00, 0xc0])
        self.assertEqual(out[-3:], [0x99, 0x00, 0xc0])

    def test_write_file(self):
        a = self._asm()
        out = "/tmp/write_test.bin"
        a.assemble(".byte 72\n.byte 69\n.byte 76\n.byte 76\n.byte 79", out)

        with open(out) as f:
            self.assertEqual(f.read(), "HELLO")

    def test_lda_0(self):
        a = self._asm()
        self.assertEqual(a.assemble("lda #0"), [169, 0])
            
    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()