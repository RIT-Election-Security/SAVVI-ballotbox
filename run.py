from app import app


def runserver(host_address: str="0.0.0.0", port: int=5001, debug: bool=False):
    """
    Run the ballotbox application server.

    Args:
        host_address: address to bind to
        port: port number to bind to
        debug: toggle debug mode    
    """
    app.run(debug=debug, port=port, host=host_address)


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest="action", help="Available actions")

    runserver_parser = subparsers.add_parser("runserver", help="Run the application")
    runserver_parser.add_argument("-debug", action="store_true", help="Run app in debug mode")
    runserver_parser.add_argument("-a", "--addr", type=str, default="0.0.0.0", help="Host to bind app to")
    runserver_parser.add_argument("-p", "--port", type=int, default=5001, help="Port to bind app to")

    args = parser.parse_args()

    if args.action == "runserver":
        runserver(host_address=args.addr, port=args.port, debug=args.debug)
