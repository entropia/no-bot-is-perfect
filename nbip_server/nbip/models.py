# coding=utf-8

import random

from django.db import models, transaction
from django.db.models import Count
from django.contrib.auth.models import User

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


# Enumeration type
class Guess(int):
    def __init__(self, value):
        assert 0 <= value < 3, "value %s out of range" % value

    def __unicode__(self):
        return {
            0: 'Richtig',
            1: 'Mensch',
            2: 'Computer',
        }[self]

# Constants
CORRECT = Guess(0)
HUMAN = Guess(1)
COMPUTER = Guess(2)

# Custom fields
class GuessField(models.PositiveSmallIntegerField):
    description = "Choice: Correct, Human or Bot"

    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        kwargs['choices'] = [ (0, 'Richtig')
           , (1, 'Mensch')
           , (2, 'Computer')
           ]
        kwargs['null'] = True
        super(GuessField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if value is None:
            return None

        if isinstance(value, Guess):
            return value

        return Guess(value)

# Exceptions

class NotEnoughWordsException(Exception):
    pass

class NotEnoughExplanationsException(Exception):
    pass

# Models

class Word(models.Model):
    class Meta:
        verbose_name = "Wort"
        verbose_name_plural = u"Wörter"

    lemma = models.CharField(max_length=200)
    correct_explanation = models.CharField(max_length=1000,
            verbose_name = "Korrekte Erklärung",
            help_text= u"<i>Wort</i> ist ein/eine <i>Erklärung</i>")
    reference = models.URLField(blank=True,
            verbose_name = "Reference",
            help_text = u"URL zu Wikipedia o.ä.")

    created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, verbose_name="Autor")

    n_explanations = models.PositiveIntegerField(
            verbose_name = "Anzahl Erklärungen",
            default = 0)

    @classmethod
    def unseen_objects(cls, player):
        explained = Explanation.objects.filter(author__exact = player).values("word")
        guessed = GameRound.objects.filter(player__exact = player).values("word")
        query = cls.objects \
            .exclude(author__exact = player.id) \
            .exclude(id__in  = explained) \
            .exclude(id__in  = guessed)
        return query

    # from http://stackoverflow.com/a/2118712/946226
    @classmethod
    def random(cls, player):
        words = cls.unseen_objects(player)

        # fetches everything; be smarter if required
        if len(words) < 1:
            raise NotEnoughWordsException()
        return random.choice(words)

    @classmethod
    # similar to random, but only consider words with enough explanations
    def random_explained(cls, player):
        words = cls.unseen_objects(player).filter(n_explanations__gte = 4)

        # fetches everything; be smarter if required
        if len(words) < 1:
            raise NotEnoughWordsException()
        return random.choice(words)

    def update_cached_fields(self):
        self.n_explanations = Explanation.objects.filter(word__exact = self.id).count()
        self.save()

    def __unicode__(self):
        return self.lemma

class Explanation(models.Model):
    class Meta:
        verbose_name = u"Erklärung"
        verbose_name_plural = u"Erklärungen"

    word = models.ForeignKey(Word, verbose_name="Wort")
    explanation = models.CharField(max_length=1000,
            verbose_name= u"Erklärung",
            help_text= u"<i>Wort</i> ist ein/eine <i>Erklärung</i>")
    author = models.ForeignKey(User, verbose_name="Autor")

    def __unicode__(self):
        return "%s ist ein/eine %s" % (self.word.lemma, self.explanation)

# Keep Word.n_explanations up-to-date
@receiver(post_save, sender=Explanation)
@receiver(post_delete, sender=Explanation)
def update_word(sender, instance, **kwargs):
    instance.word.update_cached_fields()


class GameRound(models.Model):
    class Meta:
        verbose_name = u"Spielrunde"
        verbose_name_plural = u"Spielrunde"

    word = models.ForeignKey(Word, verbose_name="Wort")
    explanations = models.ManyToManyField(Explanation, related_name='explanation+', through='GameRoundEntry')
    pos = models.PositiveSmallIntegerField()
    # What the user guessed for the correct result
    guess = GuessField()
    player = models.ForeignKey(User, verbose_name="Spieler")

    def __unicode__(self):
        return "%s (%d)" % (self.word.lemma, self.id)

    @classmethod
    @transaction.atomic
    def start_new_round(cls, player):
        # pick a valid word (not seen before)
        word = Word.random_explained(player=player)

        # The word has not been seen by the user (not submitted by him, no
        # explanations created by him, not played before).
        # In particular, all explanations are not by him, so this check later
        # is redundant.
        # Later we might want to exclude this player's bot's explanations.
        expls = word.explanation_set.all()

        assert len(expls) >= 4, "n_explanations was not up to date?"
        expl = random.sample(expls, 4)

        poss = range(5)
        random.shuffle(poss)

        round = GameRound(
            word = word,
            guess = None,
            pos = poss.pop(),
            player = player,
            )
        round.save()
        for e in expl:
            GameRoundEntry(
                gameround = round,
                explanation = e,
                pos = poss.pop(),
                guess = None,
            ).save()
        return round

    def get_explanations(self):
        expls = [None,None,None,None,None]
        expls[self.pos] = {
            'text': self.word.correct_explanation,
            'guess': self.guess,
            'actual': CORRECT,
        }
        for e in GameRoundEntry.objects.filter(gameround=self):
            expls[e.pos] = {
                    'text': e.explanation.explanation,
                    'guess': e.guess,
                    'actual': HUMAN, # TODO: COMPUTER
            }
        return expls


    @transaction.atomic
    def set_guesses(self, guesses):
        # TODO: These assertions should be enforced by the client code (JS)
        assert self.guess is None
        assert len(guesses) == 5
        for g in guesses:
            assert len(guesses) == 5

        assert guesses.count(CORRECT) == 1, "Not exactly one answer 'correct'"
        assert guesses.count(HUMAN) == 2, "Not exactly two answers 'human'"
        assert guesses.count(COMPUTER) == 2, "Not exactly two answers 'computer'"

        self.guess = guesses[self.pos]
        for e in GameRoundEntry.objects.filter(gameround=self):
            assert e.pos < 5
            e.guess = guesses[e.pos]
            e.save()
        self.save()


class GameRoundEntry(models.Model):
    class Meta:
        verbose_name = u"Spielrunden-Erkärung"
        verbose_name_plural = u"Spielrunden-Erkärung"
        ordering = ['pos']
        unique_together = ('gameround','explanation','pos')

    gameround = models.ForeignKey(GameRound)
    explanation = models.ForeignKey(Explanation)
    pos = models.PositiveSmallIntegerField()
    guess = GuessField()

