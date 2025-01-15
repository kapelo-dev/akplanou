from django.db import models
from datetime import timedelta
from django.utils import timezone

class Abonnement(models.Model):
    libelle = models.CharField(max_length=100)
    cout = models.DecimalField(max_digits=10, decimal_places=2)
    max_livres = models.IntegerField()
    max_jours = models.IntegerField()
    duree = models.IntegerField()  # Durée de l'abonnement en jours

    def __str__(self):
        return self.libelle

class Membre(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    adresse = models.CharField(max_length=200)
    telephone = models.CharField(max_length=20)
    abonnement = models.ForeignKey(Abonnement, on_delete=models.CASCADE)
    actif = models.BooleanField(default=True)
    date_inscription = models.DateField(auto_now_add=True)
    date_expiration = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Enregistrer d'abord l'instance pour s'assurer que date_inscription est définie
        super(Membre, self).save(*args, **kwargs)

        # Maintenant, calculer la date d'expiration
        if self.date_inscription and self.abonnement and self.abonnement.duree:
            self.date_expiration = self.date_inscription + timedelta(days=self.abonnement.duree)
            super(Membre, self).save(update_fields=['date_expiration'])

    def __str__(self):
        return f"{self.nom} {self.prenom}"
class Livre(models.Model):
    titre = models.CharField(max_length=200)
    auteur = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13)
    edition = models.CharField(max_length=100)
    genre = models.CharField(max_length=50)
    couverture = models.ImageField(upload_to='couvertures/', null=True, blank=True)

    def __str__(self):
        return self.titre
    def exemplaires_disponibles(self):
        return self.exemplaire_set.filter(disponible=True).count()

class Exemplaire(models.Model):
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE)
    numero = models.IntegerField()
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.livre.titre} - Exemplaire {self.numero}"

class Emprunt(models.Model):
    membre = models.ForeignKey(Membre, on_delete=models.CASCADE)
    exemplaire = models.ForeignKey(Exemplaire, on_delete=models.CASCADE)
    date_emprunt = models.DateField(auto_now_add=True)
    date_retour = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.membre} - {self.exemplaire}"

    def date_retour_prevue(self):
        return self.date_emprunt + timedelta(days=self.membre.abonnement.max_jours)
