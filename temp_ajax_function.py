@login_required
@require_POST
def modifier_presence_eleve_ajax(request):
    """Vue AJAX pour modifier une présence d'élève sans redirection"""
    presence_id = request.POST.get('presence_id')
    status = request.POST.get('status')
    commentaire = request.POST.get('commentaire')
    
    if not presence_id or not status:
        return JsonResponse({'success': False, 'message': 'Données incomplètes'}, status=400)
    
    try:
        presence = get_object_or_404(PresenceEleve, pk=presence_id)
        
        # Vérifier si l'utilisateur est autorisé à modifier cette présence
        est_admin_user = is_admin(request.user)
        est_prof_classe = False
        
        if hasattr(request.user, 'professeur'):
            # Vérifier si le professeur enseigne dans la classe de l'élève
            if presence.classe:
                est_prof_classe = presence.classe in request.user.professeur.get_all_classes()
        
        if not (est_admin_user or est_prof_classe):
            return JsonResponse({'success': False, 'message': 'Non autorisé'}, status=403)
        
        # Mettre à jour les champs present et justifie en fonction du statut
        if status == 'present':
            presence.present = True
            presence.justifie = False
        elif status == 'absent_justifie':
            presence.present = False
            presence.justifie = True
        elif status == 'absent':
            presence.present = False
            presence.justifie = False
        else:
            return JsonResponse({'success': False, 'message': 'Statut invalide'}, status=400)
        
        # Mettre à jour le commentaire
        presence.commentaire = commentaire
        presence.save()
        
        return JsonResponse({
            'success': True, 
            'message': 'Présence modifiée avec succès',
            'status': status,
            'commentaire': commentaire or '-'
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
