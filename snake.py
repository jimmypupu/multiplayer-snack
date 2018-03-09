import sys
import math
import random
import copy


player_count = int(input())  # the number of at the start of this game
my_id = int(input())  # your bot's id

MOVE = {
    'DOWN': [0, 1],
    'LEFT': [-1, 0],
    'RIGHT': [1, 0],
    'UP': [0, -1],
}

def move_point(x, y, move):
    if move is not None:
        x = (x + MOVE[move][0] + 30) % 30
        y = (y + MOVE[move][1] + 15) % 15
    return x, y

class Board():
    def __init__(self, my_id, player_count):
        self.board = [[-1 for _ in range(15)] for _ in range(30)]
        self.my_id = my_id
        self.prev = ''
        self.prev_pos = [[-1, -1] for i in range(player_count)]
        self.current = [[0, 0] for i in range(player_count)]
        self.alive = [i for i in range(player_count)]
        self.helper_bots = -1
        self.rounds = 0

    def update(self, x, y, player_id):
        if self.current[player_id] == self.prev_pos[player_id] and player_id in self.alive:
            self.alive.pop(self.alive.index(player_id))
        self.board[x][y] = player_id

    def danger(self):
        for i in self.alive:
            if i == self.my_id:
                continue
            x = self.current[i][0]
            y = self.current[i][1]
            if self.board[(x+1)%30][y] == -1:
                self.board[(x+1)%30][y] = 5
            if self.board[(x+29)%30][y] == -1:
                self.board[(x+29)%30][y] = 5
            if self.board[x][(y+1)%15] == -1:
                self.board[x][(y+1)%15] = 5
            if self.board[x][(y+14)%15] == -1:
                self.board[x][(y+14)%15] = 5
            
    def remove_danger(self):
        for i in self.alive:
            x = self.current[i][0]
            y = self.current[i][1]
            if self.board[(x+1)%30][y] == 5:
                self.board[(x+1)%30][y] = -1
            if self.board[(x+29)%30][y] == 5:
                self.board[(x+29)%30][y] = -1
            if self.board[x][(y+1)%15] == 5:
                self.board[x][(y+1)%15] = -1
            if self.board[x][(y+14)%15] == 5:
                self.board[x][(y+14)%15] = -1

    def remove(self, x, y):
        self.board[x][y] = -1

    def move(self, pid, move):
        if move == 'DEPLOY':
            self.helper_bots -= 1
            if self.prev != '':
                x, y = self.current[self.my_id][0], self.current[self.my_id][1]
                xx, yy = x, y
                for i in range(30):
                    xx, yy = move_point(xx, yy, self.prev)
                    FLAG = True
                    for j in self.alive:
                        if self.current[j][0] == xx and self.current[j][1] == yy:
                            FLAG = False
                            break
                    if FLAG:
                        if self.board[xx][yy] != -1:
                            self.remove(xx, yy)
                            self.move(self.my_id, self.prev)
                            break
                    else:
                        self.move(self.my_id, self.prev)
                        break
        else:
            self.current[pid][0], self.current[pid][1] = move_point(
                    self.current[pid][0], self.current[pid][1], move)

    def get_score(self):
        x, y = self.current[self.my_id][0], self.current[self.my_id][1]
        if self.board[x][y] != -1:
            return [-999]

        score2 = 0
        for i in self.alive:
            if i == self.my_id:
                continue
            dis = distance(x, y, self.current[i][0], self.current[i][1])
            if dis <= 3:
                score2 += 1
            else:
                score2 += 3/dis
        score2 /= (len(self.alive)-1)
        
        dists = []
        for i in range(player_count):
            if i != my_id:
                dists.append(distance(x, y, self.current[i][0], self.current[i][1]))
            else:
                dists.append(999)
        score0 = int(min(dists) > 1)
        
        player_scores = []
        print(self.alive,file=sys.stderr)
        for i in range(player_count):
            if i not in self.alive:
                r = 0
            else:
                r = reachable_points(self, self.current[i][0], self.current[i][1], i)
            player_scores.append(r)
        score1 = player_scores[my_id] / (sum(player_scores)+1)
        print(player_scores, file=sys.stderr)
        
        print(self.prev_pos[my_id], file = sys.stderr)
        score3 = 0
        if self.rounds < 35:
            if self.board[(x+1)%30][y] != -1 and self.board[(x+1)%30][y] != self.my_id  and ((x+1)%30 != self.prev_pos[my_id][0] and y != self.prev_pos[my_id][1]):
                score3 = 1
            elif self.board[(x+29)%30][y] != -1 and self.board[(x+29)%30][y] != self.my_id  and ((x+29)%30 != self.prev_pos[my_id][0] and y != self.prev_pos[my_id][1]):
                score3 = 1
            elif self.board[x][(y+1)%15] != -1 and self.board[x][(y+1)%15] != self.my_id  and (x != self.prev_pos[my_id][0] and (y+1)%15 != self.prev_pos[my_id][1]):
                score3 = 1
            elif self.board[x][(y+14)%15] != -1 and self.board[x][(y+14)%15] != self.my_id  and (x != self.prev_pos[my_id][0] and (y+14)%15 != self.prev_pos[my_id][1]):
                score3 = 1
            elif self.board[(x+1)%30][(y+1)%15] != -1 and self.board[(x+1)%30][(y+1)%15] != self.my_id:
                score3 = 0.5
            elif self.board[(x+29)%30][(y+1)%15] != -1 and self.board[(x+29)%30][(y+1)%15] != self.my_id:
                score3 = 0.5
            elif self.board[(x+1)%30][(y+14)%15] != -1 and self.board[(x+1)%30][(y+14)%15] != self.my_id:
                score3 = 0.5
            elif self.board[(x+29)%30][(y+14)%15] != -1 and self.board[(x+29)%30][(y+14)%15] != self.my_id:
                score3 = 0.5

        else:
            if self.board[(x+1)%30][y] != -1 and ((x+1)%30 != self.prev_pos[my_id][0] and y != self.prev_pos[my_id][1]):
                score3 = 1
            elif self.board[(x+29)%30][y] != -1 and ((x+29)%30 != self.prev_pos[my_id][0] and y != self.prev_pos[my_id][1]):
                score3 = 1
            elif self.board[x][(y+1)%15] != -1 and (x != self.prev_pos[my_id][0] and (y+1)%15 != self.prev_pos[my_id][1]):
                score3 = 1
            elif self.board[x][(y+14)%15] != -1 and (x != self.prev_pos[my_id][0] and (y+14)%15 != self.prev_pos[my_id][1]):
                score3 = 1
            elif self.board[(x+1)%30][(y+1)%15] != -1:
                score3 = 0.5
            elif self.board[(x+29)%30][(y+1)%15] != -1:
                score3 = 0.5
            elif self.board[(x+1)%30][(y+14)%15] != -1:
                score3 = 0.5
            elif self.board[(x+29)%30][(y+14)%15] != -1:
                score3 = 0.5

            
        score4 = (self.helper_bots/3)
        print(str(score0)+" "+str(score1)+" "+str(score2)+" "+str(score3)+" "+str(score4), file=sys.stderr)
        
        return [score0,1*score1+0.2*score2+0.4*score3+0.8*score4]

