"""Tests for manifest data structure."""

from uuid import uuid4

import pytest

from psi_agent.workspace.manifest import (
    Layer,
    Manifest,
    ManifestParseError,
    parse_manifest,
    serialize_manifest,
)


class TestLayer:
    """Tests for Layer dataclass."""

    def test_layer_default_values(self) -> None:
        """Layer with default values has no parent or tag."""
        layer = Layer()
        assert layer.parent is None
        assert layer.tag is None

    def test_layer_with_parent(self) -> None:
        """Layer can have a parent UUID."""
        parent_uuid = uuid4()
        layer = Layer(parent=parent_uuid)
        assert layer.parent == parent_uuid
        assert layer.tag is None

    def test_layer_with_tag(self) -> None:
        """Layer can have a tag."""
        layer = Layer(tag="v1.0")
        assert layer.parent is None
        assert layer.tag == "v1.0"

    def test_layer_with_parent_and_tag(self) -> None:
        """Layer can have both parent and tag."""
        parent_uuid = uuid4()
        layer = Layer(parent=parent_uuid, tag="v1.1")
        assert layer.parent == parent_uuid
        assert layer.tag == "v1.1"


class TestManifest:
    """Tests for Manifest dataclass."""

    def test_manifest_default_values(self) -> None:
        """Manifest with default values has empty layers and no default."""
        manifest = Manifest()
        assert manifest.layers == {}
        assert manifest.default is None

    def test_get_root_layers(self) -> None:
        """get_root_layers returns layers without parent."""
        root_uuid = uuid4()
        child_uuid = uuid4()
        manifest = Manifest(
            layers={
                root_uuid: Layer(tag="root"),
                child_uuid: Layer(parent=root_uuid, tag="child"),
            },
            default=child_uuid,
        )
        roots = manifest.get_root_layers()
        assert roots == [root_uuid]

    def test_get_children(self) -> None:
        """get_children returns direct children of a layer."""
        root_uuid = uuid4()
        child1_uuid = uuid4()
        child2_uuid = uuid4()
        manifest = Manifest(
            layers={
                root_uuid: Layer(),
                child1_uuid: Layer(parent=root_uuid),
                child2_uuid: Layer(parent=root_uuid),
            },
            default=child1_uuid,
        )
        children = manifest.get_children(root_uuid)
        assert set(children) == {child1_uuid, child2_uuid}

    def test_resolve_chain(self) -> None:
        """resolve_chain returns chain from root to target."""
        root_uuid = uuid4()
        mid_uuid = uuid4()
        leaf_uuid = uuid4()
        manifest = Manifest(
            layers={
                root_uuid: Layer(tag="root"),
                mid_uuid: Layer(parent=root_uuid, tag="mid"),
                leaf_uuid: Layer(parent=mid_uuid, tag="leaf"),
            },
            default=leaf_uuid,
        )
        chain = manifest.resolve_chain(leaf_uuid)
        assert chain == [root_uuid, mid_uuid, leaf_uuid]

    def test_resolve_chain_root_layer(self) -> None:
        """resolve_chain on root layer returns just the root."""
        root_uuid = uuid4()
        manifest = Manifest(
            layers={root_uuid: Layer(tag="root")},
            default=root_uuid,
        )
        chain = manifest.resolve_chain(root_uuid)
        assert chain == [root_uuid]

    def test_resolve_chain_invalid_uuid(self) -> None:
        """resolve_chain raises ValueError for invalid UUID."""
        manifest = Manifest()
        with pytest.raises(ValueError, match="not found"):
            manifest.resolve_chain(uuid4())

    def test_lookup_by_tag(self) -> None:
        """lookup_by_tag returns UUID for given tag."""
        layer_uuid = uuid4()
        manifest = Manifest(
            layers={layer_uuid: Layer(tag="v1.0")},
            default=layer_uuid,
        )
        result = manifest.lookup_by_tag("v1.0")
        assert result == layer_uuid

    def test_lookup_by_tag_not_found(self) -> None:
        """lookup_by_tag raises ValueError for unknown tag."""
        manifest = Manifest()
        with pytest.raises(ValueError, match="No layer found"):
            manifest.lookup_by_tag("unknown")

    def test_get_all_tags(self) -> None:
        """get_all_tags returns mapping of tags to UUIDs."""
        uuid1 = uuid4()
        uuid2 = uuid4()
        manifest = Manifest(
            layers={
                uuid1: Layer(tag="v1.0"),
                uuid2: Layer(tag="v1.1"),
            },
            default=uuid2,
        )
        tags = manifest.get_all_tags()
        assert tags == {"v1.0": uuid1, "v1.1": uuid2}


