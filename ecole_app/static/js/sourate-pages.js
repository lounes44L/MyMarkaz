/**
 * Script pour gérer la sélection dynamique des sourates et pages
 * Ce script permet de charger les pages correspondantes à une sourate sélectionnée
 */

document.addEventListener('DOMContentLoaded', function() {
    // Fonctions pour les formulaires de mémorisation
    setupSouratePageSelection('sourate-select', 'debut-page-select', 'fin-page-select');
    
    // Fonctions pour les formulaires d'écoute
    setupSouratePageSelection('sourate-select-ecoute', 'debut-page-select-ecoute', 'fin-page-select-ecoute');
    
    // Fonctions pour les formulaires de répétition
    setupSouratePageSelection('sourate-select-repetition', 'page-select-repetition');
    
    // Activer les champs désactivés avant la soumission du formulaire
    setupFormSubmitHandler();
});

/**
 * Configure la sélection dynamique des pages en fonction de la sourate
 * @param {string} sourateSelectId - ID du select de sourate
 * @param {string} debutPageSelectId - ID du select de page de début
 * @param {string} finPageSelectId - ID du select de page de fin (optionnel)
 */
function setupSouratePageSelection(sourateSelectId, debutPageSelectId, finPageSelectId = null) {
    const sourateSelect = document.getElementById(sourateSelectId);
    const debutPageSelect = document.getElementById(debutPageSelectId);
    
    if (!sourateSelect || !debutPageSelect) return;
    
    let finPageSelect = null;
    if (finPageSelectId) {
        finPageSelect = document.getElementById(finPageSelectId);
    }
    
    // Fonction pour charger les pages d'une sourate
    function loadSouratePages(sourateIndex) {
        // Activer les champs de sélection de page
        debutPageSelect.disabled = true;
        if (finPageSelect) finPageSelect.disabled = true;
        
        // Vider les options actuelles
        debutPageSelect.innerHTML = '<option value="">Chargement...</option>';
        if (finPageSelect) finPageSelect.innerHTML = '<option value="">Chargement...</option>';
        
        // Appel AJAX pour récupérer les pages de la sourate
        fetch(`/api/sourate-pages/?sourate_index=${sourateIndex}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error('Erreur:', data.error);
                    return;
                }
                
                // Remplir les options de page
                debutPageSelect.innerHTML = '';
                if (finPageSelect) finPageSelect.innerHTML = '';
                
                data.pages.forEach(([pageValue, pageLabel]) => {
                    const debutOption = document.createElement('option');
                    debutOption.value = pageValue;
                    debutOption.textContent = pageLabel;
                    debutPageSelect.appendChild(debutOption);
                    
                    if (finPageSelect) {
                        const finOption = document.createElement('option');
                        finOption.value = pageValue;
                        finOption.textContent = pageLabel;
                        finPageSelect.appendChild(finOption);
                    }
                });
                
                // Activer les champs de sélection de page
                debutPageSelect.disabled = false;
                if (finPageSelect) finPageSelect.disabled = false;
            })
            .catch(error => {
                console.error('Erreur lors de la récupération des pages:', error);
                debutPageSelect.innerHTML = '<option value="">Erreur de chargement</option>';
                if (finPageSelect) finPageSelect.innerHTML = '<option value="">Erreur de chargement</option>';
            });
    }
    
    // Événement de changement de sourate
    sourateSelect.addEventListener('change', function() {
        const sourateIndex = this.value;
        if (sourateIndex) {
            loadSouratePages(sourateIndex);
        } else {
            // Réinitialiser et désactiver les champs de page
            debutPageSelect.innerHTML = '<option value="">Sélectionnez d\'abord une sourate</option>';
            debutPageSelect.disabled = true;
            
            if (finPageSelect) {
                finPageSelect.innerHTML = '<option value="">Sélectionnez d\'abord une sourate</option>';
                finPageSelect.disabled = true;
            }
        }
    });
    
    // Charger les pages si une sourate est déjà sélectionnée
    if (sourateSelect.value) {
        loadSouratePages(sourateSelect.value);
    } else {
        // Initialiser les champs de page
        debutPageSelect.innerHTML = '<option value="">Sélectionnez d\'abord une sourate</option>';
        debutPageSelect.disabled = true;
        
        if (finPageSelect) {
            finPageSelect.innerHTML = '<option value="">Sélectionnez d\'abord une sourate</option>';
            finPageSelect.disabled = true;
        }
    }
}

/**
 * Configure les gestionnaires d'événements pour activer les champs désactivés avant la soumission du formulaire
 */
function setupFormSubmitHandler() {
    // Trouver tous les formulaires qui contiennent des champs de répétition
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            // Activer tous les champs select désactivés pour qu'ils soient envoyés avec le formulaire
            const disabledSelects = this.querySelectorAll('select[disabled]');
            disabledSelects.forEach(select => {
                // Seulement activer si le champ a une valeur sélectionnée
                if (select.value) {
                    select.disabled = false;
                }
            });
        });
    });
}
