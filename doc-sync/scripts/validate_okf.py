#!/usr/bin/env python3
"""Validate an OKF knowledge bundle. Stdlib only, no deps.

Works on any OKF v0.2 bundle, not just doc-sync output. Severities follow the
spec's well-formedness rules — only the three hard rules are errors; the spec
requires consumers to tolerate everything else, so all v0.1-residue and
trust-signal checks below are warnings only and never affect the exit code.

Errors (exit 1):
  - a non-reserved .md without parseable frontmatter or with empty `type`
  - a reserved file (subdir index.md / any log.md) that carries frontmatter
Warnings (exit 0): missing/blank `okf_version` on the bundle-root index.md (it
  is OPTIONAL per spec), broken cross-links, log.md date headings not
  YYYY-MM-DD, legacy `timestamp` key (v0.1 residue, should be `generated.at`),
  residual `# Citations` heading (should be `sources` + `[^id]` footnotes),
  `status` outside draft|stable|deprecated, malformed `generated`/`verified`,
  `stale_after` not YYYY-MM-DD or already past, a verification voided by a
  later `generated.at`, `okf_version` present but not "0.2", footnote/source
  cross-reference mismatches. Plus a trust-tier breakdown summary line.

Usage: validate_okf.py [BUNDLE_DIR]   (default: docs/okf)
"""
import sys, re, pathlib, datetime

# Tolerate a leading BOM (﻿) and CRLF or LF line endings.
FM = re.compile(r"\A﻿?---\r?\n(.*?)\r?\n---\r?\n", re.S)
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
DATE = re.compile(r"^##\s+\d{4}-\d{2}-\d{2}\s*$")
YMD = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Inline flow mapping, e.g. `{ by: doc-sync/2.3.0, at: 2026-07-28T14:00:00Z }`.
FLOW_MAP = re.compile(r"\{([^{}]*)\}")
FLOW_ENTRY = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*:\s*([^,}]+)")
FOOTNOTE_REF = re.compile(r"\[\^([^\]]+)\]")
FOOTNOTE_DEF = re.compile(r"^\[\^([^\]]+)\]:", re.M)


def frontmatter(text):
    m = FM.match(text)
    return m.group(1) if m else None


def scalar(fm, key):
    """A simple `key: value` scalar on its own line, or None if absent/exotic."""
    m = re.search(rf"^{key}:[ \t]*(.+)$", fm, re.M)
    if not m:
        return None
    v = m.group(1).strip()
    if v.startswith(("{", "[", "|", ">")) or v == "":
        return None  # not a simple scalar — leave to a dedicated parser
    return v.strip("\"'")


def parse_flow_map(s):
    """Parse `{ by: x, at: y }` into a dict, or None if it doesn't look like one."""
    s = s.strip()
    m = FLOW_MAP.fullmatch(s)
    if not m:
        return None
    inner = m.group(1)
    d = {}
    for em in FLOW_ENTRY.finditer(inner):
        d[em.group(1)] = em.group(2).strip().strip("\"'")
    return d if d else None


def parse_generated(fm):
    """Return (dict_or_None, malformed_bool). None+False = key absent."""
    m = re.search(r"^generated:[ \t]*(.+)$", fm, re.M)
    if not m:
        return None, False
    d = parse_flow_map(m.group(1))
    if d is None:
        return None, True  # present but unparseable shape
    if "by" not in d or "at" not in d:
        return d, True
    return d, False


def parse_verified(fm):
    """Return (list_of_dicts, malformed_bool). ([], False) = key absent."""
    m = re.search(r"^verified:[ \t]*(.*)$", fm, re.M)
    if not m:
        return [], False
    rest_after = m.group(1).strip()
    if rest_after and not rest_after.startswith("#"):
        # Inline: `verified: { by: x, at: y }` (a single mapping, not a list).
        d = parse_flow_map(rest_after)
        if d is None:
            return [], True
        malformed = "by" not in d or "at" not in d
        return [d], malformed
    # Block list: subsequent `  - { by: x, at: y }` lines.
    entries = []
    malformed = False
    lines = fm.splitlines()
    idx = next((i for i, l in enumerate(lines) if l.startswith("verified:")), None)
    if idx is None:
        return [], False
    i = idx + 1
    saw_item = False
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        item = re.match(r"^\s*-\s*(.+)$", line)
        if item is None:
            break
        saw_item = True
        d = parse_flow_map(item.group(1))
        if d is None:
            malformed = True
        else:
            if "by" not in d or "at" not in d:
                malformed = True
            entries.append(d)
        i += 1
    if not saw_item:
        # `verified:` with nothing parseable underneath — too exotic to trust;
        # skip silently rather than risk a false positive.
        return [], False
    return entries, malformed


def instant(s):
    """ISO 8601 datetime -> comparable datetime, or None if unparseable.

    Comparing the raw strings would misjudge `...T15:00:00Z` against
    `...T16:00:00+02:00` (the same instant), so parse before comparing.
    """
    try:
        return datetime.datetime.fromisoformat(str(s).strip().replace("Z", "+00:00"))
    except ValueError:
        return None


def has_sources_key(fm):
    return re.search(r"^sources:", fm, re.M) is not None


def parse_source_ids(fm):
    """Best-effort list of `sources[].id` values. Empty if absent."""
    ids = []
    for m in re.finditer(r"^\s*-\s*id:[ \t]*(.+)$", fm, re.M):
        ids.append(m.group(1).strip().strip("\"'"))
    return ids


