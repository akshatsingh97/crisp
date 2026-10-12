Run `docker system prune -a --volumes` to remove all unused images, containers, networks, and volumes. This command deletes data and cannot be undone. Check what you need first.

"Unused" means not used by a running container. Stop containers first if you want to remove everything.

**Remove everything, including running containers**

1. Stop all containers:
   ```
   docker stop $(docker ps -aq)
   ```
2. Remove all containers:
   ```
   docker rm $(docker ps -aq)
   ```
3. Remove all images:
   ```
   docker rmi -f $(docker images -aq)
   ```
4. Remove all volumes. This deletes database data and other stored files:
   ```
   docker volume rm $(docker volume ls -q)
   ```
5. Remove unused networks and build cache:
   ```
   docker network prune -f
   docker builder prune -a -f
   ```

**Remove only what is unused**

```
docker system prune -a --volumes
```

Docker asks for confirmation. Add `-f` to skip the prompt.

Notes:
- In Docker 23 and later, `docker system prune` skips named volumes unless you add `--volumes`. Anonymous volumes are pruned by default in Docker 25 and later with `--volumes`.
- If a command prints "requires at least 1 argument", nothing of that type exists. This is safe to ignore.
- Run `docker system df` before and after to see the space freed.
- On Docker Desktop for Mac or Windows, the disk image file does not always shrink after cleanup. Use the Docker Desktop "Clean / Purge data" option or reduce the disk image size in Settings.
- To keep some items, use filters, for example `docker image prune -a --filter "until=168h"` removes images older than 7 days.
