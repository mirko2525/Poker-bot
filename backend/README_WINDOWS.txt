===================================================
GUIDA RAPIDA AVVIO POKER BOT (WINDOWS)
===================================================

1. INSTALLAZIONE / RIPARAZIONE
   Se e la prima volta o se hai errori (es. "python-multipart missing"),
   fai doppio click su:
   
   >> fix_dependencies.bat

   Questo script scarichera tutte le librerie necessarie.

2. AVVIO AUTOMATICO
   Per usare il bot (Server + Client + Overlay), fai doppio click su:

   >> run_auto_poker.bat

   Si apriranno 3 finestre:
   - Server (Finestra nera): Lasciala aperta.
   - Client (Finestra nera): Cerca PokerStars e scatta foto.
   - Overlay (Finestra grafica): Mostra i consigli "AI COACH".

---------------------------------------------------
RISOLUZIONE PROBLEMI COMUNI
---------------------------------------------------

A) "Libreria 'motor' non trovata" (Testo Giallo)
   -> E NORMALE. Ignoralo. Il bot funzionera lo stesso usando la memoria RAM.

B) "Form data requires python-multipart" (Testo Rosso)
   -> Manca una libreria. Chiudi tutto ed esegui "fix_dependencies.bat".

C) "Screenshot not found"
   -> Assicurati che PokerStars sia aperto e visibile a schermo.
   -> Il client cercherà finestre con nome "PokerStars", "Table", "Hold'em".

D) L'Overlay resta su "IN ATTESA..."
   -> Controlla la finestra del Client. Se dice "Inviato!", allora il server sta elaborando.
   -> Se il Client da errore, controlla che il Server sia acceso.

===================================================
Buon Game! 🍀
===================================================
