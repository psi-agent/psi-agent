"""Manifest data structure for workspace squashfs images."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from uuid import UUID

from loguru import logger


class ManifestParseError(Exception):
    """Raised when manifest JSON parsing fails."""

    pass


@dataclass
class Layer:
    """A layer in the workspace squashfs.

    Args:
        parent: Optional parent layer UUID. Root layers have no parent.
        tag: Optional human-readable tag for the layer.
    """

    parent: UUID | None = None
    tag: str | None = None


@dataclass
class Manifest:
    """Manifest for a workspace squashfs image.

    Args:
        layers: Mapping of layer UUID to Layer metadata.
        default: UUID of the default (latest) layer.
    """

    layers: dict[UUID, Layer] = field(default_factory=dict)
    default: UUID | None = None

    def get_root_layers(self) -> list[UUID]:
        """Get all root layers (layers without parent).

        Returns:
            List of root layer UUIDs.
        """
        return [uuid for uuid, layer in self.layers.items() if layer.parent is None]

    def get_children(self, parent_uuid: UUID) -> list[UUID]:
        """Get all direct children of a layer.

        Args:
            parent_uuid: UUID of the parent layer.

        Returns:
            List of child layer UUIDs.
        """
        return [uuid for uuid, layer in self.layers.items() if layer.parent == parent_uuid]

    def resolve_chain(self, target_uuid: UUID) -> list[UUID]:
        """Resolve the complete layer chain from root to target.

        Args:
            target_uuid: UUID of the target layer.

        Returns:
            List of UUIDs from root (first) to target (last).

        Raises:
            ValueError: If target_uuid is not in layers.
        """
        if target_uuid not in self.layers:
            raise ValueError(f"Layer {target_uuid} not found in manifest")

        chain: list[UUID] = [target_uuid]
        current = target_uuid

        while True:
            layer = self.layers[current]
            if layer.parent is None:
                break
            if layer.parent not in self.layers:
                raise ValueError(f"Parent layer {layer.parent} not found for layer {current}")
            chain.append(layer.parent)
            current = layer.parent

        chain.reverse()
        return chain

    def lookup_by_tag(self, tag: str) -> UUID:
        """Look up a layer UUID by its tag.

        Args:
            tag: The tag to search for.

        Returns:
            The UUID of the layer with the given tag.

        Raises:
            ValueError: If no layer has the given tag.
        """
        for uuid, layer in self.layers.items():
            if layer.tag == tag:
                return uuid
        raise ValueError(f"No layer found with tag '{tag}'")

    def get_all_tags(self) -> dict[str, UUID]:
        """Get all tags and their corresponding layer UUIDs.

        Returns:
            Mapping of tag to layer UUID.
        """
        return {layer.tag: uuid for uuid, layer in self.layers.items() if layer.tag is not None}


def parse_manifest(json_str: str) -> Manifest:
    """Parse a manifest from JSON string.

    Args:
        json_str: JSON string to parse.

    Returns:
        Parsed Manifest object.

    Raises:
        ManifestParseError: If JSON is invalid or doesn't match expected structure.
    """
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ManifestParseError(f"Invalid JSON: {e}") from e

    if not isinstance(data, dict):
        raise ManifestParseError("Manifest must be a JSON object")

    if "layers" not in data:
        raise ManifestParseError("Manifest must have 'layers' field")

    if "default" not in data:
        raise ManifestParseError("Manifest must have 'default' field")

    layers_data = data["layers"]
    if not isinstance(layers_data, dict):
        raise ManifestParseError("'layers' must be an object")

    layers: dict[UUID, Layer] = {}
    for uuid_str, layer_data in layers_data.items():
        try:
            layer_uuid = UUID(uuid_str)
        except ValueError as e:
            raise ManifestParseError(f"Invalid UUID '{uuid_str}': {e}") from e

        if not isinstance(layer_data, dict):
            raise ManifestParseError(f"Layer '{uuid_str}' must be an object")

        parent: UUID | None = None
        if "parent" in layer_data:
            try:
                parent = UUID(layer_data["parent"])
            except ValueError as e:
                raise ManifestParseError(f"Invalid parent UUID in layer '{uuid_str}': {e}") from e

        tag: str | None = layer_data.get("tag")
        if tag is not None and not isinstance(tag, str):
            raise ManifestParseError(f"Tag in layer '{uuid_str}' must be a string")

        layers[layer_uuid] = Layer(parent=parent, tag=tag)

    # Validate parent references
    for uuid, layer in layers.items():
        if layer.parent is not None and layer.parent not in layers:
            raise ManifestParseError(f"Layer {uuid} references non-existent parent {layer.parent}")

    # Validate default
    try:
        default_uuid = UUID(data["default"])
    except ValueError as e:
        raise ManifestParseError(f"Invalid default UUID: {e}") from e

    if default_uuid not in layers:
        raise ManifestParseError(f"Default layer {default_uuid} not found in layers")

    # Validate tag uniqueness
    tags: dict[str, UUID] = {}
    for uuid, layer in layers.items():
        if layer.tag is not None:
            if layer.tag in tags:
                raise ManifestParseError(
                    f"Duplicate tag '{layer.tag}' in layers {tags[layer.tag]} and {uuid}"
                )
            tags[layer.tag] = uuid

    logger.debug(f"Parsed manifest with {len(layers)} layers, default={default_uuid}")
    return Manifest(layers=layers, default=default_uuid)


def serialize_manifest(manifest: Manifest) -> str:
    """Serialize a manifest to JSON string.

    Args:
        manifest: Manifest object to serialize.

    Returns:
        JSON string representation of the manifest.
    """
    layers_data: dict[str, dict[str, str]] = {}
    for uuid, layer in manifest.layers.items():
        layer_data: dict[str, str] = {}
        if layer.parent is not None:
            layer_data["parent"] = str(layer.parent)
        if layer.tag is not None:
            layer_data["tag"] = layer.tag
        layers_data[str(uuid)] = layer_data

    data = {
        "layers": layers_data,
        "default": str(manifest.default) if manifest.default else "",
    }

    result = json.dumps(data, indent=2)
    logger.debug(f"Serialized manifest with {len(manifest.layers)} layers")
    return result
