-- Cloudflare D1 compatible schema for all Django tables

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
);

CREATE TABLE Eleve (
    id INTEGER PRIMARY KEY,
    nom TEXT NOT NULL,
    prenom TEXT,
    date_naissance TEXT,
    telephone TEXT,
    adresse TEXT,
    email TEXT,
    date_creation TEXT NOT NULL,
    classe INTEGER REFERENCES Classe(id),
    creneau INTEGER REFERENCES Creneau(id),
    composante INTEGER REFERENCES Composante(id)
);

CREATE TABLE Paiement (
    id INTEGER PRIMARY KEY,
    montant REAL NOT NULL,
    date TEXT NOT NULL,
    methode TEXT NOT NULL,
    commentaire TEXT,
    date_creation TEXT NOT NULL,
    eleve INTEGER REFERENCES Eleve(id),
    composante INTEGER REFERENCES Composante(id)
);

CREATE TABLE Professeur (
    id INTEGER PRIMARY KEY,
    nom TEXT NOT NULL,
    date_creation TEXT NOT NULL,
    creneau INTEGER REFERENCES Creneau(id),
    composante INTEGER REFERENCES Composante(id)
);

CREATE TABLE Composante (
    id INTEGER PRIMARY KEY,
    nom TEXT NOT NULL UNIQUE,
    description TEXT,
    active INTEGER DEFAULT 1,
    date_creation TEXT NOT NULL
);

CREATE TABLE ListeAttente (
    id INTEGER PRIMARY KEY,
    nom TEXT NOT NULL,
    prenom TEXT,
    date_naissance TEXT,
    telephone TEXT,
    email TEXT,
    remarque TEXT,
    date_ajout TEXT NOT NULL,
    ajoute_definitivement INTEGER DEFAULT 0,
    composante INTEGER REFERENCES Composante(id)
);

CREATE TABLE SiteConfig (
    id INTEGER PRIMARY KEY,
    key TEXT NOT NULL UNIQUE,
    value TEXT NOT NULL
);

CREATE TABLE CarnetPedagogique (
    id INTEGER PRIMARY KEY,
    date_creation TEXT NOT NULL,
    eleve INTEGER UNIQUE REFERENCES Eleve(id),
    composante INTEGER REFERENCES Composante(id)
);

CREATE TABLE EcouteAvantMemo (
    id INTEGER PRIMARY KEY,
    date TEXT NOT NULL,
    debut_page INTEGER NOT NULL,
    fin_page INTEGER NOT NULL,
    remarques TEXT,
    carnet INTEGER REFERENCES CarnetPedagogique(id),
    enseignant INTEGER REFERENCES Professeur(id)
);

CREATE TABLE Memorisation (
    id INTEGER PRIMARY KEY,
    date TEXT NOT NULL,
    debut_page INTEGER NOT NULL,
    fin_page INTEGER NOT NULL,
    remarques TEXT,
    carnet INTEGER REFERENCES CarnetPedagogique(id),
    enseignant INTEGER REFERENCES Professeur(id)
);

CREATE TABLE Repetition (
    id INTEGER PRIMARY KEY,
    sourate TEXT NOT NULL,
    page INTEGER NOT NULL,
    nombre_repetitions INTEGER DEFAULT 0,
    derniere_date TEXT NOT NULL,
    carnet INTEGER REFERENCES CarnetPedagogique(id)
);

CREATE TABLE Revision (
    id INTEGER PRIMARY KEY,
    semaine INTEGER NOT NULL,
    date TEXT NOT NULL,
    jour TEXT NOT NULL,
    nombre_hizb INTEGER DEFAULT 0,
    carnet INTEGER REFERENCES CarnetPedagogique(id)
);

CREATE TABLE NoteExamen (
    id INTEGER PRIMARY KEY,
    titre TEXT NOT NULL,
    type_examen TEXT NOT NULL,
    sourate_concernee TEXT,
    note REAL NOT NULL,
    note_max REAL DEFAULT 20,
    date_examen TEXT NOT NULL,
    commentaire TEXT,
    date_creation TEXT NOT NULL,
    date_modification TEXT NOT NULL,
    classe INTEGER REFERENCES Classe(id),
    eleve INTEGER REFERENCES Eleve(id),
    professeur INTEGER REFERENCES Professeur(id)
);

CREATE TABLE ParametreSite (
    id INTEGER PRIMARY KEY,
    montant_defaut_eleve REAL DEFAULT 200.0,
    date_modification TEXT NOT NULL
);

CREATE TABLE ProgressionCoran (
    id INTEGER PRIMARY KEY,
    sourate_actuelle TEXT,
    page_actuelle INTEGER DEFAULT 1,
    direction_memorisation TEXT DEFAULT 'debut',
    date_mise_a_jour TEXT NOT NULL,
    eleve INTEGER UNIQUE REFERENCES Eleve(id)
);

CREATE TABLE NiveauEleve (
    id INTEGER PRIMARY KEY,
    nom TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE InscriptionEleve (
    id INTEGER PRIMARY KEY,
    date_debut TEXT NOT NULL,
    date_fin TEXT,
    active INTEGER DEFAULT 1,
    ancien_niveau TEXT,
    raison_changement TEXT,
    date_changement TEXT,
    date_creation TEXT NOT NULL,
    date_modification TEXT NOT NULL,
    annee_scolaire INTEGER,
    classe INTEGER REFERENCES Classe(id),
    creneau INTEGER REFERENCES Creneau(id),
    eleve INTEGER REFERENCES Eleve(id),
    niveau INTEGER REFERENCES NiveauEleve(id)
);

CREATE TABLE TarifInscription (
    id INTEGER PRIMARY KEY,
    nombre_heures INTEGER NOT NULL,
    montant_annuel REAL NOT NULL,
    annee_scolaire INTEGER
);

CREATE TABLE CompetenceLivre (
    id INTEGER PRIMARY KEY,
    lecon INTEGER NOT NULL,
    description TEXT NOT NULL,
    ordre INTEGER DEFAULT 0,
    date_creation TEXT NOT NULL
);

CREATE TABLE EvaluationCompetence (
    id INTEGER PRIMARY KEY,
    statut TEXT NOT NULL,
    date_evaluation TEXT NOT NULL,
    commentaire TEXT,
    date_creation TEXT NOT NULL,
    date_modification TEXT NOT NULL,
    competence INTEGER REFERENCES CompetenceLivre(id),
    eleve INTEGER REFERENCES Eleve(id)
);
