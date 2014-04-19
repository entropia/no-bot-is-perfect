from django.test import TestCase

from django.contrib.auth.models import User
from nbip.models import *

class SelectionMethodTests(TestCase):
    def setUp(self):
        self.users = []
        for i in range(1,7):
            self.users.append(User.objects.create_user(
                "user%d" % i,
                "test@example.com",
                "p455w0rd"
            ))

    def testRandomNoWord(self):
        with self.assertRaises(NotEnoughWordsException):
            Word.random(player = self.users[0])

    def testRandomOwnWord(self):
        Word(lemma = 'Test', author=self.users[0]).save()
        with self.assertRaises(NotEnoughWordsException):
            Word.random(player=self.users[0])

    def testRandomOtherWord(self):
        w1 = Word(lemma = 'Test', author=self.users[0])
        w1.save()
        w = Word.random(player=self.users[1])
        self.assertEqual(w,w1)

    def testRandomExplainedWord(self):
        w1 = Word(lemma = 'Test', author=self.users[0])
        w1.save()
        Explanation(word = w1, explanation = "foo1", author = self.users[1]).save()
        with self.assertRaises(NotEnoughWordsException):
            Word.random(player=self.users[1])

    def testNewRoundNoWord(self):
        with self.assertRaises(NotEnoughWordsException):
            round = GameRound.start_new_round(player = self.users[0])

    def testNewRoundOwnWord(self):
        Word(lemma = 'Test', author=self.users[0]).save()
        with self.assertRaises(NotEnoughWordsException):
            round = GameRound.start_new_round(player = self.users[0])

    def testNewRoundNoExplanations(self):
        w1 = Word(lemma = 'Test', author=self.users[0])
        w1.save()
        with self.assertRaises(NotEnoughExplanationsException):
            round = GameRound.start_new_round(player = self.users[1])

    def testNewRoundOwnExplanations(self):
        w1 = Word(lemma = 'Test', author=self.users[0])
        w1.save()
        Explanation(word = w1, explanation = "foo1", author = self.users[1]).save()
        Explanation(word = w1, explanation = "foo2", author = self.users[2]).save()
        Explanation(word = w1, explanation = "foo3", author = self.users[3]).save()
        Explanation(word = w1, explanation = "foo4", author = self.users[4]).save()
        with self.assertRaises(NotEnoughWordsException):
            round = GameRound.start_new_round(player = self.users[1])

    def testNewRoundCreation(self):
        w1 = Word(lemma = 'Test', author=self.users[0])
        w1.save()
        Explanation(word = w1, explanation = "foo1", author = self.users[1]).save()
        Explanation(word = w1, explanation = "foo2", author = self.users[2]).save()
        Explanation(word = w1, explanation = "foo3", author = self.users[3]).save()
        Explanation(word = w1, explanation = "foo4", author = self.users[4]).save()
        round = GameRound.start_new_round(player = self.users[5])
        self.assertEqual(round.word,w1)

    def testNewExplainedWord(self):
        w1 = Word(lemma = 'Test', author=self.users[0])
        w1.save()
        Explanation(word = w1, explanation = "foo1", author = self.users[1]).save()
        Explanation(word = w1, explanation = "foo2", author = self.users[2]).save()
        Explanation(word = w1, explanation = "foo3", author = self.users[3]).save()
        Explanation(word = w1, explanation = "foo4", author = self.users[4]).save()
        Explanation(word = w1, explanation = "foo5", author = self.users[5]).save()
        with self.assertRaises(NotEnoughWordsException):
            round = GameRound.start_new_round(player = self.users[1])


