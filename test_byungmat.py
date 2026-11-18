"""
병맛 연애 시뮬레이션 테스트
실행: python -m unittest -v test_byungmat.py
(외부 라이브러리 없이 파이썬 기본 unittest만 사용)
"""
import os
import random
import tempfile
import time
import tkinter as tk
import unittest

import byungmat_love as game


class TestJosa(unittest.TestCase):
    """조사(이/가, 은/는 ...)가 이름에 맞게 붙는지 확인"""

    def test_받침_없는_이름(self):
        self.assertEqual(game.fill("{N이} {N은} {N을} {N과} {N아}", "철수"),
                         "철수가 철수는 철수를 철수와 철수야")

    def test_받침_있는_이름(self):
        self.assertEqual(game.fill("{N이} {N은} {N을} {N과} {N아}", "민준"),
                         "민준이 민준은 민준을 민준과 민준아")

    def test_영어_이름은_받침_없음으로_처리(self):
        self.assertFalse(game.has_batchim("Tom"))

    def test_빈_이름이어도_에러가_나지_않음(self):
        self.assertFalse(game.has_batchim(""))
        self.assertEqual(game.fill("{N}", ""), "")


class TestEnding(unittest.TestCase):
    """엔딩 판정 경계값 확인 (위에서부터 먼저 맞는 엔딩)"""

    def ending_title(self, score, pigeon=0, dead=False):
        return game.get_ending(score, pigeon, "철수", dead)[0]

    def test_즉사가_가장_우선(self):
        self.assertIn("즉사", self.ending_title(999, pigeon=10, dead=True))

    def test_비둘기_4개면_점수와_상관없이_히든(self):
        self.assertIn("히든", self.ending_title(999, pigeon=4))
        self.assertIn("히든", self.ending_title(-999, pigeon=5))

    def test_비둘기_3개는_히든_아님(self):
        self.assertNotIn("히든", self.ending_title(200, pigeon=3))

    def test_점수_경계값(self):
        cases = [(100, "TRUE"), (99, "노멀"), (60, "노멀"), (59, "친구"),
                 (30, "친구"), (29, "읽씹"), (0, "읽씹"), (-1, "배드")]
        for score, keyword in cases:
            with self.subTest(score=score):
                self.assertIn(keyword, self.ending_title(score))

    def test_엔딩_본문에_태그가_남지_않음(self):
        for score in (150, 70, 40, 5, -50):
            for pigeon in (0, 4):
                for dead in (False, True):
                    _, body, _ = game.get_ending(score, pigeon, "민준", dead)
                    self.assertNotIn("{", body)


class TestSceneData(unittest.TestCase):
    """장면 데이터(대본)가 올바른 형식인지 확인"""

    def test_챕터는_10개(self):
        self.assertEqual(len(game.SCENES), 10)

    def test_모든_장면_형식(self):
        for scene in game.SCENES:
            with self.subTest(title=scene["title"]):
                self.assertTrue(scene["title"] and scene["text"])
                self.assertEqual(len(scene["choices"]), 4)
                for choice in scene["choices"]:
                    self.assertIn(len(choice), (3, 4))
                    delta = choice[1]
                    if isinstance(delta, tuple):
                        self.assertLessEqual(delta[0], delta[1])
                    else:
                        self.assertIsInstance(delta, int)
                    if len(choice) == 4:
                        self.assertIn(choice[3], ("PIGEON", "DEATH"))

    def test_즉사_선택지가_3개_이상(self):
        deaths = [c for s in game.SCENES for c in s["choices"]
                  if game.choice_tag(c) == "DEATH"]
        self.assertGreaterEqual(len(deaths), 3)

    def test_비둘기_엔딩은_도달_가능(self):
        pigeon_scenes = sum(
            any(game.choice_tag(c) == "PIGEON" for c in scene["choices"])
            for scene in game.SCENES)
        self.assertGreaterEqual(pigeon_scenes, game.PIGEON_GOAL)

    def test_장면_텍스트에_태그가_남지_않음(self):
        for gender in ("남", "여"):
            for scene in game.SCENES:
                text = game.scene_text(scene["text"], gender, "민준")
                self.assertNotIn("{", text)
                for choice in scene["choices"]:
                    self.assertNotIn("{", game.scene_text(choice[0], gender, "민준"))
                    self.assertNotIn("{", game.scene_text(choice[2], gender, "민준"))

    def test_챕터5는_캐릭터_취향을_물어봄(self):
        chapter5 = game.SCENES[4]["text"]
        self.assertIn("닭가슴살", game.scene_text(chapter5, "남", "철수"))
        self.assertIn("민트초코", game.scene_text(chapter5, "여", "영희"))

    def test_roll_delta(self):
        rng = random.Random(1)
        self.assertEqual(game.roll_delta(7, rng), 7)
        for _ in range(100):
            self.assertTrue(-5 <= game.roll_delta((-5, 5), rng) <= 5)


