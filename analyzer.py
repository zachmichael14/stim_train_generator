from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def _get_original_filename(file_name):
    def _remove_timestamp(file_name: Path):
        parts = file_name.rsplit("_", 2)
        return "_".join(parts[:-2])

    def _remove_log_details(file_name: Path):
        parts = file_name.split("_", 2)
        return parts[-1]

    file_name = Path(file_name).stem
    file_name = _remove_timestamp(file_name)
    file_name = _remove_log_details(file_name)

    return f"{file_name}.csv"

def analyze_pulses(file_path,
                   voltage_threshold=0.5,
                   expected_pulse_duration=0.002,
                   frequency=1):
    df = pd.read_csv(file_path, names=["voltage", "dg28"])
    # print(df)
    
    df["time"] = np.arange(len(df)) / 50000  # 50kHz sampling rate
    # print(df)

    df["pulse"] = (df["voltage"] >= voltage_threshold).astype(int)
    # df["pulse"] = (df["dg28"] >= voltage_threshold).astype(int)
    # df.to_csv(f"{frequency}_Hz_detail.csv")

    # df["dg28_pulse"] = (df["dg28"] >= voltage_threshold).astype(int)
    pulse_starts = df[df["pulse"].diff() == 1]["time"]
    print(pulse_starts)
    # pulse_starts = df[df["dg28_pulse"].diff() == 1]["time"]

    periods = pulse_starts.diff().dropna()

    try:
        expected_period = 1 / frequency
    except TypeError as e:
        return

    # Compute latency
    latency = periods - expected_period


    print(f"~~~~~~~~ AVG LATENCY AND STDDEV FOR {frequency} ~~~~~~~~~~")
    mean_latency = np.mean(latency)
    # print(avg_latency)
    stddev_latency = np.std(latency)
    print(f"{mean_latency * 1000:.4f} ms")
    print(f"{stddev_latency * 1000:.4f} ms")

    print(f"~~~~~~~~ PERCENT ERRORS AND MEAN PERCENT ERROR FOR {frequency} ~~~~~~~~~")
    period_error = np.abs(((periods - expected_period)/periods)) * 100
    mean_percent_error = np.mean(period_error)
    print(f"Mean percent error: {mean_percent_error:.2f}%")

    fig, ax2 = plt.subplots(1, 1, figsize=(12, 7))
    fig.canvas.manager.set_window_title(f"{frequency} Hz")

    n, bins, patches = ax2.hist(latency * 1000, bins=50, edgecolor="black")
    ax2.set_title(f"Latency for {frequency} Hz")
    ax2.set_xlabel("Latency (ms)")
    ax2.set_xticks([])
    ax2.set_ylabel("Count")
    
    for count, patch, bin_left, bin_right in zip(n, patches, bins[:-1], bins[1:]):
        if count > 0:
            # Annotate count above the bar
            ax2.text(patch.get_x() + patch.get_width() / 2, count, int(count), 
                     ha="center", va="bottom")
            # Annotate bin range below the bar
            ax2.text(patch.get_x() + patch.get_width() / 2, 0, 
                     f"{bin_left:.2f} - {bin_right:.2f}", 
                     ha="center", va="top", fontsize=8, rotation=90)
            
    # Annotate mean latency and stddev inside the plot
    ax2.annotate(f"Mean latency: {mean_latency*1000:.5f} ms +- {stddev_latency*1000:.5f} ms",
                 xy=(0.65, 0.95), xycoords="axes fraction", ha="left", va="top", fontsize=8, 
                 bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="white"))
    
    # Annotate mean latency and stddev inside the plot
    ax2.annotate(f"Percent error: {mean_percent_error:.3f}",
                 xy=(0.7, 0.90), xycoords="axes fraction", ha="left", va="top", fontsize=8, 
                 bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="white"))
    
    
    plt.tight_layout()
    plt.show(block=False)
    
    return {
        "mean_percent_error": mean_percent_error,
        "period_error": period_error,
        "mean_period": np.mean(periods),
        "pulse_count": len(pulse_starts),
        "mean_latency": mean_latency,
        "stddev_latency": stddev_latency
    }

