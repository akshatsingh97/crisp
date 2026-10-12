Run `docker system prune -a --volumes` to remove all unused images, containers, networks, and volumes.

This command deletes data. It removes volumes that no container uses, and that data cannot be recovered. Back up any volume you need first.

**Prune only unused items**

1. Run `docker system prune -a --volumes`.
2. Type `y` when Docker asks you to confirm. Add `-f` to skip the prompt.

This removes:
- Stopped containers
- Networks that no container uses
- All images that no container uses (the `-a` flag)
- Volumes that no container uses (the `--volumes` flag)
- Build cache

Running containers and the images, volumes, and networks they use stay in place.

**Delete everything, including running containers**

1. Stop and remove all containers:
   ```
   docker stop $(docker ps -aq)
   docker rm -f $(docker ps -aq)
   ```
2. Remove all images:
   ```
   docker rmi -f $(docker images -aq)
   ```
3. Remove all volumes:
   ```
   docker volume rm $(docker volume ls -q)
   ```
4. Clear the build cache:
   ```
   docker builder prune -a -f
   ```

If a list is empty, the command prints a usage error. This is harmless, so skip that step.

**Check the result**

- Run `docker system df` to see disk use by type. Run it before and after to measure the space you freed.

**Troubleshooting**

- If a volume is in use, Docker refuses to remove it. Remove the container that uses it first.
- On Docker Desktop for Mac or Windows, the disk image file may not shrink after cleanup. Open Docker Desktop, go to Settings, then Resources, and reduce the disk image size, or use the Troubleshoot menu to clean up data.
- To keep volumes, leave out `--volumes` from the prune command.
