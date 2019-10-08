import click
from collections import defaultdict
import json


@click.command(context_settings={'help_option_names': ['--help', '-h']})
@click.argument('file')
def portus(file):
    """Define a group of commands."""
    with open(file, 'r') as f:
        cells = [cell['source'] for cell in json.load(f)['cells']
                 if cell['cell_type'] == 'code']

    files = defaultdict(list)
    for cell in cells:
        if cell[0].startswith('# port'):
            files[cell[0].split()[-1]].append(''.join(cell[1:]))
    # print(len(files))
    # print(list(files.items())[0])


if __name__ == '__main__':
    portus()
