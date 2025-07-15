import os
import json
import xml.etree.ElementTree as ET
from pathlib import Path

def clean_tag_name(tag):
    """Nettoie le nom de tag en supprimant les préfixes de namespace"""
    # Supprime le préfixe {http://www.battlescribe.net/schema/gameSystemSchema}
    if tag.startswith('{http://www.battlescribe.net/schema/gameSystemSchema}'):
        return tag.replace('{http://www.battlescribe.net/schema/gameSystemSchema}', '')
    # Supprime le préfixe {http://www.battlescribe.net/schema/catalogueSchema}
    if tag.startswith('{http://www.battlescribe.net/schema/catalogueSchema}'):
        return tag.replace('{http://www.battlescribe.net/schema/catalogueSchema}', '')
    return tag

def parse_xml_to_dict(element):
    """Convertit un élément XML en dictionnaire Python"""
    result = {}
    
    # Ajoute les attributs
    if element.attrib:
        result.update(element.attrib)
    
    # Traite les enfants
    for child in element:
        # Nettoie le nom du tag
        clean_tag = clean_tag_name(child.tag)
        child_data = parse_xml_to_dict(child)
        
        if clean_tag in result:
            # Si l'élément existe déjà, le convertir en liste
            if not isinstance(result[clean_tag], list):
                result[clean_tag] = [result[clean_tag]]
            result[clean_tag].append(child_data)
        else:
            result[clean_tag] = child_data
    
    # Ajoute le texte si présent
    if element.text and element.text.strip():
        if result:  # S'il y a des attributs ou enfants, ajouter le texte comme valeur spéciale
            result['_text'] = element.text.strip()
        else:  # Sinon, utiliser directement le texte
            result = element.text.strip()
    
    return result

def read_cat_file(file_path):
    """Lit et parse un fichier .cat"""
    if not file_path:
        return
    
    try:
        # Lire le fichier avec encodage UTF-8
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Supprimer le BOM UTF-8 si présent
        content = content.replace('\ufeff', '')
        
        # Parser le XML
        root = ET.fromstring(content)
        result = parse_xml_to_dict(root)
        
        return result
        
    except Exception as e:
        print(f"Erreur lors du traitement de {file_path}: {e}")
        return None

def main():
    """Fonction principale"""
    cat_dir = Path("./cat")
    output_dir = Path("./SourceIntoJsonFormat")
    
    # Vérifier que le répertoire source existe
    if not cat_dir.exists():
        print("Le répertoire 'cat' n'existe pas")
        return
    
    # Créer le répertoire de destination s'il n'existe pas
    output_dir.mkdir(exist_ok=True)
    print(f"Fichiers JSON seront créés dans : {output_dir}")
    
    # Parcourir tous les fichiers .cat et .gst
    for extension in ["*.cat", "*.gst"]:
        for file_path in cat_dir.glob(extension):
            print(f"Traitement de {file_path.name}...")
            
            # Lire et parser le fichier
            result = read_cat_file(file_path)
            
            if result is not None:
                # Créer le nom du fichier JSON de sortie
                json_filename = file_path.stem + '.json'
                json_path = output_dir / json_filename
                
                # Écrire le résultat en JSON
                try:
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2, ensure_ascii=False)
                    print(f"  ✓ Converti en {json_filename}")
                except Exception as e:
                    print(f"  ✗ Erreur lors de l'écriture de {json_filename}: {e}")
            else:
                print(f"  ✗ Échec du traitement de {file_path.name}")

if __name__ == "__main__":
    main() 