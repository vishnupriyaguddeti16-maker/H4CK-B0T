from pathlib import Path

SCAN_FILE = Path("scan_result.txt")
OUTPUT_FILE = Path("validation_result.txt")
HEADER_NAMES = {
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
}


def read_scan_results(file_path):
    """Read the scan result file and validate that it exists and is not empty."""
    if not file_path.exists():
        raise FileNotFoundError("scan_result.txt is missing. Run scanner.py first.")

    content = file_path.read_text(encoding="utf-8")

    if not content.strip():
        raise ValueError("scan_result.txt is empty. No scan data was found.")

    return content


def extract_target(content):
    """Try to extract the target URL from the scan report."""
    for line in content.splitlines():
        if line.startswith("Target:"):
            return line.split(":", 1)[1].strip()
    return "Unknown target"


def parse_scan_results(content):
    """Parse the scan report and gather only the security header observations."""
    findings = []

    for raw_line in content.splitlines():
        line = raw_line.strip()

        if not line or ":" not in line:
            continue

        name, value = line.split(":", 1)
        name = name.strip()
        value = value.strip()

        if name in HEADER_NAMES:
            findings.append({
                "Finding name": name,
                "Observation": f"{name}: {value}",
                "Status": value,
            })

    if not findings:
        raise ValueError(
            "Unexpected file contents. The scan file does not include the expected header findings."
        )

    return findings


def classify_finding(finding_name, value):
    """Convert each raw header result into a beginner-friendly validation finding."""
    status = value.strip()

    if status == "NOT FOUND":
        return {
            "Finding name": finding_name,
            "Observation": f"{finding_name}: {status}",
            "Validation status": "Potential Finding",
            "Basic explanation": (
                f"The {finding_name} header was not detected in the HTTP response. "
                "This is a configuration observation, not a confirmed vulnerability. "
                "It may indicate weaker browser protections or missing defense-in-depth controls."
            ),
        }

    if status == "PRESENT":
        return {
            "Finding name": finding_name,
            "Observation": f"{finding_name}: PRESENT",
            "Validation status": "No issue found",
            "Basic explanation": (
                f"The {finding_name} header is present. This suggests the site is already providing "
                "this protective setting."
            ),
        }

    return {
        "Finding name": finding_name,
        "Observation": f"{finding_name}: {status}",
        "Validation status": "Potential Finding",
        "Basic explanation": (
            f"The {finding_name} value was unusual or unexpected. This requires a quick review of the "
            "scanner output before making a conclusion."
        ),
    }


def generate_validation_report(target, findings):
    """Build the report text saved to validation_result.txt."""
    report_lines = [
        "H4CK-B0T Validation Report",
        "==========================",
        f"Target: {target}",
        "",
    ]

    for index, finding in enumerate(findings, start=1):
        report_lines.extend([
            f"Potential Finding {index}",
            f"Finding name: {finding['Finding name']}",
            f"Observation: {finding['Observation']}",
            f"Validation status: {finding['Validation status']}",
            f"Basic explanation: {finding['Basic explanation']}",
            "",
        ])

    return "\n".join(report_lines).strip() + "\n"


def write_error_report(file_path, message):
    """Write a safe, readable error report when validation cannot proceed."""
    report = (
        "H4CK-B0T Validation Report\n"
        "==========================\n"
        "Validation status: Unable to validate\n"
        f"Error: {message}\n"
    )
    file_path.write_text(report, encoding="utf-8")


def main():
    """Main entry point for the validation step in the H4CK-B0T workflow."""
    try:
        content = read_scan_results(SCAN_FILE)
        target = extract_target(content)
        raw_findings = parse_scan_results(content)

        validated_findings = []
        for item in raw_findings:
            validated_findings.append(
                classify_finding(item["Finding name"], item["Status"])
            )

        # Only keep the header results that represent a meaningful validation concern.
        validation_findings = [
            finding for finding in validated_findings if finding["Validation status"] == "Potential Finding"
        ]

        if not validation_findings:
            validation_findings = validated_findings

        report_text = generate_validation_report(target, validation_findings)
        OUTPUT_FILE.write_text(report_text, encoding="utf-8")

        print("\n[+] Validation started...")
        print(f"[+] Target: {target}")
        print(f"[+] Validation results saved to {OUTPUT_FILE}")

    except FileNotFoundError as exc:
        write_error_report(OUTPUT_FILE, str(exc))
        print(f"[-] {exc}")
        print(f"[-] A validation error report was written to {OUTPUT_FILE}")

    except ValueError as exc:
        write_error_report(OUTPUT_FILE, str(exc))
        print(f"[-] {exc}")
        print(f"[-] A validation error report was written to {OUTPUT_FILE}")

    except Exception as exc:
        write_error_report(OUTPUT_FILE, f"Unexpected error: {exc}")
        print("[-] Validation failed")
        print(f"[-] Error: {exc}")
        print(f"[-] A validation error report was written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
