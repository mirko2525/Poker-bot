import os
import sys

print("="*50)
print("TEST IMPORT GROQ")
print("="*50)

try:
    from groq import Groq
    print("✅ Libreria 'groq' trovata!")
    print(f"   Percorso: {sys.modules['groq'].__file__}")
except ImportError as e:
    print("❌ ERRORE: Libreria 'groq' NON trovata.")
    print(f"   Dettaglio: {e}")
    print("\nSOLUZIONE:")
    print("Esegui 'fix_dependencies.bat' per installarla.")

print("="*50)
input("Premi INVIO per chiudere...")
