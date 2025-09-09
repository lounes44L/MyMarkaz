-- Add page_debut and page_fin columns to the ObjectifMensuel table
ALTER TABLE ecole_app_objectifmensuel ADD COLUMN page_debut integer NULL;
ALTER TABLE ecole_app_objectifmensuel ADD COLUMN page_fin integer NULL;
