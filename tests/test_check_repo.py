import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'check_repo.py'
SPEC = importlib.util.spec_from_file_location('check_repo', SCRIPT)
CHECK_REPO = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK_REPO)


def valid_storyboard():
    rows, prompts = [], []
    dialogue = ['หนึ่ง', 'สอง', 'สาม', 'สี่', 'ห้า', 'หก']
    for index, line in enumerate(dialogue, start=1):
        shot = f'S{index:02}'
        start, end = (index - 1) * 8, index * 8
        speaker = 'L01' if index % 2 else 'Z01'
        name = 'Lin' if speaker == 'L01' else 'Zhao'
        rows.append(f'| {shot} | 00:{start:02}–00:{end:02} | {speaker}: “{line}” |')
        prompts.append(f'```text\nShot {shot}. Only {name} speaks. "{line}"\n```')
    return '\n'.join(rows + prompts)


class StoryboardTests(unittest.TestCase):
    def test_valid_storyboard(self):
        self.assertEqual(CHECK_REPO.validate_storyboard(valid_storyboard()), [])

    def test_timeline_gap_is_rejected(self):
        text = valid_storyboard().replace('00:16–00:24', '00:17–00:25')
        errors = CHECK_REPO.validate_storyboard(text)
        self.assertTrue(any('timeline gap' in error for error in errors))

    def test_changed_dialogue_is_rejected(self):
        text = valid_storyboard().replace('Only Lin speaks. "สาม"', 'Only Lin speaks. "คำอื่น"')
        errors = CHECK_REPO.validate_storyboard(text)
        self.assertTrue(any('changed dialogue' in error for error in errors))

    def test_wrong_speaker_is_rejected(self):
        text = valid_storyboard().replace('Only Zhao speaks. "สอง"', 'Only Lin speaks. "สอง"')
        errors = CHECK_REPO.validate_storyboard(text)
        self.assertTrue(any('speaker does not match' in error for error in errors))


class CompletionEvidenceTests(unittest.TestCase):
    def test_accepted_requires_evidence(self):
        errors = CHECK_REPO.completion_evidence_errors('ACCEPTED', '')
        self.assertTrue(any('missing completion evidence' in error for error in errors))

    def test_published_requires_url(self):
        errors = CHECK_REPO.completion_evidence_errors('PUBLISHED', 'ตรวจโพสต์แล้ว')
        self.assertTrue(any('post URL' in error for error in errors))

    def test_published_with_url_passes(self):
        self.assertEqual(
            CHECK_REPO.completion_evidence_errors(
                'PUBLISHED', 'https://example.com/post/123'
            ),
            [],
        )


if __name__ == '__main__':
    unittest.main()
