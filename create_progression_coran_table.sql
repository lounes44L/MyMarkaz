CREATE TABLE IF NOT EXISTS "ecole_app_progressioncoran" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "sourate_actuelle" varchar(100) NULL,
    "page_actuelle" integer NOT NULL,
    "direction_memorisation" varchar(10) NOT NULL,
    "date_mise_a_jour" datetime NOT NULL,
    "eleve_id" integer NOT NULL REFERENCES "ecole_app_eleve" ("id") DEFERRABLE INITIALLY DEFERRED
);

-- Create index for the foreign key
CREATE INDEX IF NOT EXISTS "ecole_app_progressioncoran_eleve_id_idx" ON "ecole_app_progressioncoran" ("eleve_id");

-- Add the migration record to django_migrations table
INSERT INTO django_migrations (app, name, applied) 
VALUES ('ecole_app', '0041_progressioncoran', datetime('now'));
