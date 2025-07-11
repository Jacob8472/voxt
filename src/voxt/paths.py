"""
voxt.paths - all filesystem look-ups live here.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Final
from functools import lru_cache
from voxt.utils.libw import diagn

# ─────────────────────────────────────────────────────────────────────────────
# XDG-compatible base dirs
HOME: Final = Path.home()
CONFIG_DIR: Final = Path(os.getenv("XDG_CONFIG_HOME", HOME / ".config")) / "voxt"
DATA_DIR: Final = Path(os.getenv("XDG_DATA_HOME", HOME / ".local" / "share")) / "voxt"

CONFIG_FILE: Final = CONFIG_DIR / "config.yaml"

# ─────────────────────────────────────────────────────────────────────────────
# Whisper-cli resolver
# ---------------------------------------------------------------------------

def _locate_whisper_cli() -> Path:
    """Return an absolute :class:`pathlib.Path` to *whisper-cli*.

    Order (first hit wins):
      1. ``$VOXT_WC_BIN`` – explicit override.
      2. Repo-local build  → ``whisper.cpp/build/bin/whisper-cli``.
      3. First executable named *whisper-cli* found on ``$PATH``.

    Raises ``FileNotFoundError`` if nothing is found.
    """

    # 1. Environment override ---------------------------------------------
    env = os.getenv("VOXT_WC_BIN")
    if env:
        p = Path(env).expanduser().resolve()
        if p.is_file():
            return p

    # 2. Inside the git repo / editable install ---------------------------
    repo_candidate = (
        Path(__file__).parents[2]
        / "whisper.cpp" / "build" / "bin" / "whisper-cli"
    )
    if repo_candidate.is_file():
        return repo_candidate

    # 3. Anything available on $PATH --------------------------------------
    which = shutil.which("whisper-cli")
    if which:
        return Path(which).resolve()

    # Nothing worked ------------------------------------------------------
    raise FileNotFoundError(
        "Could not locate *whisper-cli*. Checked $VOXT_WC_BIN, repo-local build and $PATH. "
        "Run setup.sh or build whisper.cpp manually."
    )

# ---------------------------------------------------------------------------
#  Lazy resolver – cache first successful result for the rest of the run
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def whisper_cli() -> Path:  # noqa: D401
    """Return an absolute Path to *whisper-cli* (raises if not found)."""
    return _locate_whisper_cli()

# ─────────────────────────────────────────────────────────────────────────────
#  Output directory for transcripts, logs, temp files, …
# ---------------------------------------------------------------------------
OUTPUT_DIR: Final = DATA_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
#  Convenience helper for packaged resources
# ---------------------------------------------------------------------------

def resource_path(*sub: str | os.PathLike[str]) -> Path:
    """Return the absolute path of a data file shipped within the package."""
    return Path(__file__).with_suffix("").with_name("data").joinpath(*sub)

# ─────────────────────────────────────────────────────────────────────────────
#  Base model discovery
# ---------------------------------------------------------------------------

def _locate_base_model() -> Path:
    """Return absolute Path to the default base model (ggml-base.en.bin)."""

    # 1. Environment override -------------------------------------------
    env = os.getenv("VOXT_MODEL_PATH")
    if env:
        env_path = Path(env).expanduser().resolve()
        if env_path.is_file():
            return env_path

    # 2. XDG data dir – canonical location ------------------------------
    data_candidate = DATA_DIR / "models" / "ggml-base.en.bin"
    if data_candidate.exists():
        return data_candidate.resolve()

    # 3. Repo-local (editable/dev install) ------------------------------
    repo_candidate = (
        Path(__file__).parents[2]
        / "whisper.cpp" / "models" / "ggml-base.en.bin"
    )
    if repo_candidate.exists():
        return repo_candidate.resolve()

    raise FileNotFoundError(
        "Could not locate the default Whisper model (ggml-base.en.bin).\n"
        "Checked $VOXT_MODEL_PATH, XDG data dir, and repo-local.\n"
        "Run setup.sh or download the model manually."
    )

@lru_cache(maxsize=1)
def base_model() -> Path:  # noqa: D401
    """Return the default base model path (raises if not found)."""
    return _locate_base_model()

# ---------------------------------------------------------------------------
#  Legacy helpers kept for backward-compat
# ---------------------------------------------------------------------------

def find_base_model() -> str:  # noqa: N802
    """Return the default base model path as *str* (legacy API)."""
    return str(base_model())


def find_whisper_cli() -> str:  # noqa: N802
    """Return *whisper-cli* path as *str* (legacy API)."""
    return str(whisper_cli())

# ---------------------------------------------------------------------------
#  Public utility helpers
# ---------------------------------------------------------------------------

def resolve_whisper_binary(path_hint: str) -> Path:
    """Resolve *whisper-cli* given a user hint (absolute/relative)."""
    p = Path(path_hint)
    if p.is_absolute() and p.exists():
        return p
    try:
        return _locate_whisper_cli()
    except FileNotFoundError:
        return p.resolve()


def resolve_model_path(path_hint: str) -> Path:
    """Resolve model file given a user hint (absolute/relative)."""
    p = Path(path_hint)
    if p.is_absolute() and p.exists():
        return p
    try:
        return _locate_base_model()
    except FileNotFoundError:
        return p.resolve()
