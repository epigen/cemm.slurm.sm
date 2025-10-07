import os
import glob
import datetime
from pathlib import Path


def process_logfile(logfile):
    current_error = False
    error_rule = ""
    categorized = {"Out Of Memory (OOM)": [], "Killed (not OOM)": []}
    file_cache = {}

    with open(logfile, 'r') as file:
        for line in file:
            # Look for the "Error in rule" line
            if line.startswith("Error in rule"):
                error_rule = line.split(":")[0]
                error_rule = error_rule.replace("Error in rule ", "")
                current_error = True

            # When encountering a log line while in error state, process it
            if current_error and line.startswith("    log:"):
                # Extract the second path on the log line
                parts = line.split()
                if len(parts) > 2:
                    log_file = parts[2]
                    if not '/' in log_file:
                        log_file = parts[1]
                    if ".snakemake" in log_file:
                        # Use cache to avoid re-reading the same log file multiple times
                        if log_file in file_cache:
                            category, formatted_timestamp = file_cache[log_file]
                        else:
                            try:
                                timestamp = datetime.datetime.fromtimestamp(os.path.getmtime(log_file))
                                formatted_timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                            except FileNotFoundError:
                                formatted_timestamp = "N/A"

                            # Fast classification by scanning bytes once and using lowercase checks
                            try:
                                with open(log_file, 'rb') as lf:
                                    data_bytes = lf.read()
                                    data_lower = data_bytes.lower()
                                    # Prioritize OOM detection
                                    if (b"out of memory" in data_lower) or (b" oom" in data_lower):
                                        category = "Out Of Memory (OOM)"
                                    elif b"killed" in data_lower:
                                        category = "Killed (not OOM)"
                                    else:
                                        # Find first line that contains the string "Error" (case-sensitive)
                                        first_error_line = None
                                        for raw_line in data_bytes.splitlines():
                                            if b"Error" in raw_line:
                                                try:
                                                    first_error_line = raw_line.decode('utf-8', errors='ignore').strip()
                                                except Exception:
                                                    first_error_line = "Error"
                                                break
                                        category = first_error_line if first_error_line else "No Error line"
                                        # shorten to only 90 characters to fit in the table
                                        category = category[:90]
                                        
                            except Exception:
                                category = "No Error line"

                            file_cache[log_file] = (category, formatted_timestamp)

                        entry = (error_rule, formatted_timestamp, log_file)
                        if category not in categorized:
                            categorized[category] = []
                        categorized[category].append(entry)
                current_error = False

    return categorized


def print_summary_and_sections(categorized):
    # Build ordered list of categories: OOM, Killed, then others by count desc then name
    counts = {k: len(v) for k, v in categorized.items()}
    categories = [c for c in ["Out Of Memory (OOM)", "Killed (not OOM)"] if c in categorized]
    other_categories = [c for c in categorized.keys() if c not in categories]
    other_categories.sort(key=lambda x: (-counts.get(x, 0), x))
    ordered_categories = categories + other_categories

    category_col_width = max(len("Category"), *(len(c) for c in ordered_categories))
    count_col_width = max(len("Count"), *(len(str(counts[c])) for c in ordered_categories))
    separator = "+" + "-" * (category_col_width + 2) + "+" + "-" * (count_col_width + 2) + "+"

    print(separator)
    print("| " + "Category".ljust(category_col_width) + " | " + "Count".rjust(count_col_width) + " |")
    print(separator)
    for cat in ordered_categories:
        print("| " + cat.ljust(category_col_width) + " | " + str(counts[cat]).rjust(count_col_width) + " |")
    print(separator)
    print()

    def print_section(title, entries):
        print(title)
        print("-" * len(title))
        for error_rule, formatted_timestamp, log_file in entries:
            print(f"{error_rule} {formatted_timestamp} |||||")
            print(f"  {log_file}")

    for cat in ordered_categories:
        print_section(cat, categorized[cat])
        print()


# Get the last snakemake logfile
log_files = glob.glob(os.path.expanduser('~/projects/*/results/logs/snake_sbatch/*conductor*.out'))
log_files.extend(glob.glob(os.path.expanduser('~/projects/*/results/logs/snake_sbatch/*conductor*.log')))
last_log = max(log_files, key=os.path.getmtime)

# Process the logfile and print summary/sections
categorized_errors = process_logfile(last_log)
print_summary_and_sections(categorized_errors)
