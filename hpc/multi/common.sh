# Shared helpers for hpc/multi/*.sh (sourced). Clusters are listed in hpc/multi/clusters.tsv.
MULTI_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_LOCAL="$(cd "$MULTI_DIR/../.." && pwd)"
REMOTE_USER="${HPC_USER:-mbabaei}"
SOCK_DIR="$HOME/.ssh/controlmasters"

cluster_names() { grep -v '^#' "$MULTI_DIR/clusters.tsv" | cut -f1; }
cluster_field() { awk -F'\t' -v n="$1" -v k="$2" '$1==n {print $k}' "$MULTI_DIR/clusters.tsv"; }
host_of()  { cluster_field "$1" 2; }
repo_of()  { cluster_field "$1" 3; }
sock_of()  { echo "$SOCK_DIR/${REMOTE_USER}@$(host_of "$1"):22"; }
rssh()     { local n="$1"; shift; ssh -o ControlPath="$(sock_of "$n")" -o BatchMode=yes "${REMOTE_USER}@$(host_of "$n")" "$@"; }
alive()    { ssh -o ControlPath="$(sock_of "$1")" -O check "${REMOTE_USER}@$(host_of "$1")" 2>/dev/null; }
# expand "all" (or nothing) into every cluster; validate names
targets()  {
  if [[ $# -eq 0 || "$1" == "all" ]]; then cluster_names; return; fi
  local n; for n in "$@"; do
    [[ -n "$(host_of "$n")" ]] || { echo "unknown cluster: $n (see hpc/multi/clusters.tsv)" >&2; return 1; }
    echo "$n"; done
}
