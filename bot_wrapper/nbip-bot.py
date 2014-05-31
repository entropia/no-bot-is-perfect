#!/usr/bin/python
# coding=utf-8


# This little wrapper takes care of talking to the nbip server.
# It expects to find two files in the current directory:
# * nbip-key.txt
#   The API key of an no-bot-is-perfect bot
# * bot
#   An executable.
#
# It will fetch a word to explain from the server, run "bot word", read an
# explanation from the standard output, send it back to the server sleep for a
# while, and repeat.
#
# So the most simple bot is
#################################
# #!/bin/sh
# echo "technischer Fachbegriff"
#################################
# but likely you want to do something smarter.

NBIP_URL="http://no-bot-is-perfect.nomeata.de/"

key = file('nbip-api.key').read().rstrip()

import requests
import subprocess
import sys
import time

while True:
    r = requests.post(NBIP_URL + "bot/get/",
            data={ 'key': key },
            )

    if r.status_code != 200:
        print "Beim Abrufen eines neuen Wortes ist ein Fehler aufgetreten:"
        print r.content
        sys.exit(0)

    word = r.text

    print u"Eine Erklärung für %s wird gesucht..." % word
    expl = subprocess.check_output(['./bot', word]).rstrip()

    print u"Erklärung „Ein/eine %s ist ein/eine %s“ wird eingereicht..." % (word, expl)
    r = requests.post(NBIP_URL + "bot/put/",
            data={ 'key': key,
                   'expl': expl},
            )
    if r.status_code != 200:
        print "Beim Einreichen ist ein Fehler aufgetreten:"
        print r.text
        sys.exit(0)

    print "Kurze Pause..."
    time.sleep(30)

