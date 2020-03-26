#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

cpu = CPU()

if len(sys.argv) != 2:
    cpu.load()
else:
    cpu.load_memory(sys.argv[1])

cpu.run()

