-- Index à créer après les tables
CREATE INDEX "ecole_app_classe_creneau_id_21c0f114" ON "ecole_app_classe" ("creneau_id");
CREATE INDEX "ecole_app_eleve_classe_id_9b43a839" ON "ecole_app_eleve" ("classe_id");
CREATE INDEX "ecole_app_eleve_creneau_id_aac8cf1c" ON "ecole_app_eleve" ("creneau_id");
CREATE INDEX "ecole_app_paiement_eleve_id_a1b0c3e8" ON "ecole_app_paiement" ("eleve_id");
CREATE INDEX "ecole_app_professeur_creneau_id_708ed5e4" ON "ecole_app_professeur" ("creneau_id");
CREATE INDEX "ecole_app_classe_professeur_id_a0ff6a93" ON "ecole_app_classe" ("professeur_id");
