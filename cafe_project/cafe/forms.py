from django import forms
from .models import TableReservation


class TableReservationForm(forms.ModelForm):
    class Meta:
        model = TableReservation
        fields = ['name', 'email', 'phone', 'date', 'time', 'table_number']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }



