import platform
import shutil
import signal
import sys
from pathlib import Path

from halo import Halo
from natsort import natsorted, ns

from tuner.helpers import (
    create_config_files,
    run_lc0_command,
    check_restarting,
    get_time_config,
    remove_old_results,
    get_results_excel,
    add_results_workbook_headers,
    add_results_to_sheet,
)

APP_DIR = Path().cwd()

if platform.system() == "Windows":
    LC0_PATH = Path(APP_DIR) / "lc0.exe"
else:
    LC0_PATH = Path(APP_DIR) / "lc0"

if not LC0_PATH.exists():
    print("Can't find lc0")
    sys.exit(1)

OPTIONS_FILE = Path(APP_DIR) / "options.json"
CONFIG_DIR = Path(APP_DIR) / "configs"
RESULTS_FILE = Path(APP_DIR) / "results.xlsx"


def signal_handler(signal, frame):
    sys.exit(1)


def main():
    signal.signal(signal.SIGINT, signal_handler)
    restart_point = check_restarting(CONFIG_DIR)
    if not restart_point:
        create_config_files(CONFIG_DIR, OPTIONS_FILE)
        remove_old_results(RESULTS_FILE)

    seconds_per_move = get_time_config(OPTIONS_FILE)
    wb, ws = get_results_excel(RESULTS_FILE)
    add_results_workbook_headers(ws)
    wb.save(filename=RESULTS_FILE.name)

    print("Press ctrl+c to stop at any time")

    spinner = Halo(text="Running Lc0", spinner="dots")
    for config_file in natsorted(CONFIG_DIR.glob("*.config"), alg=ns.PATH):
        relative_path = str(config_file.relative_to(LC0_PATH.parent))
        spinner.start(f"Running Lc0 - {relative_path}")
        results = run_lc0_command(LC0_PATH, CONFIG_DIR / config_file, seconds_per_move)

        add_results_to_sheet(ws, results, str(config_file.name))
        wb.save(filename=RESULTS_FILE.name)

        shutil.move(str(config_file.absolute()), config_file.parent / "processed")
        spinner.stop()


if __name__ == '__main__':
    main()
