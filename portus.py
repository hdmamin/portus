import click
from collections import defaultdict
import json


@click.command(context_settings={'help_option_names': ['--help', '-h']})
@click.argument('file')
@click.option('--overwrite', '-o', required=False, is_flag=True, default=False)
def portus(file, overwrite):
    """Define a group of commands."""
    with open(file, 'r') as f:
        cells = [cell['source'] for cell in json.load(f)['cells']
                 if cell['cell_type'] == 'code' and cell['source']]
    files = parse_cells(cells)
    write_files(files, overwrite)


def parse_cells(cells):
    # Create dict mapping output filename to list of code chunks.
    files = defaultdict(list)
    for cell in cells:
        if cell[0].startswith('# PORT'):
            cmd = cell[0].split()
            if len(cmd) != 3:
                click.echo(f'Incomplete port command: {cell[0]}{cell[1]}...\n')
                continue
            files[cmd[-1]].append(''.join(cell[1:]))
    return files


def write_files(files, overwrite):
    # Append code chunks to files.
    if overwrite:
        mode = 'w'
    else:
        mode = 'a'
    for file, chunks in files.items():
        with open(file, mode) as f:
            f.write('\n\n\n'.join(chunks) + '\n')

    # TO DO:
    # -refactor into mult funcs?
    # -maybe more elegant way to handle overwrite flag
    # -appending to file lacks empty line after prev last line
    # -handle case where we want file to be in diff dir
    # -add usr/bin... to first line?
    # -add imports cell?


if __name__ == '__main__':
    portus()
