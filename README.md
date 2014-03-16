no-bot-is-perfect
=================

No bot is perfect – a programming game for GPN 14

The idea
--------

We want something new. Something that hasn't been here before. We don't just
want our bots to play some random game. We want them to pass the **THE TURING
TEST**

So the setting is a game where human creativity is needed, but that is still
resticted enough for bots to have a chance at winning, or at least at looking
human. The game is (based upon) “Nobody is perfect”.

The game
--------

There are three roles in the game: Author, Fooler and Guesser.

The **author** (a human, and initially the NBIP-team) provides a word (for
example “Kryptosporidiose”) and an explanation in the fixed form
*adjective*-*substantive* (for example “...ist eine seltene
Durchfallerkrankung“.), and possibly a reference
(http://de.wikipedia.org/wiki/Kryptosporidiose).

The **fooler** (either a human, or a computer program) is given such a word,
and provides an alternative, fake explanation (“ist ein biometrisches
Authentifizerungsverfahren”).

The **guesser** (a human again) sees one word and five such explanations: The
correct one, two are provided by humans and two by computer programs. He then
has to guess which one is which.

All that happens ansynchronously, i.e. the words and explanations submitted by
authors and foolers are collected until a guesser joins. It should be avoided
that a guesser sees words or explanations provided by himself.

Humans get points for keeping the game running (providing words, providing fake
explanations, and guessing). Furthermore they get points for doing well
(fooling other people into believing their explanation is correct; guessing
correctly).

Computer programs get points for fooling other people into believing their
generated has been generated by a human, or even as correct.

Next steps
----------

 1. Implement a server for this. Current plan:
     * Django (because of its integrated admin interface), providing
     * a fancy modern simpel REST/JSON interface, for both the bots and
     * HTML/JavaScript-based websites.
 2. Fine-tunes the rules: How much points for what action?
 3. Pre-seed it with a bunch of words and explanations.
 4. Provide quick-start data for the players (Dumps of Wikipedia, Wiktionary,
    Project Gutenberg)
 5. Enjoy!

Who
---

 * Joachim “nomeata” Breitner <mail@joachim-breitner.de>
