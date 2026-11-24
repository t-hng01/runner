#!/bin/sh
export GIT_TERMINAL_PROMPT=0
out=/opt/lualibs
mkdir -p "$out" /tmp/lc
while read repo; do
  [ -z "$repo" ] && continue
  name=$(echo "$repo" | tr '/' '-')
  rm -rf "/tmp/lc/$name"
  if timeout 60 git clone --depth 1 -q "https://github.com/$repo.git" "/tmp/lc/$name" 2>/dev/null; then
    rm -rf "/tmp/lc/$name/.git"
    kb=$(du -sk "/tmp/lc/$name" | cut -f1)
    if [ "$kb" -gt 20000 ]; then echo "SKIP $repo (big)"; else mv "/tmp/lc/$name" "$out/$name"; fi
  else
    echo "SKIP $repo"
  fi
  rm -rf "/tmp/lc/$name"
done < /libs/lune-libs.txt
echo "lune libs: $(ls $out | wc -l)"
