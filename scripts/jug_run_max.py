import click
from psutil import cpu_count
from subprocess import call
import time
from tqdm import tqdm


@click.command()
@click.argument('command')
def main(command):
    call(['tmux', 'new', '-s', 'credibility allocation', '-d'])

    for _ in tqdm(xrange(cpu_count() - 2), desc='Launching processes'):
        call(['tmux', 'new-window', command])
        time.sleep(10)
    # ' jug execute code/scripts/multicore_task.py data/filtered_tasks.csv'

if __name__ == '__main__':
    main()
