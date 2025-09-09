import xml.etree.ElementTree as ET
import json

# Chemins des fichiers
xml_path = 'quran-simple.xml'
json_path = 'quran_ar.json'

# Parse XML
root = ET.parse(xml_path).getroot()

# Résultat
versets = []

for sourate in root.findall('sura'):
    num_sourate = int(sourate.get('index'))
    for aya in sourate.findall('aya'):
        num_aya = int(aya.get('index'))
        text = aya.get('text')
        versets.append({
            'sura': num_sourate,
            'aya': num_aya,
            'text': text
        })

# Structure finale
result = {
    'meta': {
        'source': 'quran-simple.xml',
        'language': 'ar',
        'sourah_count': 114
    },
    'quran': versets
}

# Sauvegarde JSON
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f'Conversion terminée ! {len(versets)} versets exportés.')
