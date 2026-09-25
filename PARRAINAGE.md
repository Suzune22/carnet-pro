# Parrainage L1

`parrainage.html` sert à former des binômes entre les nouveaux étudiants de L1 (filleul·es) et des étudiants plus avancés, de la L2 au doctorat (parrains et marraines).

- **Onglet Inscription** : le formulaire public. Chaque étudiant choisit son rôle et indique sa filière, ses centres d'intérêt et comment il préfère se rencontrer. Un parrain peut accepter jusqu'à 3 filleul·es.
- **Onglet Binômes** : l'espace des organisateurs, avec les statistiques, la formation automatique des binômes, l'association manuelle, le retrait d'un inscrit et l'export CSV.
- **Partager le formulaire** : affiche un QR code et le lien direct vers l'inscription (`parrainage.html#inscription`).

## Calcul des binômes

Pour chaque couple parrain / filleul, un score de compatibilité est calculé :

| Critère | Points |
|---|---|
| Même filière | +10 |
| Chaque centre d'intérêt en commun | +2 |
| Préférences de rencontre compatibles | +1 |
| Préférences de rencontre incompatibles (campus contre distance) | −3 |

Le bouton « Former les binômes automatiquement » attribue d'abord les couples qui ont le meilleur score, sans dépasser le nombre de filleul·es accepté par chaque parrain. Les binômes déjà formés ne sont pas modifiés. Les filleul·es qui restent sans binôme apparaissent dans une liste où on peut les associer à la main. Les parrains y sont triés par compatibilité.

## Mise en ligne (Google Sheets)

Si `API_URL` est vide dans `parrainage.html`, la page fonctionne en **mode démo** : les données restent dans le navigateur. Pour recevoir les inscriptions de tout le monde :

1. Créer une feuille Google Sheets, puis ouvrir **Extensions → Apps Script**.
2. Coller le contenu de `apps-script/parrainage.gs`.
3. Facultatif, mais conseillé : dans **Paramètres du projet → Propriétés du script**, ajouter `ADMIN_KEY` avec un code secret. Ce code sera demandé dans l'onglet Binômes. Sans lui, toute personne qui a l'URL peut voir la liste des inscrits.
4. **Déployer → Nouveau déploiement → Application Web**, avec « Exécuter en tant que : moi » et « Accès : tout le monde ».
5. Copier l'URL `…/exec` dans la constante `API_URL` en haut du script de `parrainage.html`.

Les onglets `Etudiants` et `Binomes` sont créés automatiquement dans la feuille à la première requête.
