from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ecole_app.models import Composante, Eleve, Professeur, Classe, AnneeScolaire


class ComposanteTestCase(TestCase):
    """Tests pour le système de composantes"""

    def setUp(self):
        """Configuration initiale pour les tests"""
        # Créer un utilisateur administrateur
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password123'
        )
        
        # Créer une année scolaire
        self.annee = AnneeScolaire.objects.create(
            nom='2023-2024',
            date_debut='2023-09-01',
            date_fin='2024-06-30',
            active=True
        )
        
        # Créer des composantes
        self.composante1 = Composante.objects.create(
            nom='École Enfants',
            description='Composante pour les enfants',
            active=True
        )
        
        self.composante2 = Composante.objects.create(
            nom='École Adultes',
            description='Composante pour les adultes',
            active=True
        )
        
        # Client pour les requêtes HTTP
        self.client = Client()
        
    def test_composante_creation(self):
        """Test de création d'une composante"""
        # Connexion en tant qu'admin
        self.client.login(username='admin', password='password123')
        
        # Données pour la nouvelle composante
        data = {
            'nom': 'École Femmes',
            'description': 'Composante pour les femmes'
        }
        
        # Envoi de la requête POST pour créer la composante
        response = self.client.post(reverse('creer_composante'), data)
        
        # Vérifier que la redirection a bien eu lieu
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que la composante a bien été créée
        self.assertTrue(Composante.objects.filter(nom='École Femmes').exists())
        
    def test_composante_modification(self):
        """Test de modification d'une composante"""
        # Connexion en tant qu'admin
        self.client.login(username='admin', password='password123')
        
        # Données pour la modification
        data = {
            'nom': 'École Enfants Modifiée',
            'description': 'Description modifiée',
            'active': True
        }
        
        # Envoi de la requête POST pour modifier la composante
        response = self.client.post(
            reverse('modifier_composante', args=[self.composante1.id]), 
            data
        )
        
        # Vérifier que la redirection a bien eu lieu
        self.assertEqual(response.status_code, 302)
        
        # Rafraîchir l'objet depuis la base de données
        self.composante1.refresh_from_db()
        
        # Vérifier que les modifications ont bien été appliquées
        self.assertEqual(self.composante1.nom, 'École Enfants Modifiée')
        self.assertEqual(self.composante1.description, 'Description modifiée')
        
    def test_composante_suppression(self):
        """Test de suppression d'une composante"""
        # Connexion en tant qu'admin
        self.client.login(username='admin', password='password123')
        
        # Créer une composante temporaire pour la supprimer
        composante_temp = Composante.objects.create(
            nom='Composante Temporaire',
            description='À supprimer',
            active=True
        )
        
        # Envoi de la requête POST pour supprimer la composante
        response = self.client.post(
            reverse('supprimer_composante', args=[composante_temp.id])
        )
        
        # Vérifier que la redirection a bien eu lieu
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que la composante a bien été supprimée
        self.assertFalse(Composante.objects.filter(id=composante_temp.id).exists())
        
    def test_composante_selection(self):
        """Test de sélection d'une composante"""
        # Connexion en tant qu'admin
        self.client.login(username='admin', password='password123')
        
        # Envoi de la requête POST pour sélectionner une composante
        response = self.client.post(
            reverse('selectionner_composante'),
            {'composante_id': self.composante1.id}
        )
        
        # Vérifier que la redirection a bien eu lieu
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que la composante a bien été enregistrée en session
        session = self.client.session
        self.assertEqual(session.get('composante_id'), self.composante1.id)
        
    def test_composante_isolation(self):
        """Test d'isolation des données entre composantes"""
        # Créer des élèves dans différentes composantes
        eleve1 = Eleve.objects.create(
            nom='Nom1',
            prenom='Prenom1',
            user=User.objects.create_user(username='eleve1', password='password123'),
            composante=self.composante1
        )
        
        eleve2 = Eleve.objects.create(
            nom='Nom2',
            prenom='Prenom2',
            user=User.objects.create_user(username='eleve2', password='password123'),
            composante=self.composante2
        )
        
        # Créer des professeurs dans différentes composantes
        prof1 = Professeur.objects.create(
            nom='NomProf1',
            prenom='PrenomProf1',
            user=User.objects.create_user(username='prof1', password='password123'),
            composante=self.composante1
        )
        
        prof2 = Professeur.objects.create(
            nom='NomProf2',
            prenom='PrenomProf2',
            user=User.objects.create_user(username='prof2', password='password123'),
            composante=self.composante2
        )
        
        # Créer des classes dans différentes composantes
        classe1 = Classe.objects.create(
            nom='Classe1',
            annee_scolaire=self.annee,
            composante=self.composante1
        )
        
        classe2 = Classe.objects.create(
            nom='Classe2',
            annee_scolaire=self.annee,
            composante=self.composante2
        )
        
        # Vérifier l'isolation des élèves
        self.assertEqual(Eleve.objects.filter(composante=self.composante1).count(), 1)
        self.assertEqual(Eleve.objects.filter(composante=self.composante2).count(), 1)
        
        # Vérifier l'isolation des professeurs
        self.assertEqual(Professeur.objects.filter(composante=self.composante1).count(), 1)
        self.assertEqual(Professeur.objects.filter(composante=self.composante2).count(), 1)
        
        # Vérifier l'isolation des classes
        self.assertEqual(Classe.objects.filter(composante=self.composante1).count(), 1)
        self.assertEqual(Classe.objects.filter(composante=self.composante2).count(), 1)
        
    def test_statistiques_composante(self):
        """Test d'affichage des statistiques d'une composante"""
        # Connexion en tant qu'admin
        self.client.login(username='admin', password='password123')
        
        # Créer des données pour les statistiques
        eleve = Eleve.objects.create(
            nom='Nom',
            prenom='Prenom',
            user=User.objects.create_user(username='eleve', password='password123'),
            composante=self.composante1
        )
        
        prof = Professeur.objects.create(
            nom='NomProf',
            prenom='PrenomProf',
            user=User.objects.create_user(username='prof', password='password123'),
            composante=self.composante1
        )
        
        classe = Classe.objects.create(
            nom='Classe',
            annee_scolaire=self.annee,
            composante=self.composante1,
            capacite=20
        )
        
        # Ajouter l'élève à la classe
        classe.eleves.add(eleve)
        
        # Accéder à la page de statistiques
        response = self.client.get(
            reverse('statistiques_composante', args=[self.composante1.id])
        )
        
        # Vérifier que la page s'affiche correctement
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que les données sont bien présentes dans le contexte
        self.assertEqual(response.context['composante'], self.composante1)
        self.assertEqual(response.context['total_eleves'], 1)
        self.assertEqual(response.context['total_professeurs'], 1)
        self.assertEqual(response.context['total_classes'], 1)
