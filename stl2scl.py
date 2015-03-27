#!/usr/bin/env python
# -*- coding:utf-8 -*-
# File          : stl2scl.py
# Author        : bss
# Project       : stl2scl
# Creation Date : 2015-03-27
# Description   : Convert siemens' STL code to SCL
# 

import sys
import getopt
from convert import Converter


class STL2SCL:
    def __init__(self):
        self.stl_filename = './in.txt'
        self.scl_filename = './out.scl'
        self.keep_stl = False
        self.show_label = False


    def convert(self, stl_filename):
        self.stl_filename = stl_filename
        self.convert()


    def convert(self):
        print('+Loading STL from %s' % self.stl_filename)
        self.__load()
        print('+Please wait...')
        self.__formatSTL()
        self.__toSCL()
        self.__checkLabel()
        self.__formatSCL()
        print('+Saving SCL to %s' % self.scl_filename)
        self.__save()


    def __load(self):
        fp = open(self.stl_filename)
        self.lines = fp.readlines()
        fp.close()


    def __save(self):
        fp = open(self.scl_filename, 'w')
        fp.writelines([item+'\n' for item in self.lines])
        fp.close()


    def __formatSTL(self):
        newLines = []

        for line in self.lines:
            line = line.strip()
            if line == '':
                continue

            line = line.strip(';')      # end with ;
            sp = line.split(':')
            if len(sp) > 1:             # begin with label
                newLines.append(sp[0] + ':')
                line = ' '.join(sp[1:])
            line = line.strip()
            if line == '':
                continue

            sp = line.split()
            sp1 = ' '.join(sp[1:])
            line = sp[0] + ' ' * max(8 - len(sp[0]), 1) + sp1 + ';'
            newLines.append(line)

        self.lines = newLines


    def __toSCL(self):
        converter = Converter(keep_stl = self.keep_stl)
        self.lines = converter.convert(self.lines)


    def __checkLabel(self):
        usedLabels = []
        for line in self.lines:
            if line.startswith('GOTO '):
                usedLabels.append(line[5:])

        newLines = []
        for line in self.lines:
            if line.endswith(':'):
                label = line[:-1]
                if label in usedLabels:
                    newLines.append(line)
                elif self.keep_stl:
                    newLines.append('// %s' % line)
                elif self.show_label:
                    newLines.append(line)
            else:
                newLines.append(line)

        self.lines = newLines


    def __formatSCL(self):
        newLines = []
        nestedLevel = 0
        indent = '    '

        for line in self.lines:
            if line.endswith(':'):
                newLines.append('')

            if line.startswith('ELSE'):
                newLines.append(indent * (nestedLevel-1) + line)
                continue
            elif line.startswith('IF '):
                newLines.append(indent * nestedLevel + line)
                nestedLevel += 1
            elif line.startswith('FOR '):
                newLines.append(indent * nestedLevel + line)
                nestedLevel += 1
            elif line.startswith('END_IF'):
                nestedLevel -= 1
                newLines.append(indent * nestedLevel + line)
            elif line.startswith('END_FOR'):
                nestedLevel -= 1
                newLines.append(indent * nestedLevel + line)
            else:
                newLines.append(indent * nestedLevel + line)

        self.lines = newLines


    def parseOpts(self, argv):
        try:
            opts, args = getopt.getopt(argv[1:], 'hi:o:',
                    ['help', 'input=', 'output=', 'keep-stl', 'show-label'])
        except (getopt.GetoptError, err):
            print(str(err))
            Usage()
            sys.exit(2)
        except:
            Usage()
            sys.exit(1)

        for o, a in opts:
            if o in ('-h', '--help'):
                Usage()
                sys.exit(0)
            elif o in ('-i', '--input'):
                self.stl_filename = a
            elif o in ('-o', '--output'):
                self.scl_filename = a
            elif o in ('--keep-stl'):
                self.keep_stl = True
            elif o in ('--show-label'):
                self.show_label = True



def Usage():
    print('stl2scl.py @ https://github.com/bssthu/stl2scl')
    print('usage:')
    print('-i, --input: input stl file name')
    print('-o, --output: output scl file name')
    print('--keep-stl: keep stl code as comment')
    print('--show-label: show all labels')
    print('')
    print('example:')
    print('./stl2scl.py -i in.stl -o out.scl')
    print('')


if __name__ == '__main__':
    stl2scl = STL2SCL()
    stl2scl.parseOpts(sys.argv)

    stl2scl.convert()
