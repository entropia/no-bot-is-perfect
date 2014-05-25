# coding=utf-8

from django.http import HttpResponse

from django.views.decorators.csrf import csrf_exempt



from nbip.models import *


def error(str):
    return HttpResponse(str+"\n",
        status = 400,
        content_type = "text/plain; charset=utf-8",
        reason = str)

def ok(str):
    return HttpResponse(str,
        content_type = "text/plain; charset=utf-8")

@csrf_exempt
def get(request):
    if request.method != 'POST':
        return error("Request must be a POST request")

    if 'key' not in request.POST:
        return error("Request must have a key value")

    bot = Bot.objects \
            .filter(apikey = request.POST['key']) \
            .select_related('explaining') \
            .first()
    if not bot:
        return error("Invalid API key")

    word = bot.word_to_explain()

    return ok(word.lemma)

@csrf_exempt
def put(request):
    if request.method != 'POST':
        return error("Request must be a POST request")

    if 'key' not in request.POST:
        return error("Request must contain a \"key\"")

    bot = Bot.objects \
            .filter(apikey = request.POST['key']) \
            .select_related('explaining') \
            .first()
    if not bot:
        return error("Invalid API key")

    if not bot.explaining:
        return error(u"You first need to get a word to explain")

    if 'expl' not in request.POST:
        return error("Request must contain an \"expl\"")

    bot.explain_word(request.POST['expl'])

    return ok("Thanks, explanation noted\n")