class TestParseManifest:
    """Tests for parse_manifest function."""

    def test_parse_valid_manifest(self) -> None:
        """Parse a valid manifest JSON."""
        uuid1 = uuid4()
        uuid2 = uuid4()
        json_str = f'''{{
            "layers": {{
                "{uuid1}": {{}},
                "{uuid2}": {{ "parent": "{uuid1}", "tag": "v1.1" }}
            }},
            "default": "{uuid2}"
        }}'''
        manifest = parse_manifest(json_str)
        assert len(manifest.layers) == 2
        assert manifest.default == uuid2
        assert manifest.layers[uuid1].parent is None
        assert manifest.layers[uuid1].tag is None
        assert manifest.layers[uuid2].parent == uuid1
        assert manifest.layers[uuid2].tag == "v1.1"

    def test_parse_invalid_json(self) -> None:
        """Parse raises ManifestParseError for invalid JSON."""
        with pytest.raises(ManifestParseError, match="Invalid JSON"):
            parse_manifest("not json")

    def test_parse_missing_layers(self) -> None:
        """Parse raises ManifestParseError when layers is missing."""
        with pytest.raises(ManifestParseError, match="must have 'layers'"):
            parse_manifest('{"default": "uuid"}')

    def test_parse_missing_default(self) -> None:
        """Parse raises ManifestParseError when default is missing."""
        uuid1 = uuid4()
        with pytest.raises(ManifestParseError, match="must have 'default'"):
            parse_manifest(f'{{"layers": {{"{uuid1}": {{}}}}}}')

    def test_parse_invalid_uuid(self) -> None:
        """Parse raises ManifestParseError for invalid UUID."""
        with pytest.raises(ManifestParseError, match="Invalid UUID"):
            parse_manifest('{"layers": {"not-a-uuid": {}}, "default": "not-a-uuid"}')

    def test_parse_nonexistent_parent(self) -> None:
        """Parse raises ManifestParseError for nonexistent parent."""
        uuid1 = uuid4()
        uuid2 = uuid4()
        with pytest.raises(ManifestParseError, match="references non-existent parent"):
            parse_manifest(f'''{{
                "layers": {{
                    "{uuid1}": {{ "parent": "{uuid2}" }}
                }},
                "default": "{uuid1}"
            }}''')

    def test_parse_nonexistent_default(self) -> None:
        """Parse raises ManifestParseError for nonexistent default."""
        uuid1 = uuid4()
        uuid2 = uuid4()
        with pytest.raises(ManifestParseError, match="Default layer.*not found"):
            parse_manifest(f'''{{
                "layers": {{
                    "{uuid1}": {{}}
                }},
                "default": "{uuid2}"
            }}''')

    def test_parse_duplicate_tags(self) -> None:
        """Parse raises ManifestParseError for duplicate tags."""
        uuid1 = uuid4()
        uuid2 = uuid4()
        with pytest.raises(ManifestParseError, match="Duplicate tag"):
            parse_manifest(f'''{{
                "layers": {{
                    "{uuid1}": {{ "tag": "same" }},
                    "{uuid2}": {{ "tag": "same" }}
                }},
                "default": "{uuid2}"
            }}''')


class TestSerializeManifest:
    """Tests for serialize_manifest function."""

    def test_serialize_manifest(self) -> None:
        """Serialize a manifest to JSON."""
        uuid1 = uuid4()
        uuid2 = uuid4()
        manifest = Manifest(
            layers={
                uuid1: Layer(tag="v1.0"),
                uuid2: Layer(parent=uuid1, tag="v1.1"),
            },
            default=uuid2,
        )
        json_str = serialize_manifest(manifest)
        # Parse back to verify
        parsed = parse_manifest(json_str)
        assert parsed.layers.keys() == manifest.layers.keys()
        assert parsed.default == manifest.default

    def test_serialize_roundtrip(self) -> None:
        """Serialize and parse should be identity."""
        uuid1 = uuid4()
        uuid2 = uuid4()
        original = Manifest(
            layers={
                uuid1: Layer(),
                uuid2: Layer(parent=uuid1, tag="test"),
            },
            default=uuid2,
        )
        json_str = serialize_manifest(original)
        parsed = parse_manifest(json_str)
        assert parsed.layers == original.layers
        assert parsed.default == original.default
