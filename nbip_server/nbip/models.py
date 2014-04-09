# coding=utf-8

import random

from django.db import models, transaction
from django.db.models import Count

# Custom fields

class GuessField(models.PositiveSmallIntegerField):
    description = "Choice: Correct, Human or Bot"

    def __init__(self, *args, **kwargs):
        kwargs['choices'] = [ (0, 'Richtig')
           , (1, 'Mensch')
           , (2, 'Computer')
           ]
        kwargs['null'] = True
        super(GuessField, self).__init__(*args, **kwargs)

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

    # from http://stackoverflow.com/a/2118712/946226
    @classmethod
    def random(cls):
        count = cls.objects.all().aggregate(count=Count('id'))['count']
        if count < 1:
            raise NotEnoughWordsException()
        random_index = random.randint(0, count - 1)
        return cls.objects.all()[random_index]

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

    def __unicode__(self):
        return "%s ist ein/eine %s" % (self.word.lemma, self.explanation)

class GameRound(models.Model):
    class Meta:
        verbose_name = u"Spielrunde"
        verbose_name_plural = u"Spielrunde"

    word = models.ForeignKey(Word, verbose_name="Wort")
    explanations = models.ManyToManyField(Explanation, related_name='explanation+', through='GameRoundEntry')
    pos = models.PositiveSmallIntegerField()
    # What the user guessed for the correct result
    guess = GuessField()

    @classmethod
    @transaction.atomic
    def start_new_round(cls):
        word = Word.random()
        expls = word.explanation_set.all()
        # TODO: Shuffle:
        poss = [1,0,4,3,2]
        if len(expls) < 4:
            raise NotEnoughExplanationsException(word)
        else:
            expl = expls[0:4]
            round = GameRound(
                word = word,
                guess = None,
                pos = poss[0],
                )
            round.save()
            for e, n in zip(expl,[1,2,3,4]):
                GameRoundEntry(
                    gameround = round,
                    explanation = e,
                    pos = n,
                    guess = None,
                ).save()
            return round


class GameRoundEntry(models.Model):
    class Meta:
        verbose_name = u"Spielrunden-Erkärung"
        verbose_name_plural = u"Spielrunden-Erkärung"

    gameround = models.ForeignKey(GameRound)
    explanation = models.ForeignKey(Explanation)
    pos = models.PositiveSmallIntegerField()
    guess = GuessField()

