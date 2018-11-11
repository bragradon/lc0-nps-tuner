"""
Preflight Environment checkers
"""
import json
import os
import platform
import sys
from pathlib import Path

from tuner.options_template import OPTIONS_JSON_TEMPLATE


class Environment:
    def __init__(self):
        if not self.options_path.exists():
            with open(self.options_path.absolute()) as f:
                f.write(OPTIONS_JSON_TEMPLATE)
                print("Options file missing - creating a new one. Please review")
                sys.exit(1)

        # Check Required options
        _ = [self.seconds_per_move, self.results_file_format]

    @property
    def app_path(self) -> Path:
        if not hasattr(self, "_app_path"):
            if getattr(sys, "frozen", False):
                self._app_path = Path().cwd()
            else:
                self._app_path = Path(os.path.dirname(os.path.abspath(__file__)))

        return self._app_path

    @property
    def lc0_path(self) -> Path:
        if not hasattr(self, "_lc0_path"):

            if platform.system() == "Windows":
                self._lc0_path = Path(self.app_path) / "lc0.exe"
            else:
                self._lc0_path = Path(self.app_path) / "lc0"

            if not self._lc0_path.exists():
                print(
                    "Unable to find lc0 executable - "
                    "It should be in the same directory as this program"
                )
                sys.exit(1)

        return self._lc0_path

    @property
    def options_path(self) -> Path:
        if not hasattr(self, "_options_path"):
            self._options_path = Path(self.app_path) / "options.json"

        return self._options_path

    @property
    def configs_path(self) -> Path:
        if not hasattr(self, "_configs_path"):
            self._configs_path = Path(self.app_path) / "configs"

        return self._configs_path

    @property
    def results_path(self) -> Path:
        if not hasattr(self, "_results_path"):
            self._results_path = Path(self.app_path) / self.results_filename

        return self._results_path

    @property
    def results_filename(self) -> str:
        return f"results.{self.results_file_format}"

    ####### Options ########

    @property
    def options(self) -> dict:
        if not hasattr(self, "_options"):
            path: str = self.options_path.absolute()
            self._options: dict = json.load(open(path))

        return self._options

    @property
    def seconds_per_move(self) -> str:
        try:
            return self.options["seconds_per_move"]
        except KeyError:
            print("options.json is missing the 'seconds_per_move' parameter")
            sys.exit(1)

    @property
    def results_file_format(self):
        try:
            results_filetype = self.options.get("results_file_format")
        except KeyError:
            print(
                'options.json is missing the "results_file_format" parameter'
                " - it must be one of: xlsx, csv"
            )
            sys.exit(1)

        if results_filetype not in ("xlsx", "csv"):
            print("options.json is not set correctly - it must be one of: xlsx, csv")

        return results_filetype
