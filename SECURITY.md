# Security Policy

Our goal is to keep Beacon Delivery Compass safe-by-default for product builders and developers analyzing local Git repositories. This policy is concise and user-focused; deeper engineering details live in our developer docs.

## Scope and Supported Versions
- In scope: CLI and library code under this repository that interacts with local Git repositories.
- Supported versions: main branch and releases >= 0.2.0-dev. Older tags receive best-effort fixes only.
- Data handling: the tool operates on local repos and does not exfiltrate data.

## Security Posture (Summary)
We follow defense-in-depth for inputs and file-system boundaries:
- Strict validation for commit hashes and date inputs; length limits to mitigate DoS.
- Path traversal protection using resolved, bounded paths and .git presence checks.
- Subprocess and network operations use timeouts and parameterized calls.
- Dependencies are kept current; routine vulnerability scanning is enabled.

For implementation specifics, see:
- docs/development/security/roadmap.md
- docs/development/security/ (architecture, testing, and practices)

## Reporting Vulnerabilities
Please report responsibly:
1. GitHub Security Advisories (preferred): use the repository Security tab to submit a private report.
2. Direct email to the maintainers for sensitive issues.

Include:
- A clear description, reproduction steps, and potential impact.
- Any suggested remediation.

Response targets:
- Acknowledgment within 24–72 hours.
- Triage and next steps communicated within 7 days.

## Current Controls (High-Level)
- Input Security: regex-based validation for commit hashes and dates; conservative length limits.
- Filesystem Safety: repo root boundary checks; .git verification; sanitized paths.
- Process/Network Safety: parameterized subprocess usage; 30s timeouts; HTTPS and TLS verification for outbound calls where applicable.
- Configuration: sensitive files ignored from VCS; secure examples and env-var-based credentials.

## Maintenance
- Monthly dependency vulnerability review and updates.
- Security-conscious code reviews in CI.
- Periodic security posture reviews aligned with releases.

---

Last Updated: August 2025
Security Contact: Repository maintainers
