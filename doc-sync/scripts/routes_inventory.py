#!/usr/bin/env python3
"""List an app's user-reachable routes deterministically. Stdlib only, no deps.

Reads the `apps` declared in `<bundle>/VERIFICATION.md` and runs one adapter
per app. Routes are app-relative (a Next `basePath` or a Nest global prefix is
not added) and use one parameter syntax everywhere: `[param]`.

Adapters (`routes:` key of an app):
  next-app  `root` = the `app/` dir: every `page.*`, minus route groups `(x)`,
            parallel slots `@x`, private folders `_x`; intercepted `(.)x`
            routes are skipped. Route handlers (`route.ts`) are API, not pages.
  tanstack  `root` = `routeTree.gen.ts`: the keys of `FileRoutesByTo`
            (fallback `FileRoutesByFullPath`), `$param` -> `[param]`.
  nestjs    `root` = the source dir: `@Controller('x')` + `@Get('y')`... ->
            `/x/y`, `:param` -> `[param]`.
  cmd       `routes_cmd` = a shell command run in REPO that prints one route
            per line. It is project-declared code, so it only runs with
            --allow-cmd; otherwise the app is reported as not inventoried.

Usage:
  routes_inventory.py BUNDLE [--repo DIR] [--allow-cmd]
      app<TAB>route<TAB>sources   (one line per route)
  routes_inventory.py BUNDLE --features [--repo DIR] [--allow-cmd]
      the route -> feature map, then one line per Feature concept:
      level, apps, roles, e2e count, last proof, surfaces matching no route,
      tests[] files missing. A proof goes stale when a commit since its `sha`
      touched a source file behind one of the feature's surfaces.
  routes_inventory.py --self-test
"""
import pathlib
import re
import subprocess
import sys

from validate_okf import (frontmatter, FM, flow_list, str_list, load_harness,
                          feature_level, drive_level)

PAGE_EXT = {".tsx", ".jsx", ".ts", ".js", ".mdx", ".md"}
CTRL = re.compile(r"@Controller\(\s*(?:(['\"`])(.*?)\1|\{[^}]*?path:\s*(['\"`])(.*?)\3[^}]*\})?\s*\)")
METHOD = re.compile(r"@(?:Get|Post|Put|Patch|Delete|All|Options|Head)\(\s*(?:(['\"`])(.*?)\1)?\s*\)")


def join(*parts):
    segs = [s for p in parts for s in p.split("/") if s]
    return "/" + "/".join(segs)


def next_app(root):
    for p in sorted(root.rglob("page.*")):
        if p.suffix not in PAGE_EXT or "node_modules" in p.parts:
            continue
        segs = p.parent.relative_to(root).parts
        if any(s.startswith(("(.", "_")) for s in segs):
            continue
        keep = [s for s in segs if not (s.startswith("(") and s.endswith(")")) and not s.startswith("@")]
        yield join(*keep), p


def tanstack(gen_file):
    text = gen_file.read_text()
    for name in ("FileRoutesByTo", "FileRoutesByFullPath"):
        m = re.search(rf"interface {name} \{{(.*?)\n\}}", text, re.S)
        if m:
            for path in re.findall(r"^\s*'([^']+)'\s*:", m.group(1), re.M):
                path = re.sub(r"/\$(?=/|$)", "/[...splat]", path)
                # shortcut: the source is the generated tree, not each route file;
                # map `src/routes/**` per route if surface-level staleness needs it.
                yield join(re.sub(r"\$(\w+)", r"[\1]", path)), gen_file
            return


def nestjs(root):
    for f in sorted(root.rglob("*.ts")):
        if f.name.endswith((".spec.ts", ".test.ts", ".d.ts")) or "node_modules" in f.parts:
            continue
        text = f.read_text(errors="replace")
        if "@Controller" not in text:
            continue
        events = [(m.start(), "c", m.group(2) or m.group(4) or "") for m in CTRL.finditer(text)]
        events += [(m.start(), "m", m.group(2) or "") for m in METHOD.finditer(text)]
        prefix = None
        for _, kind, val in sorted(events):
            if kind == "c":
                prefix = val
            elif prefix is not None:
                yield re.sub(r":(\w+)", r"[\1]", join(prefix, val)), f


def cmd(command, repo):
    out = subprocess.run(command, shell=True, cwd=repo, capture_output=True, text=True, check=True)
    for line in out.stdout.splitlines():
        tok = line.strip().split()
        if tok and tok[0].startswith("/"):
            yield join(tok[0]), None


def inventory(harness, repo, allow_cmd=False):
    """({(app, route): set(source paths)}, set of apps inventoried, [notes])."""
    routes, done, notes = {}, set(), []
    for app in harness["apps"]:
        name, kind, root = app.get("name"), app.get("routes"), app.get("root")
        try:
            if kind == "cmd":
                if not allow_cmd:
                    notes.append(f"{name}: routes_cmd not run (pass --allow-cmd after reading it)")
                    continue
                found = cmd(app.get("routes_cmd", ""), repo)
            elif kind in ("next-app", "tanstack", "nestjs") and root:
                path = repo / root
                if not path.exists():
                    notes.append(f"{name}: root {root} not found under {repo}")
                    continue
                found = {"next-app": next_app, "tanstack": tanstack, "nestjs": nestjs}[kind](path)
            else:
                notes.append(f"{name}: unknown adapter {kind!r} or no root")
                continue
            for route, src in found:
                srcs = routes.setdefault((name, route), set())
                if src:
                    srcs.add(str(src.relative_to(repo)) if src.is_absolute() else str(src))
            done.add(name)
        except (OSError, subprocess.CalledProcessError) as e:
            notes.append(f"{name}: adapter failed: {e}")
    return routes, done, notes


