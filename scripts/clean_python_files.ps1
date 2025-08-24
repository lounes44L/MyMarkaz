# Script PowerShell pour nettoyer les octets nuls dans les fichiers Python
# Ce script parcourt tous les fichiers Python du projet et supprime les octets nuls

# Définir le répertoire de base (répertoire parent du dossier scripts)
$baseDir = Split-Path -Parent $PSScriptRoot

Write-Host "Nettoyage des fichiers Python dans: $baseDir"

# Compteurs pour les statistiques
$totalFiles = 0
$cleanedFiles = 0

# Fonction pour nettoyer un fichier
function Clean-File {
    param (
        [string]$filePath
    )
    
    Write-Host "Vérification du fichier: $filePath"
    
    try {
        # Lire le contenu du fichier en binaire
        $content = [System.IO.File]::ReadAllBytes($filePath)
        
        # Vérifier si le fichier contient des octets nuls (0x00)
        $hasNullBytes = $false
        for ($i = 0; $i -lt $content.Length; $i++) {
            if ($content[$i] -eq 0) {
                $hasNullBytes = $true
                break
            }
        }
        
        if ($hasNullBytes) {
            Write-Host "Octets nuls trouvés dans: $filePath" -ForegroundColor Yellow
            
            # Créer une sauvegarde
            $backupPath = "$filePath.bak"
            [System.IO.File]::WriteAllBytes($backupPath, $content)
            
            # Supprimer les octets nuls
            $cleanedContent = @()
            for ($i = 0; $i -lt $content.Length; $i++) {
                if ($content[$i] -ne 0) {
                    $cleanedContent += $content[$i]
                }
            }
            
            # Écrire le contenu nettoyé
            [System.IO.File]::WriteAllBytes($filePath, $cleanedContent)
            
            Write-Host "Fichier nettoyé: $filePath (sauvegarde créée: $backupPath)" -ForegroundColor Green
            return $true
        } else {
            Write-Host "Pas d'octets nuls dans: $filePath" -ForegroundColor Green
            return $false
        }
    } catch {
        Write-Host "Erreur lors du traitement de $filePath : $_" -ForegroundColor Red
        return $false
    }
}

# Trouver tous les fichiers Python récursivement
$pythonFiles = Get-ChildItem -Path $baseDir -Filter "*.py" -Recurse -File | 
               Where-Object { $_.FullName -notlike "*\__pycache__\*" }

$totalFiles = $pythonFiles.Count
Write-Host "Nombre total de fichiers Python trouvés: $totalFiles"

# Nettoyer chaque fichier
foreach ($file in $pythonFiles) {
    $cleaned = Clean-File -filePath $file.FullName
    if ($cleaned) {
        $cleanedFiles++
    }
}

# Afficher les résultats
Write-Host "`nRésumé:"
Write-Host "- Fichiers Python analysés: $totalFiles"
Write-Host "- Fichiers nettoyés (octets nuls supprimés): $cleanedFiles"

if ($cleanedFiles -gt 0) {
    Write-Host "`n✅ Des octets nuls ont été supprimés. Vérifiez que votre application fonctionne correctement."
} else {
    Write-Host "`n✅ Aucun octet nul n'a été trouvé dans les fichiers Python."
}
