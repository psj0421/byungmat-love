"""
💘 병맛 연애 시뮬레이션 - "사랑은 타이밍, 근데 내 타이밍은 고장남"
실행: python byungmat_love.py   (tkinter는 파이썬 기본 내장!)

캐릭터 그림: images 폴더에 PNG를 넣으면 그 그림이 나오고,
            없으면 tkinter Canvas로 직접 그린 얼굴이 나온다. (images/README.txt 참고)
"""
import math
import os
import random
import sys
import time
import tkinter as tk

# ─────────────────────────────────────────────
# 게임 설정 (난이도: 지옥)
# ─────────────────────────────────────────────
START_SCORE = 10        # 시작 호감도 (예전엔 30이었음)
TRUE_SCORE = 100        # TRUE 엔딩에 필요한 호감도
PIGEON_GOAL = 4         # 비둘기 히든 엔딩에 필요한 비둘기 게이지
TIME_LIMIT = 5          # 선택지 고르는 제한 시간(초)
TIMEOUT_PENALTY = -15   # 시간 초과 시 호감도 변화
EVENT_CHANCE = 0.35     # 챕터가 끝날 때마다 돌발 이벤트가 터질 확률

WINDOW_W, WINDOW_H = 640, 680
ART_SIZE = 130          # 캐릭터 그림 칸 크기(정사각형, px)
BG = "#fff0f5"
FONT = "맑은 고딕"


def resource_path(relative):
    """파일 위치 찾기. exe로 묶이면 임시 폴더(sys._MEIPASS)에 풀리기 때문에 따로 처리한다"""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)


IMAGE_DIR = resource_path("images")


# ─────────────────────────────────────────────
# 한국어 조사 자동 처리 (철수"가" / 민준"이")
# ─────────────────────────────────────────────
def has_batchim(word):
    if not word:          # 빈 문자열이면 마지막 글자가 없으니 받침도 없음
        return False
    ch = word[-1]
    if '가' <= ch <= '힣':
        return (ord(ch) - ord('가')) % 28 != 0
    return False


def fill(text, name):
    b = has_batchim(name)
    rep = {
        "{N}": name,
        "{N이}": name + ("이" if b else "가"),
        "{N은}": name + ("은" if b else "는"),
        "{N을}": name + ("을" if b else "를"),
        "{N과}": name + ("과" if b else "와"),
        "{N아}": name + ("아" if b else "야"),
    }
    for k, v in rep.items():
        text = text.replace(k, v)
    return text


# ─────────────────────────────────────────────
# 상대 캐릭터
# ─────────────────────────────────────────────
CHARACTERS = {
    "남": {"name": "김철수", "emoji": "🧔", "file": "male",
           "desc": "3대 500 치는 게 인생 목표. 닭가슴살을 반려동물처럼 아낀다.",
           "quirk": "닭가슴살"},   # {Q} 자리에 들어가는 단어
    "여": {"name": "이영희", "emoji": "👩", "file": "female",
           "desc": "민트초코 광신도. 반민초파를 보면 조용히 수첩에 이름을 적는다.",
           "quirk": "민트초코"},
}


def scene_text(text, gender, name):
    """대사에 캐릭터 취향({Q})과 이름+조사({N이} 등)를 채워 넣는다"""
    return fill(text.replace("{Q}", CHARACTERS[gender]["quirk"]), name)


