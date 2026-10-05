import unittest
from google_play_multiday import changes, CONFIG, START, END


class MultiDayTests(unittest.TestCase):
    def test_baseline_not_arrivals(self):
        row = ['a', '2026-10-04T00:00:00+00:00', 'hash', 5, None]
        c = changes([row], [], set(), False, '2026-10-04T01:00:00+00:00')
        self.assertIsNone(c['newly_observed'])
        self.assertEqual(c['newest_age_hours'], 1)

    def test_seen_union_and_timestamp_movement(self):
        old = ['a', '2026-10-04T00:00:00+00:00', 'old', 5, None]
        rows = [['a', old[1], 'new', 1, None], ['b', '2026-10-05T00:00:00+00:00', 'h', 5, None],
                ['c', '2026-10-03T00:00:00+00:00', 'h', 4, None]]
        c = changes(rows, [old], {'a', 'c'}, True, '2026-10-05T01:00:00+00:00')
        self.assertEqual(c['newly_observed'], 1)
        self.assertEqual(c['repeated_from_any_prior_day'], 2)
        self.assertEqual(c['changed_body_or_score'], 1)
        self.assertEqual(c['newest_moved_seconds'], 86400)

    def test_old_first_seen_not_newly_posted(self):
        old = ['a', '2026-10-04T00:00:00+00:00', 'h', 5, None]
        new = ['b', '2026-10-02T00:00:00+00:00', 'h', 4, None]
        c = changes([old, new], [old], {'a'}, True, '2026-10-05T00:00:00+00:00')
        self.assertEqual(c['newly_observed'], 1)
        self.assertEqual(c['new_ids_with_at_after_prior_newest'], 0)

    def test_bounds(self):
        self.assertEqual((START, END), ('2026-10-04', '2026-10-07'))
        self.assertEqual(CONFIG['max_review_requests_per_run'], 20)


if __name__ == '__main__':
    unittest.main()
