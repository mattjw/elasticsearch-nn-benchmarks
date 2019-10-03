from invoke import task


@task
def docker_compose(ctx):
    ctx.run("docker-compose up -d")
