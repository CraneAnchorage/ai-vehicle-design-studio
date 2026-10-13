# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.4.x   | ✅ |
| 0.3.x   | ⚠️ security fixes only |
| < 0.3   | ❌ |

## Reporting a Vulnerability

Email `security@ai-vehicle-design-studio.dev` with:

- Affected version and platform (Windows 10/11, x64)
- Steps to reproduce
- Impact assessment (what a malicious plugin could do)

Do **not** open a public issue for security reports. We'll acknowledge within 72 hours.

## Threat Model

AI Vehicle Design Studio runs **third-party plugins** in-process. That is the primary attack surface. We assume:

- Plugins are untrusted by default
- Plugin manifests can lie about capabilities — the host enforces a sandbox for filesystem and network calls
- Model weights loaded from `models_cache/` could be tampered with — SHA-256 verification is required for any downloaded checkpoint

## Plugin Sandbox

Plugins run with:

- No `subprocess` unless `capabilities = ["process"]` is declared and the user grants it
- Filesystem writes confined to `exports/` and the plugin's own `data/` dir
- Network access blocked unless `capabilities = ["network"]` is declared

If you find a sandbox escape, that's a critical CVE — report immediately.