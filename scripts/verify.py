"""Verify reviewed source bytes and product/release identity before packaging."""
import argparse
import hashlib
from pathlib import Path
from package_checks import check_identity

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--release-tag", help="Exact release tag; must equal v + source and project version")
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
source = (root / "content/JuiceGooseKin1000ApRmUps.qplug").read_bytes()
if hashlib.sha256(source).hexdigest() != "d704f5034a2621256f2f63dce93bc5988e965c945852999f195b04231a51f71a":
    raise SystemExit("Update the reviewed source digest for an intentional plugin revision")
try:
    version = check_identity(source.decode("utf-8-sig"), (root / "JuiceGooseKin1000.csproj").read_text(),
        "JoshuaSmall.Qsys.JuiceGooseKin1000", args.release_tag)
except ValueError as error:
    raise SystemExit(str(error)) from error
if not (root / "icon.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n"):
    raise SystemExit("Invalid package icon")
if "https://joshua-small.github.io/qsys-juicegoose-kin1000/registration/joshuasmall.qsys.juicegoosekin1000/index.json" not in (root / "README.md").read_text():
    raise SystemExit("README Library feed does not match package identity")
print("Verified", "JuiceGooseKin1000ApRmUps.qplug", version, hashlib.sha256(source).hexdigest())
