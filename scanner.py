from run import load_config
from utils.safety import open_scoped_url, validate_target

target = input("Enter authorized target URL: ")

try:
    config = load_config()
    target = validate_target(target, config)
    print("\n[+] Security scan started...")
    print("[+] Target:", target)
    response = open_scoped_url(target, target, config, timeout=5)

    print("\n[+] Checking security headers...")

    headers_to_check = [
        "Content-Security-Policy",
        "X-Frame-Options",
        "X-Content-Type-Options"
    ]

    results = []

    for header in headers_to_check:
        value = response.headers.get(header)

        if value:
            print(f"[+] {header}: PRESENT")
            results.append(f"{header}: PRESENT")
        else:
            print(f"[-] {header}: NOT FOUND")
            results.append(f"{header}: NOT FOUND")

    # Save scan results
    with open("scan_result.txt", "w") as file:
        file.write("H4CK-B0T Security Scan Report\n")
        file.write("============================\n")
        file.write(f"Target: {target}\n\n")

        for result in results:
            file.write(result + "\n")

    print("\n[+] Scan results saved to scan_result.txt")

except Exception as e:
    print("[-] Scan failed")
    print("[-] Error:", e)
    