"""Aggregate answer CSV files by index with validation and sorted SOA values."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

EXPECTED_HEADER = ["Index", "Trial", "SOA", "Answer"]
OUTPUT_HEADER = ["Subject", "Session", "index", "Trial", "SOA", "Answer"]
FILENAME_PATTERN = re.compile(
    r"^(?P<index>\d+)_"
    r"(?P<subject>[A-Za-z]+)_"
    r"(?P<run>\d+)_answer\.csv$"
)


class AggregationError(Exception):
    """Raised when an input file fails validation."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Combine *_answer.csv files by index with SOA sorted ascending."
    )
    parser.add_argument(
        "inputs",
        nargs="*",
        help="Paths to input CSV files following the naming convention. "
        "If omitted, a file picker will open.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="aggregated_answers.csv",
        help="Output CSV file path (default: aggregated_answers.csv).",
    )
    return parser.parse_args()


def validate_filename(path: Path) -> Tuple[int, str, int]:
    match = FILENAME_PATTERN.match(path.name)
    if not match:
        raise AggregationError(
            f"File name '{path.name}' does not match "
            "[index]_[subject]_[sequence]_answer.csv"
        )
    index = int(match.group("index"))
    subject = match.group("subject")
    run = int(match.group("run"))
    return index, subject, run


