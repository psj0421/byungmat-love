# 💘 병맛 연애 시뮬레이션 (byungmat_love.py)

Python tkinter로 만든 병맛 연애 시뮬레이션 게임이에요. 진지한 연애물이 아니라 **웃긴 게 1순위**인 게임이에요.

## 사용자 정보
- AI융합소프트웨어과 1학년 학생
- 어려운 개념은 **비유를 들어서** 쉽게 설명해 주세요
- 답변이 길어지면 마지막에 **3줄 요약**을 붙여 주세요
- 답변은 한국어로 해 주세요

## 실행 방법
```bash
python byungmat_love.py
```
- 외부 라이브러리 없이 파이썬 기본 모듈(`tkinter`, `random`, `time`, `os`, `sys`, `math`)만 써요
- 창 크기는 640x680으로 고정되어 있고(`WINDOW_W`, `WINDOW_H`), 폰트는 `맑은 고딕`(Windows 기준)이에요

## 현재 상태
- ✅ 테스트 39개 통과 (`python -m unittest -v test_byungmat.py`): 조사, 엔딩 경계값, 장면 데이터, 난이도(랜덤 플레이 TRUE < 10%), 이벤트, 캐릭터 그림, 타이머, GUI 레이아웃, bat 파일 형식
- ✅ 배포 ①: `build_exe.bat` → 테스트 통과 시 `release/byungmat_love.exe`로 복사, git에 커밋해서 GitHub에서 바로 다운로드
- ✅ 배포 ②: `run.bat` 더블클릭 → 공식 Python(`pyw`/`pythonw`)으로 `byungmat_love.py` 실행. Python이 없으면 python.org 안내, `byungmat_love.py`가 옆에 없으면(run.bat만 따로 받은 경우) ZIP 받으라고 안내
- ⚠️ 서명 없는 exe라 안랩 V3가 "액세스 거부"로 막을 수 있음 → README에서 exe 먼저, 막히면 run.bat 안내
- ✅ README는 교수님 제출용: 맨 위 "제출물 한눈에 보기" 표 + 1분 확인 가이드 + 스크린샷(`docs/screenshots/`)
- 📄 기획서: `docs/기획서.md`, 인수인계: `HANDOFF.md`
- ✅ GitHub: https://github.com/psj0421/byungmat-love (Public, main 브랜치)

## 게임 흐름
```
시작 화면(상대 성별·이름 선택, 캐릭터 그림 미리보기)
  → 장면(Chapter 1~10, 7초 타이머) → 반응 화면 → (35% 확률) 돌발 이벤트 → 다음 장면 ...
  → 엔딩 화면 → 다시 하기 / 종료
  ※ 즉사 선택지를 고르면 반응 화면 다음에 바로 즉사 엔딩
```

## 게임 설정 (파일 맨 위 상수)
| 상수 | 값 | 뜻 |
|---|---|---|
| `START_SCORE` | 10 | 시작 호감도 |
| `TRUE_SCORE` | 100 | TRUE 엔딩 기준 |
| `PIGEON_GOAL` | 4 | 히든 엔딩에 필요한 비둘기 게이지 |
| `TIME_LIMIT` | 7 | 선택 제한 시간(초) |
| `TIMEOUT_PENALTY` | -15 | 시간 초과 감점 |
| `EVENT_CHANCE` | 0.35 | 돌발 이벤트 확률 |

## 코드 구조
대사·선택지 같은 **데이터**와 화면을 그리는 **로직**이 분리되어 있어요. 데이터는 대본, `LoveGame` 클래스는 그 대본을 연기하는 배우라고 생각하면 돼요.

