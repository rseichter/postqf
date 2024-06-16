#!/usr/bin/env bash
# vim: ft=sh ts=4 sw=4 noet
#
# Install PostQF from source tarball and create a launcher
# script # in the current working directory.

set -euo pipefail
declare -r RELEASE="0.5"

function die {
	echo >&2 "$@"
	exit 1
}

function download {
	local tmp=$1 url=$2
	if type curl; then
		curl -f -L -o "$tmp" "$url" || die "curl failed to download $url"
	elif type wget; then
		wget -O "$tmp" "$url" || die "wget failed to download $url"
	else
		die "Need curl or wget in PATH"
	fi
}

function main {
	local tarball="$RELEASE.tar.gz" tmp
	local url="https://github.com/rseichter/postqf/archive/refs/tags/$tarball"
	tmp="$(mktemp)"
	# shellcheck disable=2064
	trap "rm $tmp" EXIT
	download "$tmp" "$url"
	tar xzf "$tmp" --no-same-owner

	cat >postqf <<EOT
#!/usr/bin/env bash
#
# PostQF launcher script. Python code was downloaded on $(date -I) from
# $url

PYTHONPATH="$(realpath postqf-$RELEASE)" python3 -m postqf "\$@"
EOT
	chmod 0755 postqf
	echo "You can now launch PostQF using $(realpath postqf)"
}

main
