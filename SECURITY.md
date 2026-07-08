# Security Policy

## Reporting a vulnerability

Please report security issues **privately** — do not open a public issue for anything
exploitable.

- Preferred: open a [private security advisory](https://github.com/Gforce-Innovation-Kft/sf-docker-images/security/advisories/new)
  ("Report a vulnerability" under the repository's **Security** tab).
- Or email **gforceinnovation@gmail.com** with `SECURITY` in the subject.

Please include the affected image and tag, a description, and reproduction steps where possible.
We aim to acknowledge reports within a few business days and will coordinate a fix and disclosure
timeline with you.

## Supported versions

Security fixes target the latest release. Because images publish moving tags (`1`, `1.4`,
`latest`) alongside immutable ones, pulling a moving tag picks up patched rebuilds.

| Version | Supported |
|---------|-----------|
| Latest `1.x` | ✅ |
| Older majors | ❌ (upgrade to the latest release) |

## Scanning & provenance

Security is enforced in CI on every build:

- **Trivy** scans each image; results are uploaded to GitHub code scanning (Security tab).
- **SBOM** and **provenance attestations** are generated on push, so you can verify image
  contents and build origin.

Because the base images and toolchains are pinned, rebuilding a release picks up upstream
security patches deterministically. If a scan surfaces a fixable CVE, we cut a patch release.
