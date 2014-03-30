# coding=utf-8

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.forms import Form, ModelForm, CharField, HiddenInput
from django.contrib import messages
from django.core.signing import Signer

from nbip.models import Word, Explanation

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

def submit(request):
    if request.method == 'POST':
        form = SubmitForm(request.POST)
        if form.is_valid():
            word = form.save()
            messages.success(request, u"Vielen Dank für Deinen Beitrag „%s“!" % word.lemma)
            return HttpResponseRedirect('/')
    else:
        form = SubmitForm()

    context = {
        'form': form,
    }
    return render(request, 'nbip/submit.html', context)


class ExplainForm(Form):
    word_signed = CharField(widget=HiddenInput())
    explanation = CharField()

def explain(request):
    # Make sure that the user can only submit an explanation for the random word we picked
    signer = Signer()
    if request.method == 'POST':
        form = ExplainForm(request.POST)
        if form.is_valid():
            word_id = signer.unsign(form.cleaned_data['word_signed'])
            word = Word.objects.get(pk=word_id)
            explanation = Explanation(word=word, explanation= form.cleaned_data['explanation'])
            explanation.save()
            messages.success(request, u"Vielen Dank für Deine Erklärung zu „%s“!" % word.lemma)
            return HttpResponseRedirect('/')
    else:
        # TODO: Select a word that the user has not seen before
        # (not submitted nor explained)
        word = Word.random()
        form = ExplainForm(initial = {'word_signed': signer.sign(word.id)})

    context = {
        'word': word,
        'form': form,
    }
    return render(request, 'nbip/explain.html', context)

def guess(request):
    context = {
    }
    return render(request, 'nbip/guess.html', context)
