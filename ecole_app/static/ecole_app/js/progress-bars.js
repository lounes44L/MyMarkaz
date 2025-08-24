/**
 * Script pour initialiser les barres de progression dynamiques
 */
$(document).ready(function() {
    // Initialiser les barres de progression dynamiques
    $('.progress-width-dynamic').each(function() {
        var width = $(this).data('width');
        var value = $(this).data('value');
        
        // Définir la largeur via CSS
        $(this).css('width', width + '%');
        
        // Définir l'attribut ARIA aria-valuenow avec une valeur numérique
        $(this).attr('aria-valuenow', parseInt(value));
    });
});
