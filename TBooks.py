#!/usr/bin/env python

import sys, getopt
import __builtin__

lOpts, lArgs = getopt.getopt(sys.argv[1:], 't')

if len(lOpts) == 1 and lOpts[0][0] == '-t':
	__builtin__.__testing__ = True
	print 'Testing'
else:
	__builtin__.__testing__ = False

import tbooks.view.Application as Application
Application.Start()
