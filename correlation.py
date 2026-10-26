from pathlib import Path

print("[+] Correlation analysis started...")

discovery_file = "discovery_result.txt"
risk_file = "risk_result.txt"

target = "Unknown target"
findings = []
risk_items = []

# Read target information
if Path(discovery_file).exists():

    with open(discovery_file, "r", encoding="utf-8") as file:
        lines = file.readlines()

    for line in lines:
        if line.startswith("Target:"):
            target = line.strip().replace("Target:", "").strip()

# Read risk information
if Path(risk_file).exists():

    with open(risk_file, "r", encoding="utf-8") as file:
        lines = file.readlines()

    current_section = ""

    for line in lines:
        line = line.strip()

        if line == "HIGH PRIORITY":
            current_section = "HIGH"

        elif line == "MEDIUM PRIORITY":
            current_section = "MEDIUM"

        elif line == "LOW PRIORITY":
            current_section = "LOW"

        elif line and not line.startswith("-"):

            if current_section and (
                "No high-priority" not in line
                and "No medium-priority" not in line
                and "No low-priority" not in line
            ):
                risk_items.append((current_section, line))


# Create correlation report
with open("correlation_result.txt", "w", encoding="utf-8") as report:

    report.write("H4CK-B0T Correlation Report\n")
    report.write("==========================\n\n")

    report.write(f"Target: {target}\n\n")

    report.write("Security Finding Relationships\n")
    report.write("------------------------------\n")

    if risk_items:

        for priority, finding in risk_items:

            report.write(
                f"Target: {target} -> Finding: {finding} -> Risk: {priority}\n"
            )

    else:
        report.write("No findings available for correlation.\n")


print("[+] Correlation analysis completed")
print("[+] Results saved to correlation_result.txt")