def read_answer_file(path: Path, subject_index: int, session_number: int) -> List[Dict[str, str]]:
    try:
        with path.open(newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            if reader.fieldnames != EXPECTED_HEADER:
                raise AggregationError(
                    f"{path}: header must be exactly {EXPECTED_HEADER}, "
                    f"found {reader.fieldnames}"
                )

            records: List[Dict[str, str]] = []
            for lineno, row in enumerate(reader, start=2):
                if not row:
                    continue

                try:
                    row_index = int(row["Index"])
                except ValueError:
                    raise AggregationError(
                        f"{path}:{lineno} Index must be an integer, found {row['Index']!r}"
                    ) from None

                try:
                    soa_value = float(row["SOA"])
                except ValueError:
                    raise AggregationError(
                        f"{path}:{lineno} SOA must be numeric, found {row['SOA']!r}"
                    ) from None

                converted_row = {
                    "Subject": str(subject_index),
                    "Session": str(session_number),
                    "index": str(row_index),
                    "Trial": row["Trial"],
                    "SOA": row["SOA"],
                    "Answer": row["Answer"],
                }

                records.append(converted_row)

            if not records:
                raise AggregationError(f"{path} is empty after the header.")
            return records
    except FileNotFoundError as exc:
        raise AggregationError(f"File not found: {path}") from exc


def normalize_path(path_like: str | Path) -> Path:
    return Path(path_like).expanduser()


def select_input_files() -> List[Path]:
    try:
        import tkinter as tk
        from tkinter import filedialog
    except ImportError as exc:
        raise AggregationError(
            "tkinter is required for the file picker but is not available."
        ) from exc

    root = tk.Tk()
    root.withdraw()
    root.update()
    selection = filedialog.askopenfilenames(
        title="Select answer CSV files",
        filetypes=(
            ("Answer CSV", "*_answer.csv"),
            ("CSV files", "*.csv"),
            ("All files", "*"),
        ),
    )
    root.destroy()
    return [normalize_path(path) for path in selection]


def select_output_file(default_name: str, initial_dir: Optional[Path] = None) -> Optional[Path]:
    try:
        import tkinter as tk
        from tkinter import filedialog
    except ImportError as exc:
        raise AggregationError(
            "tkinter is required for the file picker but is not available."
        ) from exc

    root = tk.Tk()
    root.withdraw()
    root.update()
    options = {
        "title": "Save aggregated CSV as",
        "initialfile": default_name,
        "defaultextension": ".csv",
        "filetypes": (("CSV files", "*.csv"), ("All files", "*")),
    }
    if initial_dir is not None:
        options["initialdir"] = str(initial_dir)

    selection = filedialog.asksaveasfilename(**options)
    root.destroy()
    if not selection:
        return None
    return normalize_path(selection)


def select_output_directory(initial_dir: Optional[Path] = None) -> Optional[Path]:
    try:
        import tkinter as tk
        from tkinter import filedialog
    except ImportError as exc:
        raise AggregationError(
            "tkinter is required for the file picker but is not available."
        ) from exc

    root = tk.Tk()
    root.withdraw()
    root.update()
    options = {"title": "Select folder for aggregated CSV files"}
    if initial_dir is not None:
        options["initialdir"] = str(initial_dir)
    selection = filedialog.askdirectory(**options)
    root.destroy()
    if not selection:
        return None
    return normalize_path(selection)


def determine_default_output_name(subject_indices: List[int]) -> str:
    distinct = sorted(set(subject_indices))
    if len(distinct) == 1:
        return f"{distinct[0]}.csv"
    return "aggregated_answers.csv"


def main() -> int:
    args = parse_args()
    if args.inputs:
        input_paths = [normalize_path(path) for path in args.inputs]
    else:
        input_paths = select_input_files()
    if not input_paths:
        raise AggregationError("No input files were selected.")

    print("Aggregating from:")
    for path in input_paths:
        print(f"  {path.resolve()}")

    aggregated: Dict[int, List[Dict[str, str]]] = defaultdict(list)
    subject_order: List[int] = []

    for path in input_paths:
        try:
            subject_index, _, session_number = validate_filename(path)
        except AggregationError as exc:
            print(f"Skipping {path}: {exc}")
            continue

        if subject_index not in aggregated:
            subject_order.append(subject_index)

        try:
            records = read_answer_file(path, subject_index, session_number)
        except AggregationError as exc:
            raise AggregationError(f"{path}: {exc}") from exc

        aggregated[subject_index].extend(records)

    if not aggregated:
        raise AggregationError("No data rows found in the provided files.")

    if not subject_order:
        raise AggregationError(
            "No valid *_answer.csv files were provided after filtering."
        )

    multi_subject = len(subject_order) > 1
    written_paths: List[Path] = []

    if multi_subject:
        if args.output != "aggregated_answers.csv":
            output_base = normalize_path(args.output)
        elif args.inputs:
            output_base = input_paths[0].parent.resolve()
        else:
            chosen_dir = select_output_directory(initial_dir=input_paths[0].parent)
            if chosen_dir is None:
                raise AggregationError("Output directory selection was cancelled.")
            output_base = chosen_dir.resolve()

        if output_base.exists() and not output_base.is_dir():
            raise AggregationError(
                f"Output path {output_base} must be a directory when combining multiple indices."
            )
        output_base.mkdir(parents=True, exist_ok=True)

        print(f"Saving to directory: {output_base}")

        for index in subject_order:
            rows = aggregated[index]
            file_path = output_base / f"{index}.csv"
            try:
                with file_path.open("w", newline="", encoding="utf-8") as outfile:
                    writer = csv.DictWriter(outfile, fieldnames=OUTPUT_HEADER)
                    writer.writeheader()
                    for row in rows:
                        writer.writerow(row)
            except PermissionError as exc:
                raise AggregationError(
                    f"Could not write to {file_path}: {exc.strerror}"
                ) from exc
            except OSError as exc:
                raise AggregationError(
                    f"Could not write to {file_path}: {exc.strerror}"
                ) from exc
            written_paths.append(file_path)
    else:
        default_output_name = determine_default_output_name(subject_order)
        if args.output != "aggregated_answers.csv":
            output_path = normalize_path(args.output)
        elif args.inputs:
            output_path = (input_paths[0].parent / default_output_name).resolve()
        else:
            chosen = select_output_file(
                default_name=default_output_name,
                initial_dir=input_paths[0].parent,
            )
            if chosen is None:
                raise AggregationError("Output file selection was cancelled.")
            output_path = chosen.resolve()

        print(f"Saving to file: {output_path}")

        if output_path.exists() and output_path.is_dir():
            raise AggregationError(
                f"Output path {output_path} is a directory; please choose a file name."
            )

        rows = aggregated[subject_order[0]]

        try:
            with output_path.open("w", newline="", encoding="utf-8") as outfile:
                writer = csv.DictWriter(outfile, fieldnames=OUTPUT_HEADER)
                writer.writeheader()
                for row in rows:
                    writer.writerow(row)
        except PermissionError as exc:
            raise AggregationError(
                f"Could not write to {output_path}: {exc.strerror}"
            ) from exc
        except OSError as exc:
            raise AggregationError(
                f"Could not write to {output_path}: {exc.strerror}"
            ) from exc
        written_paths.append(output_path)

    print("Wrote aggregated data to:")
    for path in written_paths:
        print(f"  {path}")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except AggregationError as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
