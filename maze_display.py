#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   maze_display.py                                      :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: vihardy <vihardy@student.42.fr>              +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/03/31 15:37:28 by vihardy             #+#    #+#            #
#   Updated: 2026/03/31 21:34:59 by vihardy            ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from mlx_display import Display, Color, Img
from mlx import Mlx
from typing import Any, Tuple, cast, List
from time import time, sleep


class MazeDisplay(Display):
    def __init__(self, maze, width: int = 3000, height: int = 2000, name: str = "a_maze_ing", maze_color: Color = Color.WALL1) -> None:
        # if width is None or height is None:
        #     self.width, self.height = self.mlx.mlx_get_screen_size(self.mlx_ptr)
        from a_maze_ing import Maze
        super().__init__(width, height, name)
        self.maze: Maze = cast(Maze, maze)
        self.maze_color = maze_color
        self.gen_color = Color.TREE1
        self.bg_color = Color.BG1
        self.img_maze = Img(self.mlx, self.mlx_ptr, width + 1, height + 1)
        self.maze_gen = self.maze.gen_maze()
        next(self.maze_gen)
        self.end = False
        self._current: set = set()
        self._cell_size()
        self.maze_coord = (0, 0)
        self.pass_gen = False

    def _cell_size(self) -> None:
        cell_w = self.width / self.maze.length
        cell_h = self.height / self.maze.height
        self.cell_size = int(min(cell_w, cell_h))

    def _key_handler(self, key: int, param: Any) -> None:
        if key == 65307:
            self.close_win()
        if key == 112:
            self.maze_gen.send(False)
            self.pass_gen = True
        print(f"Key: {key}")


    def _loop_gen(self, param) -> None:
        if self.end:
            return
        try:
            self.maze_gen.send(True)
            self._gen_cell(self.maze.tree)
        except StopIteration:
            self.end = True
            print("stop")
            self._draw_maze()

    def run_win(self) -> None:
        self._draw_init()
        self.mlx.mlx_key_hook(self.win_ptr, self._key_handler, None)
        self.mlx.mlx_loop_hook(self.mlx_ptr, self._loop_gen, None)
        super().run_win()

    def _draw_init(self) -> None:
        cs = self.cell_size
        rows, cols = self.maze.height, self.maze.length
        for y, line in enumerate(self.maze.maze):
            for x, c in enumerate(line):
                sx, sy = x * cs, y * cs
                self.img_maze.fill_square((sx, sy), cs, cs, self.bg_color)
                if x == cols - 1:
                    self.img_maze.draw_line_HV(
                        (sx + cs, sy), (sx + cs, sy + cs), self.maze_color
                    )
                if y == rows - 1:
                    self.img_maze.draw_line_HV(
                        (sx, sy + cs), (sx + cs, sy + cs), self.maze_color
                    )
        self.add_img(self.img_maze.img, (0, 0))

    def _gen_cell(self, tree: List) -> None:
        new_set = set(tree)
        added   = new_set - self._current
        removed = self._current - new_set

        for c in added:
            self._fill_cell(c, self.gen_color)
        for c in removed:
            self._fill_cell(c, self.bg_color)
            self._draw_cell_walls(c)

        self._current = new_set
        for c in added:
            self._draw_cell_walls(c)
        self.add_img(self.img_maze.img, (0, 0))

    def _draw_maze(self) -> None:
        cs = self.cell_size
        for y, line in enumerate(self.maze.maze):
            for x in range(len(line)):
                sx, sy = x * cs, y * cs
                self.img_maze.fill_square((sx, sy), cs, cs, self.bg_color)
        self._draw_all_walls()
        self.add_img(self.img_maze.img, self.maze_coord)

    def _draw_walls(self, cells: set) -> None:
        for y, line in enumerate(self.maze.maze):
            for x, c in enumerate(line):
                if id(c) in cells:
                    self._draw_cell_walls(c)

    def _fill_cell(self, c, color: Color) -> None:
        cs = self.cell_size
        sx, sy = c.x * cs, c.y * cs
        self.img_maze.fill_square((sx, sy), cs, cs, color)


    def _draw_cell_walls(self, c) -> None:
        from a_maze_ing import Dir
        cs = self.cell_size
        sx, sy = c.x * cs, c.y * cs
        rows, cols = self.maze.height, self.maze.length
        if c.has_wall(Dir.N):
            self.img_maze.draw_line_HV((sx, sy), (sx + cs, sy), self.maze_color)
        if c.has_wall(Dir.W):
            self.img_maze.draw_line_HV((sx, sy), (sx, sy + cs), self.maze_color)
        if c.x == cols - 1:
            self.img_maze.draw_line_HV((sx + cs, sy), (sx + cs, sy + cs), self.maze_color)
        if c.y == rows - 1:
            self.img_maze.draw_line_HV((sx, sy + cs), (sx + cs, sy + cs), self.maze_color)

    def _draw_all_walls(self) -> None:
        for line in self.maze.maze:
            for c in line:
                self._draw_cell_walls(c)

    def close_win(self) -> None:
        self.img_maze.destroy()
        return super().close_win()