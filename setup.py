import argparse
import docker


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


def setup_f(rpc, experimente):
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

    config_f(rpc, experimente)
    print("Creating web image...")
    client.images.build(path=".", dockerfile="Dockerfile_web", tag="sop-web")
    print("Creating experiment image...")
    client.images.build(
        path=".", dockerfile="Dockerfile_experiment", tag="sop-experiment"
    )


def config_f(rpc, experimente):
    cnf = read_settings()
    experiment_folder = [k for k in cnf if k.startswith("SHARED_EXPERIMENT")]
    if len(experiment_folder) > 0:
        cnf.remove(experiment_folder[0])

    rpc_path = [k for k in cnf if k.startswith("RPC_PATH")]
    if len(rpc_path) > 0:
        cnf.remove(rpc_path[0])
    print("Updating settings.py...")
    cnf.append("SHARED_EXPERIMENT = '" + experimente + "'")
    cnf.append("RPC_PATH = '" + rpc + "'")
    write_settings(cnf)


def start_f():
    cnf = read_settings()

    experiment_folder = [k for k in cnf if k.startswith("SHARED_EXPERIMENT")][0].split(
        " = "
    )[1][1:-2]
    print(experiment_folder)
    client = docker.from_env()
    container_web = client.containers.create(
        "sop-web",
        name="sop-web",
        detach=True,
        volumes=[
            "/var/run/docker.sock:/var/run/docker.sock",
            experiment_folder + ":/sop/sop/experimente",
            "sop-datasets:/sop/sop/views/user_datasets",
            "sop-algorithms:/sop/sop/views/user_algorithms",
        ],
        ports={"8000/tcp": 8080},
    )
    nets = client.networks.list(names=["sop-network"])
    if len(nets) != 1:
        print("Didn't find docket network sop-network")
        exit(1)
    sop_net = nets[0]
    sop_net.connect(container_web)
    print("Starting container...")
    container_web.start()


def stop_f():
    client = docker.from_env()

    containers = client.containers.list()
    web_container = [c for c in containers if c.name == "sop-web"]
    for c in web_container:
        c.kill()

    exp_container = [c for c in containers if c.image == "sop-experiment"]
    for c in exp_container:
        c.kill()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script used to setup the sop project")
    subparsers = parser.add_subparsers(dest="command")
    setup = subparsers.add_parser(
        "setup", help="build the required docker images, networks and configure sop"
    )
    setup.add_argument("-rpc", help="the rpc url for the experiments")
    setup.add_argument(
        "-experimente", help="absolute path to the shared folder for the experiments"
    )
    config = subparsers.add_parser("config", help="setup the sop project")
    config.add_argument("-rpc", help="the rpc url for the experiments")
    config.add_argument(
        "-experimente", help="absolute path to the shared folder for the experiments"
    )
    start = subparsers.add_parser("start", help="start the software")
    stop = subparsers.add_parser("stop", help="stop the project")

    args = parser.parse_args()

    if args.command == "setup":
        rpc = None
        if args.rpc is None:
            rpc = input("Enter the rpc url: ")
        else:
            rpc = args.rpc

        exp = None
        if args.experimente is None:
            exp = input("Enter the experimente folder: ")
        else:
            exp = args.experimente

        setup_f(rpc, exp)
    elif args.command == "config":
        rpc = None
        if args.rpc is None:
            rpc = input("Enter the rpc url: ")
        else:
            rpc = args.rpc

        exp = None
        if args.experimente is None:
            exp = input("Enter the experimente folder: ")
        else:
            exp = args.experimente

        config_f(rpc, exp)
    elif args.command == "start":
        start_f()
    elif args.command == "stop":
        stop_f()
    else:
        print("Unknown command")
        parser.print_help()
        exit(1)
