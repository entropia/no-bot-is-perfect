# coding=utf-8

from django.shortcuts import render, redirect, get_object_or_404
from django.forms import Form, ModelForm, CharField, HiddenInput, ChoiceField
from django.contrib import messages
from django.core.signing import Signer
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from nbip.models import *

def index(request):
    context = {
        'n_words': Word.objects.count(),
        'n_explanations': Explanation.objects.count(),
    }
    return render(request, 'nbip/index.html', context)


class SubmitForm(ModelForm):
    class Meta:
        model = Word
        fields = ['lemma', 'correct_explanation', 'reference']

@login_required()
def submit(request):
    if request.method == 'POST':
        form = SubmitForm(request.POST)
        if form.is_valid():
            word = form.save(commit=False)
            word.author = request.user
            word.save()
            messages.success(request, u"Vielen Dank für Deinen Beitrag „%s“!" % word.lemma)
            return redirect('submit')
    else:
        form = SubmitForm()

    context = {
        'form': form,
    }
    return render(request, 'nbip/submit.html', context)


class ExplainForm(Form):
    word_signed = CharField(widget=HiddenInput())
    explanation = CharField()

@login_required()
def explain(request):
    # Make sure that the user can only submit an explanation for the random word we picked
    signer = Signer()
    if request.method == 'POST':
        form = ExplainForm(request.POST)
        if form.is_valid():
            word_id = signer.unsign(form.cleaned_data['word_signed'])
            word = Word.objects.get(pk=word_id)
            explanation = Explanation(
                        word=word,
                        explanation= form.cleaned_data['explanation'],
                        author = request.user,
                        )
            explanation.save()
            messages.success(request, u"Vielen Dank für Deine Erklärung zu „%s“!" % word.lemma)
            return redirect('index')
    else:
        try:
            word = Word.random(player = request.user)
            form = ExplainForm(initial = {'word_signed': signer.sign(word.id)})
        except NotEnoughWordsException:
            messages.error(request, u"Leider gibt es nicht genügend Wörter. Motiviere deine Freunde, ein paar neue Wörter einzugeben!")
            return redirect('index')


    context = {
        'word': word,
        'form': form,
    }
    return render(request, 'nbip/explain.html', context)

@login_required()
def new_guess(request):
    # Create a new game
    # TODO: For the current player
    # and switch to it (or to the existing running game)
    running_rounds = GameRound.objects.filter(guess__exact=None)
    if running_rounds:
        round = running_rounds[0]
        return redirect('guess', round.pk)
    else:
        try:
            round = GameRound.start_new_round(player = request.user)
        except NotEnoughWordsException:
            messages.error(request, u"Leider gibt es nicht genügend Wörter. Motiviere deine Freunde, ein paar neue Wörter einzugeben und Erklärungen zu erfinden!")
            return redirect('index')
        return redirect('guess', round.pk)

@login_required()
def guess(request, round_id):
    round = get_object_or_404(GameRound, pk=round_id)
    if round.player != request.user:
        raise PermissionDenied
    if round.guess is not None:
        return redirect('view_guess', round.pk)

    expls = round.get_explanations()
    counts = round.get_counts()

    # TODO: Check permissions
    if request.method == 'POST':
        guesses = []
        for n in range(len(expls)):
            guesses.append(int(request.POST['guess%d' % n]))

        round.set_guesses(guesses)
        return redirect('view_guess', round.pk)

    context = {
        'word': round.word,
        'explanations': expls,
        'counts': counts,
        }
    return render(request, 'nbip/guess.html', context)

@login_required()
def view_guess(request, round_id):
    round = get_object_or_404(GameRound, pk=round_id)
    if round.player != request.user:
        raise PermissionDenied
    if round.guess is None:
        return redirect('guess', round.pk)
    expls = round.get_explanations()

    context = {
        'word': round.word,
        'explanations': expls,
        }
    return render(request, 'nbip/view_guess.html', context)

def highscore(request):
    # Multiple annotations across different tables do _not_ work!
    # (Solution: Keep score in the user profile, update using triggers)
    scores = User.objects \
            .annotate(submitted_word_count = Count('submitted_words')) \
            .annotate(submitted_explanation_count = Count('submitted_explanations')) \
            .annotate(games_played = Count('gamerounds'))
    print scores.query
    return scores.values("username", "submitted_word_count", "submitted_explanation_count", "games_played")

@login_required()
def stats(request):
    context = {
    }
    return render(request, 'nbip/stats.html', context)
