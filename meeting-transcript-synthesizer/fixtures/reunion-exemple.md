# Fixture de test

Transcription piégée. Coller le bloc ci-dessous dans une session neuve, demander
un compte rendu **sans nommer le skill**, puis vérifier la sortie contre ces
critères.

Attendu :

1. La migration Postgres sort en **DÉCISION** (« ok, on part là-dessus »).
2. Le cache Redis sort en **PROPOSITION**, pas en décision (« on pourrait »).
3. Le benchmark est une **ACTION CONFIRMÉE**, responsable Marc, échéance vendredi.
4. La doc de migration est une **ACTION POTENTIELLE**, responsable « Non précisé ».
5. Le chiffre `[inaudible]` remonte en §8 Qualité de la transcription, et aucune
   valeur n'est inventée à sa place.
6. Le désaccord Sophie / Marc sur la fenêtre de coupure survit, non tranché.
7. « le DSI » n'est jamais désigné responsable d'une action : il n'est pas nommé
   et n'a rien accepté.
8. Aucune connaissance externe sur Postgres, Redis ou les stratégies de migration
   n'est ajoutée.

---

```
[00:02] Sophie : Bon, sujet du jour, la base. On est à bout sur MySQL, les
locks nous tuent en fin de mois.

[00:04] Marc : Oui. J'ai regardé, Postgres réglerait le problème de
concurrence sur les écritures.

[00:05] Sophie : Le coût de migration ?

[00:06] Marc : Deux sprints, à la louche. Le vrai risque c'est le schéma des
commandes, il y a des triggers partout.

[00:09] Sophie : Ok, on part là-dessus. Postgres, on lance sur le prochain
trimestre. Je valide.

[00:10] Marc : Noté.

[00:12] Sophie : Autre chose, la latence sur la page catalogue.

[00:13] Marc : On pourrait mettre un cache Redis devant, ça absorberait les
pics.

[00:14] Sophie : Peut-être. J'aimerais des chiffres avant de m'engager
là-dessus, on en reparle.

[00:15] Marc : Je fais le benchmark, je te sors ça pour vendredi.

[00:16] Sophie : Parfait.

[00:19] Sophie : Il faudrait aussi documenter la procédure de migration, sinon
personne ne saura rejouer ça.

[00:20] Marc : Mmh, oui.

[00:22] Sophie : Sur la migration, on coupe le service combien de temps ?

[00:23] Marc : Une fenêtre de quatre heures un dimanche, c'est le plus sûr.

[00:24] Sophie : Non, quatre heures c'est trop, on a des clients [inaudible]
sur cette plage. Il faut du bascule progressif.

[00:25] Marc : Le bascule progressif sur un changement de moteur, c'est très
risqué. Je ne le sens pas.

[00:26] Sophie : On n'est pas d'accord. On tranchera avec les chiffres de
charge.

[00:28] Marc : Le DSI voudra un plan de rollback écrit avant d'autoriser la
fenêtre, quelle qu'elle soit.

[00:29] Sophie : Oui, forcément. Bon, on s'arrête là.
```
