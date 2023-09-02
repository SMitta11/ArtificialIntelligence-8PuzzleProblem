import sys
import datetime
import copy

class Puzzle:
    def __init__(self, start_file, goal_file, method, dump_flag):
        self.start_file = start_file
        self.goal_file = goal_file
        self.method = method
        self.dump_flag = dump_flag
        
        self.nodes_popped = 0
        self.nodes_expanded = 0
        self.nodes_generated = 1
        self.max_fringe_size = 1
        
        self.result_steps = []
        self.closed_steps = []

        self.start_grid = self.__get_file_content(self.start_file)
        self.goal_grid = self.__get_file_content(self.goal_file)
        
        self.logger = None

        if self.dump_flag:
            self.__create_logger()

    def __get_file_content(self, file_name):
        grid = []
        with open(file_name, "r") as f:
            for line in f:
                if line == "END OF FILE":
                    break
                row = line.strip().split(" ")
                grid.extend(map(int, row))
        return grid

    def __create_logger(self):
        now = datetime.datetime.now()
        formatted = now.strftime("trace-%m_%d_%Y-%I_%M_%S_%p")
        filename = f"{formatted}.txt"
        self.logger = open(filename, "w")
        self.write_log(f"Command-Line Arguments : ['{self.start_file}', '{self.goal_file}', '{self.method}' , '{self.dump_flag}']")
        self.write_log(f"Method Selected : {self.method}")
        self.write_log(f"Running {self.method}")
        
    def __del__(self):
        if self.logger:
            self.logger.close()

    def write_log(self, data, new_line = True):
        if self.dump_flag and self.logger:
            self.logger.write(data)
            if new_line:
                self.logger.write("\n")

    def log_successors(self, count):
        if self.dump_flag:
            self.write_log(f"\t{count} successors generated")
            self.write_log("\tClosed: [", False)
            for index in self.closed_steps:
                self.write_log(f"{index['node']}", False)
            self.write_log("]")

    def log_no_successors(self,item):
        if self.dump_flag:
            self.write_log(f"\t{item} is already in closed so 0 successors")
            self.write_log("\tClosed: [", False)
            for index in self.closed_steps:
                self.write_log(f"{index['node']}", False)
            self.write_log("]")
    
    def log_fringe(self, fringe):
        if self.dump_flag:
            self.write_log("\tFringe: [")
            for i in fringe:
                self.write_log(f"\t\t< state = {i['node']}, action={{Move {i['val']} {i['move']}}}, d = {i['depth']}, g(n) = {i['cost']}, f(n) = {i['algo']}, Parent = Pointer to {i['prev']}")
            self.write_log("]") 
         
    def generate_results(self,  state):
        print("")
        print(f"Nodes Popped: {self.nodes_popped}")
        print(f"Nodes Expanded: {self.nodes_expanded}")
        print(f"Nodes Generated: {self.nodes_generated}")
        print(f"Max Fringe Size: {self.max_fringe_size}")
        if self.dump_flag:
            self.write_log(f"Nodes Popped: {self.nodes_popped}")
            self.write_log(f"Nodes Expanded: {self.nodes_expanded}")
            self.write_log(f"Nodes Generated: {self.nodes_generated}")
            self.write_log(f"Max Fringe Size: {self.max_fringe_size}")

        if state:
            print(f"Solution Found at depth {state['depth']} with cost of {state['cost']}.")
            result = self.solution_found(state)
            print("Steps:")
            for i in range(1, len(result)):
                print("\t"+result[i])
        else:
            print("No Solution")
    #
    def is_closed(self, current):
        for c in self.closed_steps:
            if current['node'] == c['node']:
                return True
        return False
    
    def solution_found(self, route):
        result=[]
        
        def item_exist(**params):
            for item in self.closed_steps:
                if all(item.get(key) == value for key, value in params.items()):
                    return item
            return None
        result.insert(0, f"Move {route['val']} {route['move']}" )
        curr = copy.deepcopy(route)
        while (curr['parent'] is not None):         
            depth = curr['depth']-1
            cost = curr['cost']-curr['val']
            parent_idx = curr['parent']
            node = curr['node']
            index = curr['ind']
            node[index],  node[parent_idx] = node[parent_idx], 0

            item = item_exist( depth=depth, cost=cost, ind=parent_idx, node=node)
            result.insert(0, f"Move {item['val']} {item['move']}" )
            curr = copy.deepcopy(item)
        return result
    
    def heuristic(self, curr):
        board = 3
        heu, quo, rem, temp = 0, 0, 0, 0
        for i in self.goal_grid:
            goal_i = self.goal_grid.index(i)
            curr_i = curr.index(i)
            if ((goal_i==2 and curr_i==3) or (goal_i==3 and curr_i==2) or (goal_i==5 and curr_i==6) or (goal_i==6 and curr_i==5)):
                req =  (goal_i+curr_i)%board
                diff = abs(goal_i-curr_i)
                temp = (diff+req)*i
                # print (temp)
                heu+= temp
            else:
                diff = abs(goal_i-curr_i)
                if (diff!=0):
                    rem = diff%board
                    quo =  diff//board
                    temp = (rem+quo)*i
                    heu+=temp
        return heu
    
    def get_temp_node(self, state, state_cp, ind, val, parent, move, prev = None):
        if state:
            temp_node =  {'node': state_cp['node'], 'ind': ind, 'val': val, 'parent': parent, 'move': move, 'depth': state['depth'] + 1, 'cost': state_cp['cost'] + val,'heugreedy': self.heuristic(state_cp['node']), 'heuastar': 0, 'prev': prev }
        else:
            temp_node =  {'node': state_cp['node'], 'ind': ind, 'val': val, 'parent': parent, 'move': move, 'depth': state_cp['depth'] + 1, 'cost': state_cp['cost'] + val,'heugreedy': self.heuristic(state_cp['node']), 'heuastar': 0, 'prev': prev }
        
        if (self.method == 'GREEDY'):
            temp_node['algo'] = temp_node['heugreedy']
        elif (self.method == 'A*'):
            temp_node['heuastar'] = temp_node['cost'] + temp_node['heugreedy']
            temp_node['algo'] = temp_node['heuastar']
        else:
            temp_node['algo'] = 0
        return temp_node

    def neighbors (self, state, fringe, prev = None):
        curr = state['node']
        curr_idx = curr.index(0)
        self.nodes_expanded+=1
        res = 0
        left_idx, left = -1, -1
        right_idx, right = -1, -1
        up_idx, up = -1, -1
        down_idx, down = -1, -1
        #left
        if (curr_idx not in [0, 3, 6]): 
            left_idx = curr_idx-1
            left = curr[left_idx]
        #right
        if (curr_idx not in [2, 5, 8]): 
            right_idx = curr_idx+1
            right = curr[right_idx]
        #up
        if (curr_idx not in [0, 1, 2]):
            up_idx = curr_idx-3
            up = curr[up_idx]  
        #down
        if (curr_idx not in [6, 7, 8]): 
            down_idx = curr_idx+3
            down = curr[down_idx]

        if (left!=-1): 
            state_cp = copy.deepcopy(state)
            state_cp['node'][curr_idx], state_cp['node'][left_idx] = state_cp['node'][left_idx], state_cp['node'][curr_idx]
            fringe.append(self.get_temp_node(None, state_cp, left_idx, left, curr_idx, 'Right', prev))
            self.nodes_generated+=1
            res+=1

        if (up!=-1):
            state_cp = copy.deepcopy(state)
            state_cp['node'][curr_idx], state_cp['node'][up_idx] = state_cp['node'][up_idx], state_cp['node'][curr_idx]

            fringe.append(self.get_temp_node(state, state_cp, up_idx, up, curr_idx, 'Down', prev))    
            self.nodes_generated+=1
            res+=1
        if (right!=-1): #move blank right
            state_cp = copy.deepcopy(state)
            state_cp['node'][curr_idx], state_cp['node'][right_idx] = state_cp['node'][right_idx], state_cp['node'][curr_idx]
            fringe.append(self.get_temp_node(None, state_cp, right_idx, right, curr_idx, 'Left', prev))    
            self.nodes_generated+=1
            res+=1
        if (down!=-1): #move blank down
            state_cp = copy.deepcopy(state)
            state_cp['node'][curr_idx], state_cp['node'][down_idx] = state_cp['node'][down_idx], state_cp['node'][curr_idx]
            fringe.append(self.get_temp_node(None, state_cp, down_idx, down, curr_idx, 'Up', prev))  
            self.nodes_generated+=1
            res+=1
        return res

    def get_successors(self, current, prev):
        if self.dump_flag:
            action = f"{{Move {current['val']} {current['move']}}}"
            if current['move'] is None:
                action = "Start"
            return f"< state = {current['node']}, action={{{action}}}, g(n) = {current['cost']}, d = {current['depth']}, f(n) = {current['algo']}, Parent = Pointer to {{{prev}}} >:"
        return None
    
    def solve_bfs(self):
        print("Solving using Breadth First Search")
        res = 0
        fringe=[] 
        start_idx = self.start_grid.index(0)
        prev = None
        fringe.append(
            {
                'node':self.start_grid, 
                'ind':start_idx, 
                'val':0, 
                'move':None, 
                'depth':0, 
                'cost':0, 
                'parent':None, 
                'algo':0,
                'prev': None
            })
        final_state=None

        while len(fringe)>0:
            self.nodes_popped+=1
            current = fringe[0]
            if self.dump_flag:
                successor_str = self.get_successors(current, prev)
                self.write_log(f"Generating successors to {successor_str}")
                prev = successor_str

            if current['node']==self.goal_grid:
                self.closed_steps.append(
                    {
                        'node': current['node'], 
                        'ind':current['ind'], 
                        'val':current['val'], 
                        'cost':current['cost'], 
                        'move':current['move'], 
                        'depth':current['depth'], 
                        'parent':current['parent'], 
                        'algo':current['algo']
                    })
                self.log_successors(res)
                final_state=copy.deepcopy(current)
                break
            elif self.is_closed(current): 
                self.max_fringe_size=max(self.max_fringe_size, len(fringe))
                self.log_no_successors(fringe[0]['node'])
                self.log_fringe(fringe)
                del fringe[0]
                
            else:

                self.closed_steps.append(
                    {
                        'node': current['node'], 
                        'ind':current['ind'], 
                        'val':current['val'], 
                        'parent':current['parent'], 
                        'move':current['move'], 
                        'depth':current['depth'], 
                        'cost':current['cost'], 
                        'algo':current['algo']
                    })
                
                res = self.neighbors(current, fringe, None)
                del fringe[0]
                self.max_fringe_size=max(self.max_fringe_size, len(fringe))
                self.log_successors(res)
                self.log_fringe(fringe)

        self.generate_results(final_state)
        
    def solve_ucs(self):
        print("Solving using Uniform Cost Search")
        res = 0
        fringe=[] 
        start_idx = self.start_grid.index(0)
        prev = None
        fringe.append(
            {
                'node':self.start_grid, 
                'ind':start_idx, 
                'val':0, 
                'parent':None, 
                'move':None, 
                'depth':0, 
                'cost':0, 
                'algo':0,
                'prev': None
            })
        final_state=None

        while len(fringe)>0:
            self.nodes_popped+=1
            current = fringe[0]
            if self.dump_flag:
                successor_str = self.get_successors(current, prev)
                self.write_log(f"Generating successors to {successor_str}")
                prev = None

            if current['node']==self.goal_grid:
                self.closed_steps.append(
                    {
                        'node': current['node'], 
                        'ind':current['ind'], 
                        'val':current['val'], 
                        'parent':current['parent'], 
                        'move':current['move'], 
                        'depth':current['depth'], 
                        'cost':current['cost'], 
                        'algo':current['algo']
                    })
                self.log_successors(res)
                final_state=copy.deepcopy(current)
                break
            elif self.is_closed(current): 
                self.max_fringe_size=max(self.max_fringe_size, len(fringe))
                self.log_no_successors(fringe[0]['node'])
                self.log_fringe(fringe)
                del fringe[0]
            else:

                self.closed_steps.append(
                    {
                        'node': current['node'], 
                        'ind':current['ind'], 
                        'val':current['val'], 
                        'parent':current['parent'], 
                        'move':current['move'], 
                        'depth':current['depth'], 
                        'cost':current['cost'], 
                        'algo':current['algo']
                    })
                res = self.neighbors(current, fringe, None)
                del fringe[0]
                self.max_fringe_size=max(self.max_fringe_size, len(fringe))
                fringe = sorted(fringe, key=lambda x: x['cost'])
                self.log_successors(res)
                self.log_fringe(fringe)

        self.generate_results(final_state)

    def solve_greedy(self):
        print("Solving using Greedy Search")
        res = 0
        fringe=[] 
        start_idx = self.start_grid.index(0)
        prev = None
        fringe.append(
            {
                'node':self.start_grid, 
                'ind':start_idx, 
                'val':0, 
                'parent':None, 
                'move':None, 
                'depth':0, 
                'cost':0, 
                'algo':self.heuristic(self.start_grid),
                'prev': None
            })
        final_state=None
        while len(fringe)>0:
            self.nodes_popped+=1
            current = fringe[0]
            if self.dump_flag:
                successor_str = self.get_successors(current, prev)
                self.write_log(f"Generating successors to {successor_str}")
                prev = successor_str

            if current['node']==self.goal_grid:
                self.closed_steps.append(
                    {
                        'node': current['node'], 
                        'ind':current['ind'], 
                        'val':current['val'], 
                        'parent':current['parent'], 
                        'move':current['move'], 
                        'depth':current['depth'], 
                        'cost':current['cost'], 
                        'algo':current['algo']
                    })
                self.log_successors(res)
                final_state=copy.deepcopy(current)
                break
            elif self.is_closed(current): 
                self.max_fringe_size=max(self.max_fringe_size, len(fringe))
                self.log_no_successors(fringe[0]['node'])
                self.log_fringe(fringe)
                del fringe[0]
            else:
                self.closed_steps.append(
                    {
                        'node': current['node'], 
                        'ind':current['ind'], 
                        'val':current['val'], 
                        'parent':current['parent'], 
                        'move':current['move'], 
                        'depth':current['depth'], 
                        'cost':current['cost'], 
                        'algo':current['algo']
                    })
                res = self.neighbors(current, fringe, prev)
                del fringe[0]
                self.max_fringe_size=max(self.max_fringe_size, len(fringe))
                fringe = sorted(fringe, key=lambda x: x['algo'])
                self.log_successors(res)
                self.log_fringe(fringe)
        self.generate_results(final_state)

    def solve_a_star(self):
        print("Solving using A* Search")
        res = 0
        fringe=[] 
        start_idx = self.start_grid.index(0)
        prev = None
        fringe.append(
            {
                'node':self.start_grid, 
                'ind':start_idx, 
                'val':0, 
                'parent':None, 
                'move':None, 
                'depth':0, 
                'cost':0, 
                'algo':self.heuristic(self.start_grid),
                'prev': None
            })
        final_state=None
        
        while len(fringe)>0:

            self.nodes_popped+=1
            current = fringe[0]
            if self.dump_flag:
                successor_str = self.get_successors(current, prev)
                self.write_log(f"Generating successors to {successor_str}")
                prev = successor_str
            if current['node']==self.goal_grid:
                self.closed_steps.append(
                    {
                        'node': current['node'], 
                        'ind':current['ind'], 
                        'val':current['val'], 
                        'parent':current['parent'], 
                        'move':current['move'], 
                        'depth':current['depth'], 
                        'cost':current['cost'], 
                        'algo':current['algo']
                    })
                self.log_successors(res)
                final_state=copy.deepcopy(current)
                break
            elif self.is_closed(current): 
                self.max_fringe_size=max(self.max_fringe_size, len(fringe))
                self.log_no_successors(fringe[0]['node'])
                self.log_fringe(fringe)
                del fringe[0]
                
            else:  
                self.closed_steps.append(
                    {
                        'node': current['node'], 
                        'ind':current['ind'], 
                        'val':current['val'], 
                        'parent':current['parent'], 
                        'move':current['move'], 
                        'depth':current['depth'], 
                        'cost':current['cost'], 
                        'algo':current['algo']
                    })
                res = self.neighbors(current, fringe, prev )
                del fringe[0]
                self.max_fringe_size=max(self.max_fringe_size, len(fringe))
                fringe = sorted(fringe, key=lambda x: x['algo'])
                self.log_successors(res)
                self.log_fringe(fringe)
        self.generate_results(final_state)
        
