"""Central CLI entry point for psi-agent.

This module provides a unified CLI that dynamically discovers and delegates
to component CLIs based on package structure. This enables `uvx psi-agent`
to work seamlessly without requiring users to clone the repository.

Usage:
    uvx psi-agent ai openai-completions --session-socket ./sock ...
    uvx psi-agent channel cli --session-socket ./sock ...
    uvx psi-agent session --channel-socket ./sock ...
    uvx psi-agent workspace pack --input ./workspace ...
"""

from __future__ import annotations

import argparse
import importlib
import sys
from collections.abc import Callable
from pathlib import Path


def _discover_components() -> dict[str, dict[str, Callable[[], None]]]:
    """Discover available CLI components from psi_agent package structure.

    Returns:
        Dictionary mapping component names to their subcommands and entry points.
    """
    components: dict[str, dict[str, Callable[[], None]]] = {}

    # Get psi_agent package path
    psi_agent_path = Path(__file__).parent

    # List subdirectories (potential components)
    for item in psi_agent_path.iterdir():
        if not item.is_dir() or item.name.startswith("_"):
            continue

        component_name = item.name.replace("_", "-")
        subcommands: dict[str, Callable[[], None]] = {}

        # Check for subcomponents (nested modules with main())
        for subitem in item.iterdir():
            if subitem.is_dir() and not subitem.name.startswith("_"):
                # Check for cli.py in the subdirectory
                cli_file = subitem / "cli.py"
                if cli_file.exists():
                    try:
                        submodule = importlib.import_module(
                            f"psi_agent.{item.name}.{subitem.name}.cli"
                        )
                        if hasattr(submodule, "main"):
                            subcommand_name = subitem.name.replace("_", "-")
                            subcommands[subcommand_name] = submodule.main
                    except ImportError:
                        pass
                else:
                    # Try to import the submodule directly (for modules with main())
                    try:
                        submodule = importlib.import_module(f"psi_agent.{item.name}.{subitem.name}")
                        if hasattr(submodule, "main"):
                            subcommand_name = subitem.name.replace("_", "-")
                            subcommands[subcommand_name] = submodule.main
                    except ImportError:
                        pass
            elif subitem.is_file() and subitem.suffix == ".py":
                # Check for cli.py with main() at component level
                if subitem.stem == "cli":
                    try:
                        submodule = importlib.import_module(f"psi_agent.{item.name}.cli")
                        if hasattr(submodule, "main"):
                            subcommands["_self"] = submodule.main
                    except ImportError:
                        pass

        if subcommands:
            components[component_name] = subcommands

    return components


def main() -> None:
    """Main entry point for psi-agent CLI."""
    components = _discover_components()

    if not components:
        print("No CLI components found in psi_agent package")
        sys.exit(1)

    # Build argparse parser with dynamic subcommands
    # Don't add help so it can be passed to subcommands
    parser = argparse.ArgumentParser(
        prog="psi-agent",
        description="Unified CLI entry point for psi-agent components.",
        add_help=False,
    )
    subparsers = parser.add_subparsers(dest="component", help="Component to run")

    for component_name, subcommands in sorted(components.items()):
        if "_self" in subcommands and len(subcommands) == 1:
            # Single entry point - add as direct subcommand
            subparser = subparsers.add_parser(
                component_name, help=f"Run {component_name}", add_help=False
            )
            subparser.set_defaults(func=subcommands["_self"])
        elif len(subcommands) > 1:
            # Multiple subcommands - add nested subparsers
            comp_parser = subparsers.add_parser(
                component_name, help=f"{component_name} subcommands", add_help=False
            )
            comp_subparsers = comp_parser.add_subparsers(
                dest="subcommand", help="Subcommand to run"
            )
            for subcommand_name, entry_point in sorted(subcommands.items()):
                if subcommand_name != "_self":
                    sub_parser = comp_subparsers.add_parser(
                        subcommand_name,
                        help=f"Run {component_name} {subcommand_name}",
                        add_help=False,
                    )
                    sub_parser.set_defaults(func=entry_point)

    # Parse known args to allow remaining args to pass through
    args, _ = parser.parse_known_args()

    if args.component is None:
        parser.print_help()
        sys.exit(0)

    # Check if we need a subcommand but none was provided
    if hasattr(args, "subcommand") and args.subcommand is None:
        # Print help for the component
        parser.parse_args([args.component, "--help"])
        sys.exit(0)

    # Run the discovered function
    if hasattr(args, "func"):
        # Remove our internal args before calling the function
        # The function will use tyro to parse remaining args
        remaining_args = sys.argv[2:]  # Skip 'psi-agent' and component name
        if hasattr(args, "subcommand") and args.subcommand:
            remaining_args = sys.argv[3:]  # Skip subcommand too
        sys.argv = [sys.argv[0]] + remaining_args
        args.func()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