# ─────────────────────────────────────────────
# 장면 데이터 (대본)
# 선택지: (선택지 텍스트, 호감도 변화, 상대 반응[, 태그])
#   호감도가 (최소, 최대) 튜플이면 → 그 범위에서 랜덤! 운명은 주사위다
#   태그 "PIGEON" → 비둘기 게이지 +1
#   태그 "DEATH"  → 즉사! 바로 엔딩으로 간다
# ─────────────────────────────────────────────
SCENES = [
    {
        "title": "📚 Chapter 1. 운명적인 첫 만남",
        "text": "도서관에서 {N이} 책을 떨어뜨렸다.\n제목은 『연애하는 법 for Dummies』...",
        "choices": [
            ("조용히 주워준다", 5, "\"고마워...\" (근데 표지 본 거 들켰다고 생각 중)"),
            ("책 대신 내 학생증을 건넨다", 15, "\"...? 아 번호 주는 거야? ㅋㅋㅋ 너 미쳤구나\" (호감)"),
            ("같이 바닥에 눕는다", (-25, 20), "\"...너 뭐야?\" 사서 선생님이 다가오고 있다."),
            ("비둘기를 부른다 🐦", -5, "구구구. 창문으로 비둘기 3마리가 들어왔다. {N은} 왠지 비둘기를 쳐다보고 있다.", "PIGEON"),
        ],
    },
    {
        "title": "📱 Chapter 2. 첫 카톡",
        "text": "{N}: \"뭐해?\"\n\n세상에서 가장 어려운 질문이 도착했다.",
        "choices": [
            ("\"숨 쉬는 중\"", 0, "\"ㅋㅋ 나도\" ...대화가 끝났다. 위기다."),
            ("\"너 생각 ㅎ\"", 15, "\"ㅁㅊ ㅋㅋㅋㅋ\" (캡처해서 단톡방에 올렸다고 한다)"),
            ("3일 뒤 \"ㅇㅇ\"", -25, "{N}의 프로필 상태메시지가 '사람 보는 눈 기르는 중'으로 바뀌었다."),
            ("이모티콘 47개 연속 전송", (-35, 25), "알림이 47번 울렸다. {N}의 반응은 신만이 안다."),
        ],
    },
    {
        "title": "🗺️ Chapter 3. 첫 데이트 장소",
        "text": "드디어 첫 데이트! 어디로 갈까?",
        "choices": [
            ("분위기 좋은 파스타집", 5, "\"무난하네~\" 무난함은 연애에서 칭찬일까?"),
            ("다이소 3시간 투어", 15, "\"5천원으로 이렇게 행복할 수 있다니\" 의외로 대박."),
            ("우리 할머니 댁", (-30, 25), "할머니가 {N}에게 김치 3통을 싸주셨다. 진도가 너무 빠르다."),
            ("공원에서 비둘기 모이 주기 🐦", 0, "{N은} 비둘기를 보며 처음으로 진심으로 웃었다. 근데 나를 보고 웃은 건 아니다.", "PIGEON"),
        ],
    },
    {
        "title": "🍽️ Chapter 4. 밥값 계산의 시간",
        "text": "계산서가 테이블 위에 놓였다.\n둘 다 계산서를 쳐다본다. 정적이 흐른다.",
        "choices": [
            ("쿨하게 내가 낸다", 10, "\"다음엔 내가 살게!\" 다음이 있다! 다음이 있다고!!"),
            ("가위바위보로 결정", (-10, 15), "졌다. 근데 {N이} 웃어서 괜찮다... 아마도."),
            ("화장실 간다고 하고 도망", 0, "{N은} 혼자 계산하며 인생을 돌아봤다. 그리고 당신을 모든 곳에서 차단했다.", "DEATH"),
            ("사장님께 설거지로 갚겠다고 한다", (-5, 20), "사장님: \"오 젊은이 좋아\" 둘이 같이 설거지했다. 이게 연애인가?"),
        ],
    },
    {
        "title": "💥 Chapter 5. 돌발 질문",
        "text": "{N이} 갑자기 진지하게 묻는다.\n\"너... {Q} 좋아해?\"",
        "choices": [
            ("\"당연하지. 내 인생이야\"", 20, "\"...너 나랑 결혼할래?\" (농담이겠지?)"),
            ("\"그거 먹는 사람 이해 안 됨\"", -40, "{N}의 눈빛이 차갑게 식었다. 수첩에 무언가를 적는다."),
            ("\"너만큼은 좋아해\"", 5, "\"으 오글거려\" 라면서 귀가 빨개졌다."),
            ("\"비둘기가 더 좋아\" 🐦", -10, "\"...사실 나도.\" 둘 사이에 묘한 공감대가 생겼다. 비둘기에 대한.", "PIGEON"),
        ],
    },
    {
        "title": "💔 Chapter 6. 전 애인 등장",
        "text": "카페에서 {N}의 전 애인이 다가온다.\n\"어? 오랜만이네~\"\n공기가 얼어붙었다.",
        "choices": [
            ("\"안녕하세요! 현 애인 후보입니다\"", 15, "{N이} 웃음을 참느라 어깨가 떨린다. 전 애인은 조용히 퇴장했다."),
            ("전 애인과 번호를 교환한다", 0, "{N}: \"......\" 그날 이후 {N}의 얼굴을 본 사람은 없다. 당신 포함.", "DEATH"),
            ("비둘기 소리로 위협한다 🐦", (-10, 15), "구구구구!! 전 애인은 도망갔고, 근처 비둘기들이 당신을 우두머리로 인정했다.", "PIGEON"),
            ("셋이 같이 노래방에 간다", (-25, 20), "3시간 동안 셋이 이별 노래만 불렀다. 분위기는 신만이 안다."),
        ],
    },
    {
        "title": "📝 Chapter 7. 시험 기간",
        "text": "{N이} 도서관에서 같이 공부하자고 한다.\n시험은 내일이다. 당신은 아직 1페이지도 안 봤다.",
        "choices": [
            ("진짜 열심히 공부한다", 10, "\"공부하는 모습 멋있다\" 근데 시험은 망했다."),
            ("{N}의 필기를 몰래 찍어 간다", -20, "\"...내 필기가 목적이었구나\" 차가운 눈빛. 근데 필기는 완벽했다."),
            ("공부 대신 {N}의 얼굴을 그린다", (-25, 25), "그림 실력이 처참하다. {N이} 그림을 보고 3분간 말이 없다."),
            ("\"시험 문제 유출본 있는데 볼래?\"", 0, "{N이} 학과 사무실에 신고했다. 학점과 연애가 동시에 F가 되었다.", "DEATH"),
        ],
    },
    {
        "title": "🎁 Chapter 8. 만난 지 100일",
        "text": "사귀지도 않는데 만난 지 100일이다.\n{N이} 은근히 선물을 기대하는 눈치다.",
        "choices": [
            ("손편지 10장", 10, "\"글씨가 너무 못생겨서 감동이야\" ...칭찬인가?"),
            ("다이소 5천원 선물 세트", (-20, 20), "포장지가 다이소 봉투 그대로다. 성의는 반반."),
            ("내 증명사진을 액자에 넣어 준다", -30, "\"...이걸 어디에 걸어?\" {N}의 방 구석에서 액자가 뒤집혀 있다."),
            ("{Q} 1년치 정기배송", 20, "\"너... 날 진짜 아는구나\" 택배 기사님이 매일 운다."),
        ],
    },
    {
        "title": "👨‍👩‍👧 Chapter 9. 갑자기 상견례",
        "text": "사귀지도 않았는데 {N}의 부모님이 식사하자고 하신다.\n아버님이 말없이 소주잔을 내민다.",
        "choices": [
            ("두 손으로 받고 원샷", 10, "아버님: \"좋아.\" 어머님: \"근데 쟤 누구니?\""),
            ("사이다로 바꿔서 원샷", (-5, 15), "아버님이 사이다로 건배해 주셨다. 묘하게 감동적이다."),
            ("아버님께 3대 몇 치시냐고 묻는다", (-30, 30), "아버님이 갑자기 팔씨름을 신청했다. 승패는 운명에 맡긴다."),
            ("\"아버님, 저 사실 비둘기를 사랑합니다\" 🐦", -20, "식탁에 정적이 흘렀다. 창밖에서 비둘기가 고개를 끄덕였다.", "PIGEON"),
        ],
    },
    {
        "title": "💌 Chapter 10. 운명의 고백",
        "text": "벚꽃이 흩날리는 (사실 11월이라 낙엽인) 밤.\n고백할 시간이다.",
        "choices": [
            ("진지하게 \"좋아해. 사귀자\"", 10, "{N은} 잠시 고민하더니 고개를 끄덕... 일까?"),
            ("즉석 프리스타일 랩 고백", (-30, 35), "\"Yo 너는 나의 빛 나의 와이파이~\" 지나가던 행인이 박수를 쳤다."),
            ("PPT 30장으로 연애 제안서 발표", 20, "\"7페이지 SWOT 분석에서 감동받았어\" 공대생 감성 통했다."),
            ("\"근데 너 혹시... 부업 관심 있어?\"", 0, "{N}의 표정이 굳었다. 고백이 아니라 다단계였다.", "DEATH"),
        ],
    },
]