def matches(route, surface):
    if surface.endswith("/*"):
        base = surface[:-2].rstrip("/")
        return route == (base or "/") or route.startswith(base + "/")
    return route == surface


def stale_since(repo, sha, files):
    """True when a commit after `sha` touched one of `files` (or sha is unknown)."""
    if not files:
        return False
    if not re.fullmatch(r"[0-9a-fA-F]{7,40}", sha or ""):
        return True  # bundle content is untrusted: never hand git an option-like sha
    r = subprocess.run(["git", "-C", str(repo), "log", "-1", "--format=%H", f"{sha}..HEAD", "--", *files],
                       capture_output=True, text=True)
    return r.returncode != 0 or bool(r.stdout.strip())


def features(bundle, harness, routes, done, repo):
    rows = []
    for f in sorted((bundle / "features").glob("*.md")):
        text = f.read_text()
        fm = frontmatter(text)
        if not fm or not re.search(r"^type:[ \t]*[\"']?Feature[\"']?[ \t]*$", fm, re.M):
            continue
        body = text[len(FM.match(text).group(0)):]
        surfaces = flow_list(fm, "surfaces")
        tests = str_list(fm, "tests") or []
        level, proof = feature_level(fm, body, harness)
        hit, missing = set(), []
        for s in surfaces:
            app, route = s.get("app"), s.get("route", "")
            if app not in done:
                continue  # app not inventoried: nothing to check against
            keys = [k for k in routes if k[0] == app and matches(k[1], route)]
            hit.update(keys)
            if not keys:
                missing.append(f"{app}:{route}")
        last = "-"
        if proof:
            last = proof.get("at", "?")[:10]
            files = sorted({src for k in hit for src in routes[k]})
            if stale_since(repo, proof.get("sha", ""), files):
                level, last = drive_level(fm, body), last + " (stale)"
        rows.append({"feature": f.stem, "level": level, "hit": hit,
                     "apps": sorted({s.get("app", "?") for s in surfaces}),
                     "roles": str_list(fm, "roles") or [], "e2e": len(tests), "last": last,
                     "missing": missing, "no_test": [t for t in tests if not (repo / t).exists()]})
    return rows


def main(argv):
    if "--self-test" in argv:
        return self_test()
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    bundle = pathlib.Path(args[0])
    repo = pathlib.Path(argv[argv.index("--repo") + 1] if "--repo" in argv else ".").resolve()
    harness = load_harness(bundle)
    if harness is None:
        print(f"no VERIFICATION.md in {bundle}", file=sys.stderr)
        return 1
    routes, done, notes = inventory(harness, repo, "--allow-cmd" in argv)
    for n in notes:
        print("NOTE", n, file=sys.stderr)
    if "--features" not in argv:
        for (app, route), srcs in sorted(routes.items()):
            print(f"{app}\t{route}\t{','.join(sorted(srcs)) or '-'}")
        return 0
    rows = features(bundle, harness, routes, done, repo)
    owner = {}
    for r in rows:
        for k in r["hit"]:
            owner.setdefault(k, []).append(r["feature"])
    print("## routes\napp\troute\tfeatures")
    for k in sorted(routes):
        print(f"{k[0]}\t{k[1]}\t{','.join(owner.get(k, [])) or '-'}")
    print("\n## features\nfeature\tlevel\tapps\troles\te2e\tlast_proof\tsurfaces_without_route\ttests_missing")
    for r in rows:
        print("\t".join([r["feature"], r["level"], ",".join(r["apps"]) or "-", ",".join(r["roles"]) or "-",
                         str(r["e2e"]), r["last"], ",".join(r["missing"]) or "-", ",".join(r["no_test"]) or "-"]))
    unmapped = sum(1 for k in routes if k not in owner)
    print(f"\n{len(routes)} routes, {unmapped} unmapped; " +
          ", ".join(f"{lv}: {sum(r['level'] == lv for r in rows)}"
                    for lv in ("documented", "partly-drivable", "drivable", "proven")))
    return 0


def self_test():
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        repo = pathlib.Path(d)
        for p in ["web/app/(main)/page.tsx", "web/app/(main)/viager/[id]/page.tsx",
                  "web/app/@modal/(.)photo/page.tsx", "web/app/_lib/page.tsx", "web/app/api/x/route.ts"]:
            (repo / p).parent.mkdir(parents=True, exist_ok=True)
            (repo / p).write_text("")
        assert sorted(r for r, _ in next_app(repo / "web/app")) == ["/", "/viager/[id]"]
        (repo / "gen.ts").write_text("export interface FileRoutesByTo {\n  '/': typeof A\n"
                                     "  '/dossiers/$dossierId': typeof B\n  '/files/$': typeof C\n}\n")
        assert [r for r, _ in tanstack(repo / "gen.ts")] == ["/", "/dossiers/[dossierId]", "/files/[...splat]"]
        (repo / "api").mkdir()
        (repo / "api/a.controller.ts").write_text(
            "@Controller('auth')\nclass A {\n @Post('/login') a(){}\n @Get() b(){}\n}\n"
            "@Controller({ path: 'offer', version: '1' })\nclass B {\n @Delete(':id') c(){}\n}\n")
        assert sorted(r for r, _ in nestjs(repo / "api")) == ["/auth", "/auth/login", "/offer/[id]"]
        assert matches("/auth/login", "/auth/*") and matches("/auth", "/auth/*")
        assert not matches("/authx", "/auth/*") and not matches("/viager", "/viager/[id]")
        assert stale_since(repo, "--output=/tmp/x", ["a"])  # rejected before git runs
    print("self-test ok")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
