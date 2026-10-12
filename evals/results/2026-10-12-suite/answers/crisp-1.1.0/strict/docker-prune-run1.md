Run `docker system prune -a --volumes` to remove all unused containers, images, networks, build cache, and volumes. This command cannot be undone, and it deletes data in volumes (for example, database files).

1. Run the command:

   ```
   docker system prune -a --volumes
   ```

   Docker asks you to confirm. Type `y`.

2. If you also want to remove running containers and every image and volume, run these commands:

   ```
   docker rm -f $(docker ps -aq)
   docker rmi -f $(docker images -aq)
   docker volume rm $(docker volume ls -q)
   ```

   Run them only if you are sure that you do not need any Docker data. The first command stops and deletes all containers.

3. Make sure that the space is free:

   ```
   docker system df
   ```

What the prune command removes:
- Stopped containers
- Images that no running container uses
- Networks that no container uses
- Build cache
- Volumes that no container uses

A running container keeps its image and its volumes. Add `-f` to the prune command to skip the confirmation.
