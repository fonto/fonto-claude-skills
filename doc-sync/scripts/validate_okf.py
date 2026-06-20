#!/usr/bin/env python3
"""Validate an OKF knowledge bundle. Stdlib only, no deps.

Works on any OKF v0.1 bundle, not just doc-sync output. Severities follow the
spec's well-formedness rules — only the three hard rules are errors.

Errors (exit 1):
  - a non-reserved .md without parseable frontmatter or with empty `type`
  - a reserved file (subdir index.md / any log.md) that carries frontmatter
Warnings (exit 0): missing/blank `okf_version` on the bundle-root index.md (it is
  OPTIONAL per spec), broken cross-links, log.md date headings not YYYY-MM-DD.

Usage: validate_okf.py [BUNDLE_DIR]   (default: docs/okf)
"""
import sys, re, pathlib

# Tolerate a leading BOM (﻿) and CRLF or LF line endings.
FM = re.compile(r"\A﻿?---\r?\n(.*?)\r?\n---\r?\n", re.S)
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
DATE = re.compile(r"^##\s+\d{4}-\d{2}-\d{2}\s*$")


def frontmatter(text):
    m = FM.match(text)
    return m.group(1) if m else None


def main():
    root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "docs/okf")
    if not root.is_dir():
        print(f"bundle not found: {root}")
        return 1
    errors, warnings = [], []

    for f in sorted(root.rglob("*.md")):
        rel = f.relative_to(root)
        text = f.read_text()
        fm = frontmatter(text)
        is_root_index = rel == pathlib.Path("index.md")
        reserved = f.name in ("index.md", "log.md")

        if reserved:
            if is_root_index:
                # okf_version is OPTIONAL per spec — recommend it, don't require it.
                if not fm or not re.search(r"^okf_version:", fm, re.M):
                    warnings.append(f"{rel}: bundle-root index.md should declare okf_version")
            elif fm:
                errors.append(f"{rel}: reserved file must not have frontmatter")
            if f.name == "log.md":
                for line in text.splitlines():
                    if line.startswith("## ") and not DATE.match(line):
                        warnings.append(f"{rel}: non-ISO date heading: {line.strip()!r}")
        else:
            if not fm:
                errors.append(f"{rel}: missing YAML frontmatter")
            elif not re.search(r"^type:\s*\S", fm, re.M):
                errors.append(f"{rel}: frontmatter has no non-empty `type`")

        # cross-link resolution (warnings only, per OKF spec)
        body = text[len(FM.match(text).group(0)):] if fm else text
        for target in LINK.findall(body):
            if re.match(r"^[a-z]+://", target) or target.startswith("#") or target.startswith("mailto:"):
                continue
            path = target.split("#")[0].split("?")[0]
            if not path.endswith(".md"):
                continue
            dest = (root / path.lstrip("/")) if path.startswith("/") else (f.parent / path)
            if not dest.resolve().exists():
                warnings.append(f"{rel}: broken link -> {target}")

    for w in warnings:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    n = len(list(root.rglob("*.md")))
    print(f"\n{n} files checked — {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
