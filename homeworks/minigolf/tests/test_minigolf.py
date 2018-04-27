from unittest import TestCase
from minigolf import HitsMatch, HolesMatch, Player


class PlayerTestCase(TestCase):
    def test_name(self):
        player = Player("A")
        self.assertEqual(player.name, "A")


class BaseMatchTestCase(TestCase):
    def setUp(self):
        self._players = [Player('A'), Player('B'), Player('C')]
        self._m1 = HitsMatch(3, self._players)
        self._m2 = HolesMatch(3, self._players)

    def test_init(self):
        expected_results = (3, self._players, False, 0, 0,
                            [('A', 'B', 'C'),
                                (None, None, None),
                                (None, None, None),
                                (None, None, None), ],
                            [0, 0, 0], False)
        m = self._m1
        real_results = (m._holes_number, m._players, m._finished, m._cur_hole, m._cur_player,
                        m._table, m._cur_hole_hits, m._reverse_sort_order)
        self.assertEqual(expected_results, real_results)

    def test_finished(self):
        m = self._m1
        self.assertEqual(m._finished, m.finished)
        m._finished = True
        self.assertEqual(m._finished, m.finished)

    def test_get_winners(self):
        m = self._m1
        m._finished = False
        with self.assertRaises(RuntimeError):
            m.get_winners()

        m._finished = True
        m._table = [
            ('A', 'B', 'C'),
            (2, 10, 1),
            (1, 2, 1),
            (1, 3, 2),
        ]
        self.assertEqual(m.get_winners(), [
            self._players[0], self._players[2]
        ])

        m = self._m2
        m._finished = False
        with self.assertRaises(RuntimeError):
            m.get_winners()

        m._finished = True
        m._table = [
            ('A', 'B', 'C'),
            (1, 0, 0),
            (0, 0, 0),
            (1, 0, 1),
        ]
        self.assertEqual(m.get_winners(), [self._players[0]])

    def test_get_table(self):
        m = self._m1
        m._table = [
            ('A', 'B', 'C'),
            (2, 10, 1),
            (1, 2, 1),
            (1, 3, 2),
        ]
        self.assertEqual(m.get_table(), [
            ('A', 'B', 'C'),
            (2, 10, 1),
            (1, 2, 1),
            (1, 3, 2),
        ])

    def test_update_data(self):
        m = self._m1

        m._finished = True
        m._cur_hole = m._holes_number - 1
        m.update_data()
        self.assertEqual(m._finished, True)

        m._finished = False
        m.update_data()
        self.assertEqual(m._finished, True)

        m._finished = False
        m._cur_hole = 1
        m._cur_player = 0
        self._cur_hole_hits = [1] * len(m._players)
        m.update_data()
        expected_results = (2, 2, [0, 0, 0])
        real_results = (m._cur_hole, m._cur_player, m._cur_hole_hits)
        self.assertEqual(expected_results, real_results)


