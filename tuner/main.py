import signal
import sys

import click
from halo import Halo
from natsort import natsorted, ns

from tuner.environment import Environment
from tuner.helpers import (
    check_restarting,
    create_config_files,
    get_time_config,
    remove_old_results,
    run_lc0_command,
)
from tuner.results import get_results_recorder


@click.command()
@click.option(
    "--results",
    type=click.Choice(["xlsx", "csv"]),
    default="xlsx",
    show_default=True,
    help="Results file format",
)
def main():
    env = Environment()
    signal.signal(signal.SIGINT, ctrlc_signal_handler)
    check_restarting_state(env)

    seconds_per_move = get_time_config(env.options)
    recorder = get_results_recorder(env)

    print("Press ctrl+c to stop at any time")

    spinner = Halo(text="Running Lc0", spinner="dots")
    for config_file in natsorted(env.configs_path.glob("*.config"), alg=ns.PATH):
        relative_path = str(config_file.relative_to(env.lc0_path.parent))
        spinner.start(f"Running Lc0 - {relative_path}")
        results = run_lc0_command(
            env.lc0_path, env.configs_path / config_file, seconds_per_move
        )

        recorder.record_result(results, config_file)
        spinner.stop()
    else:
        print("Tuning completed")


def ctrlc_signal_handler(signal, frame):
    sys.exit(1)


def check_restarting_state(environment: Environment):
    restart_point = check_restarting(environment.configs_path)
    if not restart_point:
        create_config_files(environment.configs_path, environment.options_path)
        remove_old_results(environment.results_path)


if __name__ == "__main__":
    main()
