-- Migration SQL pour ajouter la colonne page_debut_sourate à la table ecole_app_progressioncoran
ALTER TABLE ecole_app_progressioncoran ADD COLUMN page_debut_sourate INTEGER DEFAULT 1 NOT NULL;
