import click
from psutil import cpu_count
from subprocess import call


@click.command()
@click.argument('command')
def main(command):
    call(['tmux', 'new', '-s', 'credibility allocation', '-d'])

    for _ in xrange(cpu_count()):
        call(['tmux', 'new-window', command])
    # ' jug execute code/scripts/multicore_task.py data/filtered_tasks.csv'

if __name__ == '__main__':
    main()
