# coding=utf-8

from django.shortcuts import render, redirect, get_object_or_404
from django.forms import Form, ModelForm, CharField, HiddenInput, ChoiceField
from django.contrib import messages
from django.core.signing import Signer
from django.contrib.auth.decorators import login_required

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
            return redirect('index')
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
        # TODO: Select a word that the user has not seen before
        # (not submitted nor explained nor guessed)
        word = Word.random()
        form = ExplainForm(initial = {'word_signed': signer.sign(word.id)})

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
        round = GameRound.start_new_round(player = request.user)
        return redirect('guess', round.pk)

def guess(request, round_id):
    round = get_object_or_404(GameRound, pk=round_id)
    if round.guess is not None:
        return redirect('view_guess', round.pk)
    expls = round.get_explanations()

    # TODO: Check permissions
    if request.method == 'POST':
        guesses = []
        for n in range(5):
            guesses.append(int(request.POST['guess%d' % n]))

        round.set_guesses(guesses)
        return redirect('view_guess', round.pk)

    context = {
        'word': round.word,
        'explanations': expls,
        }
    return render(request, 'nbip/guess.html', context)

def view_guess(request, round_id):
    round = get_object_or_404(GameRound, pk=round_id)
    if round.guess is None:
        return redirect('guess', round.pk)
    expls = round.get_explanations()

    context = {
        'word': round.word,
        'explanations': expls,
        }
    return render(request, 'nbip/view_guess.html', context)
