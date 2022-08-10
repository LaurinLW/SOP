import argparse
import docker
import os


def set_setting(key: str, value: str):
    cnf = read_settings()
    s = [g for g in cnf if g.startswith(key)]
    if len(s) > 0:
        cnf.remove(s[0])
    cnf.append(key + " = '" + value + "'")
    write_settings(cnf)


def read_settings():
    lines = []
    with open("./webserver/sop/settings.py") as fp:
        for i, line in enumerate(fp):
            lines.append(line.replace("\n", ""))
    return lines


def write_settings(lines):
    data = "\n".join(lines)
    with open("./webserver/sop/settings.py", "w") as fp:
        fp.write(data)


def setup_f(experimente):
    client = docker.from_env()

    print("Creating required docker networks and volumes...")
    try:
        nets = client.networks.list(names=["sop-network"])
        if len(nets) == 0:
            client.networks.create("sop-network")
    except:
        pass
    try:
        client.volumes.create("sop-datasets")
    except:
        pass
    try:
        client.volumes.create("sop-algorithms")
    except:
        pass
    try:
        client.volumes.create("sop-results")
    except:
        pass

    config_f(experimente)
    print("Creating web image...")
    client.images.build(path=".", dockerfile="Dockerfile_web", tag="sop-web")
    print("Creating experiment image...")
    client.images.build(
        path=".", dockerfile="Dockerfile_experiment", tag="sop-experiment"
    )


def config_f(experimente):
    print('Updating settings.py...')
    set_setting('SHARED_EXPERIMENT', experimente)


def start_f():
    cnf = read_settings()

    experiment_folder = [g for g in cnf if g.startswith("SHARED_EXPERIMENT")][0].split(
        " = "
    )[1][1:-1]
    settings_file = os.path.join(os.getcwd(), "webserver", "sop", "settings.py")
    client = docker.from_env()
    container_web = client.containers.create('sop-web', 
                                             name='sop-web',
                                             detach=True, 
                                             volumes=['/var/run/docker.sock:/var/run/docker.sock', 
                                                      experiment_folder + ':/sop/experimente',
                                                      'sop-datasets:/sop/sop/views/user_datasets',
                                                      'sop-algorithms:/sop/sop/views/user_algorithms',
                                                      'sop-results:/sop/sop/results',
                                                      settings_file + ':/sop/sop/settings.py'],
                                             ports={'8000/tcp': 8080},
                                             network='bridge')
    nets = client.networks.list(names=['sop-network'])
    if len(nets) != 1:
        print("Didn't find docket network sop-network")
        exit(1)
    sop_net = nets[0]
    sop_net.connect(container_web)
    print("Starting web container...")
    container_web.start()
    container_web.reload()
    set_setting(
        "RPC_PATH",
        "http://"
        + container_web.attrs["NetworkSettings"]["Networks"]["sop-network"]["IPAddress"]
        + ":8000/rpc",
    )
    container_web.restart()


def stop_f():
    client = docker.from_env()

    print("Stopping web container...")
    containers = client.containers.list(all=True)
    web_container = [c for c in containers if c.name == "sop-web"]
    for c in web_container:
        if c.status == "running":
            c.kill()
        c.remove()

    print("Stopping experiment containers...")
    exp_container = [c for c in containers if c.image == "sop-experiment"]
    for c in exp_container:
        c.kill()
        c.remove()

def iterate_f():
    client = docker.from_env()
    client.images.build(path=".", dockerfile="Dockerfile_web", tag="sop-web")
    stop_f()
    start_f()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script used to setup the sop project")
    subparsers = parser.add_subparsers(dest="command")
    setup = subparsers.add_parser(
        "setup", help="build the required docker images, networks and configure sop"
    )
    setup.add_argument(
        "-experimente", help="absolute path to the shared folder for the experiments"
    )
    config = subparsers.add_parser("config", help="setup the sop project")
    config.add_argument(
        "-experimente", help="absolute path to the shared folder for the experiments"
    )
    start = subparsers.add_parser("start", help="start the software")
    stop = subparsers.add_parser("stop", help="stop the project")
    iterate = subparsers.add_parser("iterate", help="command for fast debugging")

    args = parser.parse_args()

    if args.command == "setup":
        exp = None
        if args.experimente is None:
            exp = input("Enter the experimente folder: ")
        else:
            exp = args.experimente

        setup_f(exp)
    elif args.command == "config":
        exp = None
        if args.experimente is None:
            exp = input("Enter the experimente folder: ")
        else:
            exp = args.experimente

        config_f(exp)
    elif args.command == "start":
        start_f()
    elif args.command == "stop":
        stop_f()
    elif args.command == "iterate":
        iterate_f()
    else:
        print("Unknown command")
        parser.print_help()
        exit(1)
