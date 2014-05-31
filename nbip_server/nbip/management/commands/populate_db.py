# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.db import transaction
from nbip.models import *

class Command(BaseCommand):
    args = ''
    help = 'Loads some example data into the database'

    @transaction.atomic
    def _load_data(self):
        # check
        if User.objects.filter(username = "admin"):
            print "Admin user already exists, aborting"
            return

        # admin
        admin = User.objects.create_user(
            "admin",
            None,
            "admin"
        )
        admin.is_staff = True
        admin.is_active = True
        admin.is_superuser = True
        admin.save()
        print "Admin user (admin / admin) created."


        # users
        users = []
        for i in range(1,5):
            users.append(User.objects.create_user(
                "user%d" % i,
                None,
                "user%d" % i
            ))
        for i in range(len(users)):
            Bot(owner = users[i], name = "bot%d" % i, apikey="bot%d" %i).save()
        print "Dummy users created"

        # a word
        w1 = Word(lemma = 'Tentillum',
                  correct_explanation = u'fadenförmiger Tentakelfortsatz',
                  reference = 'http://de.wikipedia.org/wiki/Tentilla',
                  author=users[0])
        w1.save()

        Explanation(word = w1, explanation = "katholische Reliquie", author = users[0]).save()
        Explanation(word = w1, explanation = "längliche Nudelform", author = users[1]).save()
        Explanation(word = w1, explanation = "noch etwas", author = admin).save()
        Explanation(word = w1, explanation = "britischer Wahlkreis", bot = users[2].bots.get()).save()
        Explanation(word = w1, explanation = "magischer Charakter", bot = users[3].bots.get()).save()
        Explanation(word = w1, explanation = "chinesischer Ausdruckstanz", bot = users[1].bots.get()).save()
        print "Example data created"

    def handle(self, *args, **options):
        self._load_data()
