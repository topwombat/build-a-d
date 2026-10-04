#!/usr/bin/env bash
# Non-interactive headless (no-graphics) build of the OpenVSP Python API from source.
# All third-party libs are bundled as zip/tarballs inside the OpenVSP repo
# (Libraries/*.zip), so the only network access needed is apt + a git clone of github.com.
#
# Env overrides:
#   VSP_TAG      (default OpenVSP_3.49.0)
#   SRC_ROOT     (default /opt/openvsp)       - clone + build location
#   PYTHON       (default: python3 on PATH)  - interpreter to build/install for (needs numpy)
#   JOBS         (default: nproc)
#   SKIP_APT=1   to skip apt-get install
set -euo pipefail

VSP_TAG="${VSP_TAG:-OpenVSP_3.49.0}"
SRC_ROOT="${SRC_ROOT:-/opt/openvsp}"
PYTHON="${PYTHON:-$(command -v python3)}"
JOBS="${JOBS:-$(nproc)}"

if [ "${SKIP_APT:-0}" != "1" ]; then
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -q
  apt-get install -y -q --no-install-recommends \
    build-essential cmake git swig ca-certificates \
    libxml2-dev libeigen3-dev libcminpack-dev libglm-dev
  # Python headers + libpython for the target interpreter (e.g. python3.11-dev) must be present.
fi

PYVER="$("$PYTHON" -c 'import sys;print(f"{sys.version_info[0]}.{sys.version_info[1]}")')"
PYINC="$("$PYTHON" -c 'import sysconfig;print(sysconfig.get_paths()["include"])')"
PYLIBDIR="$("$PYTHON" -c 'import sysconfig;print(sysconfig.get_config_var("LIBDIR"))')"
PYLIB="${PYLIBDIR}/libpython${PYVER}.so"
[ -f "$PYINC/Python.h" ] || { echo "Missing Python.h for $PYTHON ($PYINC); install python${PYVER}-dev" >&2; exit 1; }
[ -f "$PYLIB" ] || { echo "Missing $PYLIB; install python${PYVER}-dev / libpython${PYVER}-dev" >&2; exit 1; }
"$PYTHON" -m pip install -q 'numpy' 'setuptools'

mkdir -p "$SRC_ROOT"
if [ ! -d "$SRC_ROOT/OpenVSP/.git" ]; then
  git clone -q --depth 1 --branch "$VSP_TAG" https://github.com/OpenVSP/OpenVSP "$SRC_ROOT/OpenVSP"
fi

BUILD="$SRC_ROOT/build"
mkdir -p "$BUILD"
cmake -S "$SRC_ROOT/OpenVSP/SuperProject" -B "$BUILD" \
  -DCMAKE_BUILD_TYPE=Release \
  -DVSP_NO_GRAPHICS=ON \
  -DVSP_NO_HELP=ON \
  -DVSP_NO_DOC=ON \
  -DVSP_NO_PYDOC=ON \
  -DPYTHON_EXECUTABLE="$PYTHON" \
  -DPYTHON_INCLUDE_DIR="$PYINC" \
  -DPYTHON_INCLUDE_PATH="$PYINC" \
  -DPYTHON_LIBRARY="$PYLIB" \
  -DCMAKE_INSTALL_PREFIX="$SRC_ROOT/install"

# The SuperProject runs the inner OpenVSP "install" and "package" steps in parallel; both rebuild
# the inner "all" target and race on the python_api copy_package step ("Error copying directory ...
# python_pseudo"). So tolerate a failure here, then build+install the inner project directly.
cmake --build "$BUILD" -j "$JOBS" || echo "SuperProject build reported an error (known install/package race); continuing"
cmake --build "$BUILD/OpenVSP-prefix/src/OpenVSP-build" -j "$JOBS" --target install

# Install the python packages into the target interpreter's environment (single pip call so
# inter-package deps resolve locally; openvsp depends on degen_geom, utilities, openvsp_config).
PYPKG="$SRC_ROOT/install/python"
"$PYTHON" -m pip install --no-cache-dir \
  "$PYPKG/openvsp_config" "$PYPKG/utilities" "$PYPKG/degen_geom" "$PYPKG/vsp_airfoils" "$PYPKG/openvsp"

cd /
"$PYTHON" - <<'PYEOF'
import openvsp as vsp
print("OpenVSP:", vsp.GetVSPVersion())
vsp.AddGeom("WING"); vsp.Update()
assert "WaveDrag" in vsp.ListAnalysis()
PYEOF
