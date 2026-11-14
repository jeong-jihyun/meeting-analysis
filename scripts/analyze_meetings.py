#!/usr/bin/env python3
"""회의록 txt 폴더를 읽어 효율성 수치를 계산한다.

사용법:
    python scripts/analyze_meetings.py meetings/sample
    python scripts/analyze_meetings.py meetings/sample --csv data/output/summary.csv
    python scripts/analyze_meetings.py meetings/sample --with "연구 개발 리드"

회의록 형식은 docs/meeting-format.md 참고.
표준 라이브러리만 사용한다 (설치 불필요).
"""
import argparse
import csv
import re
import sys
from collections import Counter
from pathlib import Path


def to_min(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def split_names(text: str) -> list[str]:
    return [x.strip() for x in text.split(",") if x.strip() and x.strip() != "없음"]


def parse(path: Path) -> dict:
    t = path.read_text(encoding="utf-8")

    def grab(pattern: str, default: str = "") -> str:
        m = re.search(pattern, t)
        return m.group(1).strip() if m else default

    time_m = re.search(r"시간:\s*(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})", t)
    dur = to_min(time_m.group(2)) - to_min(time_m.group(1)) if time_m else 0

    # "4. 결정사항" ~ "5. 후속 조치" 사이의 "- " 줄 개수
    dec_block = re.search(r"4\.\s*결정사항(.*?)(?=\n\s*5\.)", t, re.S)
    decisions = len(re.findall(r"^\s*-\s+\S", dec_block.group(1), re.M)) if dec_block else 0

    return {
        "file": path.name,
        "id": grab(r"회의 ID:\s*(\S+)"),
        "date": grab(r"날짜:\s*(\S+)"),
        "type": grab(r"회의 유형:\s*(\S+)"),
        "duration_min": dur,
        "attendees": split_names(grab(r"참석자:\s*(.+)")),
        "absentees": split_names(grab(r"불참자:\s*(.+)")),
        "topics": split_names(grab(r"주요 주제:\s*(.+)")),
        "decisions": decisions,
        "actions": len(re.findall(r"액션 아이템\d+:", t)),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder", help="회의록 txt가 들어 있는 폴더")
    ap.add_argument("--csv", help="요약표를 CSV로 저장할 경로")
    ap.add_argument("--with", dest="person", help="이 사람이 참석한 회의만 보기")
    args = ap.parse_args()

    files = sorted(Path(args.folder).glob("meeting_*.txt"))
    if not files:
        print(f"회의록(meeting_*.txt)을 찾지 못했습니다: {args.folder}", file=sys.stderr)
        return 1

    rows = [parse(f) for f in files]
    if args.person:
        rows = [r for r in rows if args.person in r["attendees"]]
        print(f"[{args.person}] 참석 회의만 분석합니다.")

    n = len(rows)
    if n == 0:
        print("조건에 맞는 회의가 없습니다.")
        return 0

    for r in rows:
        r["n_att"] = len(r["attendees"])
        hours = r["duration_min"] / 60 or 1
        r["efficiency"] = round((r["decisions"] + r["actions"]) / (hours * (r["n_att"] or 1)), 2)
        r["person_minutes"] = r["duration_min"] * r["n_att"]

    avg = lambda k: sum(r[k] for r in rows) / n
    print(f"회의 수: {n}")
    print(f"평균 시간: {avg('duration_min'):.1f}분 | 평균 참석자: {avg('n_att'):.1f}명 | 평균 효율지수: {avg('efficiency'):.2f}")
    print(f"인원x분 합계: {sum(r['person_minutes'] for r in rows):,}분")
    with_abs = sum(1 for r in rows if r["absentees"])
    print(f"불참자 발생: {with_abs}/{n}건")
    print("유형별:", dict(Counter(r["type"] for r in rows)))
    print("\n주제 빈도:")
    for topic, c in Counter(t for r in rows for t in r["topics"]).most_common():
        print(f"  {topic}: {c}회")

    if args.csv:
        out = Path(args.csv)
        out.parent.mkdir(parents=True, exist_ok=True)
        cols = ["id", "date", "type", "duration_min", "n_att", "decisions", "actions", "efficiency", "person_minutes"]
        with out.open("w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
        print(f"\nCSV 저장: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