| 이름 | 역할 |
|---|---|
| `has_batchim(word)` / `fill(text, name)` | 받침 확인 / `{N이}` 같은 태그에 이름과 알맞은 조사를 넣어요 |
| `CHARACTERS` | 남: 김철수(헬스광), 여: 이영희(민트초코 광신도). `quirk`는 `{Q}` 자리 단어, `file`은 이미지 파일 이름 앞부분 |
| `scene_text(text, gender, name)` | 대사에 `{Q}`와 이름+조사를 채워요 (장면·선택지·반응·이벤트 모두) |
| `SCENES` / `EVENTS` | 장면 10개 / 돌발 이벤트 6개 데이터 |
| `choice_tag`, `roll_delta`, `pick_event`, `mood_for` | 태그 읽기, 랜덤 점수, 이벤트 뽑기, 표정 고르기 |
| `get_ending(score, pigeon, name, dead)` | 엔딩 (제목, 본문, 색) 튜플 |
| `load_character_image` / `draw_face` | PNG 불러오기 / 없을 때 Canvas로 얼굴 그리기 |
| `LoveGame` | 화면 클래스 (`show_start` → `show_scene` → `show_reaction` → `next_step` → `show_event`/`show_ending`) |

## 장면 데이터 형식
```python
{
    "title": "📚 Chapter N. 제목",
    "text": "{N이} 어쩌고...",           # {N이} 같은 조사 태그, {Q} 사용 가능
    "choices": [                          # 4개 (테스트가 4개인지 검사함)
        ("선택지", 10, "반응"),             # 호감도 고정값
        ("선택지", (-20, 30), "반응"),      # 튜플이면 그 범위 안에서 랜덤
        ("선택지", 0, "반응", "PIGEON"),    # 비둘기 게이지 +1
        ("선택지", 0, "반응", "DEATH"),     # 즉사 → 바로 즉사 엔딩
    ],
}
```
**새 챕터를 넣을 때는 `SCENES`에 딕셔너리만 추가하면 돼요.** (테스트의 `챕터는_10개`도 같이 고치기)

## 엔딩 조건 (위에서부터 먼저 맞는 엔딩이 나와요)
| 조건 | 엔딩 |
|---|---|
| 즉사 선택지 고름 | 💀 즉사: 게임 오버 |
| 비둘기 게이지 ≥ 4 | 🐦 히든: 비둘기와의 사랑 |
| 호감도 ≥ 100 | 💖 TRUE: 우리 사귀는 거 맞지? |
| ≥ 60 | 💛 노멀: 썸의 무한루프 |
| ≥ 30 | 💚 친구: 넌 좋은 사람이야 |
| ≥ 0 | 💙 읽씹: 1이 사라지지 않아 |
| < 0 | 🚨 배드: 차단당했습니다 |

## 캐릭터 그림
- `images/male_happy.png`처럼 `{male|female}_{normal|happy|sad}.png`를 넣으면 PNG가 나오고, 없으면 Canvas 그림이 나와요 (`images/README.txt`)
- 연예인 사진·다른 작품 캐릭터는 저작권 문제로 쓰지 않기

## 다음에 해 볼 만한 것 (아이디어)
- [x] 실제 실행해서 레이아웃 확인 (테스트로 자동 확인)
- [x] 랜덤 돌발 이벤트
- [x] 캐릭터 이미지 넣기 (PNG 또는 Canvas)
- [ ] 캐릭터 추가 (성별 말고 캐릭터 자체를 고르기)
- [ ] 엔딩 도감: 본 엔딩을 `json` 파일로 저장해서 수집 요소 만들기
- [ ] 효과음 (`winsound`, Windows 전용) 또는 글자가 한 글자씩 나오는 타자 효과 (`after()` 사용)

## 작업 규칙
- 분위기는 계속 **병맛**으로 유지해 주세요 (진지한 대사가 나오면 반전을 주기)
- 대사에 이름이 들어가면 조사가 틀리지 않게 `{N이}` 같은 태그를 써 주세요
- 외부 라이브러리는 꼭 필요할 때만 쓰고, 쓰게 되면 설치 방법을 적어 주세요
- 1학년이 읽고 이해할 수 있게 주석은 한국어로 쉽게 달아 주세요
- `run.bat`, `build_exe.bat`은 CRLF + 영어(ASCII)로 유지 (한글/LF면 cmd가 줄을 잘못 읽음, 테스트가 검사함). Git Bash로 쓰면 `>nul`이 `>/dev/null`로 바뀌니 Python으로 쓸 것
