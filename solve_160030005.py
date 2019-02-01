from z3 import *
import re
import sys
import time
from pathlib import Path
import json

if len(sys.argv) > 3 or len(sys.argv) < 2 :
	print('***** ERROR ***** \nUse program as:python program_name puzzles.json [output_file_name.txt], \nExamples: \npython solve_160030005.py puzzles_160030005.json\npython solve_160030005.py puzzles_160030005.json solutions_160030005.txt')
	sys.exit()

puzzles_file  = Path(sys.argv[1])
if not puzzles_file.is_file():
	print('***** ERROR ***** \nInput file doesn\'t exist')
	sys.exit(1)

if len(sys.argv) > 2:
	solutions_file  = Path(sys.argv[2])
else:
	solutions_file  = Path('./solutions_160030005.txt')


start_global = time.clock()
start_processing = time.clock()
print('--------------------------------------------------------------------------------')
print('Reading and parsing input file')
print('--------------------------------------------------------------------------------')

print('reading and storing input data', end=' ')
puzzles = []

# FOR OLD INPUT FORMAT
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

print('Sanity checks: check if each cell appears only once in the constraints', end=' ')
for p in range(len(puzzles)):
	puzzle = puzzles[p]

	# new board
	board = [[0 for i in range(len(rows))] for j in range(len(cols))]

	# fill board
	for board_pos, condition in puzzle:

		# check if only two board positions for / or -
		if condition[-1] == '/' or condition[-1] == '%' or condition[-1] == '-':
			if len(board_pos) != 2:
				print('division or subtraction constraint',board_pos,condition,'with more than two board positions in puzzle',p)
				sys.exit(1)

		# fill the board with ones
		for pos in board_pos:
			if pos[0] not in cols or pos[1] not in rows:
				print('illegal position name: ', pos)
				sys.exit(1)
			x, y = index(pos)
			board[x][y] += 1

	# problem if each position not in board atleast and atmost once
	incorrect = 0
	total = 0
	incorrect_index = []

	for row_i in range(len(board)):
		for i in range(len(board[row_i])):
			if board[row_i][i] == 0:
				incorrect += 1
				incorrect_index.append((row_i, i))	
				break
			total += 1

		if incorrect > 0:
			print('\ninput not correct at index',incorrect_index, 'in puzzle[', p,']', puzzle)
			sys.exit(1)

	if total != len(rows)*len(cols):
		incorrect += 1

	if incorrect > 0:
		print('input not correct at index',incorrect_index, 'in puzzle[', p,']', puzzle)
		sys.exit(1)

print(': done')

stop_processing = time.clock()
print()
print('Total time taken in pre-processing: ', round(stop_processing - start_processing, 2),'s')

print('--------------------------------------------------------------------------------')
print('Solving the puzzles using Z3 SAT solver')
print('--------------------------------------------------------------------------------')
start_solving = time.clock()

solutions = []
puzzle_stop_time = []
puzzle_start_time = []

# def absolute(x):
# 	return If(x>0,x,-x)

# def maximum(x, y):
# 	return If(x>y,x,y)

# def minimum(x, y):
# 	return If(x>y,y,x)

for p in range(len(puzzles)):
	puzzle_start_time.append(time.clock())

	puzzle = puzzles[p]
	print('Adding puzzle[',str('{0:02d}'.format(p)),'] constraints...', end = " ")
	sys.stdout.flush()

	constraints = []
	X = [[ Int("x_%s_%s" % (i, j)) for j in range(6) ] for i in range(6) ] 		# 6x6 matrix of integer variables
	cells_c  = [ And(1 <= X[i][j], X[i][j] <= 6) for i in range(6) for j in range(6) ] # each cell contains a value in {1, ..., 6}
	rows_c   = [ Distinct(X[i]) for i in range(6) ] 							# each row contains a digit at most once
	cols_c   = [ Distinct([ X[i][j] for i in range(6) ]) for j in range(6) ]	# each column contains a digit at most once

	s = Solver()
	s.add(cells_c)
	s.add(rows_c)
	s.add(cols_c)

	# board arithmetic constraints
	for board_poses, condition in puzzle:

		x0, y0 = index(board_poses[0])

		if condition[-1] == '+':
			total = X[x0][y0]
			for i in range(1, len(board_poses)):
				x,y = index(board_poses[i])
				total += X[x][y]
			constraints.append(total == int(condition[:-1]))

		elif condition[-1] == 'x' or condition[-1] == '*':
			product = X[x0][y0]
			for i in range(1, len(board_poses)):
				x,y = index(board_poses[i])
				product *= X[x][y]
			constraints.append(product == int(condition[:-1]))

		elif condition[-1] == '-':
			x1, y1 = index(board_poses[1])
			constraints.append(Or(X[x0][y0] - X[x1][y1] == int(condition[:-1]), X[x1][y1] - X[x0][y0] == int(condition[:-1])))
			# constraints.append( absolute( X[x0][y0] - X[x1][y1] ) == int(condition[:-1]) )

		elif condition[-1] == '/' or condition[-1] == '%':
			x1, y1 = index(board_poses[1])
			constraints.append(Or(X[x0][y0] / X[x1][y1] == int(condition[:-1]), X[x1][y1] / X[x0][y0] == int(condition[:-1])))
			# constraints.append( maximum(X[x0][y0] , X[x1][y1]) / minimum(X[x0][y0] , X[x1][y1]) == int(condition[:-1]) )

	s.add(And(constraints))

	print('checking if a solution exists...', end='')
	sys.stdout.flush()
	if s.check() == sat:
		m = s.model()
		r = [[ m.evaluate(X[i][j]) for j in range(6) ] for i in range(6) ]
		solutions.append('['+''.join([''.join([i.as_string() for i in row]) for row in r[::-1]])+']')
		# print_matrix(r)
		print('Solution found, done. ', end='')
	else:
		solutions.append([])
		print("failed to solve this puzzle. ", end='')

	puzzle_stop_time.append(time.clock())
	print('time taken: ', round(puzzle_stop_time[-1] - puzzle_start_time[-1], 2),'s')


print()
print('Writing Solutions to file',solutions_file.name, end='')
with open(solutions_file.name, 'w') as f:
	f.write('\n'.join(solutions))
print(': Done')

# stats
print()
print('Average Puzzle Solving Time: ', round((sum(puzzle_stop_time) - sum(puzzle_start_time))/len(puzzles), 2),'s')
end_global = time.clock()
print('Total time taken in solving the puzzles: ', round(end_global - start_solving, 2),'s')
print('Solutions Written to File ---->',solutions_file.name,'<-----')

print('________________________________________________________________________________')
print('Total time taken: ', round(end_global - start_global, 2),'s')
print('________________________________________________________________________________')