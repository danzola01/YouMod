#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# Use the REST API so JSON boolean inputs retain their types.
python3 - <<'PYTHON' | gh api repos/danzola01/YouMod/actions/workflows/ipa.yml/dispatches --method POST --input -
import json
from pathlib import Path

inputs = json.loads(Path('config/sidestore-inputs.json').read_text())
if bool(inputs.get('ipa_release')) == bool(inputs.get('ipa_url')):
    raise SystemExit('Supply exactly one of ipa_release or ipa_url')
print(json.dumps({'ref': 'sidestore', 'inputs': inputs, 'return_run_details': True}))
PYTHON
