# functional-doc-sync — Guide Utilisateur

## Quoi

Un skill Claude Code qui maintient une documentation fonctionnelle Markdown synchronisée avec le code, dans Git.

## Pourquoi

Le développement assisté par IA génère du code via des conversations éphémères. Sans mécanisme dédié, la documentation dérive du code en quelques jours. Ce skill force la synchronisation en intégrant la doc dans le flux de développement.

## Prérequis

- Claude Code avec support des custom skills
- Un projet Git initialisé
- Ce skill installé dans le répertoire de skills Claude Code

## Installation

Copier le dossier `functional-doc-sync/` dans votre répertoire de skills Claude Code (ex: `~/.claude/skills/` ou le répertoire configuré).

## Les 5 Commandes

| Commande | Quand l'utiliser | Durée typique |
|----------|-----------------|---------------|
| `/doc:init` | Premier run sur un projet existant | 5-20 min selon taille |
| `/doc:update` | Après chaque changement fonctionnel | 1-3 min |
| `/doc:interview` | Pour capturer le savoir tacite | 5-30 min (interactif) |
| `/doc:challenge` | Revue périodique ou post-refactoring | 3-10 min |
| `/doc:coverage` | Mesurer la complétude | 1-2 min |

## Workflow Quotidien

### Scénario typique : développement itératif

```
toi  → "Ajoute un endpoint de reset password"
claude → [code le endpoint]
toi  → "/doc:update"
claude → [met à jour docs/features/auth.md + CHANGELOG-FUNCTIONAL.md]
toi  → "commit"
claude → [commit code + doc ensemble]
```

### Premier run sur un projet existant

```
toi  → "/doc:init"
claude → [analyse le code, génère toute la structure docs/]
claude → "J'ai 14 items [À confirmer]. Voulez-vous lancer /doc:interview ?"
toi  → "oui"
claude → [pose des questions une par une sur les zones d'ombre]
```

### Revue hebdomadaire

```
toi  → "/doc:challenge"
claude → [rapport : 2 inconsistances, 1 doc morte, 3 features non documentées]
toi  → "corrige ce que tu peux"
claude → [corrige les évidences, flag le reste en [À confirmer]]
toi  → "/doc:coverage"
claude → [génère la carte de couverture]
```

## Tags Épistémiques

La doc générée utilise des tags pour indiquer la fiabilité de chaque assertion :

- **`[Code]`** — Vérifiable directement dans le code source. Fiable.
- **`[Inférence]`** — Déduit du code par l'IA. Probablement correct mais à vérifier.
- **`[À confirmer]`** — Zone d'ombre nécessitant un humain. Prioritaire en revue.
- **`[Déclaré]`** — Confirmé ou fourni par un humain. Fiable.
- **`[Décision]`** — Décision d'architecture documentée (ADR). Fiable.

### Pourquoi c'est important

L'IA lit le code et déduit des intentions. Parfois elle a raison, parfois non. Les tags rendent visible le niveau de confiance. Sans eux, la doc paraît autoritaire alors qu'elle contient des hypothèses.

### Workflow de maturation

```
[Inférence] → /doc:interview → [Déclaré]  (confirmation humaine)
[Inférence] → /doc:challenge → [Code]      (vérifié contre le code actuel)
[À confirmer] → /doc:interview → [Déclaré] (résolu par un humain)
```

L'objectif est de faire tendre la doc vers un maximum de `[Code]` et `[Déclaré]`, minimum de `[À confirmer]`.

## Structure de Documentation Générée

```
docs/
├── OVERVIEW.md              # Vision, stack, architecture macro
├── ARCHITECTURE.md          # Composants, dépendances, flux de données
├── CHANGELOG-FUNCTIONAL.md  # Journal des évolutions fonctionnelles
├── COVERAGE.md              # Carte de couverture (auto-générée)
├── features/                # Un fichier par bloc fonctionnel
│   ├── auth.md
│   ├── payments.md
│   └── ...
└── decisions/               # Architecture Decision Records
    ├── 001-choice-of-db.md
    └── ...
```

### Ce que chaque fichier contient

- **OVERVIEW.md** — Ce que fait le projet, pour qui, avec quoi (stack). Lu en premier par un nouveau dev ou un agent IA.
- **ARCHITECTURE.md** — Comment les composants s'articulent. Diagrammes de flux, dépendances entre modules.
- **features/*.md** — Le détail de chaque bloc fonctionnel : comportement attendu, règles métier, cas limites.
- **decisions/*.md** — Les "pourquoi" : chaque choix technique ou business significatif documenté avec son contexte et ses conséquences.
- **CHANGELOG-FUNCTIONAL.md** — Journal chronologique des évolutions *fonctionnelles* (pas un git log technique).
- **COVERAGE.md** — Tableau de bord : qu'est-ce qui est documenté, à quel niveau de confiance, et qu'est-ce qui manque.

## Bonnes Pratiques

### À faire

- Lancer `/doc:update` après chaque changement fonctionnel (pas les refactors purs)
- Lancer `/doc:challenge` au moins une fois par semaine sur un projet actif
- Commiter doc et code ensemble (même commit)
- Utiliser `/doc:interview` quand un collègue métier est disponible — c'est le meilleur moment pour capturer le savoir tacite

### À éviter

- Ne pas essayer de tout documenter en une fois — itérer
- Ne pas supprimer les tags `[À confirmer]` sans les avoir résolus
- Ne pas documenter l'implémentation technique dans les features (c'est le rôle du code et des commentaires)
- Ne pas créer un fichier feature par micro-fonctionnalité — grouper par domaine métier

## FAQ

**Q : Et si je fais plusieurs changements avant de lancer `/doc:update` ?**
Le mode update analyse le diff complet. Plusieurs changements seront traités ensemble. Mais plus le diff est gros, plus le risque d'oubli est élevé. Préférer des updates fréquents.

**Q : Le skill fonctionne-t-il avec n'importe quel langage ?**
Oui. L'analyse se base sur la structure du projet, les fichiers de config, et le code source. Le skill s'adapte à la stack détectée.

**Q : Comment gérer les projets multi-repo ?**
Chaque repo a sa propre `docs/`. Pour une doc transversale, créer un repo dédié `docs-system` avec des liens vers les docs de chaque repo.

**Q : La doc générée est-elle parfaite ?**
Non. C'est le point central : les tags épistémiques rendent explicite ce qui est fiable et ce qui ne l'est pas. La doc est un point de départ qui s'améliore par itération.
