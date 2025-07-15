# Système de Transformation BattleScribe vers JSON Simplifié

Ce système permet de transformer les fichiers BattleScribe (.cat/.gst) en format JSON simplifié compatible avec les fichiers de validation.

## Fichiers du système

### Scripts principaux

1. **`convert_xml.py`** - Convertit les fichiers .cat/.gst en JSON brut
2. **`transform_battlescribe.py`** - Transforme les données BattleScribe vers le format simplifié
3. **`test_transformation.py`** - Valide la qualité de la transformation

### Utilisation

#### Étape 1 : Conversion XML vers JSON brut

```bash
python convert_xml.py
```

Ce script :
- Lit tous les fichiers `.cat` et `.gst` dans le dossier `./cat`
- Supprime les préfixes de namespace `{http://www.battlescribe.net/schema/...}`
- Sauvegarde les fichiers JSON dans `./SourceIntoJsonFormat`

#### Étape 2 : Transformation vers format simplifié

```bash
python transform_battlescribe.py --source "SourceIntoJsonFormat/Imperium - Dark Angels.json" --reference "validation/darkangels.json" --output "output_darkangels.json"
```

**Paramètres :**
- `--source` : Fichier source BattleScribe (JSON brut)
- `--reference` : Fichier de référence pour la structure cible
- `--output` : Fichier de sortie transformé

#### Étape 3 : Validation de la transformation

```bash
python test_transformation.py --transformed "output_darkangels.json" --reference "validation/darkangels.json"
```

**Paramètres :**
- `--transformed` : Fichier transformé à valider
- `--reference` : Fichier de référence pour la comparaison

## Structure des données

### Format d'entrée (BattleScribe)
```json
{
  "{http://www.battlescribe.net/schema/catalogueSchema}sharedSelectionEntries": {
    "{http://www.battlescribe.net/schema/catalogueSchema}selectionEntry": [
      {
        "type": "model",
        "name": "Azrael",
        "id": "81bd-ce4e-229f-a88",
        "{http://www.battlescribe.net/schema/catalogueSchema}costs": {
          "{http://www.battlescribe.net/schema/catalogueSchema}cost": {
            "name": "pts",
            "value": "115"
          }
        }
      }
    ]
  }
}
```

### Format de sortie (Simplifié)
```json
{
  "id": "CHDA",
  "name": "Dark Angels",
  "is_subfaction": true,
  "parent_id": "SM",
  "parent_keyword": "Adeptus Astartes",
  "colours": {
    "banner": "#16291a",
    "header": "#013a17"
  },
  "allied_factions": ["AoI", "QI"],
  "datasheets": [
    {
      "id": "uuid",
      "name": "Azrael",
      "cardType": "DataCard",
      "factions": ["Dark Angels"],
      "faction_id": "CHDA",
      "source": "40k-10e",
      "abilities": {
        "core": [],
        "faction": ["Oath of Moment"],
        "other": [
          {
            "name": "Supreme Grand Master",
            "description": "...",
            "showAbility": true,
            "showDescription": true
          }
        ]
      },
      "stats": [],
      "rangedWeapons": [],
      "meleeWeapons": [],
      "keywords": ["Character", "Epic Hero", "Infantry"],
      "points": [
        {
          "name": "model",
          "model": "1",
          "cost": "115"
        }
      ],
      "composition": ["1 Azrael"]
    }
  ],
  "enhancements": [],
  "rules": {
    "army": [
      {
        "name": "Oath of Moment",
        "rule": [
          {
            "order": 1,
            "text": "...",
            "type": "text"
          }
        ]
      }
    ]
  }
}
```

## Fonctionnalités du transformateur

### Extraction des données

1. **Informations de faction** : ID, nom, couleurs, factions alliées
2. **Datasheets** : Unités avec leurs caractéristiques complètes
3. **Capacités** : Core, faction, autres capacités spéciales
4. **Statistiques** : M, T, SV, W, LD, OC
5. **Armes** : Armes de mêlée et à distance avec profils
6. **Points** : Coûts en points de pouvoir
7. **Mots-clés** : Catégories et mots-clés d'unité
8. **Règles** : Règles d'armée et spéciales

### Gestion des préfixes de namespace

Le transformateur gère automatiquement les préfixes de namespace BattleScribe :
- `{http://www.battlescribe.net/schema/catalogueSchema}`
- `{http://www.battlescribe.net/schema/gameSystemSchema}`

### Validation

Le script de test vérifie :
- Compatibilité de structure
- Présence des données essentielles
- Qualité des données extraites
- Statistiques de transformation

## Exemples d'utilisation

### Transformation d'une faction complète

```bash
# Conversion de tous les fichiers source
python convert_xml.py

# Transformation des Dark Angels
python transform_battlescribe.py \
  --source "SourceIntoJsonFormat/Imperium - Dark Angels.json" \
  --reference "validation/darkangels.json" \
  --output "output_darkangels.json"

# Validation
python test_transformation.py \
  --transformed "output_darkangels.json" \
  --reference "validation/darkangels.json"
```

### Transformation d'autres factions

```bash
# Blood Angels
python transform_battlescribe.py \
  --source "SourceIntoJsonFormat/Imperium - Blood Angels.json" \
  --reference "validation/bloodangels.json" \
  --output "output_bloodangels.json"

# Space Marines
python transform_battlescribe.py \
  --source "SourceIntoJsonFormat/Imperium - Space Marines.json" \
  --reference "validation/space_marines.json" \
  --output "output_spacemarines.json"
```

## Limitations actuelles

1. **Enhancements** : Les enhancements ne sont pas encore extraits (0 vs 20 attendus)
2. **Unités de type "unit"** : Certaines unités de type "unit" ne sont pas traitées
3. **Statistiques** : Les statistiques des unités ne sont pas encore extraites
4. **Armes** : Les armes ne sont pas encore extraites

## Améliorations futures

1. Extraction complète des enhancements
2. Support des unités de type "unit"
3. Extraction des statistiques des unités
4. Extraction des armes et leurs profils
5. Support des modificateurs et contraintes
6. Extraction des règles spéciales

## Dépendances

- Python 3.6+
- Modules standard : `json`, `argparse`, `pathlib`, `uuid`, `typing`

## Support

Pour toute question ou problème, consultez les logs de transformation qui fournissent des informations détaillées sur le processus d'extraction. 