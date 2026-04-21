import os
import sys
import subprocess

def build():
    print("Checking for PyInstaller...")
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Get the absolute path to the backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(backend_dir, "main.py")
    
    # The output folder where Electron will look for the bundled backend
    dist_path = os.path.abspath(os.path.join(backend_dir, "..", "frontend", "resources"))
    
    # Ensure the resources folder exists
    os.makedirs(dist_path, exist_ok=True)
    
    # PyInstaller arguments
    args = [
        "pyinstaller",
        "--noconfirm",          # Overwrite existing builds
        "--onedir",             # One-folder bundle (safer for FastAPI/Uvicorn than onefile)
        "--windowed",           # Don't show a console window when launched
        "--name=backend_server",# The name of the output folder/executable
        f"--distpath={dist_path}",
        
        # Uvicorn and FastAPI require several hidden imports to work when compiled
        "--hidden-import=uvicorn.logging",
        "--hidden-import=uvicorn.loops",
        "--hidden-import=uvicorn.loops.auto",
        "--hidden-import=uvicorn.protocols",
        "--hidden-import=uvicorn.protocols.http",
        "--hidden-import=uvicorn.protocols.http.auto",
        "--hidden-import=uvicorn.protocols.websockets",
        "--hidden-import=uvicorn.protocols.websockets.auto",
        "--hidden-import=uvicorn.lifespan",
        "--hidden-import=uvicorn.lifespan.on",
        
        main_script
    ]
    
    print(f"Running PyInstaller: {' '.join(args)}")
    subprocess.check_call(args)
    print("\n✅ Build complete!")
    print(f"The bundled backend is located in: {os.path.join(dist_path, 'backend_server')}")
    print("Electron can now spawn this executable from its resources folder.")

if __name__ == "__main__":
    build()
