import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scriptfmt import format_sentences, load_script, DEFAULT_TEXT


class FormatSentencesTests(unittest.TestCase):
    def test_splits_on_period(self):
        self.assertEqual(format_sentences("Olá. Mundo."), "Olá.\nMundo.")

    def test_collapses_whitespace(self):
        self.assertEqual(
            format_sentences("  Olá.   \n\n  Mundo!  "),
            "Olá.\nMundo!",
        )

    def test_question_and_exclaim(self):
        self.assertEqual(format_sentences("Vai? Sim! Ok."), "Vai?\nSim!\nOk.")

    def test_ellipsis(self):
        self.assertEqual(format_sentences("Espera… agora. Fim."), "Espera…\nagora.\nFim.")

    def test_closing_quote_after_period(self):
        self.assertEqual(
            format_sentences('Ele disse "oi." Depois saiu.'),
            'Ele disse "oi."\nDepois saiu.',
        )

    def test_empty(self):
        self.assertEqual(format_sentences("   \n  "), "")

    def test_single_sentence_no_trailing_break(self):
        self.assertEqual(format_sentences("Só uma frase."), "Só uma frase.")


class LoadScriptTests(unittest.TestCase):
    def test_prefers_clipboard(self):
        self.assertEqual(load_script("Um. Dois."), "Um.\nDois.")

    def test_ignores_blank_clipboard(self):
        self.assertEqual(load_script("   "), DEFAULT_TEXT)


if __name__ == "__main__":
    unittest.main()
