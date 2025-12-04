# app.py
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Erlaubt dem Frontend, auf dieses Backend zuzugreifen (wichtig, wenn sie auf verschiedenen Domains sind)
CORS(app) 

# Maximale Anzahl von Bildern, die wir versuchen zu finden (z.B. bis 999)
MAX_COUNT = 1000 
# HTTP-Statuscode für Erfolg
SUCCESS_STATUS = 200 

@app.route('/find_images', methods=['POST'])
def find_images():
    """
    Sucht nach Bildern, indem der Zähler in der URL hochgezählt wird, 
    bis keine Bilder mehr gefunden werden.
    """
    try:
        # Erwartet den Link vom Frontend
        data = request.get_json()
        base_url = data.get('link')
        
        if not base_url or not isinstance(base_url, str):
            return jsonify({'error': 'Ungültiger Link bereitgestellt.'}), 400

        # Annahme: Das Format ist immer XXX.jpg am Ende
        if not base_url.endswith('.jpg') or len(base_url) < 7:
             return jsonify({'error': 'Der Link muss mit einer dreistelligen Nummer und .jpg enden (z.B. 008.jpg).'}), 400

        # Den nummerierten Teil (z.B. '008') und den Rest des Links isolieren
        # Beispiel: https://.../high/008.jpg -> Basis: https://.../high/, Dateiname: 008.jpg
        # Wir suchen den Index, an dem die 3 Ziffern beginnen
        idx_start_num = base_url.rfind('/', 0, base_url.rfind('/')) + 1 # Gehe zum Ordner davor und dann eins weiter
        
        # Sicherstellen, dass die letzten 7 Zeichen Zahl-Zahl-Zahl-Punkt-j-p-g sind
        if not base_url[-7:-4].isdigit():
             return jsonify({'error': 'Der Link muss mit einer dreistelligen Nummer und .jpg enden (z.B. 008.jpg).'}), 400

        # Die Basis-URL vor der Nummer extrahieren
        base_prefix = base_url[:-7]

        found_images = []
        
        # Durchlauf von 1 bis MAX_COUNT (z.B. 999)
        for i in range(1, MAX_COUNT):
            # Formatiert die Zahl auf drei Stellen (z.B. 1 -> '001', 12 -> '012')
            counter_str = f"{i:03d}" 
            
            # Die neue URL zusammensetzen
            test_url = f"{base_prefix}{counter_str}.jpg"
            
            # Kopfzeilen setzen, um einige Server-Blockaden zu umgehen
            headers = {'User-Agent': 'Mozilla/5.0'}
            
            try:
                # Prüfen, ob die Datei existiert (nur den Header abrufen, um Bandbreite zu sparen)
                response = requests.head(test_url, headers=headers, timeout=5)
                
                # Wenn der Statuscode 200 ist, wurde das Bild gefunden
                if response.status_code == SUCCESS_STATUS:
                    found_images.append({'url': test_url, 'filename': f"{counter_str}.jpg"})
                else:
                    # Sobald ein Bild fehlt, brechen wir die Suche ab (Annahme einer sequenziellen Benennung)
                    # Dies ist der entscheidende Schritt in Ihrer Anforderung
                    if len(found_images) > 0: # Beende nur, wenn wir schon Bilder gefunden haben
                        break
                    
            except requests.exceptions.RequestException as e:
                # Bei einem Verbindungsfehler oder Timeout versuchen wir nicht weiter
                # Da es sich um einen Fehler handelt, brechen wir ab, um Endlosschleifen zu vermeiden.
                print(f"Fehler bei URL {test_url}: {e}")
                if len(found_images) > 0:
                     break # Breche ab, wenn schon Bilder gefunden wurden
                
        # Rückgabe der gefundenen URLs an das Frontend
        return jsonify({'images': found_images}), 200

    except Exception as e:
        return jsonify({'error': f'Ein unerwarteter Fehler ist aufgetreten: {str(e)}'}), 500

if __name__ == '__main__':
    # Lokaler Test auf Port 5000
    app.run(debug=True, port=5000)
