#!/usr/bin/env python3
"""
Script de transformation des données BattleScribe vers le format JSON simplifié
Transforme les fichiers .cat/.gst en format compatible avec les fichiers de validation
"""

import json
import argparse
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional

class BattleScribeTransformer:
    """Classe pour transformer les données BattleScribe vers le format JSON simplifié"""
    
    def __init__(self, source_file: str, reference_file: str, output_file: str):
        self.source_file = source_file
        self.reference_file = reference_file
        self.output_file = output_file
        self.source_data = None
        self.reference_data = None
        self.game_system_data = None
        self.shared_rules = set()  # Ensemble des règles partagées
    
    def find_key_with_prefix(self, data: Dict[str, Any], key_name: str) -> Optional[str]:
        """Trouve une clé (maintenant sans préfixe de namespace)"""
        return key_name if key_name in data else None
        
    def load_json_file(self, file_path: str) -> Dict[str, Any]:
        """Charge un fichier JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement de {file_path}: {e}")
            return {}
    
    def load_shared_rules(self):
        """Charge les règles partagées depuis Warhammer 40,000.json"""
        game_system_file = "SourceIntoJsonFormat/Warhammer 40,000.json"
        try:
            game_system_data = self.load_json_file(game_system_file)
            if "sharedRules" in game_system_data:
                shared_rules = game_system_data["sharedRules"]
                if "rule" in shared_rules:
                    rules = shared_rules["rule"]
                    if isinstance(rules, list):
                        for rule in rules:
                            if "name" in rule:
                                self.shared_rules.add(rule["name"])
                    else:
                        if "name" in rules:
                            self.shared_rules.add(rules["name"])
            print(f"✓ Chargé {len(self.shared_rules)} règles partagées")
        except Exception as e:
            print(f"⚠ Erreur lors du chargement des règles partagées: {e}")
            # Règles partagées par défaut si le fichier n'est pas trouvé
            self.shared_rules = {
                "Leader", "Pistol", "Hazardous", "Devastating Wounds", "Assault", 
                "Extra Attacks", "Twin-linked", "Anti-", "Sustained Hits", "Heavy", 
                "Melta", "Feel No Pain", "Blast", "Precision", "Indirect Fire", 
                "Lance", "Lethal Hits", "Ignores Cover", "Rapid Fire", "Torrent", 
                "Scouts", "Infiltrators", "Deep Strike", "Deadly Demise", "Stealth", 
                "Super-Heavy Walker", "Lone Operative", "Hover", "Fights First", 
                "Psychic", "Firing Deck", "One Shot"
            }
    
    def save_json_file(self, data: Dict[str, Any], file_path: str):
        """Sauvegarde un fichier JSON"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✓ Fichier sauvegardé: {file_path}")
        except Exception as e:
            print(f"✗ Erreur lors de la sauvegarde de {file_path}: {e}")
    
    def extract_faction_info(self) -> Dict[str, Any]:
        """Extrait les informations de faction depuis le fichier source"""
        faction_info = {
            "id": "CHDA",  # Dark Angels
            "name": "Dark Angels",
            "is_subfaction": True,
            "parent_id": "SM",
            "parent_keyword": "Adeptus Astartes",
            "link": "https://game-datacards.eu",
            "compatibleDataVersion": 640
        }
        
        # Extraction des couleurs depuis le fichier de référence
        if self.reference_data and "colours" in self.reference_data:
            faction_info["colours"] = self.reference_data["colours"]
        
        # Extraction des factions alliées depuis le fichier de référence
        if self.reference_data and "allied_factions" in self.reference_data:
            faction_info["allied_factions"] = self.reference_data["allied_factions"]
        
        return faction_info
    
    def extract_abilities(self, selection_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Extrait les capacités d'une unité"""
        abilities = {
            "core": [],
            "faction": ["Oath of Moment"],
            "other": [],
            "special": [],
            "wargear": [],
            "primarch": [],
            "damaged": {
                "description": "",
                "range": "",
                "showDamagedAbility": False,
                "showDescription": True
            },
            "invul": {
                "info": "",
                "showAtTop": True,
                "showInfo": False,
                "showInvulnerableSave": True,
                "value": "5+"
            }
        }
        
        # Traitement des infoLinks (règles partagées)
        info_links_key = self.find_key_with_prefix(selection_entry, "infoLinks")
        if info_links_key:
            info_links = selection_entry[info_links_key]
            info_link_key = self.find_key_with_prefix(info_links, "infoLink")
            
            if info_link_key:
                info_link_list = info_links[info_link_key] if isinstance(info_links[info_link_key], list) else [info_links[info_link_key]]
                
                for info_link in info_link_list:
                    rule_name = info_link.get("name", "")
                    
                    # Traitement des modificateurs pour les règles comme "Deadly Demise D3"
                    if "modifiers" in info_link:
                        modifiers = info_link["modifiers"]
                        modifier_key = self.find_key_with_prefix(modifiers, "modifier")
                        
                        if modifier_key:
                            modifier_list = modifiers[modifier_key] if isinstance(modifiers[modifier_key], list) else [modifiers[modifier_key]]
                            
                            for modifier in modifier_list:
                                if modifier.get("type") == "append" and modifier.get("field") == "name":
                                    rule_name += modifier.get("value", "")
                    
                    # Ajouter la règle aux capacités core si elle est dans les règles partagées
                    if rule_name in self.shared_rules:
                        abilities["core"].append(rule_name)
                    else:
                        # Pour les règles non partagées, les ajouter aux capacités other
                        abilities["other"].append({
                            "name": rule_name,
                            "description": "",  # Pas de description disponible dans infoLinks
                            "showAbility": True,
                            "showDescription": False
                        })
        
        # Recherche des profils avec les préfixes de namespace
        profiles_key = self.find_key_with_prefix(selection_entry, "profiles")
        
        if profiles_key:
            profiles = selection_entry[profiles_key]
            
            # Recherche de profile dans les clés
            profile_key = self.find_key_with_prefix(profiles, "profile")
            
            if profile_key:
                profile_list = profiles[profile_key] if isinstance(profiles[profile_key], list) else [profiles[profile_key]]
                
                for profile in profile_list:
                    if profile.get("typeId") == "9cc3-6d83-4dd3-9b64":  # Abilities profile type
                        # Recherche des caractéristiques
                        characteristics_key = self.find_key_with_prefix(profile, "characteristics")
                        
                        if characteristics_key:
                            characteristics = profile[characteristics_key]
                            
                            # Recherche de characteristic dans les clés
                            characteristic_key = self.find_key_with_prefix(characteristics, "characteristic")
                            
                            if characteristic_key:
                                char = characteristics[characteristic_key]
                                if isinstance(char, list):
                                    for c in char:
                                        if c.get("name") == "Description":
                                            ability_name = profile.get("name", "")
                                            ability_description = c.get("_text", "")
                                            
                                            # Déterminer où placer la capacité
                                            if ability_name in self.shared_rules:
                                                abilities["core"].append(ability_name)
                                            else:
                                                abilities["other"].append({
                                                    "name": ability_name,
                                                    "description": ability_description,
                                                    "showAbility": True,
                                                    "showDescription": True
                                                })
                                else:
                                    if char.get("name") == "Description":
                                        ability_name = profile.get("name", "")
                                        ability_description = char.get("_text", "")
                                        
                                        # Déterminer où placer la capacité
                                        if ability_name in self.shared_rules:
                                            abilities["core"].append(ability_name)
                                        else:
                                            abilities["other"].append({
                                                "name": ability_name,
                                                "description": ability_description,
                                                "showAbility": True,
                                                "showDescription": True
                                            })
        
        return abilities
    
    def extract_stats(self, selection_entry: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrait les statistiques d'une unité"""
        stats = []
        
        # Recherche des profils avec les préfixes de namespace
        profiles_key = self.find_key_with_prefix(selection_entry, "profiles")
        
        if profiles_key:
            profiles = selection_entry[profiles_key]
            
            # Recherche de profile dans les clés
            profile_key = self.find_key_with_prefix(profiles, "profile")
            
            if profile_key:
                profile_list = profiles[profile_key] if isinstance(profiles[profile_key], list) else [profiles[profile_key]]
                
                for profile in profile_list:
                    if profile.get("typeId") == "c547-1836-d8a-ff4f":  # Unit profile type
                        stat = {
                            "active": True,
                            "name": profile.get("name", ""),
                            "showName": False,
                            "showDamagedMarker": False
                        }
                        
                        # Recherche des caractéristiques
                        characteristics_key = self.find_key_with_prefix(profile, "characteristics")
                        
                        if characteristics_key:
                            characteristics = profile[characteristics_key]
                            
                            # Recherche de characteristic dans les clés
                            characteristic_key = self.find_key_with_prefix(characteristics, "characteristic")
                            
                            if characteristic_key:
                                chars = characteristics[characteristic_key]
                                if isinstance(chars, list):
                                    for char in chars:
                                        if char.get("name") == "M":
                                            stat["m"] = char.get("_text", "")
                                        elif char.get("name") == "T":
                                            stat["t"] = char.get("_text", "")
                                        elif char.get("name") == "SV":
                                            stat["sv"] = char.get("_text", "")
                                        elif char.get("name") == "W":
                                            stat["w"] = char.get("_text", "")
                                        elif char.get("name") == "LD":
                                            stat["ld"] = char.get("_text", "")
                                        elif char.get("name") == "OC":
                                            stat["oc"] = char.get("_text", "")
                                else:
                                    if chars.get("name") == "M":
                                        stat["m"] = chars.get("_text", "")
                                    elif chars.get("name") == "T":
                                        stat["t"] = chars.get("_text", "")
                                    elif chars.get("name") == "SV":
                                        stat["sv"] = chars.get("_text", "")
                                    elif chars.get("name") == "W":
                                        stat["w"] = chars.get("_text", "")
                                    elif chars.get("name") == "LD":
                                        stat["ld"] = chars.get("_text", "")
                                    elif chars.get("name") == "OC":
                                        stat["oc"] = chars.get("_text", "")
                        
                        if stat["name"]:  # Seulement ajouter si on a un nom
                            stats.append(stat)
        
        return stats
    
    def extract_weapons(self, selection_entry: Dict[str, Any], weapon_type: str) -> List[Dict[str, Any]]:
        """Extrait les armes d'une unité"""
        weapons = []
        
        # Recherche des selectionEntries imbriqués
        selection_entries_key = self.find_key_with_prefix(selection_entry, "selectionEntries")
        
        if selection_entries_key:
            selection_entries = selection_entry[selection_entries_key]
            
            # Recherche de selectionEntry dans les clés
            selection_entry_key = self.find_key_with_prefix(selection_entries, "selectionEntry")
            
            if selection_entry_key:
                entries_list = selection_entries[selection_entry_key] if isinstance(selection_entries[selection_entry_key], list) else [selection_entries[selection_entry_key]]
                
                # Grouper les profils par arme
                weapon_groups = {}
                
                for entry in entries_list:
                    # Recherche des profils dans chaque selectionEntry
                    profiles_key = self.find_key_with_prefix(entry, "profiles")
                    
                    if profiles_key:
                        profiles = entry[profiles_key]
                        
                        # Recherche de profile dans les clés
                        profile_key = self.find_key_with_prefix(profiles, "profile")
                        
                        if profile_key:
                            profile_list = profiles[profile_key] if isinstance(profiles[profile_key], list) else [profiles[profile_key]]
                            
                            for profile in profile_list:
                                profile_type_id = profile.get("typeId")
                                if (weapon_type == "ranged" and profile_type_id == "f77d-b953-8fa4-b762") or \
                                   (weapon_type == "melee" and profile_type_id == "8a40-4aaa-c780-9046"):
                                    
                                    weapon_name = profile.get("name", "")
                                    if weapon_name not in weapon_groups:
                                        weapon_groups[weapon_name] = {
                                            "active": True,
                                            "profiles": []
                                        }
                                    
                                    weapon_profile = {
                                        "active": True,
                                        "name": weapon_name
                                    }
                                    
                                    # Recherche des caractéristiques
                                    characteristics_key = self.find_key_with_prefix(profile, "characteristics")
                                    
                                    if characteristics_key:
                                        characteristics = profile[characteristics_key]
                                        
                                        # Recherche de characteristic dans les clés
                                        characteristic_key = self.find_key_with_prefix(characteristics, "characteristic")
                                        
                                        if characteristic_key:
                                            chars = characteristics[characteristic_key]
                                            if isinstance(chars, list):
                                                for char in chars:
                                                    if char.get("name") == "Range":
                                                        weapon_profile["range"] = char.get("_text", "")
                                                    elif char.get("name") == "A":
                                                        weapon_profile["attacks"] = char.get("_text", "")
                                                    elif char.get("name") == "BS":
                                                        weapon_profile["skill"] = char.get("_text", "")
                                                    elif char.get("name") == "S":
                                                        weapon_profile["strength"] = char.get("_text", "")
                                                    elif char.get("name") == "AP":
                                                        weapon_profile["ap"] = char.get("_text", "")
                                                    elif char.get("name") == "D":
                                                        weapon_profile["damage"] = char.get("_text", "")
                                                    elif char.get("name") == "Keywords":
                                                        keywords_text = char.get("_text", "")
                                                        if keywords_text:
                                                            weapon_profile["keywords"] = [k.strip() for k in keywords_text.split(",")]
                                            else:
                                                if chars.get("name") == "Range":
                                                    weapon_profile["range"] = chars.get("_text", "")
                                                elif chars.get("name") == "A":
                                                    weapon_profile["attacks"] = chars.get("_text", "")
                                                elif chars.get("name") == "BS":
                                                    weapon_profile["skill"] = chars.get("_text", "")
                                                elif chars.get("name") == "S":
                                                    weapon_profile["strength"] = chars.get("_text", "")
                                                elif chars.get("name") == "AP":
                                                    weapon_profile["ap"] = chars.get("_text", "")
                                                elif chars.get("name") == "D":
                                                    weapon_profile["damage"] = chars.get("_text", "")
                                                elif chars.get("name") == "Keywords":
                                                    keywords_text = chars.get("_text", "")
                                                    if keywords_text:
                                                        weapon_profile["keywords"] = [k.strip() for k in keywords_text.split(",")]
                                    
                                    weapon_groups[weapon_name]["profiles"].append(weapon_profile)
                
                weapons = list(weapon_groups.values())
        
        return weapons
    
    def extract_keywords(self, selection_entry: Dict[str, Any]) -> List[str]:
        """Extrait les mots-clés d'une unité"""
        keywords = []
        
        # Recherche des liens de catégorie avec les préfixes de namespace
        category_links_key = self.find_key_with_prefix(selection_entry, "categoryLinks")
        
        if category_links_key:
            category_links = selection_entry[category_links_key]
            
            # Recherche de categoryLink dans les clés
            category_link_key = self.find_key_with_prefix(category_links, "categoryLink")
            
            if category_link_key:
                links = category_links[category_link_key]
                if isinstance(links, list):
                    for link in links:
                        if "name" in link:
                            keywords.append(link["name"])
                else:
                    if "name" in links:
                        keywords.append(links["name"])
        
        return keywords
    
    def extract_points(self, selection_entry: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrait les points d'une unité"""
        points = []
        
        # Recherche des coûts avec les préfixes de namespace
        costs_key = self.find_key_with_prefix(selection_entry, "costs")
        
        if costs_key:
            costs = selection_entry[costs_key]
            
            # Recherche de cost dans les clés
            cost_key = self.find_key_with_prefix(costs, "cost")
            
            if cost_key:
                cost_list = costs[cost_key] if isinstance(costs[cost_key], list) else [costs[cost_key]]
                
                for cost in cost_list:
                    if cost.get("name") == "pts":
                        points.append({
                            "name": "model",
                            "model": "1",
                            "cost": cost.get("value", "0")
                        })
        
        return points
    
    def extract_datasheet(self, selection_entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extrait une fiche de données complète"""
        if selection_entry.get("type") != "model":
            return None
        
        datasheet = {
            "id": str(uuid.uuid4()),
            "name": selection_entry.get("name", ""),
            "cardType": "DataCard",
            "factions": ["Dark Angels"],
            "faction_id": "CHDA",
            "source": "40k-10e",
            "abilities": self.extract_abilities(selection_entry),
            "stats": self.extract_stats(selection_entry),
            "rangedWeapons": self.extract_weapons(selection_entry, "ranged"),
            "meleeWeapons": self.extract_weapons(selection_entry, "melee"),
            "keywords": self.extract_keywords(selection_entry),
            "points": self.extract_points(selection_entry),
            "composition": [f"1 {selection_entry.get('name', '')}"],
            "fluff": "",
            "leader": "",
            "loadout": "",
            "transport": "",
            "wargear": []
        }
        
        return datasheet
    
    def extract_enhancements(self, selection_entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extrait un enhancement"""
        if selection_entry.get("type") != "upgrade":
            return None
        
        enhancement = {
            "name": selection_entry.get("name", ""),
            "id": str(uuid.uuid4()),
            "cost": "0",
            "keywords": ["Dark Angels"],
            "excludes": [],
            "description": "",
            "faction_id": "CHDA",
            "source": "40k-10e",
            "cardType": "enhancement",
            "detachment": "Wrath of the Rock"
        }
        
        # Extraction de la description depuis les profils
        if "profiles" in selection_entry:
            profiles = selection_entry["profiles"]
            if isinstance(profiles, dict) and "profile" in profiles:
                profile_list = profiles["profile"] if isinstance(profiles["profile"], list) else [profiles["profile"]]
                
                for profile in profile_list:
                    if profile.get("typeId") == "9cc3-6d83-4dd3-9b64":  # Abilities profile type
                        if "characteristics" in profile and "characteristic" in profile["characteristics"]:
                            char = profile["characteristics"]["characteristic"]
                            if isinstance(char, list):
                                for c in char:
                                    if c.get("name") == "Description":
                                        enhancement["description"] = c.get("_text", "")
                            else:
                                if char.get("name") == "Description":
                                    enhancement["description"] = char.get("_text", "")
        
        return enhancement
    
    def extract_rules(self) -> Dict[str, Any]:
        """Extrait les règles de l'armée"""
        rules = {
            "army": [
                {
                    "name": "Oath of Moment",
                    "rule": [
                        {
                            "order": 1,
                            "text": "This ability is described in full in the Army Rules section of *Codex: Space Marines*.",
                            "type": "text"
                        }
                    ]
                },
                {
                    "name": "The Deathwing",
                    "rule": [
                        {
                            "order": 1,
                            "text": "The following **ADEPTUS ASTARTES** units gain the **DEATHWING** keyword if they are drawn from the Dark Angels Chapter:\n\n■ **TERMINATOR** units\n■ **BLADEGUARD ANCIENT**, **BLADEGUARD VETERAN SQUAD**, **STERNGUARD VETERAN SQUAD** and **VANGUARD VETERAN SQUAD WITH JUMP PACKS** units\n■ **LAND RAIDER**, **LAND RAIDER CRUSADER**, **LAND RAIDER REDEEMER**, **REPULSOR** and **REPULSOR EXECUTIONER** units\n■ **DREADNOUGHT** units",
                            "type": "text"
                        }
                    ]
                },
                {
                    "name": "The Ravenwing",
                    "rule": [
                        {
                            "order": 1,
                            "text": "The following **ADEPTUS ASTARTES** units gain the **RAVENWING** keyword if they are drawn from the Dark Angels Chapter:\n\n■ **MOUNTED** units\n■ **VEHICLE** units that can **FLY**",
                            "type": "text"
                        }
                    ]
                },
                {
                    "name": "The Unforgiven",
                    "rule": [
                        {
                            "order": 1,
                            "text": "■ If an **ADEPTUS ASTARTES** unit has a second Faction keyword on its datasheet, that Faction keyword is the name of that unit's Chapter. For example, Asmodai has both the **ADEPTUS ASTARTES** and **DARK ANGELS** Faction keywords, and is therefore from the Dark Angels Chapter.\n■ You cannot include units from more than one Chapter in your army.\n\n**Designer's Note**: The rules presented in this section assume that the **ADEPTUS ASTARTES** units in your army are from the Dark Angels Chapter, but they can also be used to represent any Dark Angels successor Chapter, such as one described in the background section of this book, or even one of your own invention. However, players who wish to faithfully recreate the Dark Angels Chapter on the tabletop should only include **DARK ANGELS EPIC HEROES** if their collection is intended to represent the First Founding Chapter itself; Ezekiel is the Chief Librarian of the Dark Angels, for example, and not of any of their successors.",
                            "type": "text"
                        }
                    ]
                }
            ]
        }
        
        return rules
    
    def transform_data(self) -> Dict[str, Any]:
        """Transforme les données source vers le format cible"""
        print("Début de la transformation...")
        
        # Chargement des fichiers
        self.source_data = self.load_json_file(self.source_file)
        self.reference_data = self.load_json_file(self.reference_file)
        
        if not self.source_data:
            print("✗ Impossible de charger le fichier source")
            return {}
        
        # Extraction des informations de base
        faction_info = self.extract_faction_info()
        
        # Extraction des datasheets
        datasheets = []
        enhancements = []
        
        # Recherche des sharedSelectionEntries avec les préfixes de namespace
        shared_entries_key = self.find_key_with_prefix(self.source_data, "sharedSelectionEntries")
        
        if shared_entries_key:
            shared_entries = self.source_data[shared_entries_key]
            print(f"Trouvé sharedSelectionEntries: {shared_entries_key}")
            
            # Recherche de selectionEntry dans les clés
            selection_entry_key = self.find_key_with_prefix(shared_entries, "selectionEntry")
            
            if selection_entry_key:
                entries = shared_entries[selection_entry_key]
                print(f"Trouvé {len(entries) if isinstance(entries, list) else 1} entrées")
                
                if isinstance(entries, list):
                    for entry in entries:
                        print(f"Traitement de: {entry.get('name', 'Unknown')} (type: {entry.get('type', 'Unknown')})")
                        
                        # Extraction des datasheets
                        datasheet = self.extract_datasheet(entry)
                        if datasheet:
                            datasheets.append(datasheet)
                            print(f"  ✓ Datasheet extraite: {datasheet['name']}")
                        
                        # Extraction des enhancements
                        enhancement = self.extract_enhancements(entry)
                        if enhancement:
                            enhancements.append(enhancement)
                            print(f"  ✓ Enhancement extrait: {enhancement['name']}")
                else:
                    print(f"Traitement de: {entries.get('name', 'Unknown')} (type: {entries.get('type', 'Unknown')})")
                    
                    # Extraction des datasheets
                    datasheet = self.extract_datasheet(entries)
                    if datasheet:
                        datasheets.append(datasheet)
                        print(f"  ✓ Datasheet extraite: {datasheet['name']}")
                    
                    # Extraction des enhancements
                    enhancement = self.extract_enhancements(entries)
                    if enhancement:
                        enhancements.append(enhancement)
                        print(f"  ✓ Enhancement extrait: {enhancement['name']}")
        else:
            print("Aucun sharedSelectionEntries trouvé")
        
        # Extraction des règles
        rules = self.extract_rules()
        
        # Construction du résultat final
        result = {
            **faction_info,
            "datasheets": datasheets,
            "enhancements": enhancements,
            "rules": rules
        }
        
        print(f"✓ Transformation terminée: {len(datasheets)} datasheets, {len(enhancements)} enhancements")
        return result
    
    def run(self):
        """Exécute la transformation complète"""
        print(f"Transformation de {self.source_file} vers {self.output_file}")
        print(f"Fichier de référence: {self.reference_file}")
        
        # Charger les règles partagées
        self.load_shared_rules()
        
        transformed_data = self.transform_data()
        
        if transformed_data:
            self.save_json_file(transformed_data, self.output_file)
            print("✓ Transformation réussie!")
        else:
            print("✗ Échec de la transformation")

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description='Transforme les données BattleScribe vers le format JSON simplifié')
    parser.add_argument('--source', type=str, required=True, help='Chemin vers le fichier source JSON')
    parser.add_argument('--reference', type=str, required=True, help='Chemin vers le fichier de référence JSON')
    parser.add_argument('--output', type=str, required=True, help='Chemin vers le fichier de sortie JSON')
    
    args = parser.parse_args()
    
    # Vérification des fichiers
    if not Path(args.source).exists():
        print(f"✗ Le fichier source {args.source} n'existe pas")
        return
    
    if not Path(args.reference).exists():
        print(f"✗ Le fichier de référence {args.reference} n'existe pas")
        return
    
    # Création du répertoire de sortie si nécessaire
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Exécution de la transformation
    transformer = BattleScribeTransformer(args.source, args.reference, args.output)
    transformer.run()

if __name__ == "__main__":
    main() 