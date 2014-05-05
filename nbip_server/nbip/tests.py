from django.test import TestCase

from nbip.models import *

class NbipTestCase(TestCase):
    def addUsers(self):
        self.users = []
        for i in range(1,7):
            self.users.append(User.objects.create_user(
                "user%d" % i,
                "test@example.com",
                "p455w0rd"
            ))
        for i in range(len(self.users)):
            Bot(owner = self.users[i], name = "bot%d" % i).save()

    # convenience functions
    def addHumanExplanation(self, word, n):
        e = Explanation(word = word, explanation = "foo1", author = self.users[n])
        e.save()
        return e

    def addBotExplanation(self, word, n):
        e = Explanation(word = word, explanation = "foo1", bot = self.users[n].bots.get())
        e.save()
        return e

class WordTests(NbipTestCase):
    def setUp(self):
        self.addUsers()

    def testHumanExplanationCount(self):
        w = Word(lemma = 'Test', author=self.users[0])
        w.save()
        self.assertEqual(w.n_human_explanations, 0)

        e = self.addHumanExplanation(w,1)
        self.assertEqual(Word.objects.get().n_human_explanations, 1)

        e.explanation = "bar"
        e.save()
        self.assertEqual(Word.objects.get().n_human_explanations, 1)

        self.addHumanExplanation(w,2)
        self.assertEqual(Word.objects.get().n_human_explanations, 2)

        e.delete()
        self.assertEqual(Word.objects.get().n_human_explanations, 1)

    def testBotExplanationCount(self):
        w = Word(lemma = 'Test', author=self.users[0])
        w.save()
        self.assertEqual(w.n_human_explanations, 0)

        e = self.addBotExplanation(w,1)
        self.assertEqual(Word.objects.get().n_bot_explanations, 1)

        e.explanation = "bar"
        e.save()
        self.assertEqual(Word.objects.get().n_bot_explanations, 1)

        self.addBotExplanation(w,2)
        self.assertEqual(Word.objects.get().n_bot_explanations, 2)

        e.delete()
        self.assertEqual(Word.objects.get().n_bot_explanations, 1)


# all the tests related to choosing correct words/explanations
class SelectionMethodTests(NbipTestCase):
    def setUp(self):
        self.addUsers()

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
        with self.assertRaises(NotEnoughWordsException):
            round = GameRound.start_new_round(player = self.users[1])

    def testNewRoundOwnExplanations(self):
        w1 = Word(lemma = 'Test', author=self.users[0])
        w1.save()
        self.addHumanExplanation(w1,1)
        self.addHumanExplanation(w1,2)
        self.addHumanExplanation(w1,3)
        self.addBotExplanation(w1,1)
        self.addBotExplanation(w1,2)
        round = GameRound.start_new_round(player = self.users[1])
        self.assertEqual(round.word,w1)


    def testNewRoundCreation(self):
        w1 = Word(lemma = 'Test', author=self.users[0])
        w1.save()
        self.addHumanExplanation(w1,1)
        self.addHumanExplanation(w1,2)
        self.addHumanExplanation(w1,3)
        self.addBotExplanation(w1,1)
        self.addBotExplanation(w1,2)
        round = GameRound.start_new_round(player = self.users[5])
        self.assertEqual(round.word,w1)

    def testNewRoundOneUsableOfTwo(self):
        w1 = Word(lemma = 'Test', author=self.users[0])
        w1.save()
        w2 = Word(lemma = 'Test', author=self.users[2])
        w2.save()
        self.addHumanExplanation(w2,1)
        self.addHumanExplanation(w2,2)
        self.addHumanExplanation(w2,3)
        self.addBotExplanation(w2,1)
        self.addBotExplanation(w2,2)
        round = GameRound.start_new_round(player = self.users[5])
        self.assertEqual(round.word,w2)

    def testNewRoundGuessed(self):
        w1 = Word(lemma = 'Test', author=self.users[0])
        w1.save()
        self.addHumanExplanation(w1,1)
        self.addHumanExplanation(w1,2)
        self.addHumanExplanation(w1,3)
        self.addBotExplanation(w1,1)
        self.addBotExplanation(w1,2)
        round = GameRound.start_new_round(player = self.users[1])
        with self.assertRaises(NotEnoughWordsException):
            GameRound.start_new_round(player = self.users[1])

    def testNewExplainedWord(self):
        w1 = Word(lemma = 'Test', author=self.users[0])
        w1.save()
        e = self.addHumanExplanation(w1,1)
        self.addHumanExplanation(w1,2)
        self.addHumanExplanation(w1,3)
        self.addBotExplanation(w1,1)
        self.addBotExplanation(w1,2)
        round = GameRound.start_new_round(player = self.users[1])
        self.assertEqual(round.word,w1)
        self.assert_(e not in round.explanations.all())


