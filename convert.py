#!/usr/bin/env python
# -*- coding:utf-8 -*-
# File          : convert.py
# Author        : bss
# Project       : stl2scl
# Creation Date : 2015-03-27
# Description   : Do the job
# 

class Converter:
    def __init__(self):
        self.method_list = {
            'save' : 'null',
            'be' : 'null',
            'set' : 'set',
            'clr' : 'clr',
            '=' : 'assign',
            'l' : 'l',
            't' : 't',
            'tak' : 'tak',
            'not' : 'not',
            'a' : 'a',
            'an' : 'an',
            'o' : 'o',
            'on' : 'on',
            'x' : 'x',
            'xn' : 'xn',
            'jcn' : 'jcn',
            'ju' : 'ju'
        }
        self.logic_list = ['set', 'save', '=', 'not', 'a', 'an', 'o', 'on', 'x', 'xn', 'r', 's']


    def convert(self, lines):
        self.sclLines = []
        self.ACCU1 = ''
        self.ACCU2 = ''
        self.RLO = ''
        self.lines = lines

        self.__toSCL()

        return self.sclLines


    def __toSCL(self):
        self.ops = []
        for line in self.lines:
            if line.endswith(':'):
                self.__addLine(line)
                continue
            stl = line.split()
            stl[1:] = [' '.join(stl[1:])]

            newOps = stl[0].lower()
            if newOps in self.method_list:
                # check logic
                if newOps in self.logic_list:
                    if (len(self.ops) > 0 and self.ops[-1] not in self.logic_list):
                        self.RLO = ''
                # convert
                self.__dispatch(newOps, stl[1][:-1])
                # save ops
                self.ops.append(newOps)
            else:
                #print('Unknown STL code: %s.' % line)
                self.__addLine(line)


    def __addLine(self, line):
        self.sclLines.append(line)


    def __dispatch(self, name, oper):
        method_name = '_Converter__stl_' + self.method_list[name]
        method = getattr(self, method_name)
        method(name, oper)


    def __stl_null(self, name, oper):
        pass


    def __stl_set(self, name, oper):
        self.RLO = '1'


    def __stl_clr(self, name, oper):
        self.RLO = '0'


    def __stl_assign(self, name, oper):    # =
        self.__addLine('%s = %s' % (oper, self.RLO))


    def __stl_l(self, name, oper):
        self.ACCU2 = self.ACCU1
        self.ACCU1 = oper


    def __stl_t(self, name, oper):
        self.__addLine('%s = %s' % (oper, self.ACCU1))


    def __stl_tak(self, name, oper):
        tmp = self.ACCU1
        self.ACCU1 = self.ACCU2
        self.ACCU2 = tmp


    def __stl_not(self, name, oper):
        self.RLO = 'NOT (%s)' % self.RLO


    def __stl_a(self, name, oper):
        self.RLO = '%s AND (%s)' % (oper, self.RLO)


    def __stl_an(self, name, oper):
        self.RLO = '%s AND NOT (%s)' % (oper, self.RLO)


    def __stl_o(self, name, oper):
        self.RLO = '%s OR (%s)' % (oper, self.RLO)


    def __stl_on(self, name, oper):
        self.RLO = '%s OR NOT (%s)' % (oper, self.RLO)


    def __stl_x(self, name, oper):
        self.RLO = '%s XOR (%s)' % (oper, self.RLO)


    def __stl_xn(self, name, oper):
        self.RLO = '%s XOR NOT (%s)' % (oper, self.RLO)


    def __stl_jcn(self, name, oper):
        self.__addLine('IF %s THEN' % self.RLO)
        self.__addLine('    GOTO %s' % oper)
        self.__addLine('END_IF')


    def __stl_ju(self, name, oper):
        self.__addLine('GOTO %s' % oper)
