#!/usr/bin/env python
# -*- coding:utf-8 -*-
# File          : convert.py
# Author        : bss
# Project       : stl2scl
# Creation Date : 2015-03-27
# Description   : Do the job
# 

class Converter:
    def __init__(self, keep_stl = False):
        self.keep_stl = keep_stl
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
            'ju' : 'ju',
            '+i' : 'plus',
            '+d' : 'plus',
            '+r' : 'plus',
            '-i' : 'minus',
            '-d' : 'minus',
            '-r' : 'minus',
            '*i' : 'multiplication',
            '*d' : 'multiplication',
            '*r' : 'multiplication',
            '/i' : 'division',
            '/d' : 'division',
            '/r' : 'division',
            'itd' : 'null',
            'dtr' : 'null',
            'rnd' : 'null',
            '>i' : '1g2',
            '>d' : '1g2',
            '>r' : '1g2',
            '<i' : '1l2',
            '<d' : '1l2',
            '<r' : '1l2',
            '=i' : '1e2',
            '=d' : '1e2',
            '=r' : '1e2',
            '>=i' : '1ge2',
            '>=d' : '1ge2',
            '>=r' : '1ge2',
            '<=i' : '1le2',
            '<=d' : '1le2',
            '<=r' : '1le2',
            'negi' : 'neg',
            'negd' : 'neg',
            'negr' : 'neg',
        }
        self.logic_list = ['set', 'save', 'not', 'a', 'an', 'o', 'on', 'x', 'xn']
        self.logic_change = ['=', 's', 'r']


    def convert(self, lines):
        self.sclLines = []
        self.ACCU1 = ''
        self.ACCU2 = ''
        self.RLO = ''
        self.lines = lines

        self.__toSCL(self.lines)

        return self.sclLines


    def __toSCL(self, lines):
        self.ops = []
        lineID = 0

        while len(lines) > lineID:
            line = lines[lineID]
            lineID += 1

            if line.endswith(':'):
                self.__addLine(line)
                continue

            if self.keep_stl:
                self.__addLine('// %s' % line)

            stl = line.split()
            stl[1:] = [' '.join(stl[1:])]

            newOps = stl[0].lower()
            if newOps in self.method_list:
                # check logic
                if (newOps in self.logic_list or newOps in self.logic_change):
                    if (len(self.ops) > 0 and self.ops[-1] not in self.logic_list):
                        self.RLO = '1'
                # convert
                self.__dispatch(newOps, stl[1][:-1])
                # save ops
                self.ops.append(newOps)
            else:
                #print('Unknown STL code: %s.' % line)
                self.__addLine(line)

            lines = self.__parseIf(lines, lineID)


    def __addLine(self, line):
        self.sclLines.append(line)


    def __parseIf(self, lines, lineID):
        if (len(self.sclLines) > 2 and self.sclLines[-1].startswith('END_IF')
                and self.sclLines[-2].startswith('GOTO ') and self.sclLines[-3].startswith('IF NOT ')):
            label = self.sclLines[-2][5:]
            # check exists
            exists = False
            for line in lines[lineID:]:
                if line == label + ':':
                    exists = True
                    break
            if exists:
                self.sclLines[-2:] = [] # remove END_IF & GOTO
                self.sclLines[-1] = 'IF ' + self.sclLines[-1][7:]   # remove NOT

                subLines = []
                while lines[lineID] != label + ':':
                    subLines.append(lines[lineID])
                    lines[lineID:lineID + 1] = []

                # if
                self.__toSCL(subLines)
                self.__addLine('END_IF')
                lines = self.__parseElse(lines, lineID)

        return lines


    def __parseElse(self, lines, lineID):
        if (len(self.sclLines) > 2 and self.sclLines[-1].startswith('END_IF')
                and self.sclLines[-2].startswith('GOTO ')):
            label = self.sclLines[-2][5:]
            # check exists
            exists = False
            for line in lines[lineID:]:
                if line == label + ':':
                    exists = True
                    break
            if exists:
                self.sclLines[-2:] = [] # remove END_IF & GOTO
                self.__addLine('ELSE')

                subLines = []
                while lines[lineID] != label + ':':
                    subLines.append(lines[lineID])
                    lines[lineID:lineID + 1] = []

                # else
                self.__toSCL(subLines)
                self.__addLine('END_IF')

        return lines


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
        if self.RLO == '1':
            self.RLO = str(oper)
        else:
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
        self.__addLine('IF NOT (%s) THEN' % self.RLO)
        self.__addLine('GOTO %s' % oper)
        self.__addLine('END_IF')


    def __stl_ju(self, name, oper):
        self.__addLine('GOTO %s' % oper)


    def __stl_plus(self, name, oper):
        self.ACCU1 = '(%s + %s)' % (self.ACCU1, self.ACCU2)


    def __stl_minus(self, name, oper):
        self.ACCU1 = '(%s - %s)' % (self.ACCU2, self.ACCU1)


    def __stl_multiplication(self, name, oper):
        self.ACCU1 = '(%s * %s)' % (self.ACCU1, self.ACCU2)


    def __stl_division(self, name, oper):
        self.ACCU1 = '(%s / %s)' % (self.ACCU2, self.ACCU1)


    def __stl_1g2(self, name, oper):
        self.RLO = '(%s > %s)' % (self.ACCU1, self.ACCU2)


    def __stl_1l2(self, name, oper):
        self.RLO = '(%s < %s)' % (self.ACCU1, self.ACCU2)


    def __stl_1e2(self, name, oper):
        self.RLO = '(%s == %s)' % (self.ACCU1, self.ACCU2)


    def __stl_1ge2(self, name, oper):
        self.RLO = '(%s >= %s)' % (self.ACCU1, self.ACCU2)


    def __stl_1le2(self, name, oper):
        self.RLO = '(%s <= %s)' % (self.ACCU1, self.ACCU2)


    def __stl_neg(self, name, oper):
        self.ACCU1 = '(-%s)' % self.ACCU1
