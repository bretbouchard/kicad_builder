import json
import subprocess
from pathlib import Path
import tempfile


def test_generate_pinmap_csv(tmp_path):
    csv = tmp_path / "pins.csv"
    csv.write_text("pin,signal\n1,IOVDD\n2,GPIO0\n")
    out = tmp_path / "out.json"
    subprocess.check_call(
        [
            "python3",
            str(Path(__file__).parents[1] / "generate_pinmap.py"),
            str(csv),
            "--out",
            str(out),
            "--package",
            "RP2040",
        ]
    )
    data = json.loads(out.read_text())
    assert data["package"] == "RP2040"
    assert data["pin_to_signal"]["1"] == "IOVDD"


def test_gen_symbol_and_footprint(tmp_path):
    # prepare a simple pinmap JSON
    pinmap = tmp_path / "pm.json"
    pinmap.write_text(
        json.dumps(
            {
                "package": "RP2040",
                "description": "rp2040",
                "pin_to_signal": {"1": "IOVDD", "2": "GPIO0"},
                "signal_to_pin": {"IOVDD": [1], "GPIO0": [2]},
            }
        )
    )
    lib_out = tmp_path / "REPO-rp2040.lib"
    fp_out = tmp_path / "REPO-rp2040-QFN56.kicad_mod"
    subprocess.check_call(["python3", str(Path(__file__).parents[1] / "gen_symbol.py"), str(pinmap), str(lib_out)])
    subprocess.check_call(["python3", str(Path(__file__).parents[1] / "gen_footprint.py"), "--out", str(fp_out)])
    assert lib_out.exists()
    assert fp_out.exists()
    # check content
    assert "symbol" in lib_out.read_text()
    assert "(module REPO-MCU-QFN56" in fp_out.read_text() or "(module REPO-MCU-QFN56" in fp_out.read_text()


def test_malformed_json(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{ notjson: }")
    script = Path(__file__).parents[1] / "generate_pinmap.py"
    try:
        subprocess.check_call(["python3", str(script), str(bad), "--out", str(tmp_path / "o.json")])
        assert False, "expected failure on malformed JSON"
    except subprocess.CalledProcessError:
        pass


def test_footprint_params(tmp_path):
    outfp = tmp_path / "my.kicad_mod"
    script = Path(__file__).parents[1] / "gen_footprint.py"
    subprocess.check_call(
        [
            "python3",
            str(script),
            "--out",
            str(outfp),
            "--pad_w",
            "0.2",
            "--pad_l",
            "0.4",
            "--ep",
            "3.0",
            "--name",
            "TEST-FP",
        ]
    )
    txt = outfp.read_text()
    assert "TEST-FP" in txt
    assert '(pad "EP" smd rect' in txt
    # when paste reduction is zero, no EP_PASTE pad should exist
    assert "EP_PASTE" not in txt
    # now with paste reduction we expect a paste pad line
    outfp2 = tmp_path / "my2.kicad_mod"
    subprocess.check_call(
        [
            "python3",
            str(script),
            "--out",
            str(outfp2),
            "--pad_w",
            "0.2",
            "--pad_l",
            "0.4",
            "--ep",
            "3.0",
            "--paste_reduction",
            "0.5",
            "--courtyard",
            "0.3",
            "--name",
            "TEST-FP2",
        ]
    )
    txt2 = outfp2.read_text()
    assert "EP_PASTE" in txt2
    assert "F.CrtYd" in txt2


def test_read_metadata(tmp_path):
    # use the sample rp2040.metadata.json in the scripts dir
    md = Path(__file__).parents[1] / "rp2040.metadata.json"
    out = subprocess.check_output(["python3", str(Path(__file__).parents[1] / "read_metadata.py"), str(md)])
    s = out.decode()
    assert "PAD_W=" in s
    assert "EP=" in s