# ─────────────────────────────────────────────
# 랜덤 돌발 이벤트 (챕터 사이에 EVENT_CHANCE 확률로 발생)
#   delta: 호감도 변화(숫자 또는 범위), pigeon: True면 비둘기 게이지 +1
# ─────────────────────────────────────────────
EVENTS = [
    {"title": "🌧️ 갑자기 비가 온다",
     "text": "우산이 하나뿐이다.\n근데 그 우산이 3단 접이식 미니 우산이다.",
     "delta": (-10, 15), "pigeon": False},
    {"title": "🐦 비둘기 습격",
     "text": "비둘기 떼가 둘을 습격했다.\n{N이} 당신 뒤에 숨었다. 비둘기들이 당신을 기억했다.",
     "delta": 5, "pigeon": True},
    {"title": "📞 엄마한테 전화 옴",
     "text": "엄마: \"밥은 먹었니? 옆에 누구니? 바꿔 봐.\"\n{N이} 당황해서 \"안녕하세요 어머님\"이라고 했다.",
     "delta": (-15, 15), "pigeon": False},
    {"title": "💩 하늘에서 축복이",
     "text": "하늘에서 새똥이 떨어졌다.\n정확히 당신 정수리에. {N이} 휴지를 건넸다.",
     "delta": -10, "pigeon": False},
    {"title": "💸 길에서 만원을 주웠다",
     "text": "{N이} 경찰서에 갖다주자고 해서 갖다줬다.\n착한 사람 인증 완료.",
     "delta": 10, "pigeon": False},
    {"title": "📸 단톡방 박제",
     "text": "당신의 셀카가 학과 단톡방에 올라갔다.\n올린 사람도, 이유도 아무도 모른다.",
     "delta": -15, "pigeon": False},
]

