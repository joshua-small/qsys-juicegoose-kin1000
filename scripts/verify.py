"""Verify package identity and source integrity before publishing."""
from pathlib import Path
import hashlib
import re
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1]
source = (root / "content/JuiceGooseKin1000ApRmUps.qplug").read_bytes()
assert hashlib.sha256(source).hexdigest() == "06553de7ae9c8bcbc6bc2e1d0918ab3159ffe7a0675267e1ca3931c357daa407", "Update the reviewed source digest for an intentional plugin revision"
info = re.search(r"PluginInfo\s*=\s*\{(.*?)\}", source.decode("utf-8-sig"), re.S)[1]
version = re.search(r'\bVersion\s*=\s*"([^"]+)"', info)[1]
project = ET.parse(root / "JuiceGooseKin1000.csproj").getroot()
assert version == project.findtext("PropertyGroup/Version"), "Plugin/package version mismatch"
assert project.findtext("PropertyGroup/PackageId") == "JoshuaSmall.Qsys.JuiceGooseKin1000"
assert (root / "icon.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
assert "https://joshua-small.github.io/qsys-juicegoose-kin1000/registration/joshuasmall.qsys.juicegoosekin1000/index.json" in (root / "README.md").read_text()
print("Verified", "JuiceGooseKin1000ApRmUps.qplug", version, hashlib.sha256(source).hexdigest())
