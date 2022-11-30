#!/usr/bin/env python
lines = open(__file__).readlines()
open(__file__, "w").writelines(lines[:4] + [lines[5], lines[4], lines[6]])
print("Good")
print()
print("Ugly")
print("Goodbye now!")
