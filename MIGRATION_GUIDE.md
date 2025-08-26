# Guide de Migration vers Cloudflare D1

## Étapes de Migration

### 1. Configuration des Variables d'Environnement

Créez un fichier `.env` à la racine du projet avec vos informations Cloudflare :

```env
# Configuration Cloudflare D1
CLOUDFLARE_ACCOUNT_ID=votre_account_id
CLOUDFLARE_DATABASE_ID=votre_database_id  
CLOUDFLARE_API_TOKEN=votre_api_token

# Activer D1 (mettre à True pour utiliser D1)
USE_CLOUDFLARE_D1=False

# Django Settings
SECRET_KEY=django-insecure-3k4ad-xui)q4+z$q33rbg(b3qp%kom&sbhay6)i(3!g=+3z(ce
DEBUG=True
```

### 2. Obtenir vos Identifiants Cloudflare

1. **Account ID** : Disponible dans le dashboard Cloudflare, section "Account ID"
2. **Database ID** : ID de votre base `mymarkaz-db` dans la section D1
3. **API Token** : Créez un token avec permissions D1 dans "My Profile" > "API Tokens"

### 3. Installation des Dépendances

```bash
pip install -r requirements.txt
```

### 4. Export des Données Actuelles

```bash
python scripts/export_data.py
```

Cela créera :
- `data_export.json` : Toutes vos données actuelles
- `schema_export.sql` : Structure des tables

### 5. Import vers Cloudflare D1

```bash
python scripts/import_to_d1.py
```

### 6. Activation de D1

Dans votre fichier `.env`, changez :
```env
USE_CLOUDFLARE_D1=True
```

### 7. Test de la Migration

```bash
python manage.py runserver
```

## Commandes Utiles

### Revenir à SQLite (rollback)
```env
USE_CLOUDFLARE_D1=False
```

### Vérifier les données exportées
```bash
python -c "import json; data=json.load(open('data_export.json')); print(f'Modèles: {len(data)}')"
```

### Test de connexion D1
```bash
python -c "from scripts.import_to_d1 import CloudflareD1Importer; CloudflareD1Importer().test_connection()"
```

## Troubleshooting

### Erreur de connexion D1
- Vérifiez vos identifiants Cloudflare
- Assurez-vous que l'API Token a les bonnes permissions
- Vérifiez que la base `mymarkaz-db` existe

### Erreur d'import
- Vérifiez que les fichiers d'export existent
- Consultez les logs pour identifier les requêtes problématiques

### Performance
- D1 a des limites de requêtes par minute
- Pour de gros volumes, ajoutez des pauses dans l'import

## Notes Importantes

- **Backup** : Gardez toujours une copie de `db.sqlite3` avant migration
- **Test** : Testez d'abord avec `USE_CLOUDFLARE_D1=False`
- **Production** : Activez D1 seulement après validation complète
