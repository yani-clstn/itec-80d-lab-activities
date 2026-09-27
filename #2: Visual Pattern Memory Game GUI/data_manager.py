import csv
import os
import statistics
from datetime import datetime


class DataManager:
    """
    Handles storage, presentation formatting, and export of interaction data.
    self.results is the real internal data structure (a list of dicts).
    Everything else (Listbox lines, summary stats, CSV rows) is derived from it.
    """

    def __init__(self):
        self.results = []

    def add_record(self, record):
        record["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.results.append(record)

    def clear(self):
        self.results = []

    def listbox_line(self, record):
        return (
            f"R{record['round']} | Grid {record['grid_size']}x{record['grid_size']} | "
            f"Complexity {record['pattern_complexity']} | "
            f"Acc {record['accuracy']:.0f}% | Time {record['completion_time']:.2f}s"
        )

    def summary_stats(self):
        if not self.results:
            return None

        accuracies = [r["accuracy"] for r in self.results]
        times = [r["completion_time"] for r in self.results]
        errors = [r["total_errors"] for r in self.results]
        perfect_complexities = [
            r["pattern_complexity"] for r in self.results if r["accuracy"] == 100.0
        ]

        return {
            "mean_accuracy": statistics.mean(accuracies),
            "median_accuracy": statistics.median(accuracies),
            "mean_time": statistics.mean(times),
            "median_time": statistics.median(times),
            "stdev_time": statistics.stdev(times) if len(times) > 1 else 0.0,
            "min_time": min(times),
            "max_time": max(times),
            "total_errors": sum(errors),
            "error_rate": sum(errors) / len(self.results),
            "max_complexity_success": max(perfect_complexities, default=0),
        }

    def export_csv(self, filepath):
        if not self.results:
            return False

        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        fieldnames = [
            "participant_id", "age_group", "experience_level", "session",
            "round", "grid_size", "pattern_complexity", "display_time_ms",
            "completion_time", "correct_cells", "incorrect_cells", "missed_cells",
            "total_errors", "accuracy", "timestamp",
        ]
        file_exists = os.path.exists(filepath)
        with open(filepath, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            for r in self.results:
                writer.writerow({k: r.get(k, "") for k in fieldnames})
        return True