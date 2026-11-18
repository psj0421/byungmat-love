# HANDOFF.md

## 프로젝트 한 줄 요약
Python tkinter 병맛 연애 시뮬레이션 게임 (6챕터, 엔딩 6개) — 기획서·테스트·exe 포함해 GitHub 업로드 준비 완료.

## 현재 상태
- 완료: 코드 리뷰 및 개선 3건, 테스트 16개, 기획서(`docs/기획서.md`), README, exe 빌드(`build_exe.bat`), git 로컬 커밋
- 진행 중: GitHub 원격 저장소에 push, Releases에 exe 업로드
- 테스트 현황: 16/16 통과

## 결정된 사항 (이유 포함)
- 배포는 PyInstaller `--onefile` exe 1개 — 설치 과정이 없어서 받는 사람이 가장 쉽게 실행 가능
- exe는 git에 넣지 않고(`.gitignore`) GitHub **Releases**에 올림 — 13MB 바이너리를 커밋하면 저장소가 무거워짐
- 기획서는 Markdown — GitHub에서 바로 보임
- 개선 3건: 빈 이름에서 `has_batchim` 에러 방지 / `QUIRK_Q` 삭제하고 `CHARACTERS[...]["quirk"]` 하나로 통일(`scene_text` 함수 추가) / 다시 하기 시 고른 성별 유지

## 다음에 할 일 (우선순위 순)
1. GitHub에 push 후 Releases에 `dist/byungmat_love.exe` 업로드
2. 직접 플레이해서 엔딩 6개 다 보기 (특히 히든 엔딩)
3. CLAUDE.md의 아이디어 목록 (돌발 이벤트, 엔딩 도감 등)

## 주의할 점 / 알려진 문제
- `build_exe.bat`은 반드시 CRLF + 영어로 유지 (한글/LF면 cmd가 줄을 잘못 읽음)
- 서명 안 된 exe라 Windows SmartScreen 경고가 뜰 수 있음 → "추가 정보 → 실행"
- 폰트 `맑은 고딕`은 Windows 기준. 다른 OS에선 글꼴이 달라 보일 수 있음

## 관련 파일
- `byungmat_love.py`, `test_byungmat.py`, `build_exe.bat`, `docs/기획서.md`, `README.md`, `CLAUDE.md`
