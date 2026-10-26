# H4CK-B0T — AI-Assisted Security Validation Platform

**H4CK-B0T** is an educational cybersecurity project designed to demonstrate a modular workflow for authorized security assessment, validation, evidence collection, risk calculation, and reporting.

The project focuses on defensive security practices, scope enforcement, and non-destructive assessment techniques.

## 🎯 Project Objectives

- Organize security assessment into modular stages.
- Enforce explicit authorization for assessment targets.
- Record observations and support evidence collection.
- Calculate risk and correlate findings.
- Generate reports for security assessment workflows.
- Provide a local dashboard and command-line entry points.

## ✨ Features

- **Target authorization:** Uses an explicit allowlist and denylist.
- **Scope validation:** Applies same-host, scheme, and port restrictions to candidate URLs.
- **Safety controls:** Includes URL validation, destination-address checks, rate limiting, and audit logging.
- **Modular architecture:** Separates discovery, scanning, validation, evidence, risk, correlation, and reporting.
- **Passive observations:** Records selected endpoint metadata as hints rather than treating it as confirmed technology identification.
- **Local dashboard:** Provides a browser-based interface for local use.
- **Automated tests:** Includes tests for project behavior and safety checks.

## 🛠️ Technology Stack

- Python
- PyYAML
- HTML and browser-based dashboard components
- Pytest for automated testing

## 📁 Project Structure

```text
H4CK-B0T/
├── app.py
├── run.py
├── main.py
├── config/
│   └── config.yaml
├── modules/
│   ├── discovery.py
│   ├── scanner.py
│   ├── validation.py
│   ├── evidence.py
│   ├── risk.py
│   ├── correlation.py
│   └── report.py
├── utils/
│   ├── logger.py
│   └── safety.py
├── tests/
│   └── test_phase1.py
├── requirements.txt
├── README.md
└── PROJECT_CHECKPOINT.md
```

## ⚙️ Installation

**Requirements:** Python 3 and pip.

Clone the repository:

```bash
git clone https://github.com/vishnupriyaguddetti16-maker/H4CK-B0T.git
cd H4CK-B0T
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the project dependencies:

```bash
python -m pip install -r requirements.txt
```

The current `requirements.txt` lists PyYAML. Install pytest separately if it is not already available and you want to run the test suite.

## 🔧 Configuration

Review `config/config.yaml` before running the project.

- Keep `safe_mode: true`.
- Add only targets you own or have explicit permission to assess.
- Ensure assessment roots are explicitly allowlisted.
- Never include usernames, passwords, API keys, or access tokens in target URLs.
- Review rate limits and denylist settings before use.

Disabling safe mode does not grant authorization to assess a target.

## ▶️ Running the Project

### Local Dashboard

Run:

```bash
python app.py
```

Open the dashboard on the same computer:

```text
http://127.0.0.1:8765
```

This is a **local address**, not a public demo link. Do not expose a scan-capable instance to the public internet.

### Command-Line Entry Point

Run:

```bash
python run.py
```

Follow the prompts and assess only explicitly authorized targets.

## 🧪 Running Tests

From the project root:

```bash
python -m pytest -q
```

Test results depend on the current code and environment. Run the tests locally to verify the current state before reporting a test count.

## 🛡️ Responsible Use

H4CK-B0T is intended for educational and authorized defensive security validation only.

The project includes safety checks intended to support:

- Explicit target authorization
- Denylist enforcement
- URL and scope validation
- Destination-address validation
- Request rate limiting
- Audit logging

These controls reduce risk but do not guarantee that every assessment is safe. Review the code and configuration before use. Never assess systems without permission.

## 🗺️ Development Status

H4CK-B0T is an **early-stage MVP under development**. The broader roadmap includes discovery, attack-surface analysis, vulnerability assessment, security validation, attack-path correlation, and reporting.

Not all planned phases are complete. Refer to `PROJECT_CHECKPOINT.md` for the project's progress notes.

## 👩‍💻 Author

**Vishnu Priya**

GitHub: [vishnupriyaguddetti16-maker](https://github.com/vishnupriyaguddetti16-maker)

## ⚠️ Disclaimer

This project is for learning and authorized defensive security validation. Users are responsible for obtaining permission before assessing any target and for following applicable laws and policies.
