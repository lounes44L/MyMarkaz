-- Schéma-- Adapted schema for Cloudflare D1
-- All CREATE TABLE statements for the full Django app

CREATE TABLE Creneau (
    id INTEGER PRIMARY KEY,
    nom TEXT NOT NULL,
    date_creation TEXT NOT NULL
);

CREATE TABLE Classe (
    id INTEGER PRIMARY KEY,
    nom TEXT NOT NULL,
    capacite INTEGER DEFAULT 20,
    date_creation TEXT NOT NULL,
    creneau INTEGER REFERENCES Creneau(id),
    professeur INTEGER REFERENCES Professeur(id)
    "capacite" INTEGER NOT NULL,
    "date_creation" DATETIME NOT NULL,
    "creneau_id" INTEGER
);
CREATE TABLE "ecole_app_eleve" (
    "id" INTEGER PRIMARY KEY,
    "nom" VARCHAR(100) NOT NULL,
    "prenom" VARCHAR(100) NOT NULL,
    "date_naissance" DATE,
    "telephone" VARCHAR(20) NOT NULL,
    "adresse" TEXT NOT NULL,
    "email" VARCHAR(254) NOT NULL,
    "date_creation" DATETIME NOT NULL,
    "classe_id" INTEGER,
    "creneau_id" INTEGER
);
CREATE TABLE "ecole_app_paiement" (
    "id" INTEGER PRIMARY KEY,
    "montant" DECIMAL NOT NULL,
    "date" DATE NOT NULL,
    "methode" VARCHAR(20) NOT NULL,
    "commentaire" TEXT NOT NULL,
    "date_creation" DATETIME NOT NULL,
    "eleve_id" INTEGER NOT NULL
);
CREATE TABLE "ecole_app_professeur" (
    "id" INTEGER PRIMARY KEY,
    "nom" VARCHAR(100) NOT NULL,
    "date_creation" DATETIME NOT NULL,
    "creneau_id" INTEGER
);
ALTER TABLE "ecole_app_classe" ADD COLUMN "professeur_id" INTEGER;
