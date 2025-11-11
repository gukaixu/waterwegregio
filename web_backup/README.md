# Waterwegregio Verhalen Kaart

Een interactieve webapplicatie voor het delen van verhalen, foto's en video's uit de Waterwegregio.

## Overzicht

Deze webapplicatie toont een interactieve kaart van de Waterwegregio waar "pins" kunnen worden geplaatst met content zoals verhalen, foto's en video's. Het project bevat een publieke viewer en een admin interface voor het beheren van content.

## Structuur

```
web/
├── index.html          # Hoofdpagina met kaart viewer
├── admin.html          # Admin interface voor beheer
├── css/
│   ├── main.css        # Algemene styling
│   └── admin.css       # Admin-specifieke styling
├── js/
│   ├── map.js          # Kaart initialisatie en pin weergave
│   ├── admin.js        # Admin functionaliteit
│   └── data.js         # Data management utilities
├── data/
│   └── pins.json       # Pin data opslag
└── README.md           # Deze file
```

## Installatie & Gebruik

### 1. Lokaal draaien

Open `index.html` in een webbrowser. Voor de beste ervaring, gebruik een lokale webserver:

**Met Python:**
```bash
cd web
python -m http.server 8000
# Bezoek http://localhost:8000
```

**Met Node.js (http-server):**
```bash
cd web
npx http-server -p 8000
# Bezoek http://localhost:8000
```

### 2. Admin toegang

- Ga naar `/admin.html`
- Wachtwoord: `waterweg2025`
- Hier kun je pins toevoegen, bewerken en verwijderen

### 3. Pins beheren

**Een nieuwe pin toevoegen:**
1. Klik op de kaart om een locatie te selecteren
2. Vul de formuliervelden in:
   - Titel (verplicht)
   - Locatie naam
   - Verhaal/beschrijving (verplicht)
   - Foto URLs (één per regel)
   - Video URLs (YouTube of Vimeo, één per regel)
3. Klik "Opslaan"

**Een pin bewerken:**
1. Klik op "Bewerken" bij een bestaand verhaal
2. Pas de velden aan
3. Klik "Opslaan"

**Een pin verwijderen:**
1. Klik op "Verwijderen" bij een verhaal
2. Bevestig de verwijdering

### 4. Data exporteren

Klik op "Exporteer Data" in de admin interface om de huidige pins als JSON file te downloaden. Upload deze file naar `data/pins.json` om de wijzigingen permanent te maken.

## Data opslag

De applicatie gebruikt twee opslag methodes:

1. **JSON file** (`data/pins.json`): Initiele data die wordt geladen bij het openen van de app
2. **LocalStorage**: Runtime wijzigingen worden hier opgeslagen (blijft bewaard per browser)

Voor permanente wijzigingen moet je de data exporteren en de `pins.json` file vervangen.

## Data structuur

Pins worden opgeslagen in het volgende formaat:

```json
{
  "pins": [
    {
      "id": "unique-id",
      "lat": 51.9225,
      "lng": 4.4792,
      "title": "Verhaal Titel",
      "location": "Wijk Naam",
      "description": "Uitgebreide beschrijving...",
      "images": ["url1.jpg", "url2.jpg"],
      "videos": ["youtube-url"],
      "created": "2025-10-28T10:00:00.000Z"
    }
  ]
}
```

## Features

### Publieke Viewer
- Interactieve kaart met OpenStreetMap
- Klikbare pins met verhalen
- Foto galerij (swipeable)
- Ingesloten video's (YouTube/Vimeo)
- Responsive design (mobiel-vriendelijk)

### Admin Interface
- Wachtwoord beschermd
- Click-to-select locatie op kaart
- Formulier voor pin management
- Overzicht van alle pins
- Edit/delete functionaliteit
- Data export naar JSON

## Video ondersteuning

De applicatie ondersteunt YouTube en Vimeo videos. Plak de volledige URL in het video veld:

**YouTube:**
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`

**Vimeo:**
- `https://vimeo.com/VIDEO_ID`

## Deployment

### GitHub Pages

1. Push de `web/` folder naar een GitHub repository
2. Ga naar Settings → Pages
3. Selecteer de branch en `/web` folder
4. De site is beschikbaar op `https://username.github.io/repo-name/`

### Netlify

1. Drag-and-drop de `web/` folder naar Netlify
2. Of connect een GitHub repository met automatische deploys

### Andere hosting

Upload alle files in de `web/` folder naar een statische hosting service. Geen server-side componenten nodig.

## Browser ondersteuning

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Technologie

- **Frontend**: Vanilla HTML, CSS, JavaScript (geen frameworks)
- **Map library**: Leaflet.js
- **Tile provider**: OpenStreetMap
- **Data format**: JSON

## Limitaties (Prototype)

- Admin wachtwoord is client-side (niet veilig voor productie)
- Data wijzigingen vereisen handmatige file upload voor persistentie
- Geen gebruikers management
- Geen image upload (alleen URLs)

## Boundary aanpassen

De boundary is momenteel een rechthoekig gebied. Voor nauwkeurige grenzen:

1. Zorg dat je Python packages geïnstalleerd hebt:
   ```bash
   pip install geopandas pandas openpyxl
   ```

2. Run het extract script:
   ```bash
   cd web
   python3 extract_boundary.py
   ```

Dit script extraheert de exacte grenzen van de 31 Waterwegregio wijken uit de GeoPackage.

## Toekomstige verbeteringen

Voor een productie versie zou je kunnen overwegen:

- Backend API voor data persistentie
- Database (PostgreSQL/MongoDB)
- Server-side authenticatie
- File upload voor afbeeldingen
- Gebruikers management
- Zoek functionaliteit
- Categorieën/tags voor pins
- Moderatie workflow

## Contact

Voor vragen of problemen, neem contact op met het projectteam.

---

*Gemaakt voor Waterwegregio | Erasmus Universiteit Rotterdam*

