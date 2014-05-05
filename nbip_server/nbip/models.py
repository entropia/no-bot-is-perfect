# coding=utf-8

import random

from django.db import models, transaction
from django.db.models import Count, Q
from django.contrib.auth.models import User
from django.conf import settings

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


# Enumeration type
class Guess(int):
    def __init__(self, value):
        if value is None:
            self=None
        else:
            value=int(value)
            assert 0 <= value < 3, "value %s out of range" % value
            self=value

    # Breaks the admin form
    #def __unicode__(self):
    #    return {
    #        0: 'Richtig',
    #        1: 'Mensch',
    #        2: 'Computer',
    #    }[int(self)]



# Constants
CORRECT = Guess(0)
HUMAN = Guess(1)
COMPUTER = Guess(2)

# Custom fields
class GuessField(models.PositiveSmallIntegerField):
    description = "Choice: Correct, Human or Bot"

    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        kwargs['choices'] = [
             (CORRECT, 'Richtig')
           , (HUMAN, 'Mensch')
           , (COMPUTER, 'Computer')
           ]
        kwargs['null'] = True
        super(GuessField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if value is None:
            return None

        if isinstance(value, Guess):
            return value

        return Guess(value)

    def formfield(self, **kwargs):
        defaults = {'coerce': lambda x: Guess(x)}
        defaults.update(kwargs)
        return super(GuessField, self).formfield(**defaults)

# Exceptions

class NotEnoughWordsException(Exception):
    pass

class NotEnoughExplanationsException(Exception):
    pass




# various stats
def _get_stats(self):
        specs = {
            'words':
                Q(),
            'own_words':
                Word.q_owner(self),
            'explained_words':
                Q(Word.q_explained(self)),
            'guessed_words':
                Q(Word.q_guessed(self)),
            'incomplete_words':
                Q(Word.q_unseen(self), ~Word.q_complete()),
            'usable_words':
                Q(Word.q_unseen(self), Word.q_complete()),
            }

        return {k: Word.objects.filter(q).count() for k, q in specs.iteritems()}
# HACK! How to do this cleanly
# (in a way so that the "user" in template's context supports this)
User.stats = _get_stats

# Models

class Bot(models.Model):
    class Meta:
        verbose_name = "Bot"
        verbose_name_plural = u"Bots"

    owner = models.ForeignKey(User, verbose_name="Benutzer", related_name = "bots")
    name = models.CharField(max_length=200, verbose_name="Bot-Name")

    def __unicode__(self):
        return "%s by %s" % (self.name, self.owner)

class Word(models.Model):
    class Meta:
        verbose_name = "Wort"
        verbose_name_plural = u"Wörter"

    lemma = models.CharField(max_length=200)
    correct_explanation = models.CharField(max_length=1000,
            verbose_name = "Korrekte Erklärung",
            help_text= u"<i>Wort</i> ist ein/eine <i>Erklärung</i>")
    reference = models.URLField(blank=True,
            verbose_name = "Referenz",
            help_text = u"URL zu Wikipedia o.ä.")

    created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, verbose_name="Autor", related_name="submitted_words")

    n_human_explanations = models.PositiveIntegerField(
            verbose_name = "Anzahl menschliche Erklärungen",
            default = 0)
    n_bot_explanations = models.PositiveIntegerField(
            verbose_name = "Anzahl Computer-Erklärungen",
            default = 0)

    # query components (Q objects)
    @classmethod
    def q_owner(cls, player):
        return Q(author__exact = player.id)

    @classmethod
    def q_explained(cls, player):
        explained = Explanation.objects.filter(author__exact = player).values("word")
        return Q(id__in = explained)

    @classmethod
    def q_guessed(cls, player):
        guessed = GameRound.objects.filter(player__exact = player).values("word")
        return Q(id__in = guessed)

    @classmethod
    def q_unseen(cls, player):
        return Q(~cls.q_owner(player) & ~cls.q_explained(player) & ~cls.q_guessed(player))

    @classmethod
    def q_answer_unseen(cls, player):
        return Q(~cls.q_owner(player) & ~cls.q_guessed(player))

    @classmethod
    def q_complete(cls):
        # +1 so that the players own explanation can be removed
        return Q(n_human_explanations__gte = settings.HUMAN_EXPLANATIONS + 1) & \
               Q(n_bot_explanations__gte   = settings.BOT_EXPLANATIONS)

    # from http://stackoverflow.com/a/2118712/946226
    @classmethod
    def random(cls, player):
        words = cls.objects.filter(cls.q_unseen(player))

        # fetches everything; be smarter if required
        if len(words) < 1:
            raise NotEnoughWordsException()
        return random.choice(words)

    @classmethod
    # similar to random, but only consider words with enough explanations
    def random_explained(cls, player):
        words = cls.objects.filter(cls.q_answer_unseen(player), cls.q_complete())

        # fetches everything; be smarter if required
        if len(words) < 1:
            raise NotEnoughWordsException()
        return random.choice(words)

    def update_cached_fields(self):
        self.n_human_explanations = \
            Explanation.objects.filter(author__isnull = False, word__exact = self.id).count()
        self.n_bot_explanations = \
            Explanation.objects.filter(bot__isnull = False, word__exact = self.id).count()
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

    # exactly one of these should be not null
    author = models.ForeignKey(User, verbose_name="Autor", blank=True, null=True, related_name="submitted_explanations")
    bot = models.ForeignKey(Bot, verbose_name="Bot", blank=True, null=True)

    def clean(self):
        if self.author is None and self.bot is None:
            raise ValidationError('Autor oder Bot müssen gesetzt sein.')
        if self.author is not None and self.bot is not None:
            raise ValidationError('Autor und Bot dürfen nicht beide gesetzt sein.')

    def type(self):
        '''HUMAN or COMPUTER'''
        if self.author is not None:
            return HUMAN
        else:
            return COMPUTER

    def __unicode__(self):
        return "%s ist ein/eine %s" % (self.word.lemma, self.explanation)

