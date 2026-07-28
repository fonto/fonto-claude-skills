---
name: synthesize
description: "Use when the user provides a meeting transcript, call notes, or raw meeting text and wants it turned into a compte rendu, minutes, decisions, or action items. Triggers: transcription de réunion, compte rendu, CR de réunion, relevé de décisions, notes de réunion, meeting notes, minutes, action items. Trigger with /meeting-transcript-synthesizer:synthesize"
---

# Meeting Transcript Synthesizer

**Announce:** "J'utilise le plugin meeting-transcript-synthesizer pour produire le compte rendu."

## Objectif

Transformer une transcription de réunion en compte rendu fiable, hiérarchisé
et exploitable.

Exécuter dans un seul appel les phases internes suivantes :

1. contrôle de qualité de la transcription ;
2. extraction factuelle ;
3. regroupement thématique ;
4. classification des conclusions ;
5. rédaction ;
6. contrôle contradictoire.

Ne montrer que le résultat final.

## Entrées

Entrée principale obligatoire : transcription texte.

Si aucune transcription texte n'est fournie (audio, vidéo, lien vers un
enregistrement), s'arrêter et demander le texte. Ne pas tenter de deviner le
contenu.

Entrées facultatives :

- langue de sortie, par défaut la langue principale de la réunion ;
- type de réunion ;
- objectif connu ;
- participants et rôles ;
- destinataire, par défaut les participants ;
- niveau de détail : court, standard ou détaillé ;
- format : Markdown, par défaut, ou JSON.

## Règles impératives

- Utiliser uniquement le contenu fourni, sans connaissance externe.
- Ne pas corriger silencieusement un nom, un acronyme ou un terme technique
  incertain ; conserver la formulation originale.
- Ne pas inventer d'attribution, de décision, de responsable ou d'échéance.
- Distinguer systématiquement : information, proposition, décision,
  action confirmée, action potentielle, question ouverte.
- En cas d'ambiguïté, retenir la qualification la moins engageante.
- Marquer toute interprétation avec [Inférence].
- Conserver une preuve courte ou un horodatage pour les éléments importants.
- Fusionner les répétitions sans supprimer les nuances, conditions ou
  désaccords.
- Si la transcription est trop dégradée pour soutenir une conclusion,
  l'indiquer explicitement.

## Procédure interne

### 1. Évaluer la source

Identifier :

- les locuteurs reconnaissables ;
- les horodatages disponibles ;
- les passages incompréhensibles ;
- les changements de sujet ou de langue ;
- les contradictions ;
- les risques de mauvaise attribution.

### 2. Construire un registre factuel

Extraire : faits et chiffres, contexte et objectifs, contraintes, positions et
arguments, désaccords, propositions, décisions explicites, actions et
engagements, responsables et échéances explicites, risques et dépendances,
questions ouvertes.

Pour chaque élément, conserver sa preuve : locuteur, citation courte ou
horodatage.

### 3. Regrouper par thème

Réorganiser la matière par thème métier. Ne pas résumer chronologiquement,
sauf demande explicite.

### 4. Classifier

- DÉCISION : décision explicitement prise ou validée.
- PROPOSITION : option suggérée mais non validée.
- ACTION CONFIRMÉE : tâche explicitement acceptée ou assignée.
- ACTION POTENTIELLE : tâche évoquée sans engagement explicite.
- QUESTION OUVERTE : point sans réponse ou sans arbitrage.
- INFORMATION : fait ou contexte ne nécessitant pas d'action.

Une formulation comme « on pourrait », « il faudrait peut-être » ou
« une option serait » reste une proposition ou une action potentielle.

### 5. Contrôle final obligatoire

Vérifier avant restitution :

1. chaque décision est explicitement soutenue ;
2. chaque action confirmée a été acceptée ou assignée explicitement ;
3. aucun responsable n'est déduit d'un rôle ou d'un poste ;
4. aucune échéance n'est inventée ;
5. les désaccords significatifs sont conservés ;
6. les conditions et réserves ne sont pas omises ;
7. chaque citation correspond à la conclusion qu'elle appuie ;
8. aucune information externe n'a été ajoutée.

Reclasser ou supprimer tout élément échouant à ce contrôle.

## Sortie par défaut, en Markdown

### 1. Résumé exécutif

De 3 à 7 puces. Décisions, changements, risques et dépendances en priorité.
Ne pas raconter la réunion chronologiquement.

### 2. Décisions

Pour chaque décision :

- Décision :
- Motif :
- Conditions ou réserves :
- Source : locuteur et horodatage, ou citation courte

Si aucune décision explicite : « Aucune décision explicite identifiée. »

### 3. Points clés par thème

Pour chaque thème :

- Contexte :
- Éléments importants :
- Positions ou désaccords :
- Conclusion :

### 4. Actions

| Statut | Action | Responsable | Échéance | Source |
|---|---|---|---|---|

Statut : Confirmée ou Potentielle.
Ne jamais déduire le responsable à partir du poste.
Ne jamais inventer d'échéance.

### 5. Risques et dépendances

| Risque ou dépendance | Impact évoqué | Réponse envisagée |
|---|---|---|

### 6. Questions ouvertes

- Question :
- Prochaine étape :
- Responsable :

### 7. Propositions non validées

- Proposition :
- Auteur : uniquement si certain
- Motif de l'absence de décision :

### 8. Qualité de la transcription

Signaler uniquement ce qui peut modifier l'interprétation : attribution
incertaine, passage incompréhensible, terme technique ou acronyme incertain,
absence d'horodatage, contradiction non résolue, changement de langue.

### 9. Niveau de confiance

- Élevé : locuteurs identifiés, conclusions explicites, transcription claire.
- Moyen : ambiguïtés ponctuelles sans effet majeur.
- Faible : dégradation affectant plusieurs conclusions.

Justifier en une phrase.

## Conventions de remplissage

- « Non précisé » : information absente de la transcription.
- « Attribution incertaine » : locuteur non identifiable.
- [Inférence] : interprétation nécessaire, à expliciter.

## Sortie JSON

Si le format demandé est JSON, produire cette structure :

```json
{
  "meeting": { "objectif": "", "type": "", "participants": [] },
  "resume_executif": [],
  "decisions": [
    { "titre": "", "decision": "", "motif": "",
      "conditions": "", "source": "" }
  ],
  "themes": [
    { "theme": "", "contexte": "", "elements": [],
      "positions": [], "conclusion": "" }
  ],
  "actions": [
    { "statut": "confirmee|potentielle", "action": "",
      "responsable": "", "echeance": "", "source": "" }
  ],
  "risques": [
    { "risque": "", "impact": "", "reponse": "" }
  ],
  "questions_ouvertes": [
    { "question": "", "prochaine_etape": "", "responsable": "" }
  ],
  "propositions_non_validees": [
    { "proposition": "", "auteur": "", "motif": "" }
  ],
  "qualite_transcription": [],
  "niveau_confiance": { "niveau": "eleve|moyen|faible",
                        "justification": "" }
}
```

Utiliser null pour toute valeur absente en JSON, et non la chaîne
« Non précisé ».
