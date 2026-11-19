"""Code shared by the analysis scripts in the source folders (HFD/, ONS/, ILO/, ...).

The repo root is on PYTHONPATH under `pixi run` (pixi.toml [activation.env]), so any script
can `from common import ...` whatever the working directory.
"""
