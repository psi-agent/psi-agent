"""Process title manipulation for hiding sensitive CLI arguments."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    pass

# Try to import setproctitle, with graceful fallback
try:
    import setproctitle

    _HAS_SETPROCTITLE = True
except ImportError:
    _HAS_SETPROCTITLE = False


def mask_sensitive_args(sensitive_keys: list[str]) -> None:
    """Mask sensitive CLI arguments from process title.

    Replaces values of specified argument keys with '***' in the process title
    to prevent sensitive information (API keys, tokens, passwords) from being
    visible in process listings (ps, top, /proc/<pid>/cmdline).

    Args:
        sensitive_keys: List of argument names to mask (e.g., ['api_key', 'token']).
                       Both underscore and hyphen variants are handled.

    Note:
        This uses the setproctitle library if available. On platforms where
        setproctitle is not available, a warning is logged and no masking occurs.
        There is a brief window between process start and this function call
        where arguments may be visible.
    """
    if not _HAS_SETPROCTITLE:
        logger.warning(
            "setproctitle not available, sensitive arguments may be visible in process list"
        )
        return

    # Get current argv
    argv = sys.argv
    masked_argv = list(argv)

    # Build both underscore and hyphen variants for each key
    key_variants: set[str] = set()
    for key in sensitive_keys:
        key_variants.add(key)
        key_variants.add(key.replace("_", "-"))
        key_variants.add(key.replace("-", "_"))

    # Mask values for matching keys
    i = 0
    while i < len(masked_argv) - 1:
        arg = masked_argv[i]
        # Handle --key=value format
        if arg.startswith("--"):
            if "=" in arg:
                key_part, _ = arg.split("=", 1)
                key_name = key_part[2:]  # Remove '--'
                if key_name in key_variants:
                    masked_argv[i] = f"{key_part}=***"
            else:
                # Handle --key value format
                key_name = arg[2:]  # Remove '--'
                if key_name in key_variants:
                    masked_argv[i + 1] = "***"
        i += 1

    # Set the new process title
    new_title = " ".join(masked_argv)
    setproctitle.setproctitle(new_title)
    logger.debug("Masked sensitive arguments in process title")
