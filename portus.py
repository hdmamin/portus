import click
from collections import defaultdict
import json
import os
from pathlib import Path


@click.command(context_settings={'help_option_names': ['--help', '-h']})
@click.argument('file')
@click.option('--overwrite', '-o', required=False, is_flag=True, default=False)
@click.option('--auto', '-a', required=False, is_flag=True, default=False)
@click.option('--destination', '-d', required=False, default=None)
def portus(file, overwrite, auto, destination):
    """Define a group of commands."""
    with open(file, 'r') as f:
        cells = [cell['source'] for cell in json.load(f)['cells']
                 if cell['cell_type'] == 'code' and cell['source']]
    if auto:
        files = parse_functions(file, cells, destination)
    else:
        files = parse_cells(cells)
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


def parse_functions(file, cells, destination):
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
    dest = destination or file.rstrip('ipynb') + 'py'
    files = {dest: []}
    for cell in cells:
        if cell[0].startswith('def ') or cell[0].startswith('class '):
            files[dest].append(''.join(cell))
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
