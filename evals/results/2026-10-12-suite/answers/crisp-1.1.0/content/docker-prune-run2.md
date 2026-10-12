Run `docker system prune -a --volumes`. It removes all unused images, stopped containers, unused networks, unused volumes, and the build cache.

Warning: this deletes data that you cannot recover. Volumes can hold databases and other persistent data. Check them first with `docker volume ls`.

To remove everything, including running containers, follow these steps:

1. Stop all containers:
   ```
   docker stop $(docker ps -aq)
   ```
2. Remove all containers:
   ```
   docker rm -f $(docker ps -aq)
   ```
3. Remove all images:
   ```
   docker rmi -f $(docker images -aq)
   ```
4. Remove all volumes:
   ```
   docker volume rm $(docker volume ls -q)
   ```
5. Run the prune command to clear the remaining networks and build cache:
   ```
   docker system prune -a --volumes -f
   ```

In Docker 23 and later, `docker system prune --volumes` removes only anonymous volumes (volumes without a name). Add `-a` to also remove named volumes that no container uses.

To check how much space you will free, run `docker system df`.
