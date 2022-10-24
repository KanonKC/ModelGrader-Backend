from django.contrib import admin
from api.models import Problem
from django import forms

class ProblemForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea)
    class Meta:
        model = Problem
        fields = '__all__'

# Register your models here.
class ProblemAdmin(admin.ModelAdmin):
    form = ProblemForm
    list_display = ['problem_id','language','title','time_limit']
    search_fields = ['title','time_limit']
    list_filter = ['language']

admin.site.register(Problem,ProblemAdmin)