"""
💘 병맛 연애 시뮬레이션 - "사랑은 타이밍, 근데 내 타이밍은 고장남"
실행: python byungmat_love.py   (tkinter는 파이썬 기본 내장!)
"""
import tkinter as tk
import random

# ─────────────────────────────────────────────
# 한국어 조사 자동 처리 (철수"가" / 영희"가" / 민준"이")
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
    "남": {"name": "김철수", "emoji": "🧔",
           "desc": "3대 500 치는 게 인생 목표. 닭가슴살을 반려동물처럼 아낀다.",
           "quirk": "닭가슴살"},   # Chapter 5의 {Q} 자리에 들어가는 단어
    "여": {"name": "이영희", "emoji": "👩",
           "desc": "민트초코 광신도. 반민초파를 보면 조용히 수첩에 이름을 적는다.",
           "quirk": "민트초코"},
}

# ─────────────────────────────────────────────
# 장면 데이터
# 선택지: (선택지 텍스트, 호감도 변화, 상대 반응)
#   호감도가 (최소, 최대) 튜플이면 → 랜덤! 운명은 주사위다
#   "PIGEON" 태그가 붙으면 비둘기 히든 엔딩 게이지 상승
# ─────────────────────────────────────────────
SCENES = [
    {
        "title": "📚 Chapter 1. 운명적인 첫 만남",
        "text": "도서관에서 {N이} 책을 떨어뜨렸다.\n제목은 『연애하는 법 for Dummies』...\n\n당신의 선택은?",
        "choices": [
            ("조용히 주워준다", 10, "\"고마워...\" (근데 표지 본 거 들켰다고 생각 중)"),
            ("책 대신 내 학생증을 건넨다", 20, "\"...? 아 번호 주는 거야? ㅋㅋㅋ 너 미쳤구나\" (호감)"),
            ("같이 바닥에 눕는다", (-15, 25), "\"...너 뭐야?\" 사서 선생님이 다가오고 있다."),
            ("비둘기를 부른다 🐦", 0, "구구구. 창문으로 비둘기 3마리가 들어왔다. {N은} 왠지 비둘기를 쳐다보고 있다.", "PIGEON"),
        ],
    },
    {
        "title": "📱 Chapter 2. 첫 카톡",
        "text": "{N}: \"뭐해?\"\n\n세상에서 가장 어려운 질문이 도착했다.",
        "choices": [
            ("\"숨 쉬는 중\"", 5, "\"ㅋㅋ 나도\" ...대화가 끝났다. 위기다."),
            ("\"너 생각 ㅎ\"", 15, "\"ㅁㅊ ㅋㅋㅋㅋ\" (캡처해서 단톡방에 올렸다고 한다)"),
            ("3일 뒤 \"ㅇㅇ\"", -20, "{N}의 프로필 상태메시지가 '사람 보는 눈 기르는 중'으로 바뀌었다."),
            ("이모티콘 47개 연속 전송", (-30, 30), "알림이 47번 울렸다. {N}의 반응은 신만이 안다."),
        ],
    },
    {
        "title": "🗺️ Chapter 3. 첫 데이트 장소",
        "text": "드디어 첫 데이트! 어디로 갈까?",
        "choices": [
            ("분위기 좋은 파스타집", 10, "\"무난하네~\" 무난함은 연애에서 칭찬일까?"),
            ("다이소 3시간 투어", 20, "\"5천원으로 이렇게 행복할 수 있다니\" 의외로 대박."),
            ("우리 할머니 댁", (-20, 30), "할머니가 {N}에게 김치 3통을 싸주셨다. 진도가 너무 빠르다."),
            ("공원에서 비둘기 모이 주기 🐦", 5, "{N은} 비둘기를 보며 처음으로 진심으로 웃었다. 근데 나를 보고 웃은 건 아니다.", "PIGEON"),
        ],
    },
    {
        "title": "🍽️ Chapter 4. 밥값 계산의 시간",
        "text": "계산서가 테이블 위에 놓였다.\n둘 다 계산서를 쳐다본다. 정적이 흐른다.",
        "choices": [
            ("쿨하게 내가 낸다", 10, "\"다음엔 내가 살게!\" 다음이 있다! 다음이 있다고!!"),
            ("가위바위보로 결정", 15, "졌다. 근데 {N이} 웃어서 괜찮다."),
            ("화장실 간다고 하고 도망", -35, "{N은} 혼자 계산하며 인생을 돌아봤다."),
            ("사장님께 설거지로 갚겠다고 한다", (0, 25), "사장님: \"오 젊은이 좋아\" 둘이 같이 설거지했다. 이게 연애인가?"),
        ],
    },
    {
        "title": "💥 Chapter 5. 돌발 상황",
        "text": "{N이} 갑자기 진지하게 묻는다.\n\"너... {Q} 좋아해?\"",
        "choices": [
            ("\"당연하지. 내 인생이야\"", 20, "\"...너 나랑 결혼할래?\" (농담이겠지?)"),
            ("\"그거 먹는 사람 이해 안 됨\"", -40, "{N}의 눈빛이 차갑게 식었다. 수첩에 무언가를 적는다."),
            ("\"너만큼은 좋아해\"", 10, "\"으 오글거려\" 라면서 귀가 빨개졌다."),
            ("\"비둘기가 더 좋아\" 🐦", -5, "\"...사실 나도.\" 둘 사이에 묘한 공감대가 생겼다. 비둘기에 대한.", "PIGEON"),
        ],
    },
    {
        "title": "💌 Chapter 6. 운명의 고백",
        "text": "벚꽃이 흩날리는 (사실 11월이라 낙엽인) 밤.\n고백할 시간이다.",
        "choices": [
            ("진지하게 \"좋아해. 사귀자\"", 15, "{N은} 잠시 고민하더니 고개를 끄덕... 일까?"),
            ("즉석 프리스타일 랩 고백", (-25, 35), "\"Yo 너는 나의 빛 나의 와이파이~\" 지나가던 행인이 박수를 쳤다."),
            ("PPT 30장으로 연애 제안서 발표", 25, "\"7페이지 SWOT 분석에서 감동받았어\" 공대생 감성 통했다."),
            ("\"근데 너 혹시... 부업 관심 있어?\"", -60, "{N}의 표정이 굳었다. 고백이 아니라 다단계였다."),
        ],
    },
]

