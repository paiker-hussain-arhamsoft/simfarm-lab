FROM instedd/verboice:3.5.1

USER root
RUN apt-get update && apt-get install -y --no-install-recommends --allow-unauthenticated default-mysql-client netcat-openbsd && rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /entrypoint.sh
COPY verboice_tool.rb /usr/local/bin/verboice_tool.rb

RUN chmod +x /entrypoint.sh /usr/local/bin/verboice_tool.rb

ENTRYPOINT ["/entrypoint.sh"]
CMD ["puma", "-e", "production", "-b", "tcp://0.0.0.0:80"]
