from django import forms
from .models import Attempt, Tester


class AttemptForm(forms.ModelForm):
    #tester_choice = forms.MultipleChoiceField()
    comments = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'id':'comment_area', 'placeholder': 'Place Comments Here...','rows':14}))
    class Meta:
        model = Attempt
        fields = ['comments',]
    
#class TesterForm(forms.ModelForm):
#    testers = Tester.objects.all()
#    test_list []
#    for tester in testers:
#        test_list.append(tester.username)
#    test_list= tuple(test_list)
#    tester_choice = forms.ChoiceField(choices=test_list)
#
#    class Meta:
#        model = Attempt
#        fields = ['tester',]
