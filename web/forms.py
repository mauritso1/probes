from django import forms
from datetimewidget.widgets import DateTimeWidget


frequency_choices = [("0", "All")] + [(x, x) for x in range(2412, 2472, 5)]

class ProbeSearchForm(forms.Form):
    BSSID = forms.CharField(label='BSSID', max_length=20, required=False)
    source_address = forms.CharField(label='Source address', max_length=20, required=False)
    frequency = forms.ChoiceField(label='Frequency', choices=frequency_choices)
    signal_strength_from = forms.ChoiceField(label='Signal strength from', choices=[(x, x) for x in range(-100, 0)]) 
    signal_strength_to = forms.ChoiceField(label='Signal strength to', choices=[(x, x) for x in range(0, -100, -1)])
    time_from = forms.DateTimeField(widget=DateTimeWidget(options={'minuteStep':1}, bootstrap_version=3), label='Time from', required=False)
    time_to = forms.DateTimeField(widget=DateTimeWidget(options={'minuteStep':1}, bootstrap_version=3), label='Time to', required=False)
