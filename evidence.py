from pathlib import Path

print("[+] Evidence collection started...")

files_to_collect = [
    "discovery_result.txt",
    "scan_result.txt",
    "validation_result.txt"
]

with open("evidence_result.txt", "w", encoding="utf-8") as evidence_file:

    evidence_file.write("H4CK-B0T Evidence Report\n")
    evidence_file.write("========================\n\n")

    for filename in files_to_collect:

        evidence_file.write(f"\n--- {filename} ---\n")

        if Path(filename).exists():

            with open(filename, "r", encoding="utf-8") as source_file:
                content = source_file.read()

            evidence_file.write(content)

        else:
            evidence_file.write("File not found.\n")

print("[+] Evidence collection completed")
print("[+] Evidence saved to evidence_result.txt")