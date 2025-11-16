#!/usr/bin/env python3
"""
Script di verifica import per LIVE ADVISOR
Verifica che tutti i moduli necessari siano importabili
"""

import sys
from pathlib import Path

# Aggiungi backend al path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

print("=" * 60)
print("🔍 VERIFICA IMPORT - LIVE ADVISOR")
print("=" * 60)
print()

print(f"📁 Backend directory: {backend_dir}")
print(f"🐍 Python version: {sys.version}")
print()

# Test import VisionPokerEngine
print("1️⃣  Testing VisionPokerEngine...")
try:
    from vision_to_handstate import VisionPokerEngine
    print("   ✅ VisionPokerEngine importato")
    print(f"   📍 Classe: {VisionPokerEngine}")
except ImportError as e:
    print(f"   ❌ ERRORE: {e}")
except Exception as e:
    print(f"   ❌ ERRORE: {e}")

print()

# Test import MockEquityEngine
print("2️⃣  Testing MockEquityEngine...")
try:
    from server import MockEquityEngine
    print("   ✅ MockEquityEngine importato")
    print(f"   📍 Classe: {MockEquityEngine}")
except ImportError as e:
    print(f"   ❌ ERRORE: {e}")
except Exception as e:
    print(f"   ❌ ERRORE: {e}")

print()

# Test import DecisionEngine
print("3️⃣  Testing DecisionEngine...")
try:
    from server import DecisionEngine
    print("   ✅ DecisionEngine importato")
    print(f"   📍 Classe: {DecisionEngine}")
except ImportError as e:
    print(f"   ❌ ERRORE: {e}")
except Exception as e:
    print(f"   ❌ ERRORE: {e}")

print()

# Test import HandState e Decision
print("4️⃣  Testing HandState e Decision...")
try:
    from server import HandState, Decision
    print("   ✅ HandState importato")
    print("   ✅ Decision importato")
    print(f"   📍 HandState: {HandState}")
    print(f"   📍 Decision: {Decision}")
except ImportError as e:
    print(f"   ❌ ERRORE: {e}")
except Exception as e:
    print(f"   ❌ ERRORE: {e}")

print()

# Lista file Python disponibili
print("5️⃣  File Python in backend:")
py_files = sorted(backend_dir.glob("*.py"))
for f in py_files:
    size_kb = f.stat().st_size / 1024
    print(f"   📄 {f.name} ({size_kb:.1f} KB)")

print()
print("=" * 60)

# Test completo di inizializzazione
print("6️⃣  Test completo di inizializzazione...")
try:
    from vision_to_handstate import VisionPokerEngine
    from server import MockEquityEngine, DecisionEngine, HandState, Decision
    
    # Prova a creare le istanze
    vision_engine = VisionPokerEngine()
    equity_engine = MockEquityEngine()
    decision_engine = DecisionEngine()
    
    print("   ✅ Tutti i motori inizializzati con successo!")
    print()
    
    # Mostra status
    status = vision_engine.get_engine_status()
    print(f"   📊 VisionEngine status:")
    print(f"      - Room config: {status.get('room_config_loaded', False)}")
    print(f"      - Card templates: {status.get('card_templates', 0)}")
    print(f"      - Digit templates: {status.get('digit_templates', 0)}")
    print(f"      - Ready: {status.get('fully_ready', False)}")
    
except Exception as e:
    print(f"   ❌ ERRORE durante inizializzazione: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("✅ Verifica completata!")
print("=" * 60)
