#  API Génératrice d'attestation covid via coordinées géographiques (🗝️ Clef_des_champs 🌾)

Génère un certificat daté de 30 minutes, avc une adresse située à envoron 300m du point demandé.

_C'est la clef des champs. 🎃_

---

- Le fichier pdf est en fait une image en pdf, car éditer un PDF c'est une torture, et puis la différence est nulle et puis PIL c'est génial

**À noter:** La "database csv" est dans la branche db. Elle est générée par mes soins à partir des données d'openStreetMap sur la base d'un quadrillage à 300m via un KD-Tree. J'ai quadrillé l'IDF uniquement. Pour la France enti1ere cela représente 9M de points à chercher sur la database qui en contient 20M - la db est assez light à la campagne - et demande de mettre une feuille par branche pour optimiser les query, ce qui implique un grand arbre - **18GB de RAM !** - et de longs temps de calculs - 5400s - donc c'est pas possible sur raspberry (je sais pas si des algo out-of-core existent).

---

## build & run

J'ai mis ca sur un docker pour des raspberry 64 bits. Pour le port j'ai hardcodé le 28411 parsque pourquoi pas.

- **build:** `docker build -t clefdeschamps .`

- **run:** `sudo docker run -it -p 28411:28411 clefdeschamps`

---

### ⚠️ Defaults ⚠️
- Il n'y a aucune authentification, d'une part parsque ca marche tr bien comme ca, c'est Flask, juste Flask, pas de ngnik par dessus. À améliorer (je le ferai pas moi-même). 
- A chaque event "update", je met à jour les infos de l'attestation, mais n'importe qui peut télécharder la dernière attestation mise à jour. Faites un système de sessions ou je sais pas quoi avec des cookies ca serait super bien ca doit pas être super compliqué non plus, et ca éviterai cela.

---

# VOILA BISOUS 😘😘😘😘😘
