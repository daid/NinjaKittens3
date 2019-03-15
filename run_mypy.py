import mypy.api
import sys
import os


global_exit_code = 0


def run(*args: str) -> None:
    global global_exit_code
    stdout, stderr, exit_code = mypy.api.run(list(args))
    if exit_code != 0:
        print("Failure on:", *args)
        print(stdout, stderr)
        global_exit_code = exit_code


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

sys.exit(global_exit_code)
