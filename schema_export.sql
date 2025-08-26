BEGIN;
--
-- Create model Creneau
--
CREATE TABLE "ecole_app_creneau" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "nom" varchar(100) NOT NULL, "date_creation" datetime NOT NULL);
--
-- Create model Classe
--
CREATE TABLE "ecole_app_classe" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "nom" varchar(100) NOT NULL, "capacite" integer NOT NULL, "date_creation" datetime NOT NULL, "creneau_id" bigint NULL REFERENCES "ecole_app_creneau" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model Eleve
--
CREATE TABLE "ecole_app_eleve" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "nom" varchar(100) NOT NULL, "prenom" varchar(100) NOT NULL, "date_naissance" date NULL, "telephone" varchar(20) NOT NULL, "adresse" text NOT NULL, "email" varchar(254) NOT NULL, "date_creation" datetime NOT NULL, "classe_id" bigint NULL REFERENCES "ecole_app_classe" ("id") DEFERRABLE INITIALLY DEFERRED, "creneau_id" bigint NULL REFERENCES "ecole_app_creneau" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model Paiement
--
CREATE TABLE "ecole_app_paiement" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "montant" decimal NOT NULL, "date" date NOT NULL, "methode" varchar(20) NOT NULL, "commentaire" text NOT NULL, "date_creation" datetime NOT NULL, "eleve_id" bigint NOT NULL REFERENCES "ecole_app_eleve" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model Professeur
--
CREATE TABLE "ecole_app_professeur" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "nom" varchar(100) NOT NULL, "date_creation" datetime NOT NULL, "creneau_id" bigint NULL REFERENCES "ecole_app_creneau" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Add field professeur to classe
--
ALTER TABLE "ecole_app_classe" ADD COLUMN "professeur_id" bigint NULL REFERENCES "ecole_app_professeur" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "ecole_app_classe_creneau_id_21c0f114" ON "ecole_app_classe" ("creneau_id");
CREATE INDEX "ecole_app_eleve_classe_id_9b43a839" ON "ecole_app_eleve" ("classe_id");
CREATE INDEX "ecole_app_eleve_creneau_id_aac8cf1c" ON "ecole_app_eleve" ("creneau_id");
CREATE INDEX "ecole_app_paiement_eleve_id_a1b0c3e8" ON "ecole_app_paiement" ("eleve_id");
CREATE INDEX "ecole_app_professeur_creneau_id_708ed5e4" ON "ecole_app_professeur" ("creneau_id");
CREATE INDEX "ecole_app_classe_professeur_id_a0ff6a93" ON "ecole_app_classe" ("professeur_id");
COMMIT;
