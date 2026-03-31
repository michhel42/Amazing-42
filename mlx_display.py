#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   mlx_display.py                                       :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: vihardy <vihardy@student.42.fr>              +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/03/31 11:36:49 by vihardy             #+#    #+#            #
#   Updated: 2026/03/31 21:07:41 by vihardy            ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from mlx import Mlx
from typing import Tuple, Any
from enum import Enum


class Color(str, Enum):
    RED         = '#FF0000FF'
    GREEN       = "#00FF00FF"
    BLUE        = "#0000FFFF"
    WHITE       = "#FFFFFFFF"
    BLACK       = "#000000FF"
    TRANSPARENT = "#00000000"
    ORANGE      = "#FFA500FF"
    BG          = "#1A0A00FF"
    WALL        = "#FF6B2BFF"
    TREE        = "#FFE066FF"
    BG1          = "#0D1117FF"
    WALL1        = "#00FF41FF"
    TREE1        = "#39FF14FF"

def color_to_bytes(color: Color) -> bytes:
    hex_str = color.value.lstrip('#')

    r = int(hex_str[0:2], 16)
    g = int(hex_str[2:4], 16)
    b = int(hex_str[4:6], 16)
    a = int(hex_str[6:8], 16)

    return bytes([b, g, r, a])  # adapte selon ton format

class Img:
    def __init__(self, mlx, mlx_ptr: Any, width: int, height: int) -> None:
        self.mlx = mlx
        self.img = self.mlx.mlx_new_image(mlx_ptr, width, height)
        self.mlx_ptr = mlx_ptr
        self.width = width
        self.height = height
        self.data, self.bpp, self.sl, self.endian = self.mlx.mlx_get_data_addr(self.img)
        self.iformat = 0

    def coord_to_offset(self, coord):
        return coord[1] * self.sl + coord[0] * (self.bpp // 8)

    def put_pixel(self, coord: Tuple[int, int], color: Color) -> None:
        offset = self.coord_to_offset(coord)
        self.data[offset:offset + 4] = color_to_bytes(color)

    def draw_line_HV(self, start: Tuple[int, int], end: Tuple[int, int], color: Color) -> None:
        if start[0] == end[0]:
            x = start[0]
            for y in range(start[1], end[1] + 1):
                self.put_pixel((x, y), color)
        elif start[1] == end[1]:
            y = start[1]
            for x in range(start[0], end[0] + 1):
                self.put_pixel((x, y), color)
        else:
            raise ValueError("Start and End are not on the same line (horizontal or vertical)")

    def draw_square(self, start: Tuple[int, int], width: int, height: int, color: Color) -> None:
        if start[0] + width > self.width or start[1] + height > self.height:
            raise ValueError("The Square cant fit in the image")
        self.draw_line_HV(start, (start[0] + width ,start[1]), color)
        self.draw_line_HV(start, (start[0] ,start[1] + height), color)
        self.draw_line_HV((start[0] + width, start[1]), (start[0] + width, start[1] + height), color)
        self.draw_line_HV((start[0], start[1] + height), (start[0] + width, start[1] + height), color)

    def fill_square(self, start: Tuple[int, int], width: int, height: int, color: Color) -> None:
        for y in range(start[1], start[1] + height):
            for x in range(start[0], start[0] + width):
                self.put_pixel((x, y), color)

    def destroy(self) -> None:
        self.mlx.mlx_destroy_image(self.mlx_ptr, self.img)

class Display:
    mlx = Mlx()
    def __init__(self, width: int, height: int, name: str) -> None:
        self.mlx_ptr = self.mlx.mlx_init()
        self.win_ptr = self.mlx.mlx_new_window(self.mlx_ptr, width, height, name)
        self.height = height
        self.width = width

    def add_img(self, img: Img, coord: Tuple[int, int]) -> None:
        self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr, img, coord[0], coord[1])

    def run_win(self) -> None:
        self.mlx.mlx_loop(self.mlx_ptr)

    def clear(self) -> None:
        self.mlx.mlx_clear_window(self.mlx_ptr, self.win_ptr)

    def close_win(self) -> None:
        self.mlx.mlx_destroy_window(self.mlx_ptr, self.win_ptr)
        self.mlx.mlx_loop_exit(self.mlx_ptr)


if __name__ == "__main__":
    win = Display(500, 800, "test")
    img = Img(win.mlx_ptr, 500, 800)
    img.draw_square((30, 40), 200, 150, Color.RED)
    win.add_img(img.img, (0, 0))
    win.run_win()