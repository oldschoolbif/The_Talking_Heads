#!/usr/bin/env python3
"""Check available avatar providers."""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.avatar_generator import AvatarGenerator
from src.utils.config_loader import load_config

config = load_config('config/config.yaml')
gen = AvatarGenerator(config, output_dir=Path('.cache/temp/avatars'))

print('Available avatar providers:')
for name, provider in gen.providers.items():
    available = provider.is_available() if hasattr(provider, 'is_available') else 'N/A'
    print(f'  {name}: {available}')