class TestDifficulty(unittest.TestCase):
    """'어렵게' 요구사항: 아무렇게나 고르면 TRUE 엔딩은 거의 안 나와야 함"""

    def play_randomly(self, rng):
        score, pigeon = game.START_SCORE, 0
        for scene in game.SCENES:
            choice = rng.choice(scene["choices"])
            tag = game.choice_tag(choice)
            if tag == "DEATH":
                return game.get_ending(score, pigeon, "철수", True)[0]
            if tag == "PIGEON":
                pigeon += 1
            score += game.roll_delta(choice[1], rng)
        return game.get_ending(score, pigeon, "철수")[0]

    def test_랜덤_플레이로는_TRUE가_10퍼센트_미만(self):
        rng = random.Random(42)
        titles = [self.play_randomly(rng) for _ in range(3000)]
        true_rate = sum("TRUE" in t for t in titles) / len(titles)
        self.assertLess(true_rate, 0.10)

    def test_잘_고르면_TRUE_도달_가능(self):
        best = game.START_SCORE
        for scene in game.SCENES:
            safe = [c for c in scene["choices"] if game.choice_tag(c) is None]
            best += max(c[1][1] if isinstance(c[1], tuple) else c[1] for c in safe)
        self.assertGreaterEqual(best, game.TRUE_SCORE)


class TestEvents(unittest.TestCase):
    """랜덤 돌발 이벤트"""

    def test_이벤트_형식(self):
        self.assertGreaterEqual(len(game.EVENTS), 5)
        for event in game.EVENTS:
            self.assertTrue(event["title"] and event["text"])
            self.assertNotIn("{", game.scene_text(event["text"], "여", "민준"))

    def test_확률이_0이면_안_나옴_1이면_꼭_나옴(self):
        rng = random.Random(0)
        self.assertIsNone(game.pick_event(rng, chance=0))
        self.assertIn(game.pick_event(rng, chance=1), game.EVENTS)


class TestCharacterArt(unittest.TestCase):
    """캐릭터 그래픽: 표정 고르기와 PNG 불러오기"""

    def test_표정은_변화량으로_결정(self):
        self.assertEqual(game.mood_for(10), "happy")
        self.assertEqual(game.mood_for(-3), "sad")
        self.assertEqual(game.mood_for(0), "normal")

    def test_이미지_없으면_None(self):
        root = tk.Tk()
        try:
            with tempfile.TemporaryDirectory() as empty:
                self.assertIsNone(game.load_character_image("남", "happy", empty))
        finally:
            root.destroy()

    def test_큰_PNG는_칸에_맞게_줄여서_불러옴(self):
        root = tk.Tk()
        try:
            with tempfile.TemporaryDirectory() as folder:
                big = tk.PhotoImage(width=400, height=300)
                big.put("pink", to=(0, 0, 400, 300))
                big.write(os.path.join(folder, "female_sad.png"), format="png")
                img = game.load_character_image("여", "sad", folder)
                self.assertIsNotNone(img)
                self.assertLessEqual(img.width(), game.ART_SIZE)
                self.assertLessEqual(img.height(), game.ART_SIZE)
        finally:
            root.destroy()


PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


def read_project_file(name):
    with open(os.path.join(PROJECT_DIR, name), "rb") as f:
        return f.read()


class TestBatchFiles(unittest.TestCase):
    """run.bat(게임 실행)과 build_exe.bat(빌드) 파일 검사"""

    def test_cmd가_읽을_수_있는_형식(self):
        # 한글이 있거나 줄바꿈이 LF면 cmd가 줄을 잘못 읽는다 (build_exe.bat에서 겪은 문제)
        for name in ("run.bat", "build_exe.bat"):
            with self.subTest(file=name):
                data = read_project_file(name)
                data.decode("ascii")  # 한글이 섞여 있으면 여기서 에러
                self.assertEqual(data.count(b"\n"), data.count(b"\r\n"))
                # 줄바꿈(CR, LF) 말고 눈에 안 보이는 제어문자가 섞이면 안 됨 (예: \b → 백스페이스)
                hidden = sorted({b for b in data if b < 32 and b not in (10, 13)})
                self.assertEqual(hidden, [])

    def test_run_bat은_공식_Python으로_게임을_실행(self):
        data = read_project_file("run.bat")
        self.assertIn(b"byungmat_love.py", data)
        self.assertNotIn(b".exe", data)          # 서명 없는 exe는 쓰지 않는다
        self.assertIn(b"import tkinter", data)   # 진짜 Python이 있는지 확인한다

    def test_Python이_없으면_설치_페이지_안내(self):
        self.assertIn(b"python.org", read_project_file("run.bat"))


