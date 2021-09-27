import sys
import queue
import time
import datetime


def bfs():
    start= time()
    node_generated=0
    visited=[]
    if isWinning(state):
        end=time()
        return state
    node = State(BOXES, PLAYER, 0, None)
    node_generated+=1
    q=queue.Queue()
    q.put(node)
    solving=True
    while solving:
        if q.empty():
            print("No solution")
        else :
            curr_node=q.get()
            neighbors = [handleMoves(current, move) for move in moves]
        for state in neighbors:
            if (state == None):    
                continue
            elif ((set(state.boxes), state.player) in visited):  
                continue
            else:
                visited.append((set(state.boxes), state.player))
                q.put(state)
    return None
