import sys
import io

# Parse CLI flags
args = sys.argv[1:]
if len(args) == 0:
    print("Usage: 'python index_combiner.py index1.txt index2.txt index3.txt' etc.")

# Get file data
index = {}
for count, filename in enumerate(args):
    with io.open(filename, "r", encoding="utf-8") as f:
        for line in f.read().split("\n"):
            if ": " not in line:
                continue
            index_key, pages = line.split(": ")
            if index_key not in index:
                index[index_key] = ""
            index[index_key] += f"{count + 1}({pages}) | "

# Trim trailing " | "s
for key in index.keys():
    index[key] = index[key].rstrip(" | ")

# Turn index -> lines
lines = []
for key in index.keys():
    lines.append(f"{key}: {index[key]}")
lines.sort()

# Print output
for line in lines:
    sys.stdout.buffer.write((line + '\n').encode('utf-8'))