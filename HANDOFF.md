# HANDOFF.md

## 프로젝트 한 줄 요약
Python tkinter 병맛 연애 시뮬레이션 (10챕터, 지옥 난이도, 7초 타이머, 즉사 선택지, 돌발 이벤트, 캐릭터 그림) — GitHub 업로드만 남음.

## 현재 상태
- 완료: v2 업데이트(그래픽·병맛·난이도), 테스트 34개, 기획서/README/CLAUDE.md 갱신, exe 재빌드 및 실행 확인, 로컬 커밋
- 진행 중: GitHub push (저장소 주소 대기), Releases에 exe 업로드
- 테스트 현황: 34/34 통과

## 결정된 사항 (이유 포함)
- 그래픽은 "PNG 있으면 PNG, 없으면 Canvas 그림" (설계안 C) — 예쁜 일러스트는 이미지가 필요하지만, 이미지가 없어도 게임이 돌아가야 해서
- 난이도는 메뉴 없이 전체적으로 어렵게: 시작 10, TRUE 100, 즉사 4개, 타이머 7초(처음 5초였는데 플레이해 보니 너무 빡세서 늘림), 비둘기 히든 4개
- 난이도는 테스트로 증명: 랜덤 플레이 3000판에서 TRUE 10% 미만, 잘 고르면 TRUE 도달 가능
- exe는 git에 넣지 않고 GitHub Releases에 올림 (13MB 바이너리)
- 엔딩 경계값 테스트의 기대값을 바꾼 건 사용자가 "어렵게"를 요청해서 요구사항이 바뀌었기 때문 (테스트 약화 아님)

## 다음에 할 일 (우선순위 순)
1. GitHub push → Releases에 `dist/byungmat_love.exe` 업로드
2. 7초로 늘린 뒤 다시 플레이해서 난이도 확인 (`TIME_LIMIT` 한 줄만 바꾸면 됨)
3. (선택) `images/`에 캐릭터 PNG 6장 넣고 `build_exe.bat` 다시 실행
4. 아이디어: 엔딩 도감(json), 효과음, 타자 효과

## 주의할 점 / 알려진 문제
- `build_exe.bat`은 반드시 CRLF + 영어로 유지 (한글/LF면 cmd가 줄을 잘못 읽음)
- 이모지는 tkinter에서 흑백으로 보임 (Windows Tk 한계)
- PhotoImage는 PNG만 읽음, JPG 안 됨. 그리고 변수에 잡아두지 않으면 그림이 사라짐(`self.art_image`)
- 서명 안 된 exe라 SmartScreen 경고 → "추가 정보 → 실행"

## 관련 파일
- `byungmat_love.py`, `test_byungmat.py`, `build_exe.bat`, `images/README.txt`, `docs/기획서.md`, `README.md`, `CLAUDE.md`
