#!/usr/bin/env python3
"""
Script de test pour valider la transformation des données BattleScribe
Compare le fichier transformé avec le fichier de référence
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Any

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Charge un fichier JSON"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur lors du chargement de {file_path}: {e}")
        return {}

def compare_structures(transformed: Dict[str, Any], reference: Dict[str, Any], path: str = "") -> List[str]:
    """Compare les structures de deux dictionnaires et retourne les différences"""
    differences = []
    
    # Vérification des clés principales
    expected_keys = [
        "id", "name", "is_subfaction", "parent_id", "parent_keyword", 
        "link", "compatibleDataVersion", "colours", "allied_factions",
        "datasheets", "enhancements", "rules"
    ]
    
    for key in expected_keys:
        if key not in transformed:
            differences.append(f"Clé manquante: {path}.{key}")
        elif key not in reference:
            differences.append(f"Clé inattendue dans le fichier transformé: {path}.{key}")
    
    # Vérification des datasheets
    if "datasheets" in transformed and "datasheets" in reference:
        transformed_datasheets = transformed["datasheets"]
        reference_datasheets = reference["datasheets"]
        
        print(f"Datasheets transformées: {len(transformed_datasheets)}")
        print(f"Datasheets de référence: {len(reference_datasheets)}")
        
        # Vérification de la structure des datasheets
        if transformed_datasheets:
            first_transformed = transformed_datasheets[0]
            expected_datasheet_keys = [
                "id", "name", "cardType", "factions", "faction_id", "source",
                "abilities", "stats", "rangedWeapons", "meleeWeapons", 
                "keywords", "points", "composition", "fluff", "leader", 
                "loadout", "transport", "wargear"
            ]
            
            for key in expected_datasheet_keys:
                if key not in first_transformed:
                    differences.append(f"Clé manquante dans datasheet: {key}")
    
    # Vérification des enhancements
    if "enhancements" in transformed and "enhancements" in reference:
        transformed_enhancements = transformed["enhancements"]
        reference_enhancements = reference["enhancements"]
        
        print(f"Enhancements transformés: {len(transformed_enhancements)}")
        print(f"Enhancements de référence: {len(reference_enhancements)}")
    
    # Vérification des règles
    if "rules" in transformed and "rules" in reference:
        transformed_rules = transformed["rules"]
        reference_rules = reference["rules"]
        
        if "army" in transformed_rules and "army" in reference_rules:
            print(f"Règles d'armée transformées: {len(transformed_rules['army'])}")
            print(f"Règles d'armée de référence: {len(reference_rules['army'])}")
    
    return differences

def validate_data_quality(transformed: Dict[str, Any]) -> List[str]:
    """Valide la qualité des données transformées"""
    issues = []
    
    if "datasheets" in transformed:
        for i, datasheet in enumerate(transformed["datasheets"]):
            # Vérification des données essentielles
            if not datasheet.get("name"):
                issues.append(f"Datasheet {i}: nom manquant")
            
            if not datasheet.get("points"):
                issues.append(f"Datasheet {i} ({datasheet.get('name', 'Unknown')}): points manquants")
            
            if not datasheet.get("keywords"):
                issues.append(f"Datasheet {i} ({datasheet.get('name', 'Unknown')}): mots-clés manquants")
            
            # Vérification des capacités
            abilities = datasheet.get("abilities", {})
            if not abilities.get("faction"):
                issues.append(f"Datasheet {i} ({datasheet.get('name', 'Unknown')}): capacités de faction manquantes")
    
    return issues

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description='Teste la transformation des données BattleScribe')
    parser.add_argument('--transformed', type=str, required=True, help='Chemin vers le fichier transformé')
    parser.add_argument('--reference', type=str, required=True, help='Chemin vers le fichier de référence')
    
    args = parser.parse_args()
    
    # Vérification des fichiers
    if not Path(args.transformed).exists():
        print(f"✗ Le fichier transformé {args.transformed} n'existe pas")
        return
    
    if not Path(args.reference).exists():
        print(f"✗ Le fichier de référence {args.reference} n'existe pas")
        return
    
    # Chargement des fichiers
    print("Chargement des fichiers...")
    transformed_data = load_json_file(args.transformed)
    reference_data = load_json_file(args.reference)
    
    if not transformed_data:
        print("✗ Impossible de charger le fichier transformé")
        return
    
    if not reference_data:
        print("✗ Impossible de charger le fichier de référence")
        return
    
    print("✓ Fichiers chargés avec succès")
    
    # Comparaison des structures
    print("\n=== Comparaison des structures ===")
    differences = compare_structures(transformed_data, reference_data)
    
    if differences:
        print("✗ Différences de structure détectées:")
        for diff in differences:
            print(f"  - {diff}")
    else:
        print("✓ Structures compatibles")
    
    # Validation de la qualité des données
    print("\n=== Validation de la qualité des données ===")
    issues = validate_data_quality(transformed_data)
    
    if issues:
        print("✗ Problèmes de qualité détectés:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✓ Qualité des données satisfaisante")
    
    # Résumé
    print("\n=== Résumé ===")
    if not differences and not issues:
        print("✓ Transformation réussie! Le fichier transformé est compatible avec le format de référence.")
    else:
        print("⚠ Transformation partiellement réussie. Des améliorations sont nécessaires.")
    
    # Statistiques
    if "datasheets" in transformed_data:
        print(f"\nStatistiques:")
        print(f"- Datasheets extraites: {len(transformed_data['datasheets'])}")
        
        datasheets_with_points = sum(1 for d in transformed_data['datasheets'] if d.get('points'))
        print(f"- Datasheets avec points: {datasheets_with_points}")
        
        datasheets_with_keywords = sum(1 for d in transformed_data['datasheets'] if d.get('keywords'))
        print(f"- Datasheets avec mots-clés: {datasheets_with_keywords}")
        
        datasheets_with_abilities = sum(1 for d in transformed_data['datasheets'] if d.get('abilities', {}).get('other'))
        print(f"- Datasheets avec capacités: {datasheets_with_abilities}")

if __name__ == "__main__":
    main() 