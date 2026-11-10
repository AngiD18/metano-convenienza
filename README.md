# Dove conviene fare metano?

Web app statica per iPhone, pubblicabile su GitHub Pages, dedicata al confronto di tre distributori di metano in provincia di Padova.

- ValliCarburanti – Arzerello, via Borgo Botteghe 45
- Tamoil – Candiana, via del Mare 6
- Enilive – Padova, corso Stati Uniti 27

## Funzionalità

- Calcolo del costo di un rifornimento e del metano consumato nei chilometri aggiuntivi.
- Modifica manuale di prezzi e deviazioni (prezzi manuali **non** sovrascritti automaticamente).
- Calcolo del percorso con Nominatim e OSRM, e mappa OpenStreetMap.
- Prezzi MIMIT letti dal file locale `data/prices.json`, pubblicato sullo stesso sito: niente proxy nel browser.
- Informazioni del tragitto salvate in `localStorage` **solo sul dispositivo**; nessun indirizzo privato nel repository.
- Interfaccia compatibile con Safari e con l'installazione nella schermata Home.

## Pubblicazione

1. Repository pubblico `AngiD18/metano-convenienza` (codice dell'app, nessun dato personale).
2. In **Settings → Pages → Build and deployment → Source**, scegli **GitHub Actions**.
3. Il workflow `.github/workflows/pages.yml` pubblica il sito al push su `main` e tenta di aggiornare i prezzi due volte al giorno.
4. Apri l'URL mostrato nella sezione Pages, poi Safari → Condividi → Aggiungi alla schermata Home.

Gli aggiornamenti automatici richiedono che le GitHub Actions siano abilitate sul repository e che il workflow abbia permesso di scrittura sui contenuti. Se MIMIT non è disponibile, il sito continua a mostrare gli ultimi dati pubblicati e i prezzi inseriti dall'utente.

La procedura identifica i distributori verificando sia indirizzo e comune sia, quando possibile, l'identificativo ministeriale. Non applica prezzi di altri impianti se il controllo non riesce.

## Origini dei dati e limiti

Prezzi ufficiali MIMIT: https://www.mimit.gov.it/it/open-data/elenco-dataset/carburanti-prezzi-praticati-e-anagrafica-degli-impianti

Percorsi: servizi pubblici OpenStreetMap / Nominatim / OSRM. Le distanze sono stime; gli orari per l'erogazione del metano possono differire dagli orari generali del distributore. Il calcolo monetizza solo il metano aggiuntivo, non tempo di viaggio, usura né pedaggi.

**Privacy:** il repository GitHub Pages è pubblico e non include indirizzi personali, posizione o tragitti predefiniti. Partenza e destinazione vengono inserite dall’utente e salvate esclusivamente nel `localStorage` del browser utilizzato, non su GitHub. Gli indirizzi vengono inviati a Nominatim/OSRM soltanto dopo aver premuto «Calcola deviazioni stradali»; le richieste possono essere registrate da quei servizi. È presente il comando «Cancella i miei dati» per eliminare le preferenze locali. La pagina pubblica resta accessibile a chiunque conosca il link; non è prevista autenticazione.