def extract_frequency(file_path):
    import re
    # Use regular expression to find the frequency pattern (e.g., 30_hz)
    match = re.search(r"_(\d+)_[Hh]", str(file_path))
    
    if match:
        # Extract the frequency (as an integer)
        frequency = int(match.group(1))
        return frequency
    else:
        # Handle cases where the frequency pattern is not found
        return None
    
def plot_latencies(latency_data):
    # Collect latencies from the latency_data dictionary
    latencies = []
    
    # Extract latencies from the latencies dictionary
    for freq, values in latency_data.items():
        latencies.append(values["mean"])  # Use the mean latency for plotting

    # Create a histogram of latencies
    plt.figure(figsize=(12, 6))
    counts, bins, patches = plt.hist(latencies, bins=50, edgecolor="black", alpha=0.7)  # Adjust number of bins as needed

    plt.title("Histogram of Mean Latencies")
    plt.xlabel("Mean Latency (ms)")  # Mean latency on the x-axis
    plt.ylabel("Number of Occurrences")  # Number of occurrences on the y-axis
    plt.grid(axis="y", alpha=0.75)

    # Annotate each bin with the count and bin range
    for count, x in zip(counts, bins):
        if count > 0:
            # Calculate the position for the annotation
            bin_label = f"{x:.4f} - {bins[bins.tolist().index(x)+1]:.6f}"
            plt.text(x + (bins[1] - bins[0]) / 2, count, f"{bin_label}", ha="center", va="bottom", rotation=90)
    plt.tight_layout()
    plt.show(block=False)

def plot_average_latency(latency_data):
    frequencies = list(latency_data.keys())
    averages = [values["mean"]*1000 for values in latency_data.values()]

    plt.figure(figsize=(12, 6))
    plt.plot(frequencies, averages, marker="x")
    plt.title("Average Latency vs Frequency")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Average Latency (ms)")
    plt.grid()
    plt.xticks(frequencies)  # Ensure all frequencies are labeled on the x-axis
    plt.tight_layout()
    plt.show(block=False)

# Function to plot standard deviation against frequency
def plot_std_deviation(latency_data):
    frequencies = list(latency_data.keys())
    stddevs = [values["stddev"]*1000 for values in latency_data.values()]

    plt.figure(figsize=(12, 6))
    plt.plot(frequencies, stddevs, color="orange", marker="x")
    plt.title("Standard Deviation of Latency vs Frequency")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Standard Deviation of Latency (ms)")
    plt.grid()
    plt.xticks(frequencies)  # Ensure all frequencies are labeled on the x-axis
    plt.tight_layout()
    plt.show()


# f_path = Path("C:\\Users\\Lab\\Box\\Seanez_Lab\\SharedFolders\\RAW DATA\\Russian_Stim\\DAQ_Test\\DAQ_Test_20240930\\DAQ_Test_20240930__1_Hz.csv")
# analyze_pulses(f_path, frequency=1)

dir_path = Path("C:\\Users\\Lab\\Box\\Seanez_Lab\\SharedFolders\\RAW DATA\\Russian_Stim\\DAQ_Test\\DAQ_Test_20241001")

latencies = {}

for file in dir_path.iterdir():
    if file.is_file() and "roi" not in str(file).casefold() and ("hertz" in str(file).casefold() or "hz" in str(file).casefold()):

        print(f"File: {file}")
        frequency = extract_frequency(file)
        results = analyze_pulses(file, frequency=frequency)
        latencies[frequency] = {
            "mean": results["mean_latency"],
            "stddev": results["stddev_latency"],
        }

        original = pd.read_csv(f"{frequency}hz_5_interval_const_amp_ramped.csv")
        expected_pulses = len(original["frequency"])

        # expected_pulses = 30 / (1 / frequency)
        detected_pulses = results["pulse_count"]
        missed_pulses = expected_pulses - detected_pulses
        # print("Pulses:")
        # print(f"\tExpected: {expected_pulses}")
        # print(f"\tDetected: {detected_pulses}")
        # print(f"\tMissed: {missed_pulses} ({missed_pulses/expected_pulses:.1%})")

        print(f"~~~ Done with {frequency} Hz ~~~ \n")

latencies = dict(sorted(latencies.items()))
# After all files have been processed, plot the latencies
plot_latencies(latencies)

# Plot average latency vs frequency
plot_average_latency(latencies)

# Plot standard deviation vs frequency
plot_std_deviation(latencies)

print("~~~ Fin ~~~")