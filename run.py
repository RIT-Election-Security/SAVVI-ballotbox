from app import app


def runserver(host_address: str="0.0.0.0", port: int=5001, debug: bool=False, key:str=None, cert:str=None):
    """
    Run the ballotbox application server.

    Args:
        host_address: address to bind to
        port: port number to bind to
        debug: toggle debug mode    
    """
    if (key or cert) and not key or not cert:
        print("Both cert and key required if one presented")
        exit(1)
    
    app.run(debug=debug, port=port, host=host_address, keyfile=key, certfile=cert)


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest="action", help="Available actions")

    runserver_parser = subparsers.add_parser("runserver", help="Run the application")
    runserver_parser.add_argument("-debug", action="store_true", help="Run app in debug mode")
    runserver_parser.add_argument("-a", "--addr", type=str, default="0.0.0.0", help="Host to bind app to")
    runserver_parser.add_argument("-p", "--port", type=int, default=5001, help="Port to bind app to")
    runserver_parser.add_argument("-key", type=str, help="Path to TLS key file")
    runserver_parser.add_argument("-cert", type=str, help="Path to TLS certificate file")

    args = parser.parse_args()

    if args.action == "runserver":
        runserver(host_address=args.addr, port=args.port, debug=args.debug, key=args.key, cert=args.cert)
