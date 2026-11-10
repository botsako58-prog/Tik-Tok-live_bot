FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
      lua5.1 liblua5.1-0-dev luarocks build-essential libssl-dev ca-certificates \
    && luarocks install luasocket \
    && luarocks install lua-cjson \
    && luarocks install luasec \
    && apt-get purge -y build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY main.lua .
CMD ["lua5.1", "main.lua"]
