from django.contrib import admin
from api.models import Problem,Account
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

class AccountAdmin(admin.ModelAdmin):
    list_display = ['account_id','username','email','is_admin','is_active']
    list_filter = ['is_admin','is_active']

admin.site.register(Problem,ProblemAdmin)
admin.site.register(Account,AccountAdmin)