LOGS_FOLDER = "C:/Users/user/Desktop/2024/Prosperity/logs"
INPUT_FILE = f"{LOGS_FOLDER}/round2/test1.log"
OUTPUT_FILE = f"{LOGS_FOLDER}/round2/test1_converted.log"

# Replace //n with /n

with open(INPUT_FILE, "r") as f:
    lines = f.readlines()
    lines = [line.replace("\\n", "\n") for line in lines]

with open(OUTPUT_FILE, "w") as f:
    f.writelines(lines)
