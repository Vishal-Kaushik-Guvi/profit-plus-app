"""
Setup script for Flet web deployment on headless servers (Render, Railway, etc.)
Creates a dummy flet_desktop module so flet can start in web-only mode.
"""
import os
import site
import sys

try:
    import flet_desktop
    print("flet_desktop already available - no action needed.")
except ImportError:
    try:
        sp = site.getsitepackages()[0]
    except Exception:
        sp = os.path.join(os.path.dirname(sys.executable), '..', 'lib', f'python{sys.version_info.major}.{sys.version_info.minor}', 'site-packages')
    
    path = os.path.join(sp, 'flet_desktop')
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, '__init__.py'), 'w') as f:
        f.write('# Dummy module for headless server deployment\n')
    print(f"Created dummy flet_desktop module at: {path}")
