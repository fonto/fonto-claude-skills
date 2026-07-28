# meeting-transcript-synthesizer

Transforme une transcription de réunion en compte rendu fiable, hiérarchisé et
exploitable.

## Utilisation

```
/meeting-transcript-synthesizer:synthesize
```

Le skill se déclenche aussi tout seul quand tu fournis une transcription et
demandes un compte rendu, un CR, un relevé de décisions ou des action items.

**Entrée obligatoire : une transcription texte.** Ce plugin ne transcrit pas
l'audio. Si tu fournis un enregistrement sans texte, il s'arrête et demande la
transcription plutôt que de deviner.

**Entrées facultatives :** langue de sortie, type de réunion, objectif,
participants et rôles, destinataire, niveau de détail (court, standard,
détaillé), format (Markdown par défaut, ou JSON).

## Sortie

Résumé exécutif, décisions, points clés par thème, tableau des actions, risques
et dépendances, questions ouvertes, propositions non validées, qualité de la
transcription, niveau de confiance.

## Garanties de fidélité

- Aucun responsable déduit d'un poste ou d'un rôle.
- Aucune échéance inventée.
- Distinction stricte entre information, proposition, décision, action
  confirmée, action potentielle et question ouverte ; en cas d'ambiguïté, la
  qualification la moins engageante l'emporte.
- Preuve conservée (locuteur, citation courte ou horodatage) pour les éléments
  importants.
- Désaccords, conditions et réserves préservés.
- Toute interprétation marquée `[Inférence]`.
- Contrôle contradictoire avant restitution : tout élément non soutenu par la
  transcription est reclassé ou supprimé.

## Test

`fixtures/reunion-exemple.md` est une transcription piégée. Colle-la dans une
session neuve, demande un compte rendu sans nommer le skill, et vérifie que la
sortie tient : voir les critères en tête du fichier.
