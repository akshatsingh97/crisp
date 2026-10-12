Stop everything, then run one prune command:

```bash
docker stop $(docker ps -q)
docker system prune -a --volumes -f
```

This removes all stopped containers, all unused images, unused networks, the build cache, and unused volumes.

**Warning:** This cannot be undone. Volumes hold data such as databases. Back up anything you need first.

If volumes remain, run this too. Docker Engine 25 and later removes only anonymous volumes with `--volumes`:

```bash
docker volume prune -a -f
```

You can also remove each type by itself:

```bash
docker rm -f $(docker ps -aq)          # all containers
docker rmi -f $(docker images -aq)     # all images
docker volume rm $(docker volume ls -q)  # all volumes
```

If a list is empty, the command prints an error. This is harmless.

To see how much space you will free, run `docker system df` before and after.
