/**
 * Script pour gérer la sélection dynamique des sourates et pages
 * Ce script permet de charger les pages correspondantes à une sourate sélectionnée
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing sourate-pages.js');
    
    // Fonctions pour les formulaires de mémorisation
    const sourateSelect = document.getElementById('id_sourate_select');
    const debutPageSelect = document.getElementById('id_debut_page');
    const finPageSelect = document.getElementById('id_fin_page');
    
    // S'assurer que les champs de page ne sont pas désactivés
    if (debutPageSelect) {
        debutPageSelect.disabled = false;
        console.log('Enabled debut_page select');
    }
    
    if (finPageSelect) {
        finPageSelect.disabled = false;
        console.log('Enabled fin_page select');
    }
    
    // S'assurer que le champ de page pour les répétitions n'est pas désactivé
    const pageSelect = document.getElementById('id_page');
    if (pageSelect) {
        pageSelect.disabled = false;
        console.log('Enabled page select for repetition');
    }
    
    if (sourateSelect && debutPageSelect) {
        console.log('Found memorisation form elements');
        setupSouratePageSelection(sourateSelect, debutPageSelect, finPageSelect);
    } else {
        console.log('Memorisation form elements not found');
    }
    
    // Fonctions pour les formulaires d'écoute
    const sourateSelectEcoute = document.getElementById('sourate-select-ecoute');
    const debutPageSelectEcoute = document.getElementById('debut-page-select-ecoute');
    const finPageSelectEcoute = document.getElementById('fin-page-select-ecoute');
    
    if (sourateSelectEcoute && debutPageSelectEcoute) {
        setupSouratePageSelection(sourateSelectEcoute, debutPageSelectEcoute, finPageSelectEcoute);
    }
    
    // Fonctions pour les formulaires de répétition
    const sourateSelectRepetition = document.getElementById('id_sourate_select');
    const pageSelectRepetition = document.getElementById('id_page');
    
    if (sourateSelectRepetition && pageSelectRepetition && !finPageSelect) {
        console.log('Found repetition form elements');
        setupSouratePageSelection(sourateSelectRepetition, pageSelectRepetition, null);
    }
    
    // Activer les champs désactivés avant la soumission du formulaire
    setupFormSubmitHandler();
});

/**
 * Fonction pour configurer la sélection de pages en fonction de la sourate
 * @param {string} sourateSelectId - ID du sélecteur de sourate
 * @param {string} debutPageSelectId - ID du sélecteur de page de début
 * @param {string} finPageSelectId - ID du sélecteur de page de fin (optionnel)
 * @param {boolean} singlePageMode - Mode page unique pour les répétitions
 */
function setupSouratePageSelection(sourateSelectId, debutPageSelectId, finPageSelectId = null, singlePageMode = false) {
    console.log(`Setting up sourate-page selection for: ${sourateSelectId}, ${debutPageSelectId}, ${finPageSelectId || 'no fin page'}, singlePageMode: ${singlePageMode}`);
    
    // Récupérer les éléments du DOM
    const sourateSelect = document.getElementById(sourateSelectId);
    const debutPageSelect = document.getElementById(debutPageSelectId);
    const finPageSelect = finPageSelectId ? document.getElementById(finPageSelectId) : null;
    
    // Vérifier que les éléments existent
    if (!sourateSelect || !debutPageSelect) {
        console.error(`Elements not found: sourateSelect=${!!sourateSelect}, debutPageSelect=${!!debutPageSelect}`);
        return;
    }
    
    console.log('Elements found, setting up event handlers');
    
    // Fonction pour charger les pages d'une sourate
    function loadSouratePages(sourateIndex) {
        console.log(`Loading pages for sourate ${sourateIndex}`);
        
        // Vider les sélecteurs de pages
        debutPageSelect.innerHTML = '';
        if (finPageSelect) finPageSelect.innerHTML = '';
        
        // Ajouter une option par défaut
        const defaultDebutOption = document.createElement('option');
        defaultDebutOption.value = "";
        defaultDebutOption.textContent = "Chargement...";
        debutPageSelect.appendChild(defaultDebutOption);
        
        if (finPageSelect) {
            const defaultFinOption = document.createElement('option');
            defaultFinOption.value = "";
            defaultFinOption.textContent = "Chargement...";
            finPageSelect.appendChild(defaultFinOption);
        }
        
        // Activer les champs de sélection de page
        debutPageSelect.disabled = false;
        if (finPageSelect) finPageSelect.disabled = false;
        
        // Appel AJAX pour récupérer les pages de la sourate
        fetch(`/api/sourate-pages/?sourate_index=${sourateIndex}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erreur HTTP: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Pages received:', data);
                
                // Vider les sélecteurs
                debutPageSelect.innerHTML = '';
                if (finPageSelect) finPageSelect.innerHTML = '';
                
                // Ajouter une option par défaut
                const defaultDebutOption = document.createElement('option');
                defaultDebutOption.value = "";
                defaultDebutOption.textContent = "Sélectionnez une page";
                debutPageSelect.appendChild(defaultDebutOption);
                
                if (finPageSelect) {
                    const defaultFinOption = document.createElement('option');
                    defaultFinOption.value = "";
                    defaultFinOption.textContent = "Sélectionnez une page";
                    finPageSelect.appendChild(defaultFinOption);
                }
                
                // Vérifier si nous avons des pages
                if (data.pages && data.pages.length > 0) {
                    console.log('Nombre de pages reçues:', data.pages.length);
                    
                    // Ajouter les options de page
                    data.pages.forEach(([pageValue, pageLabel]) => {
                        console.log('Ajout de la page:', pageValue, pageLabel);
                        
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
                } else {
                    console.warn('Aucune page reçue pour cette sourate');
                }
            })
            .catch(error => {
                console.error('Erreur lors de la récupération des pages:', error);
                debutPageSelect.innerHTML = '<option value="">Erreur de chargement</option>';
                if (finPageSelect) finPageSelect.innerHTML = '<option value="">Erreur de chargement</option>';
            });
    }
    
    // Événement de changement de sourate
    sourateSelect.addEventListener('change', function() {
        console.log('Sourate changed to:', this.value);
        const sourateIndex = this.value;
        if (sourateIndex) {
            loadSouratePages(sourateIndex);
        } else {
            // Réinitialiser les sélecteurs de page
            debutPageSelect.innerHTML = '<option value="">Sélectionnez d\'abord une sourate</option>';
            if (finPageSelect) {
                finPageSelect.innerHTML = '<option value="">Sélectionnez d\'abord une sourate</option>';
            }
        }
    });
    
    // Charger les pages si une sourate est déjà sélectionnée
    if (sourateSelect.value) {
        console.log('Initial sourate value:', sourateSelect.value);
        loadSouratePages(sourateSelect.value);
    } else {
        console.log('No initial sourate value');
        // Initialiser les champs de page
        debutPageSelect.innerHTML = '<option value="">Sélectionnez d\'abord une sourate</option>';
        
        if (finPageSelect) {
            finPageSelect.innerHTML = '<option value="">Sélectionnez d\'abord une sourate</option>';
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
