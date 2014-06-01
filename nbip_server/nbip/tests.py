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
            Bot(owner = self.users[i], name = "bot%d" % i, apikey = "bot%d" % i).save()

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


class WordTests(NbipTestCase):
    def setUp(self):
        self.addUsers()
        self.word = Word(lemma = 'Test', author=self.users[0])
        self.word.save()

    def clean_explanation1():
        e = Explanation(word = self.word, explanation = "foo", author = self.users[0])
        self.assertEqual(e.clean_explanation(), "foo")

    def clean_explanation2():
        e = Explanation(word = self.word, explanation = "ein foo", author = self.users[0])
        self.assertEqual(e.clean_explanation(), "foo")

    def clean_explanation3():
        e = Explanation(word = self.word, explanation = "ist ein foo", author = self.users[0])
        self.assertEqual(e.clean_explanation(), "foo")

    def clean_explanation4():
        e = Explanation(word = self.word, explanation = "Ein Test ist ein foo", author = self.users[0])
        self.assertEqual(e.clean_explanation(), "foo")



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

    def testRandomPreferNeedyWord(self):
        w1 = Word(lemma = 'Test', author=self.users[0])
        w1.save()
        w2 = Word(lemma = 'Test2', author=self.users[0])
        w2.save()
        self.addHumanExplanation(w1,1)
        self.addHumanExplanation(w1,2)
        self.addHumanExplanation(w1,3)
        self.addHumanExplanation(w2,1)
        for _ in range(10):
            w = Word.random(player=self.users[4])
            self.assertEqual(w,w2)

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

    def testNewRoundNotEnoughOwnExplanations(self):
        w1 = Word(lemma = 'Test', author=self.users[0])
        w1.save()
        self.addHumanExplanation(w1,1)
        self.addHumanExplanation(w1,2)
        self.addBotExplanation(w1,2)
        self.addBotExplanation(w1,3)
        with self.assertRaises(NotEnoughExplanationsException):
            round = GameRound.start_new_round(player = self.users[1])

    def testNewRoundNotEnoughOwnBotExplanations(self):
        w1 = Word(lemma = 'Test', author=self.users[0])
        w1.save()
        self.addHumanExplanation(w1,2)
        self.addHumanExplanation(w1,3)
        self.addBotExplanation(w1,1)
        self.addBotExplanation(w1,2)
        with self.assertRaises(NotEnoughExplanationsException):
            round = GameRound.start_new_round(player = self.users[1])

    def testNewRoundOwnExplanations(self):
        w1 = Word(lemma = 'Test', author=self.users[0])
        w1.save()
        self.addHumanExplanation(w1,1)
        self.addHumanExplanation(w1,2)
        self.addHumanExplanation(w1,3)
        self.addBotExplanation(w1,2)
        self.addBotExplanation(w1,3)
        round = GameRound.start_new_round(player = self.users[1])
        self.assertEqual(round.word,w1)

    def testNewRoundOwnBotExplanations(self):
        w1 = Word(lemma = 'Test', author=self.users[0])
        w1.save()
        self.addHumanExplanation(w1,2)
        self.addHumanExplanation(w1,3)
        self.addBotExplanation(w1,1)
        self.addBotExplanation(w1,2)
        self.addBotExplanation(w1,3)
        round = GameRound.start_new_round(player = self.users[1])
        self.assertEqual(round.word,w1)


    def testNewRoundCreation(self):
        w1 = Word(lemma = 'Test', author=self.users[0])
        w1.save()
        self.addHumanExplanation(w1,1)
        self.addHumanExplanation(w1,2)
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
        self.addBotExplanation(w1,2)
        self.addBotExplanation(w1,3)
        round = GameRound.start_new_round(player = self.users[1])
        with self.assertRaises(NotEnoughWordsException):
            GameRound.start_new_round(player = self.users[1])

    def testNewExplainedWord(self):
        w1 = Word(lemma = 'Test', author=self.users[0])
        w1.save()
        e = self.addHumanExplanation(w1,1)
        self.addHumanExplanation(w1,2)
        self.addHumanExplanation(w1,3)
        e2 = self.addBotExplanation(w1,1)
        self.addBotExplanation(w1,2)
        self.addBotExplanation(w1,3)
        round = GameRound.start_new_round(player = self.users[1])
        self.assertEqual(round.word,w1)
        self.assert_(e not in round.explanations.all())
        self.assert_(e2 not in round.explanations.all())


