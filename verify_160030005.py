import re
import sys
import time
from pathlib import Path
import json

start_global = time.clock()
start_processing = time.clock()

if len(sys.argv) > 4 or len(sys.argv) < 3 :
	# print('\n***** ERROR ***** \nUse program as: \npython program_name.py puzzles.json solutions.txt [print_problems], \
	# \n\tprint_problems: set this to 1, to print all the inconsistencies in each puzzle, if any, default zero\
	# \n\nExample: \npython verification_160030005.py puzzles_160030005.json solutions_160030005.txt 1\n')
	print('\n***** ERROR ***** \nUse program as: \npython program_name.py puzzles.json solutions.txt, \
	\n\n\tpuzzles.json: json file with puzzle board constraints\
	\n\tsolutions.txt: txt file with solutions of the puzzles in puzzles.json\
	\n\nExample: \npython verification_160030005.py puzzles_160030005.json solutions_160030005.txt\n')
	sys.exit()

if len(sys.argv) == 4:
	print_problems = int(sys.argv[3])
else:
	print_problems = 0

puzzles_file  = Path(sys.argv[1])
if not puzzles_file.is_file():
	print('***** ERROR ***** \nPuzzles file doesn\'t exist')
	sys.exit(1)

solutions_file  = Path(sys.argv[2])
if not solutions_file.is_file():
	print('***** ERROR ***** \nSolutions file doesn\'t exist')
	sys.exit(1)


print('--------------------------------------------------------------------------------')
print('Reading and parsing input file')
print('--------------------------------------------------------------------------------')

print('reading and storing input data', end=' ')
puzzles = []

# FOR OLD INPUT
# with open(puzzles_file.name, 'r') as f:
# 	for puzzle_string in f:
# 		if puzzle_string.strip() == '':
# 			# ignore blank lines
# 			continue
# 		puzzle = []
# 		puzzle_string.replace('puzzle: ' , '')
# 		for constraint in re.findall('\((.*?)\)', puzzle_string):
# 			condition = constraint[constraint.rfind(',')+1:]
# 			puzzle_pos = re.findall('\{(.*?)\}', constraint)[0].split(',')
# 			puzzle.append(([bp.strip() for bp in puzzle_pos], condition))
# 		puzzles.append(puzzle)

with open(puzzles_file.name, 'r') as f:
	puzzles = json.load(f)

print(': done')

'''
Board numberings:
	a  b  c  d  e  f 	
  ---------------------	
0 | a6 b6 c6 d6 e6 f6 |	6
1 | a5 b5 c5 d5 e5 f5 |	5
2 | a4 b4 c4 d4 e4 f4 |	4
3 | a3 b3 c3 d3	e3 f3 |	3
4 | a2 b2 c2 d2	e2 f2 |	2
5 | a1 b1 c1 d1 e1 f1 |	1
  ---------------------	
	0  1  2  3  4  5
'''

print('Making row and column maps', end=' ')
cols = ['a', 'b', 'c', 'd', 'e', 'f']
rows = ['6', '5', '4', '3', '2', '1']
rows_map = {}
cols_map = {}

for i in range(len(cols)):
	cols_map[cols[i]] = i

for i in range(len(rows)):
	rows_map[rows[i]] = i

def index(pos, rows_map=rows_map, cols_map=cols_map):
	return rows_map[pos[1]], cols_map[pos[0]]
print(': done')


print('reading and storing solution data', end=' ')
solutions = []
with open(solutions_file.name, 'r') as f:
	for solution_string in f:
		# solution_string : a1 .. f1 a2 .. f2 ... a6 .. f6
		if solution_string[0] == '[':
			solution_string = solution_string.strip()[1:-1] 	# remove '[' and ']' at the start and end
		solutions.append(solution_string)

print(': done')


stop_processing = time.clock()
print()
print('Total time taken in pre-processing: ', round(stop_processing - start_processing, 2),'s')

print('--------------------------------------------------------------------------------')
print('Verifying the solutions of puzzles')
print('--------------------------------------------------------------------------------')
start_solving = time.clock()

puzzle_start_time = []

puzzle_stop_time = []
problems = []