class HitsMatchTestCase(TestCase):
    def setUp(self):
        self._players = [Player('A'), Player('B'), Player('C')]
        self._m = HitsMatch(3, self._players)

    def test_init(self):
        expected_results = (3, self._players, False, 0, 0,
                            [('A', 'B', 'C'),
                                (None, None, None),
                                (None, None, None),
                                (None, None, None), ],
                            [0, 0, 0], False, [0, 1, 2])
        m = self._m
        real_results = (m._holes_number, m._players, m._finished, m._cur_hole, m._cur_player,
                        m._table, m._cur_hole_hits, m._reverse_sort_order, m._still_played)
        self.assertEqual(expected_results, real_results)

    def test_hip(self):
        m = self._m
        m._finished = True
        with self.assertRaises(RuntimeError):
            m.hit()

        m._finished = False
        self._first_hole(m)
        self._second_hole(m)
        self._third_hole(m)

        with self.assertRaises(RuntimeError):
            m.hit()

        self.assertEqual(m.get_winners(), [
            m._players[0], m._players[2]
        ])

    def test_update_data(self):
        m = self._m
        m._still_played = [0] * len(m._players)
        m.update_data()
        self.assertEqual(m._still_played, [0, 1, 2])

    def _first_hole(self, m):
        m.hit()     # 1
        m.hit()     # 2
        m.hit(True) # 3
        m.hit(True) # 1
        for _ in range(8):
            m.hit() # 2

        self.assertFalse(m.finished)
        self.assertEqual(m.get_table(), [
            ('A', 'B', 'C'),
            (2, 10, 1),
            (None, None, None),
            (None, None, None),
        ])

    def _second_hole(self, m):
        m.hit() # 2
        for _ in range(3):
            m.hit(True) # 3, 1, 2

        self.assertFalse(m.finished)
        self.assertEqual(m.get_table(), [
            ('A', 'B', 'C'),
            (2, 10, 1),
            (1, 2, 1),
            (None, None, None),
        ])

    def _third_hole(self, m):
        m.hit()     # 3
        m.hit(True) # 1
        m.hit()     # 2
        self.assertEqual(m.get_table(), [
            ('A', 'B', 'C'),
            (2, 10, 1),
            (1, 2, 1),
            (1, None, None),
        ])
        m.hit(True) # 3
        m.hit()     # 2
        m.hit(True) # 2

        self.assertTrue(m.finished)
        self.assertEqual(m.get_table(), [
            ('A', 'B', 'C'),
            (2, 10, 1),
            (1, 2, 1),
            (1, 3, 2),
        ])


class HolesMatchTestCase(TestCase):
    def setUp(self):
        self._players = [Player('A'), Player('B'), Player('C')]
        self._m = HolesMatch(3, self._players)

    def test_init(self):
        expected_results = (3, self._players, False, 0, 0,
                            [('A', 'B', 'C'),
                                (None, None, None),
                                (None, None, None),
                                (None, None, None), ],
                            [0, 0, 0], True, False, 0)
        m = self._m
        real_results = (m._holes_number, m._players, m._finished, m._cur_hole, m._cur_player,
                        m._table, m._cur_hole_hits, m._reverse_sort_order, m._cur_hole_success_exists,
                        m._steps_count)
        self.assertEqual(expected_results, real_results)

    def test_hip(self):
        m = self._m
        m._finished = True
        with self.assertRaises(RuntimeError):
            m.hit()

        m._finished = False
        self._first_hole(m)
        self._second_hole(m)
        self._third_hole(m)

        with self.assertRaises(RuntimeError):
            m.hit()

        self.assertEqual(m.get_winners(), [m._players[0]])

    def test_update_data(self):
        m = self._m
        m._cur_hole_success_exists = True
        m._steps_count = 20
        m.update_data()
        self.assertEqual(m._cur_hole_success_exists, False)
        self.assertEqual(m._steps_count, 0)

    def _first_hole(self, m):
        m.hit(True) # 1
        m.hit()     # 2
        m.hit()     # 3

        self.assertFalse(m.finished)
        self.assertEqual(m.get_table(), [
            ('A', 'B', 'C'),
            (1, 0, 0),
            (None, None, None),
            (None, None, None),
        ])

    def _second_hole(self, m):
        for _ in range(10):
            for _ in range(3):
                m.hit() # 2, 3, 1

        self.assertFalse(m.finished)
        self.assertEqual(m.get_table(), [
            ('A', 'B', 'C'),
            (1, 0, 0),
            (0, 0, 0),
            (None, None, None),
        ])

    def _third_hole(self, m):
        for _ in range(9):
            for _ in range(3):
                m.hit() # 3, 1, 2
        m.hit(True) # 3
        self.assertEqual(m.get_table(), [
            ('A', 'B', 'C'),
            (1, 0, 0),
            (0, 0, 0),
            (None, None, 1),
        ])
        m.hit(True) # 1
        m.hit()     # 2

        self.assertTrue(m.finished)
        self.assertEqual(m.get_table(), [
            ('A', 'B', 'C'),
            (1, 0, 0),
            (0, 0, 0),
            (1, 0, 1),
        ])
