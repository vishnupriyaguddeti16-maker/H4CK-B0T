#!/usr/bin/env python3
"""Phase 1 entry point for H4CK-B0T."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from modules import discovery, scanner, validation, evidence, risk, correlation, report
from utils.logger import setup_logger
from utils.safety import validate_target


def _simple_yaml_value(value):
    """Read the scalar YAML values used by this project's small config file."""
    value = value.strip()
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if value.lower() in {"null", "~"}:
        return None
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        return [] if not inner else [_simple_yaml_value(part) for part in inner.split(",")]
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def _load_simple_yaml(text):
    """Fallback parser for the simple mapping/list structure in config/config.yaml."""
    config = {}
    section = None
    lines = text.splitlines()
    for index, raw_line in enumerate(lines):
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        content = line.strip()
        if indent == 0 and ":" in content:
            key, value = content.split(":", 1)
            key, value = key.strip(), value.strip()
            if value:
                config[key] = _simple_yaml_value(value)
                section = None
            else:
                next_line = next((item.strip() for item in lines[index + 1:] if item.strip()), "")
                config[key] = [] if next_line.startswith("-") else {}
                section = key
        elif section is not None and content.startswith("-") and isinstance(config.get(section), list):
            config[section].append(_simple_yaml_value(content[1:].strip()))
        elif section is not None and ":" in content and isinstance(config.get(section), dict):
            key, value = content.split(":", 1)
            config[section][key.strip()] = _simple_yaml_value(value)
    return config


def load_config():
    """Load the application configuration from config/config.yaml."""
    config_path = ROOT / "config" / "config.yaml"
    try:
        import yaml
    except ImportError:
        with config_path.open("r", encoding="utf-8") as handle:
            config = _load_simple_yaml(handle.read())
    else:
        with config_path.open("r", encoding="utf-8") as handle:
            config = yaml.safe_load(handle) or {}

    config.setdefault("authorized_targets", [])
    config.setdefault("denylist", [])
    config.setdefault("safe_mode", True)
    config.setdefault("request_rate_limit", 1)
    config.setdefault("logging", {})
    if "logging" in config and isinstance(config["logging"], dict):
        config["logging"].setdefault("level", "INFO")
        config["logging"].setdefault("file", "logs/h4ckbot.log")
        config["logging"].setdefault("audit_log", "logs/h4ckbot_audit.log")
    return config


def main():
    """Run the Phase 1 H4CK-B0T pipeline."""
    config = load_config()
    logger = setup_logger(config)
    audit_logger = logger.audit_logger

    target = input("Enter the authorized target URL: ").strip()

    try:
        target = validate_target(target, config)
    except ValueError as exc:
        logger.error(str(exc))
        audit_logger.error("Authorization blocked: %s", str(exc))
        print(f"[-] Target blocked: {exc}")
        return 1

    logger.info("Starting H4CK-B0T Phase 1 pipeline for %s", target)
    audit_logger.info("Pipeline started for target %s", target)

    discovery_data = discovery.run_discovery(target, config, logger)
    discovered_endpoints = [
        item for item in (discovery_data or {}).get("discovered_endpoints", []) if isinstance(item, dict) and item.get("url")
    ]
    scan_data = scanner.run_scan(discovered_endpoints or [target], config, logger)
    validation_data = validation.run_validation(scan_data, config, logger)
    evidence_data = evidence.collect_evidence(discovery_data, scan_data, validation_data, config, logger)
    risk_data = risk.calculate_risk(validation_data, config, logger)
    correlation_data = correlation.correlate_findings(discovery_data, validation_data, risk_data, config, logger)
    report_data = report.generate_report(target, discovery_data, scan_data, validation_data, evidence_data, risk_data, correlation_data, config, logger)

    logger.info("Pipeline completed for %s", target)
    audit_logger.info("Pipeline completed for target %s", target)

    print("\n[+] H4CK-B0T Phase 1 pipeline completed")
    print(f"[+] Target: {target}")
    print("[+] Results saved in results/")
    print("[+] Logs saved in logs/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
