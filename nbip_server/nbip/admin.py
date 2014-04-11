from django.contrib import admin

from nbip.models import *

admin.site.register(Word)
admin.site.register(Explanation)

class GameRoundEntryInline(admin.TabularInline):
    model = GameRoundEntry
    extra = 0
    readonly_fields = ('explanation','pos')
    fields = ('explanation','pos','guess')

    def has_delete_permission(self, request, obj=None):
        return None

class GameRoundAdmin(admin.ModelAdmin):
    inlines = [GameRoundEntryInline]

admin.site.register(GameRound, GameRoundAdmin)
