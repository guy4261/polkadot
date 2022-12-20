#!/usr/bin/env python
inputfile = "input.txt"

topk_elves = list()
k = 1

current_elf = 0

for line in open(inputfile):
	line = line.strip("\r\n")
	if len(line) == 0:
		topk_elves.append(current_elf)
		topk_elves.sort()
		topk_elves = topk_elves[-k:]
		current_elf = 0
	else:
		# it's calories
		current_elf += int(line)

topk_elves.append(current_elf)
topk_elves.sort()
topk_elves = topk_elves[-k:]

print(sum(topk_elves))
