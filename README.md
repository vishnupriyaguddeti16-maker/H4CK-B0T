# H4CK-B0T

H4CK-B0T is a beginner-friendly defensive security validation project. It demonstrates a simple assessment workflow for authorized targets only, using a safe, non-destructive approach focused on observation and validation.

## Phase 1 Scope

This Phase 1 release focuses on the project foundation:

- safe project structure
- authorization and denylist checks
- centralized logging
- modular pipeline organization
- JSON result files
- basic tests

This does not include advanced exploitation, enumeration, or other later-phase features.

**Trainer status:** Trainer Phase 1 Discovery remains **NOT complete**. The passive hints described below are small increments to the existing same-host inventory; they do not mean Phase 1 or all six trainer phases are complete.

## Architecture

The Phase 1 flow is:

1. Discovery
2. Scan
3. Validation
4. Evidence collection
5. Risk calculation
6. Correlation
7. Reporting

### Discovery classifications

Discovery inventories the authorized root and configured same-host candidate paths. For an already-observed reachable endpoint, it adds `Possible API endpoint` only when the existing `Content-Type` indicates JSON and the URL path contains an `api` path segment, case-insensitively. For example, `/api/users` with JSON receives the hint; `/users` with JSON remains ordinary JSON content, and `/api/users` with non-JSON content does not receive it.

For an already-observed reachable endpoint with a non-empty `Server` header, discovery also adds `Unverified Server header observation: <trimmed observed value>`. This is an observation only: the value is not parsed into a product, version, framework, or confirmed technology.

These are passive hints, not API or technology discovery or confirmation. They use only already-collected endpoint metadata: they make no additional network requests and read no response bodies. The API classification, existing endpoint metadata, candidate filtering, authorization and safety controls remain unchanged. Risk and report semantics are unchanged.

Latest reported tests (from the prior Codex run; not rerun for this documentation update): focused tests **40 passed, 85 deselected**; full suite **125 passed, 0 failed**.

## Project structure

```text
H4CK-B0-T/
├── run.py
├── requirements.txt
├── README.md
├── config/
│   └── config.yaml
├── modules/
│   ├── __init__.py
│   ├── discovery.py
│   ├── scanner.py
│   ├── validation.py
│   ├── evidence.py
│   ├── risk.py
│   ├── correlation.py
│   └── report.py
├── utils/
│   ├── __init__.py
│   ├── logger.py
│   └── safety.py
├── results/
├── logs/
└── tests/
```

## Installation

```bash
python -m pip install -r requirements.txt
```

## Configuration

Edit [config/config.yaml](config/config.yaml) to set the authorized targets. Every assessment root must be explicitly listed here, regardless of the `safe_mode` setting. `safe_mode` does not grant permission to assess targets that are not allowlisted.
Do not include usernames or passwords in target URLs; credentialed URLs are rejected even if allowlisted. The CLI, legacy entry points, dashboard, and direct module calls enforce authorization before making assessment requests.

Example:

```yaml
authorized_targets:
  - https://example.com

denylist: []
safe_mode: true
request_rate_limit: 1
```

## Running the project

### Web dashboard

Start the local dashboard with:

```bash
python app.py
```

Then open `http://127.0.0.1:8765` in your browser. The dashboard displays the configured authorized targets, starts the existing seven-stage pipeline, and presents findings and risk summaries from the saved report. It listens only on the local machine. Assessment requests require both an explicit allowlist match in `config/config.yaml` and an authorization confirmation in the dashboard.

The dashboard does not add targets to the allowlist. Review and edit `authorized_targets` in `config/config.yaml` yourself, and keep `safe_mode: true`. Results remain in `results/`; audit and application logs remain in `logs/`.

### Command line

The original command-line workflow is also available:

```bash
python run.py
```

When prompted, enter only an explicitly authorized target. The root target must appear in `authorized_targets` even when `safe_mode` is disabled. The legacy `main.py` discovery script uses the same authorization, denylist, timeout, rate-limit, and scoped redirect protections.

## Results and logs

- JSON results are stored in the `results/` directory.
- Logs are stored in the `logs/` directory.
- Audit logs are also written to the configured audit log path.

## Safety and authorization requirements

This project is for authorized defensive security validation only. It must never scan a target that is not explicitly authorized. The safety checks in `utils/safety.py` enforce:

- URL validation
- allowlist enforcement
- denylist enforcement
- same-host, same-scheme, and same-port scope enforcement
- resolved IP validation and address-pinned HTTP(S) connections
- rejection of non-global and special-purpose destinations, except explicitly allowlisted loopback targets
- direct assessment connections that bypass environment-configured proxies
- basic rate limiting
- centralized audit logging

## Important note

This is a safe MVP for demonstration and educational use only. It intentionally avoids destructive or intrusive testing.
