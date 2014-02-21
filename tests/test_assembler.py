#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_assembler
----------------------------------

Tests for `py65asm` module.
"""

import unittest

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
        self.assertEqual(a.getArgument("#%10101011"), ('im', 0b10101011))
        self.assertEqual(a.getArgument("#010"), ('im', 010))
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


    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()