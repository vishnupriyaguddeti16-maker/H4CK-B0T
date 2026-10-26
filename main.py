from run import load_config
from urllib.parse import urlparse
from utils.logger import setup_logger
from utils.safety import open_scoped_url, validate_target


def main():
    """Run the legacy discovery report through the shared authorization controls."""
    config = load_config()
    logger = setup_logger(config)
    audit_logger = logger.audit_logger

    target = input("Enter authorized target URL: ").strip()

    try:
        target = validate_target(target, config)
    except ValueError as exc:
        logger.error(str(exc))
        audit_logger.error("Authorization blocked: %s", str(exc))
        print(f"[-] Target blocked: {exc}")
        return 1

    print("\n[+] Discovery started...")
    print("[+] Target:", target)

    parsed_url = urlparse(target)
    protocol = parsed_url.scheme
    domain = parsed_url.hostname
    port = parsed_url.port
    path = parsed_url.path

    print("[+] Protocol:", protocol)
    print("[+] Domain:", domain)
    print("[+] Port:", port)
    print("[+] Path:", path)

    logger.info("Starting legacy discovery for %s", target)
    audit_logger.info("Discovery started for target %s", target)

    try:
        timeout = int(config.get("timeout_seconds", 5) or 5)
        with open_scoped_url(target, target, config, timeout=timeout) as response:
            status_code = response.status
            server = response.headers.get("Server")
            content_type = response.headers.get("Content-Type")

        print("[+] Target is reachable")
        print("[+] Status Code:", status_code)
        print("[+] Server:", server)
        print("[+] Content Type:", content_type)

        with open("discovery_result.txt", "w", encoding="utf-8") as file:
            file.write("H4CK-B0T Discovery Report\n")
            file.write("=========================\n")
            file.write(f"Target: {target}\n")
            file.write(f"Protocol: {protocol}\n")
            file.write(f"Domain: {domain}\n")
            file.write(f"Port: {port}\n")
            file.write(f"Path: {path}\n")
            file.write(f"Status Code: {status_code}\n")
            file.write(f"Server: {server}\n")
            file.write(f"Content Type: {content_type}\n")

        audit_logger.info("Discovery completed for target %s", target)
        print("\n[+] Discovery results saved to discovery_result.txt")
        return 0
    except Exception as exc:
        logger.error("Discovery failed for %s: %s", target, exc)
        audit_logger.error("Discovery failed for target %s: %s", target, exc)
        print("[-] Could not connect to target")
        print("[-] Error:", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())