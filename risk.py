from pathlib import Path

print("[+] Risk prioritization started...")

validation_file = "validation_result.txt"

high_priority = []
medium_priority = []
low_priority = []

if Path(validation_file).exists():

    with open(validation_file, "r", encoding="utf-8") as file:
        lines = file.readlines()

    for line in lines:
        line = line.strip()

        if "NOT FOUND" in line:
            medium_priority.append(line)

        elif "PRESENT" in line:
            low_priority.append(line)

else:
    print("[-] validation_result.txt not found")


with open("risk_result.txt", "w", encoding="utf-8") as report:

    report.write("H4CK-B0T Risk Prioritization Report\n")
    report.write("==================================\n\n")

    report.write("HIGH PRIORITY\n")
    report.write("-------------\n")

    if high_priority:
        for item in high_priority:
            report.write(item + "\n")
    else:
        report.write("No high-priority items identified.\n")

    report.write("\nMEDIUM PRIORITY\n")
    report.write("----------------\n")

    if medium_priority:
        for item in medium_priority:
            report.write(item + "\n")
    else:
        report.write("No medium-priority items identified.\n")

    report.write("\nLOW PRIORITY\n")
    report.write("------------\n")

    if low_priority:
        for item in low_priority:
            report.write(item + "\n")
    else:
        report.write("No low-priority items identified.\n")


print("[+] Risk prioritization completed")
print("[+] Results saved to risk_result.txt")