def scene_text(scene, gender, name):
    """장면 대사에 캐릭터 취향({Q})과 이름+조사({N이} 등)를 채워 넣는다"""
    text = scene["text"].replace("{Q}", CHARACTERS[gender]["quirk"])
    return fill(text, name)

# ─────────────────────────────────────────────
# 엔딩
# ─────────────────────────────────────────────
def get_ending(score, pigeon, name):
    if pigeon >= 3:
        return ("🐦 히든 엔딩: 비둘기와의 사랑",
                f"{fill('{N은}', name)} 결국 비둘기 '구구'와 사귀게 되었다.\n"
                "결혼식 축가는 당신이 불렀다.\n\n"
                "...사랑은 원래 예측 불가능한 거야.", "#8e8e8e")
    if score >= 80:
        return ("💖 TRUE 엔딩: 우리 사귀는 거 맞지?",
                fill("{N}: \"너 진짜 이상한데... 그게 좋아.\"\n\n"
                     "100일 기념으로 다이소에서 커플템을 샀다.\n"
                     "총액 4,000원. 행복은 가격순이 아니다.", name), "#ff4d88")
    if score >= 50:
        return ("💛 노멀 엔딩: 썸의 무한루프",
                fill("{N}: \"우리... 좀 더 알아가 보자?\"\n\n"
                     "그 '좀 더'가 2년째다.\n"
                     "친구들은 이제 그냥 사귀라고 한다.", name), "#f5b041")
    if score >= 20:
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
# 게임 본체
# ─────────────────────────────────────────────
BG = "#fff0f5"
FONT = "맑은 고딕"

