#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   a_maze_ing.py                                        :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: vihardy <vihardy@student.42.fr>              +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/03/27 21:57:31 by vihardy             #+#    #+#            #
#   Updated: 2026/03/28 06:51:57 by vihardy            ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List
from abc import ABC, abstractmethod
import random


class Dir(Enum):
    N = 0
    E = 1
    S = 2
    W = 3

DIR_DELTA = {
    Dir.N: (0, -1),
    Dir.S: (0, 1),
    Dir.E: (1, 0),
    Dir.W: (-1, 0)
}

OPPOSITE = {
    Dir.N: Dir.S,
    Dir.S: Dir.N,
    Dir.E: Dir.W,
    Dir.W: Dir.E,
}

class Axe(Enum):
    V = "vertical"
    H = "horizontal"


class Cell:
    def __init__(self, x: int, y: int) -> None:
        self.x: int = x
        self.y: int = y
        self.wall = 15
        self.active = False

    def add_wall(self, dir: Dir) -> None:
        self.wall = self.wall | (1 << dir.value)

    def rem_wall(self, dir: Dir) -> None:
        self.wall = self.wall & ~(1 << dir.value)

    def inv_wall(self, dir: Dir) -> None:
        self.wall = self.wall ^ (1 << dir.value)

    def hexa_wall(self) -> str:
        return f"{self.wall:01X}"

    def has_wall(self, dir: Dir) -> bool:
        return bool(self.wall & (1 << dir.value))

    def neighbors(self, maze: List[List["Cell"]]) -> Dict[Dir, "Cell"]:
        h = len(maze)
        w = len(maze[0])
        res: Dict[Dir, "Cell"] = {}
        for d, (dx, dy) in DIR_DELTA.items():
            nx, ny = self.x + dx, self.y + dy
            if 0 <= nx < w and 0 <= ny < h:
                res[d] = maze[ny][nx]
        return res


class Maze(ABC):
    def __init__(self, height: int, length: int, seed: int) -> None:
        self.height = height
        self.length = length
        self.seed = seed
        self.maze: List[List[Cell]] = [[Cell(x, y) for x in range(length)] for y in range(height)]

    @property
    def seed(self) -> int:
        return self.__seed

    @seed.setter
    def seed(self, value: int) -> None:
        random.seed(value)
        self.__seed = value

    def gen_output(self, file: str) -> None:
        with open(file, "w") as f:
            for line in self.maze:
                for cell in line:
                    f.write(cell.hexa_wall())
                f.write("\n")

    def show(self) -> None:
        for line in self.maze:
            prt1 = ""
            prt2 = ""
            for cell in line:
                if cell.has_wall(Dir.N):
                    prt1 += "+---"
                else:
                    prt1 += "+   "
                if cell.has_wall(Dir.W):
                    prt2 += "|   "
                else:
                    prt2 += "    "
            prt1 += "+"
            prt2 += "|"
            print(prt1)
            print(prt2)
        prt1 = "".join("+---" for _ in range(self.length)) + "+"
        print(prt1)

    @staticmethod
    def verif_cell(func: Callable[[Cell, Cell, Axe], bool]) -> Callable[[Cell, Cell, Axe], bool]:
        @wraps(func)
        def wrapper(cell1: Cell, cell2: Cell, axe: Axe) -> bool:
            dx = cell2.x - cell1.x
            dy = cell2.y - cell1.y
            if (dx, dy) == (0, 1):
                return func(cell1, cell2, Axe.V)
            if (dx, dy) == (0, -1):
                return func(cell2, cell1, Axe.V)
            if (dx, dy) == (1, 0):
                return func(cell1, cell2, Axe.H)
            if (dx, dy) == (-1, 0):
                return func(cell2, cell1, Axe.H)
            return False
        return wrapper

    @staticmethod
    def connect_cell(cell1: Cell, cell2: Cell) -> bool:
        dx = cell2.x - cell1.x
        dy = cell2.y - cell1.y

        for d, (mx, my) in DIR_DELTA.items():
            if (dx, dy) == (mx, my):
                cell1.rem_wall(d)
                cell2.rem_wall(OPPOSITE[d])
                return True
        return False

    @abstractmethod
    def gen_maze(self) -> Any:
        pass

class DFSRecursive(Maze): # DFS/Prim
    def __init__(self, height: int, length: int, seed: int) -> None:
        super().__init__(height, length, seed)
        self.tree: List[Cell] = []

    def rec_finder(self) -> None:
        neighbors = self.tree[-1].neighbors(self.maze)
        while(len(neighbors)):
            key = random.choice(list(neighbors.keys()))
            if not neighbors[key].active:
                neighbors[key].active = True
                self.connect_cell(self.tree[-1], neighbors[key])
                self.tree.append(neighbors[key])
                self.rec_finder()
            del neighbors[key]
        self.tree.pop(-1)
        
    def gen_maze(self) -> Any:
        x, y = (random.randint(0, self.length - 1),
                random.randint(0, self.height - 1))
        start = self.maze[y][x]
        start.active = True
        self.tree.append(start)
        try:
            self.rec_finder()
        except RecursionError as e:
            print(f"Erreur: {e}")


class DFSIterative(Maze): # DFS/Prim
    def __init__(self, height: int, length: int, seed: int) -> None:
        super().__init__(height, length, seed)
        self.tree: List[Cell] = []

    def iter_finder(self) -> None:
        while (len(self.tree)):
            current = self.tree[-1]
            ngb = current.neighbors(self.maze)
            ngb = {key:value for key, value in ngb.items() if not value.active}
            if len(ngb.items()) == 0:
                self.tree.pop()
            else:
                key = random.choice(list(ngb.keys()))
                ngb[key].active = True
                self.connect_cell(current, ngb[key])
                self.tree.append(ngb[key])
        
    def gen_maze(self) -> Any:
        x, y = (random.randint(0, self.length - 1),
                random.randint(0, self.height - 1))
        start = self.maze[y][x]
        start.active = True
        self.tree.append(start)
        self.iter_finder()


class GrowingTreeIterative(Maze): # Mon favoris!!!
    def __init__(self, height: int, length: int, seed: int) -> None:
        super().__init__(height, length, seed)
        self.tree: List[Cell] = []

    def iter_finder(self) -> None:
        while (len(self.tree)):
            current = random.choice(self.tree)
            ngb = current.neighbors(self.maze)
            ngb = {key:value for key, value in ngb.items() if not value.active}
            if len(ngb.items()) == 0:
                self.tree.remove(current)
            else:
                key = random.choice(list(ngb.keys()))
                ngb[key].active = True
                self.connect_cell(current, ngb[key])
                self.tree.append(ngb[key])
        
    def gen_maze(self) -> Any:
        x, y = (random.randint(0, self.length - 1),
                random.randint(0, self.height - 1))
        start = self.maze[y][x]
        start.active = True
        self.tree.append(start)
        self.iter_finder()








if __name__ == "__main__":
    height, length = int(input("height:")), int(input("length:"))
    seed = int(input("seed:"))
    print("GrowingTreeIterative:")
    maze = GrowingTreeIterative(height, length, seed)
    maze.gen_maze()
    maze.show()
    print("DFSIterative:")
    maze2 = DFSIterative(height, length, seed)
    maze2.gen_maze()
    maze2.show()
    print("DFSRecursive:")
    maze3 = DFSRecursive(height, length, seed)
    maze3.gen_maze()
    maze3.show()