# 앞부분만 f-string: {N}은 나중에 fill()이 채워야 해서 일반 문자열로 이어 붙인다
TIMEOUT_REACTION = (f"당신이 고민하는 사이 {TIME_LIMIT}초가 지났다.\n"
                    + "{N}: \"...? 읽씹이야?\"")


# ─────────────────────────────────────────────
# 작은 도우미 함수들 (테스트하기 쉽게 화면과 분리)
# ─────────────────────────────────────────────
def choice_tag(choice):
    """선택지의 4번째 값(태그)을 돌려준다. 없으면 None"""
    return choice[3] if len(choice) > 3 else None


def roll_delta(delta, rng=random):
    """호감도 변화량 결정. 튜플이면 그 범위에서 랜덤으로 뽑는다"""
    if isinstance(delta, tuple):
        return rng.randint(*delta)
    return delta


def pick_event(rng=random, chance=EVENT_CHANCE):
    """chance 확률로 돌발 이벤트 하나를 고른다. 안 터지면 None"""
    if rng.random() < chance:
        return rng.choice(EVENTS)
    return None


def mood_for(delta):
    """호감도 변화량 → 캐릭터 표정 (happy / sad / normal)"""
    if delta > 0:
        return "happy"
    if delta < 0:
        return "sad"
    return "normal"


# ─────────────────────────────────────────────
# 엔딩
# ─────────────────────────────────────────────
def get_ending(score, pigeon, name, dead=False):
    if dead:
        return ("💀 즉사 엔딩: 게임 오버",
                fill("{N과}의 연애는 시작도 전에 끝났다.\n"
                     "선택 하나로 인생이 바뀔 수 있다는 걸 배웠다.\n\n"
                     "(교훈: 말하기 전에 3초만 생각하자)", name), "#000000")
    if pigeon >= PIGEON_GOAL:
        return ("🐦 히든 엔딩: 비둘기와의 사랑",
                fill("{N은} 결국 비둘기 '구구'와 사귀게 되었다.\n"
                     "결혼식 축가는 당신이 불렀다.\n\n"
                     "...사랑은 원래 예측 불가능한 거야.", name), "#8e8e8e")
    if score >= TRUE_SCORE:
        return ("💖 TRUE 엔딩: 우리 사귀는 거 맞지?",
                fill("{N}: \"너 진짜 이상한데... 그게 좋아.\"\n\n"
                     "100일 기념으로 다이소에서 커플템을 샀다.\n"
                     "총액 4,000원. 행복은 가격순이 아니다.", name), "#ff4d88")
    if score >= 60:
        return ("💛 노멀 엔딩: 썸의 무한루프",
                fill("{N}: \"우리... 좀 더 알아가 보자?\"\n\n"
                     "그 '좀 더'가 2년째다.\n"
                     "친구들은 이제 그냥 사귀라고 한다.", name), "#f5b041")
    if score >= 30:
        return ("💚 친구 엔딩: 넌 좋은 사람이야",
                fill("{N}: \"넌 진짜 좋은 친구야!\"\n\n"
                     "그리고 {N은} 3개월 뒤 다른 사람과 사귀었다.\n"
                     "축하 메시지는 당신이 제일 먼저 보냈다.", name), "#58d68d")
    if score >= 0:
        return ("💙 읽씹 엔딩: 1이 사라지지 않아",
                "카톡을 보냈다.\n1이 사라졌다.\n답장이 없다.\n\n"
                "그렇게 겨울이 왔다. ❄️", "#5dade2")
    return ("🚨 배드 엔딩: 차단당했습니다",
            fill("{N}에게 차단당했다.\n인스타도, 카톡도, 당근마켓도.\n\n"
                 "학과 단톡방에 당신의 이름이 '주의 인물'로 공유되었다.", name), "#2c3e50")