class LoveGame:
    def __init__(self, root):
        self.root = root
        root.title("💘 병맛 연애 시뮬레이션")
        root.geometry("620x620")
        root.configure(bg=BG)
        root.resizable(False, False)
        self.frame = None
        self.show_start()

    # 화면 비우기
    def clear(self):
        if self.frame:
            self.frame.destroy()
        self.frame = tk.Frame(self.root, bg=BG)
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)

    def btn(self, text, cmd, color="#ff85a2"):
        b = tk.Button(self.frame, text=text, command=cmd, font=(FONT, 12),
                      bg=color, fg="white", activebackground="#ff5c8a",
                      relief="flat", cursor="hand2", wraplength=520, pady=8)
        b.pack(fill="x", pady=5)
        return b

    # ── 시작 화면 ──
    def show_start(self):
        self.clear()
        tk.Label(self.frame, text="💘 사랑은 타이밍 💘", font=(FONT, 24, "bold"),
                 bg=BG, fg="#ff4d88").pack(pady=(10, 0))
        tk.Label(self.frame, text="(근데 내 타이밍은 고장남)", font=(FONT, 11),
                 bg=BG, fg="#999").pack(pady=(0, 20))

        tk.Label(self.frame, text="공략할 상대를 고르세요", font=(FONT, 13, "bold"),
                 bg=BG).pack(pady=5)

        # 다시 하기로 돌아와도 전에 고른 성별을 기억한다 (처음엔 "여")
        last_gender = getattr(self, "g", "여")
        self.gender = tk.StringVar(value=last_gender)
        self.name_var = tk.StringVar(value=CHARACTERS[last_gender]["name"])
        self.desc_label = tk.Label(self.frame, text="", font=(FONT, 10), bg=BG,
                                   fg="#666", wraplength=500)

        def on_pick():
            c = CHARACTERS[self.gender.get()]
            self.name_var.set(c["name"])
            self.desc_label.config(text=f"{c['emoji']} {c['desc']}")

        row = tk.Frame(self.frame, bg=BG)
        row.pack(pady=5)
        for g, label in [("남", "🧔 남자"), ("여", "👩 여자")]:
            tk.Radiobutton(row, text=label, variable=self.gender, value=g,
                           command=on_pick, font=(FONT, 13), bg=BG,
                           selectcolor="#ffd6e0").pack(side="left", padx=20)
        self.desc_label.pack(pady=5)
        on_pick()

        tk.Label(self.frame, text="이름 바꾸기 (최애 이름 넣어도 됨 ㅋ)",
                 font=(FONT, 11), bg=BG).pack(pady=(15, 3))
        tk.Entry(self.frame, textvariable=self.name_var, font=(FONT, 13),
                 justify="center").pack()

        tk.Label(self.frame, text="", bg=BG).pack(pady=10)
        self.btn("💕 연애 시작 (책임은 안 짐)", self.start_game)

    def start_game(self):
        name = self.name_var.get().strip() or "익명"
        self.name = name
        self.g = self.gender.get()
        self.score = 30          # 기본 호감도
        self.pigeon = 0
        self.idx = 0
        self.show_scene()

    # ── 호감도 바 ──
    def draw_heart_bar(self):
        tk.Label(self.frame, text=f"{CHARACTERS[self.g]['emoji']} {self.name}의 호감도",
                 font=(FONT, 10), bg=BG).pack(anchor="w")
        c = tk.Canvas(self.frame, width=580, height=22, bg="#eee", highlightthickness=0)
        c.pack(pady=(0, 10))
        val = max(0, min(100, self.score))
        color = "#ff4d88" if val >= 60 else "#f5b041" if val >= 30 else "#5dade2"
        c.create_rectangle(0, 0, 5.8 * val, 22, fill=color, width=0)
        c.create_text(290, 11, text=f"{self.score} / 100", font=(FONT, 10, "bold"))

    # ── 장면 화면 ──
    def show_scene(self):
        if self.idx >= len(SCENES):
            return self.show_ending()
        self.clear()
        self.draw_heart_bar()
        s = SCENES[self.idx]
        tk.Label(self.frame, text=s["title"], font=(FONT, 16, "bold"),
                 bg=BG, fg="#ff4d88").pack(pady=(5, 10))
        tk.Label(self.frame, text=scene_text(s, self.g, self.name), font=(FONT, 12),
                 bg="white", wraplength=540, justify="center",
                 padx=15, pady=20, relief="groove").pack(fill="x", pady=(0, 15))

        choices = s["choices"][:]
        random.shuffle(choices)  # 매번 순서 섞기 → 재플레이 재미
        for ch in choices:
            self.btn(ch[0], lambda c=ch: self.choose(c))

    def choose(self, ch):
        delta = ch[1]
        if isinstance(delta, tuple):
            delta = random.randint(*delta)
        if len(ch) > 3 and ch[3] == "PIGEON":
            self.pigeon += 1
        self.score += delta
        self.show_reaction(ch[2], delta)

    # ── 반응 화면 ──
    def show_reaction(self, reaction, delta):
        self.clear()
        self.draw_heart_bar()
        if delta > 0:
            sign, col, face = f"호감도 +{delta} 💗", "#ff4d88", random.choice(["(*´▽`*)", "꺄아", "심쿵"])
        elif delta < 0:
            sign, col, face = f"호감도 {delta} 💔", "#3498db", random.choice(["(ㅠ_ㅠ)", "아...", "띠용"])
        else:
            sign, col, face = "호감도 변화 없음 😐", "#888", "......?"

        tk.Label(self.frame, text=face, font=(FONT, 28), bg=BG).pack(pady=(20, 5))
        tk.Label(self.frame, text=fill(reaction, self.name), font=(FONT, 13),
                 bg="white", wraplength=540, padx=15, pady=20,
                 relief="groove").pack(fill="x", pady=10)
        tk.Label(self.frame, text=sign, font=(FONT, 15, "bold"), bg=BG, fg=col).pack(pady=10)
        if self.pigeon:
            tk.Label(self.frame, text="🐦" * self.pigeon + "  (비둘기 게이지... 뭔가 이상하다)",
                     font=(FONT, 10), bg=BG, fg="#888").pack()

        self.idx += 1
        tk.Label(self.frame, text="", bg=BG).pack(pady=10)
        self.btn("다음 ▶", self.show_scene)

    # ── 엔딩 화면 ──
    def show_ending(self):
        self.clear()
        title, body, color = get_ending(self.score, self.pigeon, self.name)
        tk.Label(self.frame, text="- THE END -", font=(FONT, 12), bg=BG, fg="#aaa").pack(pady=(20, 5))
        tk.Label(self.frame, text=title, font=(FONT, 18, "bold"), bg=BG,
                 fg=color, wraplength=560).pack(pady=10)
        tk.Label(self.frame, text=body, font=(FONT, 12), bg="white",
                 wraplength=540, padx=15, pady=25, relief="groove").pack(fill="x", pady=10)
        tk.Label(self.frame, text=f"최종 호감도: {self.score}", font=(FONT, 12, "bold"),
                 bg=BG).pack(pady=10)
        self.btn("🔄 다시 하기 (다른 엔딩 보러 가기)", self.show_start)
        self.btn("🚪 현실로 돌아가기 (과제하러...)", self.root.destroy, color="#aaa")


if __name__ == "__main__":
    root = tk.Tk()
    LoveGame(root)
    root.mainloop()