# Keep Word.n_*_explanations up-to-date
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
    player = models.ForeignKey(User, verbose_name="Spieler", related_name="gamerounds")

    def __unicode__(self):
        return "%s (%d)" % (self.word.lemma, self.id)

    @classmethod
    @transaction.atomic
    def start_new_round(cls, player):
        # pick a valid word where the user has not seen the answer before
        word = Word.random_explained(player=player)

        # The word has not been seen by the user (not submitted by him, no
        # explanations created by him, not played before).
        # In particular, all explanations are not by him, so this check later
        # is redundant.
        # Later we might want to exclude this player's bot's explanations.
        human_expls = word.explanation_set \
            .filter(author__isnull = False) \
            .exclude(author = player)
        bot_expls = word.explanation_set.filter(bot__isnull = False)

        assert len(human_expls) >= settings.HUMAN_EXPLANATIONS, \
                    "n_human_explanations was not up to date?"
        assert len(bot_expls) >= settings.BOT_EXPLANATIONS, \
                    "n_bot_explanations was not up to date?"
        expl = random.sample(human_expls, settings.HUMAN_EXPLANATIONS) + \
               random.sample(bot_expls, settings.BOT_EXPLANATIONS)

        poss = range(1 + len(expl))
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
        entries = GameRoundEntry.objects.filter(gameround=self)
        expls = [None] * (1 + entries.count())
        expls[self.pos] = {
            'text': self.word.correct_explanation,
            'guess': self.guess,
            'actual': CORRECT,
        }
        for e in entries:
            expls[e.pos] = {
                    'text': e.explanation.explanation,
                    'guess': e.guess,
                    'actual': e.explanation.type(),
            }
        return expls

    def get_counts(self):
        counts = {
            CORRECT: 1,
            HUMAN: 0,
            COMPUTER: 0,
            }
        for e in GameRoundEntry.objects.filter(gameround=self):
            counts[e.explanation.type()] += 1
        return counts


    @transaction.atomic
    def set_guesses(self, guesses):
        # TODO: These assertions should be enforced by the client code (JS)
        assert self.guess is None

        entries = GameRoundEntry.objects.filter(gameround=self)

        required = [CORRECT] + [e.explanation.type() for e in entries]

        assert len(guesses) == len(required), \
            "Wrong number of answers"

        assert guesses.count(CORRECT) == required.count(CORRECT), \
            "Wrong number of answers 'correct'"
        assert guesses.count(HUMAN) == required.count(HUMAN), \
            "Wrong number of answers 'human'"
        assert guesses.count(COMPUTER) == required.count(COMPUTER), \
            "Wrong number of answers 'computer'"

        self.guess = guesses[self.pos]
        for e in entries:
            assert e.pos < len(guesses)
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

