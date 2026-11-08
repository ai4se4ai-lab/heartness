#!/usr/bin/env bash
set -euo pipefail
mkdir -p build/tools
task_spin_dir=$(mktemp -d)
trap 'rm -rf "$task_spin_dir"' EXIT
git clone --quiet https://github.com/nimble-code/Spin.git "$task_spin_dir/Spin"
git -C "$task_spin_dir/Spin" checkout --quiet 4883fbb1b1ef1f75fa9dda78efe1ad8910baf819
make -C "$task_spin_dir/Spin/Src"
cp "$task_spin_dir/Spin/Src/spin" build/tools/spin
build/tools/spin -V
