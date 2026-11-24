FROM node:20-slim AS nodesrc

FROM python:3.12-slim AS libs
RUN apt-get update && apt-get install -y --no-install-recommends git curl ca-certificates && rm -rf /var/lib/apt/lists/*
COPY fetch_lune.sh fetch_java.sh lune-libs.txt java-libs.txt /libs/
RUN sh /libs/fetch_lune.sh
RUN sh /libs/fetch_java.sh

FROM python:3.12-slim
COPY --from=nodesrc /usr/local/bin/node /usr/local/bin/node
COPY --from=nodesrc /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -sf /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
 && ln -sf /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx
COPY --from=libs /opt/lualibs /opt/lualibs
COPY --from=libs /opt/javalibs /opt/javalibs
WORKDIR /app
COPY requirements.txt node-packages.txt ./
RUN pip install --no-cache-dir flask waitress lupa
RUN grep -v '^\s*$' requirements.txt | while read p; do pip install --no-cache-dir "$p" || echo "SKIP $p"; done
RUN mkdir -p /opt/nodelibs && cd /opt/nodelibs && npm init -y >/dev/null \
 && while read p; do [ -n "$p" ] && (npm install --no-audit --no-fund --ignore-scripts "$p" || echo "SKIP $p"); done < /app/node-packages.txt \
 && npm cache clean --force
COPY . .
RUN mkdir -p /app/tools \
 && chown -R root:root /app \
 && chmod -R go-rwx /app \
 && chmod 711 /app \
 && chmod 755 /app/tools \
 && chmod 644 /app/lua_host.py \
 && chmod -R a+rX /opt/nodelibs /opt/lualibs /opt/javalibs
CMD ["python", "server.py"]
