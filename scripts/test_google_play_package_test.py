"""Offline checks only: python3 -m unittest discover -s scripts -p 'test_*.py'."""
import unittest
from datetime import datetime
from google_play_package_test import minimize, summarize, compare, public_summary


def example(identity='a', content='Useful', score=5):
    return minimize({'reviewId': identity, 'content': content, 'score': score,
                     'at': datetime(2026, 9, 28), 'userName': 'DO NOT KEEP',
                     'userImage': 'DO NOT KEEP', 'appVersion': None})


class EvidenceTests(unittest.TestCase):
    def test_privacy_and_timezone(self):
        row = example()
        self.assertNotIn('content', row)
        self.assertNotIn('userName', row)
        self.assertNotIn('DO NOT KEEP', str(row))
        self.assertEqual(row['at_utc'], '2026-09-28T00:00:00+00:00')
        self.assertEqual(row['body_characters'], 6)

    def test_quality_and_duplicates(self):
        result = summarize([example(), example(), example('b', '', 9)])
        self.assertEqual(result['duplicate_ids'], 1)
        self.assertEqual(result['empty_bodies'], 1)
        self.assertEqual(result['invalid_scores'], 1)
        self.assertEqual(result['missing']['app_version'], 3)

    def test_repeat_distinguishes_new_from_changed(self):
        result = compare([example()], [example(content='Changed', score=1), example('b')])
        self.assertEqual(result['new_to_sample_ids'], ['b'])
        self.assertEqual(result['changed_body_ids'], ['a'])
        self.assertEqual(result['changed_score_ids'], ['a'])
        self.assertEqual(result['jaccard'], .5)

    def test_compact_preserves_id_evidence(self):
        rows = [example(str(i)) for i in range(5)]
        report = {'rounds': [{'apps': [{'pages': [{'rows': rows}]}]}]}
        page = public_summary(report)['rounds'][0]['apps'][0]['pages'][0]
        self.assertEqual(page['review_ids'], list(map(str, range(5))))
        self.assertEqual(len(page['sample_rows']), 3)
        self.assertEqual(page['summary']['unique_ids'], 5)
        self.assertIn('rows', report['rounds'][0]['apps'][0]['pages'][0])


if __name__ == '__main__':
    unittest.main()
