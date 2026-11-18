# HANDOFF.md

## 프로젝트 한 줄 요약
Python tkinter 병맛 연애 시뮬레이션 (10챕터, 지옥 난이도, 7초 타이머, 즉사 선택지, 돌발 이벤트, 캐릭터 그림) — GitHub 업로드 완료: https://github.com/psj0421/byungmat-love

## 현재 상태
- 완료: 제출용 README(한눈에 보기 표, 스크린샷), 실행 방식을 exe → run.bat로 변경, v2 업데이트(그래픽·병맛·난이도), 테스트 37개, 기획서/README/CLAUDE.md 갱신, exe 재빌드 및 실행 확인, 로컬 커밋
- 진행 중: 없음 (GitHub 업로드 완료, Public)
- 테스트 현황: 37/37 통과

## 결정된 사항 (이유 포함)
- 그래픽은 "PNG 있으면 PNG, 없으면 Canvas 그림" (설계안 C) — 예쁜 일러스트는 이미지가 필요하지만, 이미지가 없어도 게임이 돌아가야 해서
- 난이도는 메뉴 없이 전체적으로 어렵게: 시작 10, TRUE 100, 즉사 4개, 타이머 7초(처음 5초였는데 플레이해 보니 너무 빡세서 늘림), 비둘기 히든 4개
- 난이도는 테스트로 증명: 랜덤 플레이 3000판에서 TRUE 10% 미만, 잘 고르면 TRUE 도달 가능
- 배포는 exe 대신 `run.bat` + 공식 Python — 다운로드한 exe를 안랩 V3가 "액세스 거부"로 막았음. 폴더를 바꿔도, 내가 빌드한 exe를 새로 복사해도 막힘(원래 있던 파일만 실행됨). setup.exe 설치파일도 서명 없는 exe라 같은 문제라서 제외. release/ 폴더는 저장소에서 삭제
- 엔딩 경계값 테스트의 기대값을 바꾼 건 사용자가 "어렵게"를 요청해서 요구사항이 바뀌었기 때문 (테스트 약화 아님)

## 다음에 할 일 (우선순위 순)
1. (완료) README 제출자 기입 — GitHub 웹에서 직접 수정함. 이후 작업 전엔 꼭 `git pull` 먼저
2. 7초로 늘린 뒤 다시 플레이해서 난이도 확인 (`TIME_LIMIT` 한 줄만 바꾸면 됨)
3. (선택) `images/`에 캐릭터 PNG 6장 넣기 (run.bat 방식은 다시 빌드할 필요 없음)
4. 아이디어: 엔딩 도감(json), 효과음, 타자 효과

## 주의할 점 / 알려진 문제
- `run.bat`, `build_exe.bat`은 반드시 CRLF + ASCII (테스트가 검사). Git Bash printf로 쓰면 `>nul`이 `>/dev/null`로 바뀌는 함정 있음. 저장소는 .gitattributes(*.bat eol=crlf)로 GitHub ZIP에서도 CRLF 유지 (ZIP 받아서 run.bat 실행까지 확인함)
- 이모지는 tkinter에서 흑백으로 보임 (Windows Tk 한계)
- PhotoImage는 PNG만 읽음, JPG 안 됨. 그리고 변수에 잡아두지 않으면 그림이 사라짐(`self.art_image`)
- 다운로드한 exe가 "액세스 거부"로 안 열림 → 안랩 V3 평판 기반 실행 차단으로 추정 (V3 MeD 로그에 기록, Defender/스마트 앱 컨트롤은 무관). → 그래서 run.bat 방식으로 변경. exe를 다시 배포하려면 코드 서명이 필요

## 관련 파일
- `byungmat_love.py`, `test_byungmat.py`, `run.bat`, `build_exe.bat`, `images/README.txt`, `docs/기획서.md`, `README.md`, `CLAUDE.md`
