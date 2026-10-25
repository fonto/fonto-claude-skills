#!/usr/bin/env python3
"""Tests for the doc-sync 2.4 verification extension (validator + routes inventory).

Run: python3 -m unittest discover -s doc-sync/scripts -p 'test_*.py'
"""
import datetime
import pathlib
import subprocess
import sys
import tempfile
import textwrap
import unittest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import routes_inventory  # noqa: E402

NOW = datetime.datetime.now(datetime.timezone.utc)
RECENT = (NOW - datetime.timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
OLD = (NOW - datetime.timedelta(days=90)).strftime("%Y-%m-%dT%H:%M:%SZ")
GEN = (NOW - datetime.timedelta(days=200)).strftime("%Y-%m-%dT%H:%M:%SZ")

HARNESS = """\
---
type: Verification Harness
title: test harness
generated: {{ by: doc-sync/2.4.0, at: {gen} }}
apps:
  - {{ name: web, routes: next-app, root: web/app }}
  - {{ name: api, routes: nestjs, root: api }}
roles: [guest, buyer]
accounts:
  - {{ role: buyer, email: buyer@example.test, secret_env: E2E_PASSWORD }}
safety: {{ allowed_targets: [local, worktree], forbid_env: [production] }}
proof: {{ actor: process:test-verify, freshness_days: 30 }}
---

# Harness
"""

VERIFICATION = """
## Verification

### Sub-features
- `login` log in [To confirm: TC ids]

### How to get to it (user POV)
- web `/login` → form

### Driving it
Preconditions: seeded DB{pre}
- **Login.** fill `input[name="email"]` → redirected [Code]

### Proof (observable end state)
- `/profile` shows the email [Inference]

### Gotchas
- slow validation [To confirm]
"""


def feature(surfaces="", tests="", verified="", section="", pre=""):
    fm = f"---\ntype: Feature\ntitle: X\ngenerated: {{ by: doc-sync/2.4.0, at: {GEN} }}\n"
    fm += surfaces + tests + verified + "confidence: code\n---\n\n# X\n\n## Purpose\n\n[Code] x.\n"
    return fm + (VERIFICATION.format(pre=pre) if section else "")


SURF = "surfaces:\n  - { app: web, route: /login }   # comment\n  - { app: api, route: /auth/* }\n"


class Bundle:
    def __init__(self, d, harness=True, **features):
        self.root = pathlib.Path(d) / "bundle"
        (self.root / "features").mkdir(parents=True)
        (self.root / "index.md").write_text('---\nokf_version: "0.2"\n---\n\n# B\n')
        if harness:
            (self.root / "VERIFICATION.md").write_text(HARNESS.format(gen=GEN))
        for name, text in features.items():
            (self.root / "features" / f"{name}.md").write_text(text)


def validate(*args):
    r = subprocess.run([sys.executable, str(HERE / "validate_okf.py"), *map(str, args)],
                       capture_output=True, text=True)
    return r.returncode, r.stdout


class ValidatorTests(unittest.TestCase):
    def test_levels_summary(self):
        with tempfile.TemporaryDirectory() as d:
            b = Bundle(d,
                       plain=feature(),
                       partial=feature(SURF, section=True, pre=" [To confirm: seed]"),
                       drivable=feature(SURF, section=True),
                       proven=feature(SURF, section=True, verified=(
                           f"verified:\n  - {{ by: process:test-verify, at: {RECENT}, sha: abc123 }}\n")),
                       expired=feature(SURF, section=True, verified=(
                           f"verified:\n  - {{ by: process:test-verify, at: {OLD}, sha: abc123 }}\n")))
            code, out = validate(b.root)
            self.assertEqual(code, 0, out)
            self.assertIn("verification — documented: 1, partly-drivable: 1, drivable: 2, proven: 1", out)

    def test_gotchas_to_confirm_does_not_block_drivable(self):
        with tempfile.TemporaryDirectory() as d:
            b = Bundle(d, a=feature(SURF, section=True))
            self.assertIn("drivable: 1,", validate(b.root)[1])

    def test_warnings(self):
        with tempfile.TemporaryDirectory() as d:
            surf = SURF + "  - { app: mobile, route: /x }\n"
            b = Bundle(d, a=feature(surf, tests="roles: [buyer, pirate]\ntests: [e2e/a.spec.ts, e2e/gone.spec.ts]\n",
                                    verified=f"verified:\n  - {{ by: process:test-verify, at: {RECENT} }}\n"))
            (pathlib.Path(d) / "e2e").mkdir()
            (pathlib.Path(d) / "e2e/a.spec.ts").write_text("")
            v = b.root / "VERIFICATION.md"
            v.write_text(v.read_text().replace("[local, worktree]", "[local, staging]")
                         .replace("secret_env: E2E_PASSWORD", "password: hunter2")
                         .replace("routes: nestjs", "routes: rails"))
            code, out = validate(b.root, d)
            self.assertEqual(code, 0, out)
            self.assertIn("'mobile' is not declared in VERIFICATION.md", out)
            self.assertIn("'e2e/gone.spec.ts' does not exist", out)
            self.assertNotIn("a.spec.ts' does not exist", out)
            self.assertIn("proof entry by process:test-verify has no sha", out)
            self.assertIn("role 'pirate' is not declared", out)
            self.assertNotIn("role 'buyer'", out)
            self.assertIn("goes beyond local/worktree", out)
            self.assertIn("carries ['password']", out)
            self.assertIn("'rails' not one of", out)

    def test_surfaces_without_harness(self):
        with tempfile.TemporaryDirectory() as d:
            b = Bundle(d, harness=False, a=feature(SURF))
            self.assertIn("surfaces declared but the bundle has no VERIFICATION.md", validate(b.root)[1])

    def test_no_id_key_leaks_into_sources(self):
        with tempfile.TemporaryDirectory() as d:
            b = Bundle(d, a=feature(SURF, section=True))
            self.assertNotIn("footnote", validate(b.root)[1])

    def test_unchanged_on_okf01_fixture(self):
        with tempfile.TemporaryDirectory() as d:
            fx = pathlib.Path(d) / "fx"
            subprocess.run(["bash", str(HERE / "make_okf01_fixture.sh"), str(fx)],
                           check=True, capture_output=True)
            code, out = validate(fx)
            self.assertEqual(code, 0, out)
            self.assertNotIn("verification —", out)
            self.assertIn("0 errors, 7 warnings", out)


class RoutesTests(unittest.TestCase):
    def test_self_test(self):
        self.assertEqual(routes_inventory.self_test(), 0)

    def test_features_mode_and_stale_proof(self):
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d)
            for p in ["web/app/login/page.tsx", "web/app/orphan/page.tsx"]:
                (repo / p).parent.mkdir(parents=True, exist_ok=True)
                (repo / p).write_text("x")
            (repo / "api").mkdir()
            (repo / "api/auth.controller.ts").write_text("@Controller('auth')\nclass A { @Post('login') a(){} }\n")
            git = ["git", "-C", d, "-c", "user.name=t", "-c", "user.email=t@t"]
            subprocess.run(git[:3] + ["init", "-q"], check=True)
            subprocess.run(git + ["add", "-A"], check=True)
            subprocess.run(git + ["commit", "-qm", "a"], check=True)
            sha = subprocess.run(git + ["rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
            surf = SURF + "  - { app: web, route: /gone }\n"
            proof = f"verified:\n  - {{ by: process:test-verify, at: {RECENT}, sha: {sha} }}\n"
            b = Bundle(d, auth=feature(surf, tests="tests:\n  - e2e/missing.spec.ts\n",
                                       verified=proof, section=True))

            def run():
                return subprocess.run([sys.executable, str(HERE / "routes_inventory.py"), str(b.root),
                                       "--features", "--repo", d], capture_output=True, text=True).stdout

            out = run()
            self.assertIn("web\t/login\tauth", out)
            self.assertIn("web\t/orphan\t-", out)
            self.assertIn("api\t/auth/login\tauth", out)
            row = next(l for l in out.splitlines() if l.startswith("auth\t")).split("\t")
            self.assertEqual(row[1], "proven")
            self.assertEqual(row[6], "web:/gone")
            self.assertEqual(row[7], "e2e/missing.spec.ts")
            self.assertIn("3 routes, 1 unmapped", out)

            (repo / "web/app/login/page.tsx").write_text("changed")
            subprocess.run(git + ["commit", "-qam", "b"], check=True)
            row = next(l for l in run().splitlines() if l.startswith("auth\t")).split("\t")
            self.assertEqual(row[1], "drivable")
            self.assertTrue(row[5].endswith("(stale)"))

    def test_cmd_adapter_needs_opt_in(self):
        with tempfile.TemporaryDirectory() as d:
            b = Bundle(d)
            v = b.root / "VERIFICATION.md"
            v.write_text(v.read_text().replace(
                "  - { name: api, routes: nestjs, root: api }",
                "  - { name: sf, routes: cmd, routes_cmd: \"printf '/a\\n/b\\n'\" }"))
            harness = routes_inventory.load_harness(b.root)
            routes, done, notes = routes_inventory.inventory(harness, pathlib.Path(d))
            self.assertNotIn("sf", done)
            self.assertTrue(any("--allow-cmd" in n for n in notes))
            routes, done, _ = routes_inventory.inventory(harness, pathlib.Path(d), allow_cmd=True)
            self.assertEqual(sorted(r for a, r in routes if a == "sf"), ["/a", "/b"])


if __name__ == "__main__":
    unittest.main()
