#!/usr/bin/env python3
"""Check if USD Python API is available."""

try:
    from pxr import Usd, UsdGeom, Gf
    print("USD Python API (pxr) is available!")
    print(f"Usd version: {Usd.__version__ if hasattr(Usd, '__version__') else 'unknown'}")
    print("Modules available:")
    print(f"  - Usd: {Usd}")
    print(f"  - UsdGeom: {UsdGeom}")
    print(f"  - Gf: {Gf}")
except ImportError as e:
    print("USD Python API (pxr) is NOT installed")
    print(f"Error: {e}")
    print("\nTo install USD Python API:")
    print("  Option 1: Install via Omniverse (comes with Omniverse)")
    print("  Option 2: pip install usd-core (if available)")
    print("  Option 3: Build from source: https://github.com/PixarAnimationStudios/USD")

