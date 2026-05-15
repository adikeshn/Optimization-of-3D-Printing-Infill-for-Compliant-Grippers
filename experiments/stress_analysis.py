import re
import numpy as np

file_path = "vtu/finr3.vtu"

with open(file_path, "r", errors="ignore") as f:
    text = f.read()

match = re.search(
    r'<DataArray[^>]*Name="Stress:von Mises"[^>]*>(.*?)</DataArray>',
    text,
    re.S
)

def percentile_band_avg(vals, low_pct, high_pct):
    low = np.percentile(vals, low_pct)
    high = np.percentile(vals, high_pct)
    band = vals[(vals >= low) & (vals <= high)]
    return np.mean(band)

def trimmed_mean(vals, trim_pct):
    low = np.percentile(vals, trim_pct)
    high = np.percentile(vals, 100 - trim_pct)
    trimmed = vals[(vals >= low) & (vals <= high)]
    return np.mean(trimmed)


if match is None:
    raise ValueError("Could not find Stress:von Mises array.")

stress = np.fromstring(match.group(1), sep=" ")
stress = stress[np.isfinite(stress)]

def top_percent_avg(values, percent):
    n = max(1, int(np.ceil((percent / 100) * len(values))))
    return np.mean(np.sort(values)[-n:])
print("number of elements", len(stress))
print("95th percentile stress:", np.percentile(stress, 95))
print("99th percentile stress:", np.percentile(stress, 99))
print("Top 5% avg stress:", top_percent_avg(stress, 5))
print("Top 10% avg stress:", top_percent_avg(stress, 10))
print("Top 5-20% avg stress:", percentile_band_avg(stress, 80, 95))
print("Mean stress:", np.mean(stress))
print("Median stress:", np.median(stress))
print("10% trimmed mean stress:", trimmed_mean(stress, 10))
print("Max / 99th percentile stress:", np.max(stress) / np.percentile(stress, 99))
print("Top 5% avg / median stress:", top_percent_avg(stress, 5) / np.median(stress))