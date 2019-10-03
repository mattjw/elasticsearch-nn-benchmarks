from invoke import task


@task(name="docker-env")
def docker_env(ctx):
    ctx.run("docker-compose up -d")
