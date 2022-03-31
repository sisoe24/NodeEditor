from importlib.resources import path
import os
import pathlib

current_dir = os.path.dirname(__file__)
p = pathlib.Path(current_dir)

# __all__ = [file for file in p.glob('*.py') if file.name.startswith('node')]