for p in range(len(puzzles)):
	puzzle_start_time.append(time.clock())

	if print_problems:
		problems.append([])
	puzzle = puzzles[p]

	print('Checking Puzzle[',str('{0:02d}'.format(p)),']...', end = " ")

	solution = solutions[p]
	count = 0
	incorrect = 0

	# if no solution given to check
	if len(solution) == 0:
		incorrect += 1
		print('solution [EMPTY]          ', end='')
		puzzle_stop_time.append(time.clock())
		print('time taken: ', round(puzzle_stop_time[-1] - puzzle_start_time[-1], 2),'s')
		continue

	# check if consistent length
	if len(solution) != len(rows)*len(cols):
		incorrect += 1
		print('solution [INCORRECT LEN]  ', end='')
		puzzle_stop_time.append(time.clock())
		print('time taken: ', round(puzzle_stop_time[-1] - puzzle_start_time[-1], 2),'s')
		continue

	# fill board from solution
	X = [[-1 for i in range(6)] for j in range(6)]
	for r in range(6)[::-1]:
		for c in range(6):

			# check if digit, necessary?
			if not solution[count].isdigit():
				incorrect += 1
				break
				# if not print_problems:
				# 	break
				# else:
				# 	problems[p].append(solution[count]+' at position '+str(count)+' is not a digit')

			# convert digit to integer
			num = int(solution[count])

			# check if digit in range
			if num > len(rows) or num < 1:
				incorrect += 1
				break
				# if not print_problems:
				# 	break
				# else:
				# 	problems[p].append(str(num)+' not in between 1 and 6')

			# add digit to board
			X[r][c] = num
			count += 1
		
		# if not print_problems:
		# 	if incorrect > 0:
		# 		break		# out of this for loop

		if incorrect > 0:
			break		# out of this for loop

	# check if all distinct in a row
	for r in range(6):
		row_distinct = []
		for c in range(6):
			row_distinct.append(X[r][c])
		if set(row_distinct) != set(range(1,7)):
			incorrect += 1
			break
			# if not print_problems:
			# 	break
			# else:
			# 	problems[p].append('numbers in row '+str(r)+' not distinct: '+ str(row_distinct))

	# check if distinct in a column
	for c in range(6):
		column_distinct = []
		for r in range(6):
			column_distinct.append(X[r][c])
		if set(column_distinct) != set(range(1,7)):
			incorrect += 1
			break
			# if not print_problems:
			# 	break
			# else:
			# 	problems[p].append('numbers in column '+str(c)+' not distinct: '+ str(column_distinct))


	# check if board arithmetic constraints satisfied
	for board_poses, condition in puzzle:

		x0, y0 = index(board_poses[0])

		if condition[-1] == '+':
			total = X[x0][y0]
			for i in range(1, len(board_poses)):
				x,y = index(board_poses[i])
				total += X[x][y]
			if total != int(condition[:-1]):
				incorrect += 1
				break
				# if not print_problems:
				# 	break
				# else:
				# 	problems[p].append('problem in' +str(board_poses)+' '+str(condition)+' sum = '+str(total))

		elif condition[-1] == 'x' or condition[-1] == '*':
			product = X[x0][y0]
			for i in range(1, len(board_poses)):
				x,y = index(board_poses[i])
				product *= X[x][y]
			if product != int(condition[:-1]):
				incorrect += 1
				break
				# if not print_problems:
				# 	break
				# else:
				# 	problems[p].append('problem in' +str(board_poses)+' '+str(condition)+' product = '+str(product))

		elif condition[-1] == '-':
			x1, y1 = index(board_poses[1])
			if X[x0][y0] - X[x1][y1] != int(condition[:-1]) and X[x1][y1] - X[x0][y0] != int(condition[:-1]):
				incorrect += 1
				break
				# if not print_problems:
				# 	break
				# else:
				# 	problems[p].append('problem in' +str(board_poses)+' '+str(condition))

		elif condition[-1] == '/' or condition[-1] == '%':
			x1, y1 = index(board_poses[1])
			if X[x0][y0] / X[x1][y1] != int(condition[:-1]) and X[x1][y1] / X[x0][y0] != int(condition[:-1]):
				incorrect += 1
				break
				# if not print_problems:
				# 	break
				# else:
				# 	problems[p].append('problem in' +str(board_poses)+' '+str(condition))

	if incorrect == 0:
		print('solution [OK]             ', end='')
	else:
		print('solution [INCORRECT]      ', end='')

	puzzle_stop_time.append(time.clock())
	print('time taken: ', round(puzzle_stop_time[-1] - puzzle_start_time[-1], 2),'s')

print()

for p in range(len(problems)):
	if len(problems[p]) > 0:
		print('Problems in Puzzle[',p,']')
		print('\t\n','\t\n'.join(problems[p]))

print()
print('Average Puzzle Verifying Time: ', round((sum(puzzle_stop_time) - sum(puzzle_start_time))/len(puzzles), 2),'s')
end_global = time.clock()
print('Total time taken in verifying all the puzzles: ', round(end_global - start_solving, 2),'s')

print('________________________________________________________________________________')
print('Total time taken: ', round(end_global - start_global, 2),'s')
print('________________________________________________________________________________')