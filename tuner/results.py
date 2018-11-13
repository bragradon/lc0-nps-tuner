import csv
import shutil
from pathlib import Path
from re import Match

from openpyxl import Workbook, load_workbook

from tuner.environment import Environment

RECORDERS = {}


def get_results_recorder(environment: Environment) -> "ResultsRecorder":
    return RECORDERS[environment.results_file_format](environment)


def register(filetype):
    def inner(recorder):
        RECORDERS[filetype] = recorder

    return inner


class ResultsRecorder:
    def __init__(self, environment: Environment):
        self.environment = environment

    def record_result(self, *args, **kwargs):
        raise NotImplementedError

    @staticmethod
    def extract_results(results: Match):
        if results is not None:
            depth, seldepth, nps = (
                results.group("depth"),
                results.group("seldepth"),
                results.group("nps"),
            )
        else:
            depth, seldepth, nps = None, None, None

        return depth, seldepth, nps

    def complete_run(self, config_file):
        shutil.move(str(config_file.absolute()), config_file.parent / "processed")


@register("xlsx")
class XLSXResultsRecorder(ResultsRecorder):
    def __init__(self, environment: Environment):
        super().__init__(environment)

        self.wb, self.ws = self.get_results_excel()
        self.add_results_workbook_headers(self.ws)
        self.save_workbook()

    def get_results_excel(self):
        results = self.environment.results_path.absolute()

        try:
            wb = load_workbook(str(results))
        except FileNotFoundError:
            wb = Workbook()

        if "Results" not in wb.sheetnames:
            ws = wb.create_sheet(title="Results", index=0)
        else:
            ws = wb["Results"]

        return wb, ws

    def add_results_workbook_headers(self, worksheet):
        worksheet["A1"] = "LC0 Parameters Run Results"
        worksheet["A2"] = "Filename"
        worksheet["B2"] = "NPS"
        worksheet["C2"] = "DEPTH"
        worksheet["D2"] = "SELDEPTH"

        worksheet["F2"] = "Best NPS"
        worksheet["G2"] = "Filename"
        worksheet["F3"] = "=MAX(B:B)"
        worksheet["G3"] = '=INDIRECT("A" & MATCH(MAX(B:B), B:B, 0))'

        worksheet["F5"] = "Best Depth"
        worksheet["G5"] = "Filename"
        worksheet["F6"] = "=MAX(C:C)"
        worksheet["G6"] = '=INDIRECT("A" & MATCH(MAX(C:C), C:C, 0))'

        worksheet["F8"] = "Best SelDepth"
        worksheet["G8"] = "Filename"
        worksheet["F9"] = "=MAX(D:D)"
        worksheet["G9"] = '=INDIRECT("A" & MATCH(MAX(D:D), D:D, 0))'

    def save_workbook(self):
        self.wb.save(filename=self.environment.results_path.name)

    def record_result(self, results: Match, config_file: Path):
        depth, seldepth, nps = self.extract_results(results)
        config_filename = str(config_file.name)

        row = int(config_filename.split(".")[0])
        self.ws.cell(row + 2, 1, config_filename)
        self.ws.cell(row + 2, 2, int(nps if nps else 0))
        self.ws.cell(row + 2, 3, int(depth if depth else 0))
        self.ws.cell(row + 2, 4, int(seldepth if seldepth else 0))

        self.save_workbook()
        self.complete_run(config_file)


@register("csv")
class CSVResultsRecorder(ResultsRecorder):
    def __init__(self, environment: Environment):
        super().__init__(environment)

        file_path = str(self.environment.results_path.absolute())
        self.file = open(file_path, "w")
        self.writer = csv.DictWriter(
            self.file, fieldnames=("Filename", "NPS", "DEPTH", "SELDEPTH")
        )
        self.writer.writeheader()

    def __del__(self):
        self.file.close()

    def record_result(self, results: Match, config_file: Path):
        depth, seldepth, nps = self.extract_results(results)

        row = {
            "Filename": str(config_file.name),
            "NPS": nps,
            "DEPTH": depth,
            "SELDEPTH": seldepth,
        }
        self.writer.writerow(row)
        self.complete_run(config_file)
