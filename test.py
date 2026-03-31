from mlx import Mlx

# Hook sur l'événement fermeture


# Boucle principale



def key_handler(key, param):
    print(f"Key: {key}")
    if key == 65307:
        mlx.mlx_destroy_window(mlx_ptr, win_ptr)
        mlx.mlx_loop_exit(mlx_ptr)

def put_pixel(data, x, y, color, size_line):
    index = y * size_line + x * 4
    data[index:index+4] = color.to_bytes(4, 'little')


mlx = Mlx()



mlx_ptr = mlx.mlx_init()
win_ptr = mlx.mlx_new_window(mlx_ptr, 800, 600, "window")
width = 400
length = 300
img = mlx.mlx_new_image(mlx_ptr, width, length)
data, bpp, size_line, endian = mlx.mlx_get_data_addr(img)

for y in range(100, 200):
    for x in range(100, 200):
        put_pixel(data, x, y, 0xFF0000, size_line)

mlx.mlx_put_image_to_window(mlx_ptr, win_ptr, img, 0, 0)

mlx.mlx_key_hook(win_ptr, key_handler, None)  # 65307 = touche ESC

mlx.mlx_string_put(mlx_ptr, win_ptr, 50, 50, 0xFFFFFF, "Hello MLX")

mlx.mlx_loop(mlx_ptr)
