import sys
import os
import importlib.util

def check_import(module_name, package_name=None):
    if package_name is None:
        package_name = module_name
    
    try:
        importlib.import_module(module_name)
        print(f"✅ {package_name}: INSTALLATO")
        return True
    except ImportError:
        print(f"❌ {package_name}: MANCANTE")
        return False

print("="*40)
print("VERIFICA AMBIENTE POKER BOT")
print("="*40)
print(f"Python: {sys.version.split()[0]}")
print("-" * 20)

# Core
check_import("fastapi")
check_import("uvicorn")
check_import("requests")
check_import("multipart", "python-multipart") # Il modulo si chiama spesso multipart o python_multipart internamente

# AI & Vision
check_import("groq")
check_import("cv2", "opencv-python")
check_import("PIL", "pillow")
check_import("emergentintegrations")

# Desktop Client
check_import("mss")
check_import("pygetwindow")
check_import("PyQt5")

print("-" * 20)
print("Se vedi delle X rosse, esegui 'fix_dependencies.bat'")
print("="*40)
input("Premi INVIO per chiudere...")
