# meeting-analysis

회의록(텍스트)과 음성 파일을 정리하고, 회의 효율성을 분석하는 프로젝트입니다.
책 「MCP로 똑똑하게 일하는 법」 실습(filesystem MCP + Sequential Thinking MCP)을 바탕으로 만들었습니다.

## 폴더 구조

```
meeting-analysis/
├── audio/
│   ├── raw/          녹음 원본 (mp3, m4a, wav)        ← GitHub에 안 올라감
│   └── processed/    잡음 제거·변환한 음성             ← GitHub에 안 올라감
├── transcripts/
│   ├── raw/          클로바노트 등에서 받은 txt 원본    ← GitHub에 안 올라감
│   └── clean/        참석자·주제를 정리한 전사본
├── meetings/
│   └── sample/       형식 확인용 샘플 회의록 3건       ← GitHub에 올라감
├── scripts/          분석 스크립트
├── skills/           Claude 스킬 파일(SKILL.md)
├── docs/             회의록 형식 등 문서
└── data/output/      분석 결과 CSV                    ← GitHub에 안 올라감
```

## 어디에 무엇을 넣나

| 가진 파일 | 넣을 곳 |
|---|---|
| 회의 녹음 mp3/m4a | `audio/raw/` |
| 클로바노트에서 받은 txt | `transcripts/raw/` |
| 형식을 맞춘 회의록 `meeting_YYYYMMDD_ID.txt` | `meetings/` 아래 새 폴더 |
| 새로 만든 분석 코드 | `scripts/` |

## 빠른 시작

설치할 것이 없습니다. Python 3.9 이상이면 됩니다.

```bash
python scripts/analyze_meetings.py meetings/sample
python scripts/analyze_meetings.py meetings/sample --csv data/output/summary.csv
python scripts/analyze_meetings.py meetings/sample --with "연구 개발 리드"
```

출력: 회의 수, 평균 시간·참석자 수, 효율지수, 불참 발생 건수, 유형별 건수, 주제 빈도.

효율지수 = (결정사항 수 + 액션아이템 수) ÷ (회의 시간(시간) × 참석자 수)

## 개인정보 주의

음성 파일과 전사본에는 이름과 회사 내용이 들어 있습니다. `.gitignore`가 `audio/raw`, `audio/processed`, `transcripts/raw`, `data/output`을 자동으로 제외합니다. 이 폴더들은 PC에만 남으니, 따로 백업하세요.
