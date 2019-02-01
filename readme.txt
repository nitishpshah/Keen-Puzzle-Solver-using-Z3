run programs: ----------------------------------------------------------------

Solving the puzzles:
python solve_160030005.py puzzles_160030005.json

Verifing the solutions:
python verify_160030005.py puzzles_160030005.json solutions_160030005.txt
--------------------------------------------------------------------------------

SMAPLE OUTPUTS:

*********************************************************************************************
>>> python .\solution_160030005.py .\puzzles_160030005.txt
*********************************************************************************************
--------------------------------------------------------------------------------
Reading and parsing input file
--------------------------------------------------------------------------------
reading and storing input data : done
Sanity checks: check if each cell appears only once in the constraints : done

Total time taken in pre-processing:  0.0 s
--------------------------------------------------------------------------------
Solving the puzzles using Z3 SAT solver
--------------------------------------------------------------------------------
Adding the common constraints for the puzzles: done
Adding puzzle[ 0 ] constraints... checking if a solution exists...done. time taken:  0.4 s
Adding puzzle[ 1 ] constraints... checking if a solution exists...done. time taken:  0.33 s
Adding puzzle[ 2 ] constraints... checking if a solution exists...done. time taken:  2.32 s

Writing Solutions to file solutions.txt: Done

Average Puzzle Solving Time:  1.02 s
Total time taken in solving the puzzles:  3.08 s
________________________________________________________________________________
Total time taken:  3.08 s
________________________________________________________________________________


*********************************************************************************************
>>> python .\verification_160030005.py .\puzzles_160030005.txt .\solutions_160030005.txt
*********************************************************************************************

--------------------------------------------------------------------------------
Reading and parsing input file
--------------------------------------------------------------------------------
reading and storing input data : done
reading and storing solution data : done

Total time taken in pre-processing:  0.0 s
--------------------------------------------------------------------------------
Verifying the solutions of puzzles
--------------------------------------------------------------------------------
Checking Puzzle[ 0 ]... solution [OK]        time taken:  0.0 s
Checking Puzzle[ 1 ]... solution [OK]        time taken:  0.0 s
Checking Puzzle[ 2 ]... solution [OK]        time taken:  0.0 s


Average Puzzle Verifying Time:  0.0 s
Total time taken in verifying all the puzzles:  0.0 s
________________________________________________________________________________
Total time taken:  0.0 s
________________________________________________________________________________