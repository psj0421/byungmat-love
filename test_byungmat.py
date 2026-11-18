"""
병맛 연애 시뮬레이션 테스트
실행: python -m unittest -v test_byungmat.py
(외부 라이브러리 없이 파이썬 기본 unittest만 사용)
"""
import random
import tkinter as tk
import unittest

import byungmat_love as game

WINDOW_HEIGHT = 620


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

    def ending_title(self, score, pigeon=0):
        return game.get_ending(score, pigeon, "철수")[0]

    def test_비둘기_3개면_점수와_상관없이_히든(self):
        self.assertIn("히든", self.ending_title(999, pigeon=3))
        self.assertIn("히든", self.ending_title(-999, pigeon=4))

    def test_비둘기_2개는_히든_아님(self):
        self.assertNotIn("히든", self.ending_title(100, pigeon=2))

    def test_점수_경계값(self):
        cases = [(80, "TRUE"), (79, "노멀"), (50, "노멀"), (49, "친구"),
                 (20, "친구"), (19, "읽씹"), (0, "읽씹"), (-1, "배드")]
        for score, keyword in cases:
            with self.subTest(score=score):
                self.assertIn(keyword, self.ending_title(score))

    def test_엔딩_본문에_태그가_남지_않음(self):
        for score in (100, 60, 30, 5, -50):
            for pigeon in (0, 3):
                _, body, _ = game.get_ending(score, pigeon, "민준")
                self.assertNotIn("{", body)


class TestSceneData(unittest.TestCase):
    """장면 데이터(대본)가 올바른 형식인지 확인"""

    def test_모든_장면_형식(self):
        for scene in game.SCENES:
            with self.subTest(title=scene["title"]):
                self.assertTrue(scene["title"] and scene["text"])
                self.assertGreaterEqual(len(scene["choices"]), 2)
                for choice in scene["choices"]:
                    self.assertIn(len(choice), (3, 4))
                    delta = choice[1]
                    if isinstance(delta, tuple):
                        self.assertLessEqual(delta[0], delta[1])
                    else:
                        self.assertIsInstance(delta, int)
                    if len(choice) == 4:
                        self.assertEqual(choice[3], "PIGEON")

    def test_비둘기_엔딩은_도달_가능(self):
        pigeon_scenes = sum(
            any(len(c) == 4 for c in scene["choices"]) for scene in game.SCENES)
        self.assertGreaterEqual(pigeon_scenes, 3)

    def test_장면_텍스트에_태그가_남지_않음(self):
        for gender in ("남", "여"):
            for scene in game.SCENES:
                text = game.scene_text(scene, gender, "민준")
                self.assertNotIn("{", text)

    def test_챕터5는_캐릭터_취향을_물어봄(self):
        chapter5 = game.SCENES[4]
        self.assertIn("닭가슴살", game.scene_text(chapter5, "남", "철수"))
        self.assertIn("민트초코", game.scene_text(chapter5, "여", "영희"))


class TestGui(unittest.TestCase):
    """실제 tkinter 창을 띄워서 확인 (창은 테스트 끝나면 바로 닫힘)"""

    def setUp(self):
        self.root = tk.Tk()
        self.app = game.LoveGame(self.root)

    def tearDown(self):
        self.root.destroy()

    def lowest_widget_bottom(self):
        """현재 화면에서 가장 아래 위젯의 바닥 y좌표 (창 기준)"""
        self.root.update()
        frame = self.app.frame
        return max(frame.winfo_y() + w.winfo_y() + w.winfo_height()
                   for w in frame.winfo_children())

    def test_모든_화면이_창_안에_들어감(self):
        random.seed(0)
        self.assertLessEqual(self.lowest_widget_bottom(), WINDOW_HEIGHT)
        for _ in range(20):
            self.app.gender.set(random.choice(["남", "여"]))
            self.app.start_game()
            while self.app.idx < len(game.SCENES):
                self.assertLessEqual(self.lowest_widget_bottom(), WINDOW_HEIGHT)
                self.app.choose(random.choice(game.SCENES[self.app.idx]["choices"]))
                self.assertLessEqual(self.lowest_widget_bottom(), WINDOW_HEIGHT)
            self.app.show_scene()  # 마지막 → 엔딩 화면
            self.assertLessEqual(self.lowest_widget_bottom(), WINDOW_HEIGHT)

    def test_빈_이름은_익명으로(self):
        self.app.name_var.set("   ")
        self.app.start_game()
        self.assertEqual(self.app.name, "익명")

    def test_다시하기_해도_고른_성별_유지(self):
        self.app.gender.set("남")
        self.app.start_game()
        self.app.show_start()  # 다시 하기 버튼과 같은 동작
        self.assertEqual(self.app.gender.get(), "남")
        self.assertEqual(self.app.name_var.get(), "김철수")

    def test_비둘기_선택지는_게이지_증가(self):
        self.app.start_game()
        pigeon_choice = next(c for c in game.SCENES[0]["choices"] if len(c) == 4)
        self.app.choose(pigeon_choice)
        self.assertEqual(self.app.pigeon, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
