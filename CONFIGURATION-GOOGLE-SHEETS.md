# Gérer la carte depuis Google Sheets

Le propriétaire modifie ses prix dans un tableur ; le site les reprend au
chargement suivant. Aucun serveur, aucun mot de passe dans le code : le compte
administrateur, c'est le compte Google du restaurant.

---

## Mise en place — une seule fois, 10 minutes

### 1. Créer la feuille

1. Ouvrir [sheets.new](https://sheets.new) avec le compte Google **du restaurant**
   (pas le vôtre : c'est lui le propriétaire des données).
2. `Fichier` → `Importer` → onglet `Importer` → déposer `menu-belle-vue.csv`.
3. Dans la fenêtre d'import : *Type de séparateur* = **Virgule**,
   *Convertir le texte en nombres* = **Non**. Ce second point est important,
   sinon Google transforme `34,00` en date ou en `3400`.
4. Renommer le fichier, par exemple « Carte Belle Vue ».

### 2. Publier la feuille en CSV

1. `Fichier` → `Partager` → `Publier sur le Web`.
2. Onglet `Lien`. À gauche choisir la **feuille** (pas « document entier »),
   à droite choisir **Valeurs séparées par des virgules (.csv)**.
3. Cliquer `Publier`, confirmer.
4. Copier l'adresse obtenue. Elle ressemble à :

```
https://docs.google.com/spreadsheets/d/e/2PACX-1vAbCdEf.../pub?gid=0&single=true&output=csv
```

### 3. Brancher le site

Ouvrir `index.html`, tout en haut du `<script>`, et coller l'adresse :

```js
const CONFIG = {
  ...
  feuille: "https://docs.google.com/spreadsheets/d/e/2PACX-.../pub?gid=0&single=true&output=csv"
};
```

Vide, le site utilise la carte inscrite dans le fichier. Renseignée, la feuille
prend le dessus. Republier `index.html` sur GitHub, et c'est fini.

---

## Usage quotidien

| Pour… | Faire… |
|---|---|
| changer un prix | modifier la colonne `prix` |
| signaler une rupture | mettre `non` dans `disponible` |
| remettre le plat | remettre `oui` |
| corriger un texte | modifier `plat` ou `description` |
| poser une pastille | écrire `Signature`, `Nouveau`… dans `etiquette` |
| changer une photo | voir la section ci-dessous |

Rien à enregistrer : Google enregistre tout seul. Le changement est visible sur
le site au rechargement suivant, en général sous une minute.

### Changer la photo d'un plat

La colonne `photo` accepte trois formes. La première demande un accès à GitHub,
les deux autres non — c'est celles-là qu'utilisera le restaurateur.

**Un nom de fichier** — `pizzas-3.jpg`. L'image doit avoir été déposée à côté de
`index.html` sur GitHub. Réservé à qui gère le dépôt.

**Un lien de partage Google Drive.** Le gérant dépose sa photo dans son Drive,
clic droit → `Partager` → `Toute personne disposant du lien`, puis
`Copier le lien`, et colle le lien tel quel dans la cellule. Le site le convertit
tout seul en lien d'image : collé brut, un lien Drive affiche une page web, pas
une image. **Le partage doit être « toute personne disposant du lien »**, sinon
le client verra un cadre vide.

**Une adresse d'image quelconque** — `https://…/photo.jpg`. Les liens Dropbox
sont également convertis.

Une cellule vide retire la photo : la plaque or reprend sa place. Une valeur qui
n'est ni un nom de fichier image ni une adresse `http` est ignorée.

Conseil : redimensionnez à environ 900 px de large avant d'envoyer. Une photo de
téléphone fait 4 Mo, et vingt photos de ce poids rendent le menu pénible à
charger sur le réseau du restaurant.

### La colonne `id` ne se touche pas

C'est la clé qui relie chaque ligne au bon plat. La modifier casse le lien.
Les lignes peuvent en revanche être **triées ou déplacées** librement : le site
lit les `id`, pas l'ordre des lignes.

### Ajouter un plat

Créer une ligne avec un `id` **inédit** commençant par la rubrique voulue, suivi
d'un tiret et d'un nombre libre :

- `pizzas-90` → apparaît dans les Pizzas
- `desserts-50` → apparaît dans les Desserts
- `crepes-sucrees-30` → apparaît dans les Crêpes sucrées

Prenez des nombres élevés (50, 90…) pour ne jamais heurter les identifiants
existants. Un `id` dont la rubrique n'existe pas est simplement ignoré.

### Supprimer un plat

Mettre `non` dans `disponible` plutôt que d'effacer la ligne : le plat disparaît
du site et revient d'un mot. Si une rubrique entière passe en `non`, elle
disparaît aussi du menu et du bandeau de navigation.

---

## Ce qui se passe si Google ne répond pas

La carte inscrite dans `index.html` reste la référence de secours. Le site
affiche **d'abord** cette carte, puis applique la feuille quand elle arrive.
Concrètement :

- coupure internet côté client → le menu s'affiche, aux anciens prix ;
- panne Google → idem ;
- feuille dépubliée par erreur → idem ;
- réponse trop lente → abandon au bout de 6 secondes, ancienne carte conservée.

Le menu ne peut donc jamais s'afficher vide. La contrepartie : un client hors
ligne peut voir un prix périmé. **Pensez donc à reporter les gros changements
de tarifs dans `index.html` une ou deux fois par an**, pour que la carte de
secours ne dérive pas trop de la vraie.

En bas de page, la mention « Carte à jour · 14:32 » n'apparaît que si la feuille
a bien été lue. Son absence est le signe que quelque chose cloche — c'est le
moyen le plus simple de vérifier que le montage fonctionne.

---

## Points de vigilance

**La feuille publiée est publique.** Elle est lisible par quiconque a l'adresse.
Ne mettez donc jamais de marges, de coûts d'achat ou de notes internes dans ce
document : créez un second onglet non publié pour ça, ou un fichier séparé.

**Ne publiez qu'un seul onglet.** Le `gid=0` de l'adresse désigne le premier.
Si vous ajoutez des onglets de travail, vérifiez que l'adresse pointe toujours
sur le bon.

**Format des prix.** `45`, `45,00`, `45.00` et `45 DT` sont tous compris.
Une cellule vide laisse le prix inchangé — pour afficher zéro, écrire `0`.

**Décalage de cache.** Google sert parfois une version vieille de quelques
minutes. Le site ajoute un horodatage à chaque requête pour l'éviter, mais si
une correction tarde, attendez deux minutes avant de conclure à un problème.