def main():
    if len(sys.argv) < 3:
        print("Usage: python3 expense_8_puzzle.py <start-file> <goal-file> <method> <dump-flag>")
        return

    start_file = sys.argv[1]
    goal_file = sys.argv[2]

    method = "A*"  # Default method is A* Search
    dump_flag = False  # Default dump_flag is False

    if len(sys.argv) >= 4:
        if sys.argv[3].upper() in ("BFS","UCS","GREEDY"):
            method = sys.argv[3].upper()
        if sys.argv[3].lower() in ("true", "false"):
            dump_flag = sys.argv[3].lower() == "true"
    if len(sys.argv) >= 5:
        dump_flag = sys.argv[4].lower() == "true"

    puzzle_instance = Puzzle(start_file, goal_file, method, dump_flag)

    print(f"Start File: {puzzle_instance.start_file}")
    print(f"Goal File: {puzzle_instance.goal_file}")
    print(f"Method: {puzzle_instance.method}")
    print(f"Dump Flag: {puzzle_instance.dump_flag}")

    if puzzle_instance.method == "BFS":
        puzzle_instance.solve_bfs()
    elif puzzle_instance.method == "UCS":
        puzzle_instance.solve_ucs()
    elif puzzle_instance.method == "GREEDY":
        puzzle_instance.solve_greedy()
    else:
        puzzle_instance.solve_a_star()

if __name__ == "__main__":
    main()
