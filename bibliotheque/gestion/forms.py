from django import forms
from .models import Membre, Livre, Abonnement, Emprunt, Exemplaire

class MembreForm(forms.ModelForm):
    class Meta:
        model = Membre
        fields = ['nom', 'prenom', 'adresse', 'telephone', 'abonnement', 'actif']

    def __init__(self, *args, **kwargs):
        super(MembreForm, self).__init__(*args, **kwargs)
        self.fields['abonnement'].queryset = Abonnement.objects.all()
class LivreForm(forms.ModelForm):
    class Meta:
        model = Livre
        fields = ['titre', 'auteur', 'isbn', 'edition', 'genre', 'couverture']

class AbonnementForm(forms.ModelForm):
    class Meta:
        model = Abonnement
        fields = ['libelle', 'cout', 'max_livres', 'max_jours', 'duree']

class ExemplaireForm(forms.ModelForm):
    class Meta:
        model = Exemplaire
        fields = ['livre', 'numero', 'disponible']

class EmpruntForm(forms.ModelForm):
    membre = forms.ModelChoiceField(queryset=Membre.objects.all())
    exemplaires = forms.ModelMultipleChoiceField(
        queryset=Exemplaire.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = Emprunt
        fields = ['membre', 'exemplaires']
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, help_text='Obligatoire.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')