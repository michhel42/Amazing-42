#!/usr/bin/fish

# Répertoire racine du projet
set ROOT_PROJECT_DIR "."

# Créer un dossier temporaire
set TEMP_DIR (mktemp -d)
echo "Configure temp directory ($TEMP_DIR/)..."
mkdir $TEMP_DIR/local_libs
set -x PREFIX $TEMP_DIR/local_libs
set -x PKG_CONFIG_PATH $PREFIX/lib/pkgconfig $PKG_CONFIG_PATH
set -x CPATH $PREFIX/include $CPATH
set -x LIBRARY_PATH $PREFIX/lib $LIBRARY_PATH
set -x LD_LIBRARY_PATH $PREFIX/lib $LD_LIBRARY_PATH

# Créer un virtualenv Python
echo "Create virtual environment ($ROOT_PROJECT_DIR/.venv)..."
cd $ROOT_PROJECT_DIR
python3 -m venv .venv
source .venv/bin/activate.fish
set _ROOT_PROJECT_DIR (pwd)

# Installer xcb-keysyms (nécessaire pour MLX)
echo "Download and decompress xcb-keysyms..."
cd $TEMP_DIR
wget http://deb.debian.org/debian/pool/main/x/xcb-util-keysyms/xcb-util-keysyms_0.4.1.orig.tar.xz
tar xvf xcb-util-keysyms_0.4.1.orig.tar.xz

echo "Build xcb-keysyms..."
cd xcb-util-keysyms-0.4.1/
./configure --prefix=$TEMP_DIR/local_libs
make
make install

# Télécharger et compiler MinilibX Linux
echo "Clone and build MinilibX..."
cd $TEMP_DIR
git clone https://github.com/42Paris/minilibx-linux.git mlx
cd mlx
make

# Copier la lib dans le virtualenv pour Python
echo "Install libmlx.so into virtualenv..."
cp libmlx.so $_ROOT_PROJECT_DIR/.venv/lib/
set -x LD_LIBRARY_PATH $_ROOT_PROJECT_DIR/.venv/lib $LD_LIBRARY_PATH

# Installer le wrapper Python si le wheel est dispo
if test -f "$_ROOT_PROJECT_DIR/mlx-2.2-py3-none-any.whl"
    echo "Pip install minilibx wrapper..."
    python3 -m pip install ./mlx-2.2-py3-none-any.whl
end

# Nettoyer
echo "Cleaning ($TEMP_DIR/)..."
rm -rf $TEMP_DIR

echo "Done! Remember to keep LD_LIBRARY_PATH pointing to your virtualenv lib:"
echo "set -x LD_LIBRARY_PATH $_ROOT_PROJECT_DIR/.venv/lib \$LD_LIBRARY_PATH"