# ─────────────────────────────────────────────
# 캐릭터 그림 1: PNG 이미지 (있을 때만)
# ─────────────────────────────────────────────
def load_character_image(gender, mood, folder=None):
    """images/male_happy.png 같은 파일을 불러온다. 없거나 깨졌으면 None.
    ART_SIZE보다 크면 정수배로 줄인다(subsample: 2면 1/2 크기)."""
    folder = folder or IMAGE_DIR
    path = os.path.join(folder, f"{CHARACTERS[gender]['file']}_{mood}.png")
    if not os.path.exists(path):
        return None
    try:
        img = tk.PhotoImage(file=path)
    except tk.TclError:
        # 파일은 있는데 PNG가 아니거나 깨진 경우 → Canvas 그림으로 대신 보여준다
        return None
    factor = math.ceil(max(img.width(), img.height()) / ART_SIZE)
    if factor > 1:
        img = img.subsample(factor)
    return img


# ─────────────────────────────────────────────
# 캐릭터 그림 2: Canvas로 직접 그리기 (이미지가 없을 때)
#   130x130 칸 안에 원·다각형으로 얼굴을 그린다
# ─────────────────────────────────────────────
def draw_heart(c, x, y, size, color):
    """(x, y)를 가운데로 하는 하트 하나"""
    r = size / 2
    c.create_oval(x - size, y - r, x, y + r, fill=color, width=0)
    c.create_oval(x, y - r, x + size, y + r, fill=color, width=0)
    c.create_polygon(x - size, y, x + size, y, x, y + size * 1.3, fill=color, width=0)


def draw_face(c, gender, mood, pigeon=0):
    c.delete("all")
    skin = "#cfe3ff" if mood == "sad" else "#ffe0bd"   # 슬프면 얼굴이 파래짐
    if gender == "여":
        c.create_oval(18, 14, 112, 128, fill="#8b5a2b", width=0)          # 긴 머리
    c.create_oval(30, 26, 100, 106, fill=skin, outline="#d9a77c", width=2)  # 얼굴
    if gender == "여":
        c.create_arc(28, 18, 102, 80, start=0, extent=180, fill="#8b5a2b", width=0)  # 앞머리
    else:
        # 뾰족 머리 + 지그재그 앞머리 (점들을 이어서 다각형 하나로 그림)
        c.create_polygon(28, 64, 28, 38, 36, 14, 50, 26, 63, 4, 76, 24, 90, 10, 102, 38,
                         102, 64, 94, 44, 84, 48, 74, 38, 64, 48, 54, 38, 44, 48, 36, 44,
                         fill="#222222", width=0)
        c.create_text(112, 30, text="✨", font=(FONT, 14))                    # 잘생김 효과

    if mood == "happy":
        draw_heart(c, 50, 58, 8, "#ff4d88")                                   # 하트 눈
        draw_heart(c, 80, 58, 8, "#ff4d88")
        c.create_oval(36, 72, 50, 80, fill="#ffaac4", width=0)                # 볼 빨개짐
        c.create_oval(80, 72, 94, 80, fill="#ffaac4", width=0)
        c.create_arc(52, 70, 78, 96, start=180, extent=180, fill="#c0392b", width=0)  # 활짝 웃음
    elif mood == "sad":
        c.create_line(42, 56, 56, 62, width=3)                                # 처진 눈
        c.create_line(88, 56, 74, 62, width=3)
        c.create_rectangle(46, 64, 52, 120, fill="#5dade2", width=0)          # 폭포 눈물(병맛)
        c.create_rectangle(78, 64, 84, 120, fill="#5dade2", width=0)
        c.create_arc(54, 84, 76, 100, start=0, extent=180, style="arc", width=3)  # 시무룩
    else:
        for x in (50, 80):                                                    # 반짝이는 큰 눈
            c.create_oval(x - 7, 50, x + 7, 68, fill="#333333", width=0)
            c.create_oval(x - 4, 53, x, 58, fill="white", width=0)
        if gender == "여":
            c.create_line(42, 50, 38, 45, width=2)                            # 속눈썹
            c.create_line(88, 50, 92, 45, width=2)
        c.create_arc(55, 76, 75, 92, start=180, extent=180, style="arc", width=3)  # 미소

    if pigeon:                                                                # 머리 위 비둘기
        c.create_oval(48, 2, 82, 22, fill="#9e9e9e", width=0)
        c.create_oval(76, 0, 90, 12, fill="#7d7d7d", width=0)
        c.create_polygon(90, 5, 97, 7, 90, 9, fill="#f39c12", width=0)
        c.create_text(22, 10, text="구구" * min(pigeon, 2), font=(FONT, 8), fill="#666")