class TestGui(unittest.TestCase):
    """실제 tkinter 창을 띄워서 확인 (창은 테스트 끝나면 바로 닫힘)"""

    def setUp(self):
        self.root = tk.Tk()
        self.app = game.LoveGame(self.root, rng=random.Random(0))

    def tearDown(self):
        self.root.destroy()

    def lowest_widget_bottom(self):
        """현재 화면에서 가장 아래 위젯의 바닥 y좌표 (창 기준)"""
        self.root.update()
        frame = self.app.frame
        return max(frame.winfo_y() + w.winfo_y() + w.winfo_height()
                   for w in frame.winfo_children())

    def assert_fits(self):
        self.assertLessEqual(self.lowest_widget_bottom(), game.WINDOW_H)

    def test_모든_화면이_창_안에_들어감(self):
        rng = random.Random(0)
        self.assert_fits()
        for _ in range(15):
            self.app.gender.set(rng.choice(["남", "여"]))
            self.app.name_var.set(rng.choice(["김철수", "가나다라마바사아자차카", "Tom"]))
            self.app.start_game()
            while not self.app.finished:
                self.assert_fits()
                self.press_random_button(rng)  # 사람이 버튼 누르는 것처럼
            self.assert_fits()

    def press_random_button(self, rng):
        """현재 화면의 버튼(선택지/다음) 중 하나를 랜덤으로 누른다"""
        buttons = [w for w in self.app.frame.winfo_children()
                   if isinstance(w, tk.Button)]
        rng.choice(buttons).invoke()

    def test_빈_이름은_익명으로(self):
        self.app.name_var.set("   ")
        self.app.start_game()
        self.assertEqual(self.app.name, "익명")

    def test_시작_호감도는_낮음(self):
        self.app.start_game()
        self.assertEqual(self.app.score, game.START_SCORE)
        self.assertLess(game.START_SCORE, 30)

    def test_다시하기_해도_고른_성별_유지(self):
        self.app.gender.set("남")
        self.app.start_game()
        self.app.show_start()
        self.assertEqual(self.app.gender.get(), "남")
        self.assertEqual(self.app.name_var.get(), "김철수")

    def test_비둘기_선택지는_게이지_증가(self):
        self.app.start_game()
        pigeon_choice = next(c for c in game.SCENES[0]["choices"]
                             if game.choice_tag(c) == "PIGEON")
        self.app.choose(pigeon_choice)
        self.assertEqual(self.app.pigeon, 1)

    def test_즉사_선택지는_바로_엔딩(self):
        self.app.start_game()
        scene_idx, death = next(
            (i, c) for i, s in enumerate(game.SCENES) for c in s["choices"]
            if game.choice_tag(c) == "DEATH")
        self.app.idx = scene_idx
        self.app.show_scene()
        self.app.choose(death)
        self.app.next_step()  # 반응 화면의 '다음'
        self.assertTrue(self.app.finished)
        self.assertIn("즉사", self.app.ending_title)

    def test_제한_시간은_7초(self):
        # 플레이해 보니 5초는 너무 빡세서 7초로 결정 (사용자 피드백)
        self.assertEqual(game.TIME_LIMIT, 7)
        self.assertIn("7초", game.TIMEOUT_REACTION)

    def test_시간_초과하면_감점(self):
        self.app.start_game()
        before = self.app.score
        self.app.on_timeout()
        self.assertEqual(self.app.score, before + game.TIMEOUT_PENALTY)
        self.assertEqual(self.app.idx, 1)

    def test_타이머가_실제로_흘러서_시간초과(self):
        old = game.TIME_LIMIT
        game.TIME_LIMIT = 0.3
        try:
            self.app.start_game()
            end = time.time() + 1.5
            while time.time() < end and self.app.idx == 0:
                self.root.update()
                time.sleep(0.02)
            self.assertEqual(self.app.idx, 1)
        finally:
            game.TIME_LIMIT = old

    def test_선택하면_타이머_멈춤(self):
        self.app.start_game()
        self.app.choose(game.SCENES[0]["choices"][0])
        self.assertIsNone(self.app.timer_id)

    def test_이미지_없으면_캔버스에_얼굴을_그림(self):
        self.app.start_game()
        self.assertGreater(len(self.app.art_canvas.find_all()), 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