def reach_prop(board, occ, x, y, depth, p):
    if p == my_id:
        if depth > 0 and (board.board[x][y] != -1 or occ[x][y] != 0):
            return
    else:
        if depth > 0 and ((board.board[x][y] != -1 and board.board[x][y] != 5) or occ[x][y] != 0):
            return
    occ[x][y] = 1
    if depth > 8:
        return
    for m in ['DOWN', 'LEFT', 'RIGHT', 'UP']:
        xx, yy = move_point(x, y, m)
        reach_prop(board, occ, xx, yy, depth+1, p)

def reachable_points(board, x, y, p):
    ret = 0
    occ = [[0 for _ in range(15)] for _ in range(30)]
    reach_prop(board, occ, x, y, 0, p)
    for i in range(30):
        #ret += sum(occ[i])
        for j in range(15):
            ret += occ[i][j]
    return ret

def distance(x1, y1, x2, y2):
    left_right_dis = abs(x1-x2)
    if left_right_dis > abs(left_right_dis-30):
        left_right_dis = abs(left_right_dis-30)
    up_down_dis = abs(y1-y2)
    if up_down_dis > abs(up_down_dis-15):
        up_down_dis = abs(up_down_dis-15)
    return left_right_dis+up_down_dis

def main():
    board = Board(my_id, player_count)
    while True:
        print("my ID", my_id, file=sys.stderr)
        board.rounds += 1
        print(board.rounds, file=sys.stderr)
        get_input(board)
        
        if board.helper_bots == 0:
            availables = ['DOWN', 'LEFT', 'RIGHT', 'UP']
        else:
            availables = ['DOWN', 'LEFT', 'RIGHT', 'UP', "DEPLOY"]

        board.danger()
        scores = []
        for m in availables:
            print(m, file=sys.stderr)
            tb = copy.deepcopy(board)
            tb.prev_pos = list(board.current)
            tb.move(my_id, m)
            scores.append(tb.get_score())
        if board.prev and board.rounds < 30:
            scores[availables.index(board.prev)][-1] += (30-board.rounds)/30
        #elif board.prev:
            #scores[availables.index(board.prev)][-1] += 0.01
        print(scores, file=sys.stderr)
        board.remove_danger()
        
        candidates = []
        for i in range(len(scores)):
            if scores[i] == max(scores):
                candidates.append(availables[i])
        print(candidates, max(scores), file=sys.stderr)
        if len(candidates) == 1:
            output = candidates[0]
        else:
            if board.prev in candidates:
                output = board.prev
            else:
                output = random.choice(candidates)
        if output != 'DEPLOY':
            board.prev = output
        board.prev_pos = list(board.current)
        print(output)

def get_input(board):

    board.helper_bots = int(input())  # your number of charges left to deploy helper bots
    
    for i in range(player_count):
        # x: your bot's coordinates on the grid (0,0) is top-left
        x, y = [int(j) for j in input().split()]
        board.current[i] = [x, y]
        board.update(x, y, i)

    removal_count = int(input())  # the amount walls removed this turn by helper bots
    for i in range(removal_count):
        # remove_x: the coordinates of a wall removed this turn
        remove_x, remove_y = [int(j) for j in input().split()]
        board.remove(remove_x, remove_y)
        for j in range(player_count):
            if remove_x == board.current[j][0] and remove_y == board.current[j][1]:
                board.board[remove_x][remove_y] = j

if __name__ == '__main__':
    main()
