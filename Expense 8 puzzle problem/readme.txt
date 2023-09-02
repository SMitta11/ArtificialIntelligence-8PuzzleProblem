

Code Structure:

	Libraries Used: copy, sys, datetime

	Description:
		Program is command line arguments driven, allowing users to choose different algorithms for solving a puzzle. 
		If no algorithm is specified, the default is A*.

	Logging and Dumping:
		If the dump_flag is set to True, the program creates a new dump file named with the current date and time in the format "trace-%m_%d_%Y-%I_%M_%S_%p" (example - trace-08_09_2023-08_42_09_PM).

	Class: Puzzle
		This class serves as a container for the initial puzzle data. It provides a structured approach to handling data consistently across different algorithms. The class includes several log functions for storing various types of data in a log file.

		Class: Functions

			Function: __get_file_content()
				Reads the start and goal files and returns an array representing the puzzle configuration.
			
			Function: __create_logger()
				Creates a logging instance to manage log data.

			Function: write_log()
				Logs specified data using the logging instance.
			
			Function: log_successors(), log_no_successors(), log_fringe()
				Logs information related to successors, no successors found, and fringes.
			
			Function: get_successors()
				Retrieves successor states based on the current state, storing them in the fringe for exploration.
			
			Function: generate_results(), solution_found()
				Prints and logs the final result of the algorithm once a solution is found.
			
			Function: heuristic()
				Calculates the heuristic cost of a given state based on the Manhattan distance.
			
			Function: neighbors()
				Generates and adds different combinations of possible moves to neighboring states, generating fringes (left, up, right, down directions). 
				This process explores possible paths from the current state.
			
			Functions: solve_bfs(), solve_ucs(), solve_greedy(), solve_a_star()
				Implement the main algorithms, utilizing helper class functions to generate fringes, find solutions, and log steps.

	Function: main()
		The main() function creates an instance of the Puzzle class, and based on command-line arguments, it invokes various algorithm-solving functions.


How to run the code: 
Open terminal and run the following command
python3 expense_8_puzzle.py <start-file> <goal-file> <method> <dump-flag>

Example command to run the code: 
python3 expense_8_puzzle.py start.txt goal.txt greedy True

Information
	BFS and UCS takes some time to complete when dump_flag is provided as true in command line arguments. 
