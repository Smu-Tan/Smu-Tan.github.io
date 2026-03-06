#!/usr/bin/env python3
import re
from pathlib import Path

from scholarly import scholarly

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "_config.yml"
BIB = ROOT / "_bibliography" / "papers.bib"
OUT = ROOT / "_data" / "citations.yml"


def read_scholar_userid(path: Path) -> str:
    pattern = re.compile(r"^\s*scholar_userid\s*:\s*([^\s#]+)")
    for line in path.read_text(encoding="utf-8").splitlines():
        m = pattern.match(line)
        if m:
            return m.group(1).strip()
    raise RuntimeError("Could not find 'scholar_userid' in _config.yml")


def read_bib_google_ids(path: Path) -> set[str]:
    ids = set()
    pattern = re.compile(r"google_scholar_id\s*=\s*\{([^}]+)\}")
    for line in path.read_text(encoding="utf-8").splitlines():
        m = pattern.search(line)
        if m:
            ids.add(m.group(1).strip())
    return ids


def read_existing_counts(path: Path) -> dict[str, int]:
    if not path.exists():
        return {}
    counts: dict[str, int] = {}
    in_citations = False
    key_val = re.compile(r"^\s{2}([^:#\s][^:]*)\s*:\s*(\d+)\s*$")
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if line.strip() == "citations:":
            in_citations = True
            continue
        if not in_citations:
            continue
        m = key_val.match(line)
        if m:
            counts[m.group(1).strip()] = int(m.group(2))
    return counts


def normalize_citation_id(author_pub_id: str) -> str:
    if ":" in author_pub_id:
        return author_pub_id.split(":", 1)[1]
    return author_pub_id


def fetch_counts(scholar_userid: str, wanted_ids: set[str]) -> dict[str, int]:
    found: dict[str, int] = {}
    author = scholarly.search_author_id(scholar_userid)
    author = scholarly.fill(author, sections=["publications"])

    for pub in author.get("publications", []):
        author_pub_id = pub.get("author_pub_id", "")
        if not author_pub_id:
            continue

        normalized = normalize_citation_id(author_pub_id)
        candidates = {author_pub_id, normalized}

        if not (candidates & wanted_ids):
            continue

        detailed = scholarly.fill(pub)
        num = detailed.get("num_citations", pub.get("num_citations", 0)) or 0
        try:
            num = int(num)
        except Exception:
            num = 0

        if author_pub_id in wanted_ids:
            found[author_pub_id] = num
        if normalized in wanted_ids:
            found[normalized] = num

    return found


def write_counts(path: Path, counts: dict[str, int]) -> None:
    lines = ["citations:"]
    if not counts:
        lines.append("  {}")
    else:
        for k in sorted(counts):
            lines.append(f"  {k}: {counts[k]}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    scholar_userid = read_scholar_userid(CONFIG)
    wanted_ids = read_bib_google_ids(BIB)
    existing = read_existing_counts(OUT)

    if not wanted_ids:
        write_counts(OUT, {})
        print("No google_scholar_id entries found in papers.bib")
        return

    try:
        fetched = fetch_counts(scholar_userid, wanted_ids)
    except Exception as e:
        print(f"Warning: failed to fetch Google Scholar citations: {e}")
        fetched = {}

    merged = {k: fetched.get(k, existing.get(k, 0)) for k in wanted_ids}
    write_counts(OUT, merged)
    print(f"Updated citations for {len(merged)} entries")


if __name__ == "__main__":
    main()
