import mypy.api
import sys
import os


def run(*args: str) -> None:
    stdout, stderr, exit_code = mypy.api.run(list(args))
    if exit_code != 0:
        print("Failure on:", *args)
        print(stdout, stderr)
        sys.exit(exit_code)


run(__file__)
run("main.py")

for directory in os.listdir("plugins"):
    if os.path.isdir(os.path.join("plugins", directory)):
        for file in os.listdir(os.path.join("plugins", directory)):
            if not file.endswith(".py"):
                continue
            if file.startswith("_"):
                continue
            run("-m", "plugins.%s.%s" % (directory, file[:-3]))
