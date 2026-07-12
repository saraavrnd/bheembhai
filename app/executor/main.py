from app.core.daemon import run_keepalive_process


def main() -> None:
    run_keepalive_process("executor")
