# coding=utf-8

import random

from django.db import models
from django.db.models import Count

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
