from mlx import Mlx

TILE  = 32   # taille d'une case en pixels
WALL  = 0x55FFFF00
FLOOR = 0xFFF08080
PLAYER= 0xFFFF00FF

maze_map = [
    [1,1,1,1,1],
    [1,0,0,0,1],
    [1,0,1,0,1],
    [1,0,0,0,1],
    [1,1,1,1,1],
]  # 1 = mur, 0 = couloir

def put_pixel(data, x, y, sl, bpp, color):
    data[offset: offset + 4] = color.to_bytes(4, 'little')

def render(state):
    data, bpp, sl, _ = mlx.mlx_get_data_addr(state['img'])
    for row in range(len(maze_map)):
        for col in range(len(maze_map[0])):
            color = WALL if maze_map[row][col] == 1 else FLOOR
            for dy in range(TILE):
                for dx in range(TILE):
                    put_pixel(data, col*TILE+dx, row*TILE+dy, sl, bpp, color)
    # Dessine le joueur
    px, py = state['px'], state['py']
    for dy in range(4, TILE-4):
        for dx in range(4, TILE-4):
            put_pixel(data, px*TILE+dx, py*TILE+dy, sl, bpp, PLAYER)
    mlx.mlx_put_image_to_window(mlx_ptr, win_ptr, state['img'], 0, 0)

def on_key(keycode, state):
    moves = {65362: (0,-1), 65364: (0,1), 65361: (-1,0), 65363: (1,0)}
    if keycode == 65307: mlx.mlx_loop_exit(mlx_ptr); return
    if keycode in moves:
        dx, dy = moves[keycode]
        nx, ny = state['px']+dx, state['py']+dy
        if maze_map[ny][nx] == 0:  # pas un mur
            state['px'], state['py'] = nx, ny
            render(state)

mlx = Mlx()
mlx_ptr = mlx.mlx_init()
W, H = len(maze_map[0])*TILE, len(maze_map)*TILE
win_ptr = mlx.mlx_new_window(mlx_ptr, W, H, "Maze")
img_ptr = mlx.mlx_new_image(mlx_ptr, W, H)
state = {'img': img_ptr, 'px': 1, 'py': 1}
render(state)
mlx.mlx_key_hook(win_ptr, on_key, state)
mlx.mlx_hook(win_ptr, 17, 0, lambda p: mlx.mlx_loop_exit(mlx_ptr), state)
mlx.mlx_loop(mlx_ptr)