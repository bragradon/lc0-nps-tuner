import json
import platform
import re
import shutil
import sys
from io import StringIO
from pathlib import Path

import pexpect
import pexpect.popen_spawn
from tqdm import tqdm

LINE_REGEX = re.compile(
    r"info depth (?P<depth>\d+) seldepth (?P<seldepth>\d+) time (?P<time>\d+).*nps (?P<nps>\d+)"
)
MOVE_TIME = 60
PROCESSING_TIME = 63


def check_restarting(config_folder):
    if len(list((config_folder / "processed").glob("*.config"))) == 0:
        return False

    want_to_restart = input(
        "Do you want to restart from where the program left off? y/n/q "
    )
    if want_to_restart in ["q", "Q"]:
        sys.exit(0)
    return want_to_restart in ["y", "Y"]


def create_config_files(config_folder, options_file):
    prepare_folder(config_folder)
    options = get_config_options(options_file)
    flags = list(options.keys())
    config_options = build_config_options(flags, options, {})
    write_config_files(config_folder, config_options)


def remove_old_results(results_file):
    if results_file.exists():
        results_file.unlink()


def prepare_folder(folder: Path):
    if folder.exists():
        shutil.rmtree(str(folder.absolute()))
    Path.mkdir(folder.absolute(), exist_ok=True)
    Path.mkdir((folder / "processed").absolute(), exist_ok=True)


def get_config_options(config_file):
    config = json.load(open(config_file.absolute()))
    return config["options"]


def get_time_config(options):
    try:
        return options["seconds_per_move"]
    except KeyError:
        print("options.json is missing the 'seconds_per_move' parameter")
        sys.exit(1)


def build_config_options(flags, options, result):
    if not len(flags):
        return [result]

    calls = []
    flag = flags.pop()
    for option in options[flag]:
        result[flag] = option
        [
            calls.append(i.copy())
            for i in build_config_options(flags.copy(), options, result)
        ]

    return calls


def write_config_files(config_folder, config_options):
    for i, config_values in enumerate(
        tqdm(config_options, "Generating Configs", leave=False)
    ):
        with open((config_folder / f"{i+1}.config").absolute(), "w") as f:
            for flag, value in config_values.items():
                f.write(f"--{flag}={value}\n")


def run_lc0_command(lco: Path, config_file: Path, seconds_per_move):
    if platform.system() == "Windows":
        cmd = f"{str(lco.absolute())} -c {str(config_file.relative_to(lco.parent))}"
        child = pexpect.popen_spawn.PopenSpawn(
            cmd, timeout=max(PROCESSING_TIME, seconds_per_move * 2), encoding="utf-8"
        )
    else:
        child = pexpect.spawn(
            str(lco.absolute()),
            ["-c", str(config_file.relative_to(lco.parent))],
            timeout=max(PROCESSING_TIME, seconds_per_move * 2),
            encoding="utf-8",
        )

    output = StringIO()
    child.logfile = output
    try:
        child.sendline(f"go movetime {seconds_per_move * 1000}")
        child.expect("bestmove")
        child.sendline("quit")
        child.expect(pexpect.EOF)
    except pexpect.exceptions.TIMEOUT:
        pass
    except Exception as e:
        print()
        print(child.proc.args)
        print(output.getvalue())
        raise

    for line in output.getvalue().splitlines()[::-1]:
        match = LINE_REGEX.match(line)
        if match:
            return match
