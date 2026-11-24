#!/bin/sh
out=/opt/javalibs
mkdir -p "$out"
while read ga; do
  [ -z "$ga" ] && continue
  g=${ga%%:*}; a=${ga##*:}
  gp=$(echo "$g" | tr . /)
  base="https://repo1.maven.org/maven2/$gp/$a"
  v=$(curl -fsSL --max-time 30 "$base/maven-metadata.xml" 2>/dev/null | sed -n 's:.*<release>\(.*\)</release>.*:\1:p' | head -1)
  if [ -z "$v" ]; then echo "SKIP $ga"; continue; fi
  if ! curl -fsSL --max-time 120 -o "$out/$a-$v.jar" "$base/$v/$a-$v.jar" 2>/dev/null; then
    echo "SKIP $ga"; rm -f "$out/$a-$v.jar"
  fi
done < /libs/java-libs.txt
echo "java libs: $(ls $out | wc -l)"
