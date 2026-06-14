import pytest
from sankey._presets import (
    load_preset, list_presets, register_preset,
    PRESETS,
)


class TestLoadPreset:
    def test_nature_exists(self):
        p = load_preset("nature")
        assert p["font_family"] == "Arial"
        assert "main_palette" in p

    def test_cell_exists(self):
        p = load_preset("cell")
        assert "main_palette" in p

    def test_science_exists(self):
        p = load_preset("science")
        assert "main_palette" in p

    def test_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown preset"):
            load_preset("nonexistent")

    def test_override(self):
        p = load_preset("nature", font_size=99)
        assert p["font_size"] == 99

    def test_override_does_not_mutate_original(self):
        original = PRESETS["nature"]["font_size"]
        load_preset("nature", font_size=999)
        assert PRESETS["nature"]["font_size"] == original


class TestRegisterPreset:
    def test_register_and_load(self):
        register_preset("test", {"main_palette": ["#FFF"], "font_family": "Test"})
        p = load_preset("test")
        assert p["main_palette"] == ["#FFF"]
        PRESETS.pop("test", None)

    def test_register_overwrites(self):
        register_preset("temp", {"font_family": "Overwrite"})
        register_preset("temp", {"font_family": "New"})
        assert load_preset("temp")["font_family"] == "New"
        PRESETS.pop("temp", None)


class TestListPresets:
    def test_includes_all(self):
        names = list_presets()
        assert "nature" in names
        assert "cell" in names
        assert "science" in names
