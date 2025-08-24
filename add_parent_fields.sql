-- Script pour ajouter les colonnes manquantes à la table ecole_app_eleve
ALTER TABLE ecole_app_eleve ADD COLUMN prenom_pere VARCHAR(100) NULL;
ALTER TABLE ecole_app_eleve ADD COLUMN prenom_mere VARCHAR(100) NULL;
ALTER TABLE ecole_app_eleve ADD COLUMN telephone_secondaire VARCHAR(20) NULL;