def main():
    root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "docs/okf")
    if not root.is_dir():
        print(f"bundle not found: {root}")
        return 1
    errors, warnings = [], []
    root_res = root.resolve()
    today = datetime.date.today().isoformat()

    tiers = {"unverified": 0, "machine-confirmed": 0, "human-reviewed": 0}

    for f in sorted(root.rglob("*.md")):
        rel = f.relative_to(root)
        text = f.read_text()
        fm = frontmatter(text)
        is_root_index = rel == pathlib.Path("index.md")
        reserved = f.name in ("index.md", "log.md")
        body = text[len(FM.match(text).group(0)):] if fm else text

        if reserved:
            if is_root_index:
                if not fm or not re.search(r"^okf_version:", fm, re.M):
                    warnings.append(f"{rel}: bundle-root index.md should declare okf_version")
                elif fm:
                    v = scalar(fm, "okf_version")
                    if v is not None and v != "0.2":
                        warnings.append(f"{rel}: okf_version is {v!r}, not \"0.2\"")
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

        # --- trust-signal / v0.1-residue warnings (concepts only) ---
        if not reserved and fm:
            if re.search(r"^timestamp:", fm, re.M):
                warnings.append(f"{rel}: legacy `timestamp` key present (v0.1 residue, use generated.at)")

            status = scalar(fm, "status")
            if status is not None and status not in ("draft", "stable", "deprecated"):
                warnings.append(f"{rel}: status {status!r} outside draft|stable|deprecated")

            generated, gen_bad = parse_generated(fm)
            if gen_bad:
                warnings.append(f"{rel}: generated is malformed (needs by and at)")
            if generated:
                by = str(generated.get("by", ""))
                if by.startswith(("process:", "human:")):
                    # `generated.by` names the producer and is invariant. An actor
                    # there means an editing pass overwrote it, which also destroys
                    # whatever `verified` entry that pass should have appended.
                    warnings.append(
                        f"{rel}: generated.by is the actor {by!r} — it must name the "
                        f"producer (e.g. doc-sync/2.3.0); actors belong in `verified`")

            verified, ver_bad = parse_verified(fm)
            if ver_bad:
                warnings.append(f"{rel}: verified is malformed (needs by/at on each entry)")

            # trust tier
            if not verified:
                tiers["unverified"] += 1
            elif any(str(e.get("by", "")).startswith("human:") for e in verified):
                tiers["human-reviewed"] += 1
            else:
                tiers["machine-confirmed"] += 1

            # void verification: max(verified[].at) < generated.at
            if generated and not gen_bad and verified and not ver_bad:
                gen_at = instant(generated.get("at"))
                ats = [i for i in (instant(e.get("at")) for e in verified) if i]
                # Mixed aware/naive instants can't be compared — skip rather
                # than warn, a false positive is worse than a missed warning.
                if gen_at and ats and len({i.tzinfo is None for i in ats + [gen_at]}) == 1:
                    if max(ats) < gen_at:
                        warnings.append(f"{rel}: verification is void (generated.at is newer than max(verified[].at))")

            stale_after = scalar(fm, "stale_after")
            if stale_after is not None:
                if not YMD.match(stale_after):
                    warnings.append(f"{rel}: stale_after {stale_after!r} is not YYYY-MM-DD")
                elif stale_after < today:
                    warnings.append(f"{rel}: stale_after {stale_after!r} has expired")

            # residual `# Citations` heading in the body
            if re.search(r"^#+\s*Citations\s*$", body, re.M):
                warnings.append(f"{rel}: residual `# Citations` heading (use sources frontmatter)")

            # footnote <-> sources[].id cross-reference
            has_sources = has_sources_key(fm)
            source_ids = parse_source_ids(fm)
            if has_sources and not source_ids:
                pass  # `sources:` present but too exotic to parse — stay silent
            else:
                refs = {m for m in FOOTNOTE_REF.findall(body)} | {m for m in FOOTNOTE_DEF.findall(body)}
                for sid in source_ids:
                    if sid not in refs:
                        warnings.append(f"{rel}: sources[].id {sid!r} is never referenced by a [^{sid}] footnote")
                for r in refs:
                    if r not in source_ids:
                        warnings.append(f"{rel}: footnote [^{r}] has no matching sources[].id")

        # cross-link resolution (warnings only, per OKF spec)
        for target in LINK.findall(body):
            if re.match(r"^[a-z]+://", target) or target.startswith("#") or target.startswith("mailto:"):
                continue
            path = target.split("#")[0].split("?")[0]
            if not path.endswith(".md"):
                continue
            dest = (root / path.lstrip("/")) if path.startswith("/") else (f.parent / path)
            rdest = dest.resolve()
            if rdest != root_res and root_res not in rdest.parents:
                warnings.append(f"{rel}: link escapes bundle -> {target}")
                continue
            if not rdest.exists():
                warnings.append(f"{rel}: broken link -> {target}")

    for w in warnings:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    n = len(list(root.rglob("*.md")))
    print(f"\ntrust tiers — unverified: {tiers['unverified']}, "
          f"machine-confirmed: {tiers['machine-confirmed']}, "
          f"human-reviewed: {tiers['human-reviewed']}")
    print(f"{n} files checked — {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
