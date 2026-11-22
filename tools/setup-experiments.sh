#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
root=$PWD
state="$root/data/research/setup"
mkdir -p "$state"
exec 9>"$state/lock"
flock 9

for tool in uv git g++ bash curl sha256sum flock tar; do
    command -v "$tool" >/dev/null || { echo "Missing required command: $tool" >&2; exit 1; }
done
export UV_PROJECT_ENVIRONMENT="$root/.venv"
uv sync --locked --python 3.14.10
export PYTHON="$UV_PROJECT_ENVIRONMENT/bin/python"
unset FOW_STOCKFISH FOW_POSITIONS

revision=edb0d9db6731067ec50ce619ff372b463bc4dd5d
network=nn-1a298aa575a0.nnue
network_hash=1a298aa575a085434d29027978dc36867fe9c5bcea9376654b7a8eba1e52dfc2
source="$state/stockfish-source"
check_network() {
    printf '%s  %s\n' "$network_hash" "$1" | sha256sum --check --status
}
if ! check_network "$source/src/$network" 2>/dev/null ||
   [[ $(git -C "$source" rev-parse HEAD 2>/dev/null) != "$revision" ]] ||
   ! git -C "$source" diff --quiet HEAD; then
    staging=$(mktemp -d "$state/download.XXXXXX")
    trap 'rm -rf -- "$staging"' EXIT
    git -c advice.detachedHead=false clone --quiet --depth 1 --branch sf_19 https://github.com/official-stockfish/Stockfish.git "$staging/source"
    [[ $(git -C "$staging/source" rev-parse HEAD) == "$revision" ]]
    curl --fail --silent --show-error --location --retry 2 --max-time 120 \
        "https://data.stockfishchess.org/nn/$network" -o "$staging/source/src/$network" ||
    curl --fail --silent --show-error --location --retry 2 --max-time 120 \
        "https://raw.githubusercontent.com/official-stockfish/networks/master/$network" -o "$staging/source/src/$network"
    check_network "$staging/source/src/$network"
    rm -rf -- "$source"
    mv "$staging/source" "$source"
    rmdir "$staging"
    trap - EXIT
fi

for bot in eBotI obscuro obscuro_v3 obscuro_v4 "$@"; do
    [[ $bot =~ ^[a-zA-Z0-9_-]+$ && -f bots/$bot/build.sh ]]
    dir="bots/$bot"
    log="$state/$bot.log"
    fingerprint=$(
        printf '%s\n' "$revision" "$network_hash"
        g++ --version
        uname -sm
        "$PYTHON" --version
        git ls-files -z -- "$dir" fow starter pyproject.toml uv.lock |
            xargs -0 sha256sum
    )
    cache_key=$(printf '%s' "$fingerprint" | sha256sum | cut -d' ' -f1)
    artifacts=()
    [[ ! -f $dir/REQUIRE_STOCKFISH ]] || artifacts+=("$dir/stockfish/src/stockfish" "$dir/stockfish/src/$network")
    [[ ! -f $dir/REQUIRE_POSITIONS ]] || artifacts+=("$dir/positions")
    if [[ -f $state/$bot.key && $(cat "$state/$bot.key") == "$cache_key" && -f $log ]] &&
       [[ ! -f $dir/REQUIRE_STOCKFISH || -x $dir/stockfish/src/stockfish ]] &&
       [[ ! -f $dir/REQUIRE_POSITIONS || -x $dir/positions ]] &&
       sha256sum --check --status "$state/$bot.sha256"; then
        echo "$bot: using verified cached build"
        continue
    fi
    rm -f -- "$state/$bot.key"
    if [[ -f $dir/REQUIRE_STOCKFISH ]]; then
        rm -rf -- "$dir/stockfish.new"
        mkdir "$dir/stockfish.new"
        git -C "$source" archive HEAD | tar -x -C "$dir/stockfish.new"
        cp "$source/src/$network" "$dir/stockfish.new/src/$network"
        rm -rf -- "$dir/stockfish"
        mv "$dir/stockfish.new" "$dir/stockfish"
    fi
    bash "$dir/build.sh" 2>&1 | tee "$log"
    if [[ -f $dir/REQUIRE_STOCKFISH ]]; then
        grep -q '^build: STOCKFISH OK:' "$log"
        test -x "$dir/stockfish/src/stockfish"
        "$dir/stockfish/src/stockfish" compiler
    fi
    if [[ -f $dir/REQUIRE_POSITIONS ]]; then
        grep -q '^build: POSITION SET OK:' "$log"
        test -x "$dir/positions"
    fi
    if (( ${#artifacts[@]} )); then
        sha256sum "${artifacts[@]}" > "$state/$bot.sha256"
        printf '%s\n' "$cache_key" > "$state/$bot.key"
    fi
done