# ─────────────────────────────────────────────
# 게임 본체 (화면 담당)
# ─────────────────────────────────────────────
class LoveGame:
    def __init__(self, root, rng=None):
        self.root = root
        self.rng = rng or random.Random()   # 테스트에서 결과를 고정하려고 주입 가능
        root.title("💘 병맛 연애 시뮬레이션")
        root.geometry(f"{WINDOW_W}x{WINDOW_H}")
        root.configure(bg=BG)
        root.resizable(False, False)
        self.frame = None
        self.timer_id = None
        self.finished = False
        self.art_image = None   # PhotoImage는 변수에 잡아두지 않으면 사라진다(그림이 안 보임)
        self.show_start()

    # 화면 비우기 (돌던 타이머도 같이 멈춘다)
    def clear(self):
        self.stop_timer()
        if self.frame:
            self.frame.destroy()
        self.frame = tk.Frame(self.root, bg=BG)
        self.frame.pack(fill="both", expand=True, padx=20, pady=15)

    def btn(self, text, cmd, color="#ff85a2"):
        b = tk.Button(self.frame, text=text, command=cmd, font=(FONT, 12),
                      bg=color, fg="white", activebackground="#ff5c8a",
                      relief="flat", cursor="hand2", wraplength=560, pady=6)
        b.pack(fill="x", pady=4)
        return b

    def text_box(self, text, size=12):
        tk.Label(self.frame, text=text, font=(FONT, size), bg="white",
                 wraplength=560, justify="center", padx=15, pady=14,
                 relief="groove").pack(fill="x", pady=(0, 10))

    # ── 캐릭터 그림 (PNG 있으면 PNG, 없으면 Canvas 그림) ──
    def draw_art(self, parent, gender, mood):
        self.art_canvas = tk.Canvas(parent, width=ART_SIZE, height=ART_SIZE,
                                    bg=BG, highlightthickness=0)
        self.art_image = load_character_image(gender, mood)
        if self.art_image:
            self.art_canvas.create_image(ART_SIZE // 2, ART_SIZE // 2, image=self.art_image)
        else:
            draw_face(self.art_canvas, gender, mood, getattr(self, "pigeon", 0))
        return self.art_canvas

    # ── 위쪽 줄: 왼쪽 캐릭터 그림 + 오른쪽 호감도 바 ──
    def draw_header(self, mood):
        row = tk.Frame(self.frame, bg=BG)
        row.pack(fill="x", pady=(0, 8))
        self.draw_art(row, self.g, mood).pack(side="left")
        right = tk.Frame(row, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=(12, 0))

        tk.Label(right, text=f"{CHARACTERS[self.g]['emoji']} {self.name}의 호감도",
                 font=(FONT, 10), bg=BG).pack(anchor="w")
        bar_w = WINDOW_W - 40 - ART_SIZE - 12
        c = tk.Canvas(right, width=bar_w, height=22, bg="#eee", highlightthickness=0)
        c.pack(anchor="w")
        val = max(0, min(TRUE_SCORE, self.score))
        color = "#ff4d88" if val >= 60 else "#f5b041" if val >= 30 else "#5dade2"
        c.create_rectangle(0, 0, bar_w * val / TRUE_SCORE, 22, fill=color, width=0)
        c.create_text(bar_w // 2, 11, text=f"{self.score} / {TRUE_SCORE}",
                      font=(FONT, 10, "bold"))
        if self.pigeon:
            tk.Label(right, text="🐦" * self.pigeon + "  비둘기 게이지... 뭔가 이상하다",
                     font=(FONT, 9), bg=BG, fg="#888").pack(anchor="w", pady=(4, 0))
        return right

    # ── 시작 화면 ──
    def show_start(self):
        self.clear()
        self.finished = False
        self.pigeon = 0
        tk.Label(self.frame, text="💘 사랑은 타이밍 💘", font=(FONT, 24, "bold"),
                 bg=BG, fg="#ff4d88").pack(pady=(5, 0))
        tk.Label(self.frame, text="(근데 내 타이밍은 고장남)  ·  난이도: 지옥 🔥",
                 font=(FONT, 11), bg=BG, fg="#999").pack(pady=(0, 10))

        # 다시 하기로 돌아와도 전에 고른 성별을 기억한다 (처음엔 "여")
        last_gender = getattr(self, "g", "여")
        self.gender = tk.StringVar(value=last_gender)
        self.name_var = tk.StringVar(value=CHARACTERS[last_gender]["name"])

        art_holder = tk.Frame(self.frame, bg=BG)
        art_holder.pack()
        self.desc_label = tk.Label(self.frame, text="", font=(FONT, 10), bg=BG,
                                   fg="#666", wraplength=520)

        def on_pick():
            g = self.gender.get()
            c = CHARACTERS[g]
            self.name_var.set(c["name"])
            self.desc_label.config(text=f"{c['emoji']} {c['desc']}")
            for w in art_holder.winfo_children():
                w.destroy()
            self.draw_art(art_holder, g, "normal").pack()

        row = tk.Frame(self.frame, bg=BG)
        row.pack(pady=5)
        for g, label in [("남", "🧔 남자"), ("여", "👩 여자")]:
            tk.Radiobutton(row, text=label, variable=self.gender, value=g,
                           command=on_pick, font=(FONT, 13), bg=BG,
                           selectcolor="#ffd6e0").pack(side="left", padx=20)
        self.desc_label.pack(pady=5)
        on_pick()

        tk.Label(self.frame, text="이름 바꾸기 (최애 이름 넣어도 됨 ㅋ)",
                 font=(FONT, 11), bg=BG).pack(pady=(10, 3))
        tk.Entry(self.frame, textvariable=self.name_var, font=(FONT, 13),
                 justify="center").pack()
        tk.Label(self.frame, text=f"⚠️ 선택지는 {TIME_LIMIT}초 안에! 즉사 선택지 주의!",
                 font=(FONT, 10), bg=BG, fg="#e74c3c").pack(pady=(10, 5))
        self.btn("💕 연애 시작 (책임은 안 짐)", self.start_game)

    def start_game(self):
        self.name = self.name_var.get().strip() or "익명"
        self.g = self.gender.get()
        self.score = START_SCORE
        self.pigeon = 0
        self.idx = 0
        self.dead = False
        self.finished = False
        self.show_scene()

    # ── 장면 화면 ──
    def show_scene(self):
        if self.dead or self.idx >= len(SCENES):
            return self.show_ending()
        self.clear()
        s = SCENES[self.idx]
        mood = "happy" if self.score >= 60 else "sad" if self.score < 0 else "normal"
        right = self.draw_header(mood)
        tk.Label(right, text=s["title"], font=(FONT, 15, "bold"),
                 bg=BG, fg="#ff4d88", wraplength=440, justify="left").pack(anchor="w", pady=(8, 0))

        self.text_box(scene_text(s["text"], self.g, self.name))
        self.timer_canvas = tk.Canvas(self.frame, width=WINDOW_W - 40, height=18,
                                      bg="#eee", highlightthickness=0)
        self.timer_canvas.pack(pady=(0, 8))

        choices = s["choices"][:]
        self.rng.shuffle(choices)  # 매번 순서 섞기 → 외워서 깨기 금지
        for ch in choices:
            self.btn(scene_text(ch[0], self.g, self.name), lambda c=ch: self.choose(c))
        self.start_timer()

    # ── 제한 시간 타이머 ──
    # after(ms, 함수)는 "ms 뒤에 이 함수 실행해 줘"라는 예약이다.
    # 0.1초마다 tick이 자기 자신을 다시 예약하면서 막대를 줄여 나간다.
    def start_timer(self):
        self.deadline = time.time() + TIME_LIMIT
        self.tick()

    def tick(self):
        left = max(0.0, self.deadline - time.time())
        w = (WINDOW_W - 40) * left / TIME_LIMIT
        self.timer_canvas.delete("all")
        self.timer_canvas.create_rectangle(0, 0, w, 18, width=0,
                                           fill="#e74c3c" if left < 2 else "#ffb347")
        self.timer_canvas.create_text((WINDOW_W - 40) // 2, 9, font=(FONT, 9, "bold"),
                                      text=f"⏰ {left:.1f}초 남음")
        if left <= 0:
            self.timer_id = None
            self.on_timeout()
        else:
            self.timer_id = self.root.after(100, self.tick)

    def stop_timer(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

    def on_timeout(self):
        self.stop_timer()
        self.score += TIMEOUT_PENALTY
        self.show_reaction(TIMEOUT_REACTION, TIMEOUT_PENALTY)

    # ── 선택 ──
    def choose(self, ch):
        self.stop_timer()
        tag = choice_tag(ch)
        if tag == "DEATH":
            self.dead = True
            return self.show_reaction(ch[2], 0)
        if tag == "PIGEON":
            self.pigeon += 1
        delta = roll_delta(ch[1], self.rng)
        self.score += delta
        self.show_reaction(ch[2], delta)

    # ── 반응 화면 ──
    def show_reaction(self, reaction, delta):
        self.clear()
        if self.dead:
            sign, col, face = "💀 즉사 선택지였습니다", "#000", "(x_x)"
            mood = "sad"
        elif delta > 0:
            sign, col, face = f"호감도 +{delta} 💗", "#ff4d88", self.rng.choice(["(*´▽`*)", "꺄아", "심쿵"])
            mood = "happy"
        elif delta < 0:
            sign, col, face = f"호감도 {delta} 💔", "#3498db", self.rng.choice(["(ㅠ_ㅠ)", "아...", "띠용"])
            mood = "sad"
        else:
            sign, col, face = "호감도 변화 없음 😐", "#888", "......?"
            mood = "normal"

        right = self.draw_header(mood)
        tk.Label(right, text=face, font=(FONT, 22), bg=BG).pack(anchor="w", pady=(6, 0))
        self.text_box(scene_text(reaction, self.g, self.name), size=13)
        tk.Label(self.frame, text=sign, font=(FONT, 15, "bold"), bg=BG, fg=col).pack(pady=10)

        self.idx += 1
        self.btn("다음 ▶", self.next_step)

    # 반응 화면 다음: 엔딩 / 돌발 이벤트 / 다음 장면 중 하나
    def next_step(self):
        if self.dead or self.idx >= len(SCENES):
            return self.show_ending()
        event = pick_event(self.rng)
        if event:
            return self.show_event(event)
        self.show_scene()

    # ── 돌발 이벤트 화면 ──
    def show_event(self, event):
        self.clear()
        delta = roll_delta(event["delta"], self.rng)
        self.score += delta
        if event["pigeon"]:
            self.pigeon += 1
        right = self.draw_header(mood_for(delta))
        tk.Label(right, text="⚡ 돌발 이벤트 발생!", font=(FONT, 15, "bold"),
                 bg=BG, fg="#e67e22").pack(anchor="w", pady=(8, 0))
        tk.Label(self.frame, text=event["title"], font=(FONT, 15, "bold"),
                 bg=BG, fg="#e67e22").pack(pady=(0, 8))
        self.text_box(scene_text(event["text"], self.g, self.name), size=13)
        sign = f"호감도 {delta:+d}" if delta else "호감도 변화 없음"
        tk.Label(self.frame, text=sign, font=(FONT, 15, "bold"), bg=BG,
                 fg="#ff4d88" if delta > 0 else "#3498db").pack(pady=8)
        self.btn("어쩔 수 없지... 다음 ▶", self.show_scene)

    # ── 엔딩 화면 ──
    def show_ending(self):
        self.clear()
        self.finished = True
        title, body, color = get_ending(self.score, self.pigeon, self.name, self.dead)
        self.ending_title = title
        if self.dead or self.score < 30:
            mood = "sad"
        elif self.score >= TRUE_SCORE and self.pigeon < PIGEON_GOAL:
            mood = "happy"
        else:
            mood = "normal"
        tk.Label(self.frame, text="- THE END -", font=(FONT, 12), bg=BG, fg="#aaa").pack()
        self.draw_art(self.frame, self.g, mood).pack()
        tk.Label(self.frame, text=title, font=(FONT, 17, "bold"), bg=BG,
                 fg=color, wraplength=580).pack(pady=8)
        self.text_box(body)
        result = "중간에 즉사" if self.dead else f"최종 호감도: {self.score}"
        tk.Label(self.frame, text=result, font=(FONT, 12, "bold"), bg=BG).pack(pady=(0, 8))
        self.btn("🔄 다시 하기 (다른 엔딩 보러 가기)", self.show_start)
        self.btn("🚪 현실로 돌아가기 (과제하러...)", self.root.destroy, color="#aaa")


if __name__ == "__main__":
    root = tk.Tk()
    LoveGame(root)
    root.mainloop()
