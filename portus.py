import click
from collections import defaultdict
import json
import os
from pathlib import Path


@click.command(context_settings={'help_option_names': ['--help', '-h']})
@click.argument('file')
@click.option('--overwrite', '-o', required=False, is_flag=True, default=False,
              help="Boolean flag (default False). If passed, it will overwrite"
                   "the existing output file if one exists. Without the flag, "
                   "code will be appended to the end of the file.")
@click.option('--mode', '-m', type=click.Choice(['p', 'a', 'f', 'm']),
              required=False, default='p',
              help="Mode that determines what kind of parsing is done. 'p' is "
                   "for port mode, which only exports cells prefixed by the "
                   "# PORT command. 'a' is for all, which parses all code "
                   "cells. 'f' is for function mode, which only parses cells "
                   "containing functions and classes. 'm' is for main mode "
                   "which parses non-function/class cells (i.e. code that "
                   "might be run if __name__ == '__main__').")
@click.option('--dest_utils', '-du', required=False, default=None,
              help='Output file to save functions to. If not specified, it '
                   'will be the same as the notebook name except with '
                   '"_utils.py" replacing ".ipynb".')
@click.option('--dest_main', '-dm', required=False, default=None,
              help='Output file to save non-function code to. If not '
                   'specified, it will be the same as the notebook name except'
                   ' with a .py extension.')
def portus(file, overwrite, mode, dest_utils, dest_main):
    """Define a group of commands."""
    with open(file, 'r') as f:
        cells = [cell['source'] for cell in json.load(f)['cells']
                 if cell['cell_type'] == 'code' and cell['source']]

    # Populate dict mapping filename to code chunks.
    if mode == 'p':
        files = parse_cells(cells)
    else:
        files = parse_auto(file, mode, cells, dest_utils, dest_main)
    write_files(files, overwrite)


def parse_cells(cells):
    """Find cells with PORT command and store their code.

    Parameters
    -----------
    cells: list
        List of cells obtained within portus command.

    Returns
    --------
    defaultdict[str, list]: Maps filenames to list of strings containing code
        chunks.
    """
    cmd = '# PORT'
    files = defaultdict(list)
    for cell in cells:
        if cell[0].startswith(cmd):
            path = cell[0].lstrip(cmd).rstrip('\n')
            if not path:
                click.echo(f'Incomplete port command: {cell[:2]}...\n')
                continue
            if not cell[1:]:
                click.echo(f'Empty port cell: {cell[:2]}...\n')
                continue
            files[path].append(''.join(cell[1:]))
    return files


def parse_auto(file, mode, cells, dest_utils, dest_main):
    """
    Parameters
    -----------
    file: str
    cells: list
    destination: str, None

    Returns
    --------
    dict[str, list]: Maps filename to
    """
    dest_utils = dest_utils or f"{file.rstrip('.ipynb')}_utils.py"
    dest_main = dest_main or f"{file.rstrip('.ipynb')}.py"

    files = {dest_utils: [],
             dest_main: []}
    for cell in cells:
        is_func = cell[0].startswith('def ') or cell[0].startswith('class ')
        chunk = ''.join(cell)
        if mode in {'a', 'f'} and is_func:
            files[dest_utils].append(chunk)
        elif mode in {'a', 'm'} and not is_func:
            files[dest_main].append(chunk)
    return files


def write_files(files, overwrite):
    """Write code chunks to files.

    Parameters
    -----------
    files: defaultdict[str, list]
        Dict returned by parse_cells function, mapping filename to list of
        strings containing code chunks.
    overwrite: bool
        If True, files will be opened in write mode and old code will be
        overwritten. If False, append new code to the end of the files.
    """
    if overwrite:
        mode = 'w'
    else:
        mode = 'a'

    for file, chunks in files.items():
        os.makedirs(Path(file).parent, exist_ok=True)
        with open(file, mode) as f:
            if mode == 'a':
                f.write('\n\n')
            f.write('\n\n\n'.join(chunks) + '\n')


"""
    TO DO:
    -maybe more elegant way to handle overwrite flag
    -add imports cell automatically?
        -add all cells starting with def automatically? but which file to put in?
        -or auto create 2 files, 1 w/ all funcs and 1 w/ all loose code? maybe
            add another click command that does this (just a simple alternative
            to downloading nb as .py), but also allow more fine-grained control
            if user wants to specify filenames in each cell.
    -handle non functions to have 1 newline after instead of 2?
"""


if __name__ == '__main__':
    portus()
