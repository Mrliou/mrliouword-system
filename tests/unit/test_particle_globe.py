"""
Tests for ParticleGlobe.
"""

import json

from particle_globe import ParticleGlobe


def test_bind_particle_creates_default_point_structure():
    globe = ParticleGlobe()

    bind_id = globe.bind_particle(
        particle_id="P_TAIPEI",
        latitude=25.0330,
        longitude=121.5654,
        data={"name": "台北記憶點"},
    )

    binding = globe.get_binding("P_TAIPEI")
    assert bind_id == binding["bind_id"]
    assert binding["geometry_type"] == "point"
    assert binding["structure"]["scale"] == 1.0
    assert binding["structure"]["zoom"] == 1.0
    assert binding["lifecycle"]["stage"] == "bound"
    assert len(binding["trajectory"]) == 1


def test_record_trajectory_and_lifecycle_evolution():
    globe = ParticleGlobe()
    globe.bind_particle("P_FLOW", 25.0330, 121.5654)

    globe.record_trajectory("P_FLOW", 25.0400, 121.5700, meta={"step": 2})
    evolved = globe.evolve_particle(
        "P_FLOW",
        "evolving",
        metrics={"energy": 0.88, "phase": "trajectory-expanded"},
    )

    assert evolved["geometry_type"] == "line"
    assert len(evolved["trajectory"]) == 2
    assert evolved["lifecycle"]["stage"] == "evolving"
    assert evolved["lifecycle"]["history"][-1]["metrics"]["energy"] == 0.88


def test_update_structure_supports_point_line_surface_scale_and_zoom():
    globe = ParticleGlobe()
    globe.bind_particle("P_MESH", 25.0330, 121.5654)

    updated = globe.update_particle_structure(
        "P_MESH",
        points=[(25.0330, 121.5654, 0), (25.0400, 121.5700, 10)],
        lines=[
            [
                {"latitude": 25.0330, "longitude": 121.5654},
                {"latitude": 25.0500, "longitude": 121.5800},
            ]
        ],
        surfaces=[
            [
                {"latitude": 25.0330, "longitude": 121.5654},
                {"latitude": 25.0400, "longitude": 121.5700},
                {"latitude": 25.0380, "longitude": 121.5800},
            ]
        ],
        scale=2.5,
        zoom=1.8,
    )

    scale_state = globe.scale_particle("P_MESH", 1.2)
    zoom_state = globe.set_zoom("P_MESH", 2.2)

    assert updated["geometry_type"] == "surface"
    assert len(updated["structure"]["points"]) == 2
    assert len(updated["structure"]["lines"]) == 1
    assert len(updated["structure"]["surfaces"]) == 1
    assert round(scale_state["scale"], 2) == 3.0
    assert zoom_state["zoom"] == 2.2


def test_get_particles_in_radius_returns_sorted_matches():
    globe = ParticleGlobe()
    globe.bind_particle("P_NEAR", 25.0330, 121.5654)
    globe.bind_particle("P_FAR", 35.6895, 139.6917)

    nearby = globe.get_particles_in_radius(25.0330, 121.5654, radius_km=10)

    assert [item["particle_id"] for item in nearby] == ["P_NEAR"]
    assert nearby[0]["distance_km"] == 0.0


def test_export_kml_and_offline_globe(tmp_path):
    globe = ParticleGlobe()
    globe.bind_particle("P_EXPORT", 25.0330, 121.5654, data={"name": "export"})
    globe.record_trajectory("P_EXPORT", 25.0400, 121.5700)
    globe.update_particle_structure(
        "P_EXPORT",
        surfaces=[
            [
                {"latitude": 25.0330, "longitude": 121.5654},
                {"latitude": 25.0400, "longitude": 121.5700},
                {"latitude": 25.0380, "longitude": 121.5800},
            ]
        ],
    )

    kml_path = tmp_path / "globe.kml"
    html_path = tmp_path / "globe.html"

    globe.export_kml(str(kml_path))
    globe.generate_offline_globe(str(html_path))

    kml = kml_path.read_text(encoding="utf-8")
    html = html_path.read_text(encoding="utf-8")

    assert "<Placemark>" in kml
    assert "<LineString>" in kml
    assert "<Polygon><outerBoundaryIs><LinearRing>" in kml
    assert "粒子記憶地球儀" in html
    assert json.dumps("P_EXPORT")[1:-1] in html
