from django.shortcuts import render, redirect, get_object_or_404
from .models import Emprunt, Exemplaire, Membre, Livre, Abonnement
from .forms import EmpruntForm, MembreForm, LivreForm, AbonnementForm, ExemplaireForm
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404

from django.contrib.auth.decorators import login_required
@login_required
def gestion_membres_view(request):
    membres = Membre.objects.all()
    return render(request, 'gestion/gestion_membres.html', {'membres': membres})
def ajouter_membre_view(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        adresse = request.POST.get('adresse')
        telephone = request.POST.get('telephone')
        abonnement_id = request.POST.get('abonnement')
        actif = request.POST.get('actif') == 'True'

        abonnement = get_object_or_404(Abonnement, id=abonnement_id)
        membre = Membre(nom=nom, prenom=prenom, adresse=adresse, telephone=telephone, abonnement=abonnement, actif=actif)
        membre.save()
        return redirect('gestion_membres')
    else:
        abonnements = Abonnement.objects.all()
        return render(request, 'gestion/ajouter_membre.html', {'abonnements': abonnements})

def membre_detail_view(request, membre_id):
    membre = get_object_or_404(Membre, id=membre_id)
    emprunts_en_cours = membre.emprunt_set.filter(date_retour__isnull=True)
    return render(request, 'gestion/membre_detail.html', {'membre': membre, 'emprunts_en_cours': emprunts_en_cours})

def modifier_membre_view(request, membre_id):
    membre = get_object_or_404(Membre, id=membre_id)
    if request.method == 'POST':
        form = MembreForm(request.POST, instance=membre)
        if form.is_valid():
            form.save()
            return redirect('gestion_membres')
    else:
        form = MembreForm(instance=membre)
    return render(request, 'gestion/modifier_membre.html', {'form': form})

def supprimer_membre_view(request, membre_id):
    membre = get_object_or_404(Membre, id=membre_id)
    if request.method == 'POST':
        membre.delete()
        return redirect('gestion_membres')
    return render(request, 'gestion/supprimer_membre.html', {'membre': membre})

def ajouter_abonnement_view(request):
    if request.method == 'POST':
        form = AbonnementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gestion_abonnements')
    else:
        form = AbonnementForm()
    return render(request, 'gestion/ajouter_abonnement.html', {'form': form})
@login_required
def gestion_emprunts_view(request):
    emprunts = Emprunt.objects.all().order_by('-date_emprunt')
    return render(request, 'gestion/gestion_emprunts.html', {'emprunts': emprunts})
@login_required


def ajouter_emprunt_view(request):
    if request.method == 'POST':
        membre_id = request.POST.get('membre')
        exemplaire_ids = request.POST.get('exemplaires').split(',')
        membre = get_object_or_404(Membre, id=membre_id)

        # Vérification de l'état de l'abonnement
        if not membre.actif or membre.date_expiration < timezone.now().date():
            messages.error(request, "L'abonnement du membre est inactif ou expiré. L'emprunt est interdit.")
            return redirect('ajouter_emprunt')

        # Vérification du nombre maximum de livres empruntés
        if membre.emprunt_set.filter(date_retour__isnull=True).count() + len(exemplaire_ids) > membre.abonnement.max_livres:
            messages.error(request, "Le nombre maximum de livres empruntés a été atteint.")
            return redirect('ajouter_emprunt')

        # Si l'abonnement est actif et le nombre de livres est dans la limite, continuez avec l'emprunt
        for exemplaire_id in exemplaire_ids:
            exemplaire = get_object_or_404(Exemplaire, id=exemplaire_id)
            emprunt = Emprunt(membre=membre, exemplaire=exemplaire, date_emprunt=timezone.now())
            exemplaire.disponible = False
            exemplaire.save()
            emprunt.save()

        messages.success(request, "Emprunt ajouté avec succès.")
        return redirect('gestion_emprunts')
    else:
        membres = Membre.objects.all()
        livres = Livre.objects.all()
        return render(request, 'gestion/ajouter_emprunt.html', {'membres': membres, 'livres': livres})


def load_exemplaires(request, livre_id):
    livre = get_object_or_404(Livre, id=livre_id)
    exemplaires = Exemplaire.objects.filter(livre=livre, disponible=True)
    return JsonResponse({'exemplaires': list(exemplaires.values('id', 'livre__titre', 'numero'))})

def retour_view(request, emprunt_id):
    emprunt = get_object_or_404(Emprunt, id=emprunt_id)
    emprunt.date_retour = timezone.now()
    emprunt.exemplaire.disponible = True
    emprunt.exemplaire.save()
    emprunt.save()
    return redirect('membre_detail', membre_id=emprunt.membre.id)

def historique_view(request, membre_id):
    emprunts = Emprunt.objects.filter(membre_id=membre_id)
    return render(request, 'gestion/historique.html', {'emprunts': emprunts})


def accueil_view(request):
    return render(request, 'gestion/accueil.html')
@login_required
def gestion_livres_view(request):
    livres = Livre.objects.all()
    return render(request, 'gestion/gestion_livres.html', {'livres': livres})
@login_required
def gestion_abonnements_view(request):
    abonnements = Abonnement.objects.all()
    return render(request, 'gestion/gestion_abonnements.html', {'abonnements': abonnements})
@login_required
def gestion_exemplaires_view(request):
    livres = Livre.objects.all()
    return render(request, 'gestion/gestion_exemplaires.html', {'livres': livres})
@login_required
def ajouter_livre_view(request):
    if request.method == 'POST':
        form = LivreForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('gestion_livres')
    else:
        form = LivreForm()
    return render(request, 'gestion/ajouter_livre.html', {'form': form})
def livre_detail_view(request, livre_id):
    livre = get_object_or_404(Livre, id=livre_id)
    exemplaires = Exemplaire.objects.filter(livre=livre)
    return render(request, 'gestion/livre_detail.html', {'livre': livre, 'exemplaires': exemplaires})
def modifier_livre_view(request, livre_id):
    livre = get_object_or_404(Livre, id=livre_id)
    if request.method == 'POST':
        form = LivreForm(request.POST, request.FILES, instance=livre)
        if form.is_valid():
            form.save()
            return redirect('gestion_livres')
    else:
        form = LivreForm(instance=livre)
    return render(request, 'gestion/modifier_livre.html', {'form': form, 'livre': livre})
def supprimer_livre_view(request, livre_id):
    livre = get_object_or_404(Livre, id=livre_id)
    if request.method == 'POST':
        livre.delete()
        return redirect('gestion_livres')
    return render(request, 'gestion/supprimer_livre.html', {'livre': livre})

def modifier_abonnement_view(request, abonnement_id):
    abonnement = get_object_or_404(Abonnement, id=abonnement_id)
    if request.method == 'POST':
        libelle = request.POST.get('libelle')
        cout = request.POST.get('cout')
        max_livres = request.POST.get('max_livres')
        max_jours = request.POST.get('max_jours')
        duree = request.POST.get('duree')

        abonnement.libelle = libelle
        abonnement.cout = cout
        abonnement.max_livres = max_livres
        abonnement.max_jours = max_jours
        abonnement.duree = duree
        abonnement.save()
        return redirect('gestion_abonnements')
    else:
        return render(request, 'gestion/modifier_abonnement.html', {'abonnement': abonnement})
def supprimer_abonnement_view(request, abonnement_id):
    abonnement = get_object_or_404(Abonnement, id=abonnement_id)
    if request.method == 'POST':
        abonnement.delete()
        return redirect('gestion_abonnements')
    return render(request, 'gestion/supprimer_abonnement.html', {'abonnement': abonnement})

def ajouter_exemplaire_view(request):
    if request.method == 'POST':
        livre_id = request.POST.get('livre')
        numero = request.POST.get('numero')
        disponible = request.POST.get('disponible') == 'True'
        livre = get_object_or_404(Livre, id=livre_id)
        exemplaire = Exemplaire(livre=livre, numero=numero, disponible=disponible)
        exemplaire.save()
        return redirect('gestion_exemplaires')
    else:
        livres = Livre.objects.all()
        return render(request, 'gestion/ajouter_exemplaire.html', {'livres': livres})
def exemplaires_empruntes(self):
        # Supposons que vous avez un modèle Exemplaire avec un champ emprunte
        return self.exemplaire_set.filter(disponible=False).count()
    
def modifier_exemplaire(request, exemplaire_id):
    exemplaire = get_object_or_404(Exemplaire, id=exemplaire_id)
    if request.method == 'POST':
        form = ExemplaireForm(request.POST, instance=exemplaire)
        if form.is_valid():
            form.save()
            return redirect('livre_detail', livre_id=exemplaire.livre.id)
    else:
        form = ExemplaireForm(instance=exemplaire)
    return render(request, 'gestion/modifier_exemplaire.html', {'form': form, 'exemplaire': exemplaire})

def supprimer_exemplaire(request, exemplaire_id):
    exemplaire = get_object_or_404(Exemplaire, id=exemplaire_id)
    if request.method == 'POST':
        exemplaire.delete()
        return redirect('livre_detail', livre_id=exemplaire.livre.id)
    return render(request, 'gestion/supprimer_exemplaire.html', {'exemplaire': exemplaire})

from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignUpForm

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Redirige vers la page d'accueil après l'inscription
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

from django.contrib.auth.decorators import login_required


from django.shortcuts import render
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncDay  # Grouper par jour
from .models import Livre, Membre, Emprunt
from datetime import timedelta
@login_required
def dashboard_view(request):
    # Statistiques principales
    total_livres = Livre.objects.count()
    membres_actifs = Membre.objects.filter(actif=True).count()
    total_membres = Membre.objects.count()
    membres_inactifs = total_membres - membres_actifs
    pourcentage_actifs = (membres_actifs / total_membres) * 100 if total_membres > 0 else 0
    pourcentage_inactifs = (membres_inactifs / total_membres) * 100 if total_membres > 0 else 0
    livres_empruntes = Emprunt.objects.filter(date_retour__isnull=True).count()
    aujourd_hui = timezone.now().date()
    retours_en_attente = Emprunt.objects.filter(date_retour__lt=aujourd_hui).count()

    # Dernières activités (10 derniers emprunts)
    dernieres_activites = Emprunt.objects.select_related('membre', 'exemplaire').order_by('-date_emprunt')[:10]

    # Données pour le graphique (emprunts du dernier mois)
    un_mois_avant = aujourd_hui - timedelta(days=30)  # 1 mois en arrière
    emprunts_par_jour = (
        Emprunt.objects
        .filter(date_emprunt__gte=un_mois_avant)  # Emprunts du dernier mois
        .annotate(jour=TruncDay('date_emprunt'))  # Grouper par jour
        .values('jour')
        .annotate(total=Count('id'))  # Compter les emprunts par jour
        .order_by('jour')
    )

    # Préparer les données pour Chart.js
    labels = []
    data = []
    for emprunt in emprunts_par_jour:
        labels.append(emprunt['jour'].strftime('%d %b'))  # Format : "01 Jan"
        data.append(emprunt['total'])

    # Passer les données au template
    context = {
        'total_livres': total_livres,
        'membres_actifs': membres_actifs,
        'total_membres': total_membres,
        'membres_inactifs': membres_inactifs,
        'pourcentage_actifs': pourcentage_actifs,
        'pourcentage_inactifs': pourcentage_inactifs,
        'livres_empruntes': livres_empruntes,
        'retours_en_attente': retours_en_attente,
        'dernieres_activites': dernieres_activites,
        'labels': labels,
        'data': data,
    }
    return render(request, 'gestion/dashboard.html', context)

from django.shortcuts import render, get_object_or_404
from .models import Emprunt
from .forms import EmpruntForm

def modifier_emprunt(request, emprunt_id):
    emprunt = get_object_or_404(Emprunt, id=emprunt_id)
    if request.method == 'POST':
        form = EmpruntForm(request.POST, instance=emprunt)
        if form.is_valid():
            form.save()
            return redirect('gestion_emprunts')  # Redirige vers la liste des emprunts
    else:
        form = EmpruntForm(instance=emprunt)
    return render(request, 'gestion/modifier_emprunt.html', {'form': form})
from django.shortcuts import get_object_or_404, redirect
from .models import Emprunt

def supprimer_emprunt(request, emprunt_id):
    emprunt = get_object_or_404(Emprunt, id=emprunt_id)
    if request.method == 'POST':
        emprunt.delete()
        return redirect('gestion_emprunts')  # Redirige vers la liste des emprunts
    # Si la méthode n'est pas POST, tu peux gérer cela différemment (par exemple, afficher une erreur)

    from django.shortcuts import render, get_object_or_404, redirect
from .models import Livre, Exemplaire
from .forms import ExemplaireForm

def ajouter_exemplaire(request, livre_id):
    livre = get_object_or_404(Livre, id=livre_id)
    if request.method == 'POST':
        form = ExemplaireForm(request.POST)
        if form.is_valid():
            exemplaire = form.save(commit=False)
            exemplaire.livre = livre
            exemplaire.save()
            return redirect('livre_detail', livre_id=livre.id)
    else:
        form = ExemplaireForm()
    return render(request, 'gestion/ajouter_exemplaire.html', {'form': form, 'livre': livre})
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Emprunt, Exemplaire

def supprimer_emprunt(request, emprunt_id):
    emprunt = get_object_or_404(Emprunt, id=emprunt_id)

    if request.method == 'POST':
        # Marquer l'exemplaire comme disponible
        exemplaire = emprunt.exemplaire
        exemplaire.disponible = True
        exemplaire.save()

        # Supprimer l'emprunt
        emprunt.delete()

        messages.success(request, "L'emprunt a été supprimé avec succès.")
        return redirect('gestion_emprunts')

    return render(request, 'gestion/supprimer_emprunt.html', {'emprunt': emprunt})
