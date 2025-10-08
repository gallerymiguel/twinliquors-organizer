# Docker Compose Explanation

My Docker Compose file defines the containers my environment needs to run. In this case, each service equals one containerized part of my app. The `db` service defines how my database container should behave.

I’m using `mariadb:11.4`, and by fixing the version, I ensure consistent behavior between local, CI, and production setups. This matters because database updates can sometimes break schemas or behavior. Pinning a version avoids the “it worked yesterday, but not today” problem.

The `container_name` gives my container a permanent, predictable name instead of a random auto-generated one. This makes debugging easier since I can simply run
```
docker logs twinliquors-db
```
to instantly see the output from my database.

The `restart: unless-stopped` setting tells Docker to automatically restart the container if it crashes. This helps keep my environment reliable without needing to manually restart it.

The `env_file: .env.db` line loads environment variables from a separate file, which keeps secrets out of version control and makes configuration easier to manage across different environments.

The `volumes` section handles both persistent storage and initialization.
- The first mount, `db_data:/var/lib/mysql`, keeps my data safe even if the container is deleted or recreated.
- The second mount, `./db/init.sql:/docker-entrypoint-initdb.d/init.sql:ro`, runs an initialization script automatically the first time the database starts.

Together, these volumes give the container both persistence and automation. This allows every new developer or environment to spin up a pre-built database schema instantly.

The `healthcheck` tells Docker to test if the container is healthy by trying to connect to the database. If it fails too many times, Docker marks it as unhealthy. This adds another layer of reliability and prevents the app from starting before the database is ready.

The `ports` section helps avoid conflicts by mapping a container port to a host port on my computer.

Finally, the `volumes` section at the end ensures my database data survives across container restarts or recreations.

Overall, this YAML file is useful for local development, CI testing environments, self-hosting, and teaching or documentation purposes. It helps create a consistent, reliable, and production-like environment on any machine with a single command:
```
docker compose up -d
```
