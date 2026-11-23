import os
import sys

# Garante que o diretório raiz do projeto esteja no caminho de importação do Python
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app

# O Vercel Python runtime espera a variável 'app' no escopo global
if __name__ == '__main__':
    app.run()
