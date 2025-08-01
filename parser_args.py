import argparse

def get_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--version", action="store_true")
    parser.add_argument("--help", action="store_true")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--daemon", action="store_true")
    parser.add_argument("--pid", action="store_true")
    parser.add_argument("--no-pid", action="store_true")
    parser.add_argument("--skip-trial-com-users", action="store_true")
    parser.add_argument("--email")
    parser.add_argument("--server")
    parser.add_argument("--user")
    return parser.parse_args()

def get_args_churn():
    parser = argparse.ArgumentParser(conflict_handler='resolve')
    parser.add_argument("-t", "--total",  action="store_true")
    parser.add_argument("-y", "--year",  action="store_true")
    parser.add_argument("-m", "--month",  action="store_true")
    parser.add_argument("-h", "--help",  action="store_true")
    parser.add_argument("-p", "--pid")
    parser.add_argument("-np", "--no-pid", action="store_true")
    parser.add_argument("-nu", "--verbose", action="store_true")
    return parser.parse_args()


def get_args_update_stat():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--total", action="store_true")
    parser.add_argument("--today", action="store_true")
    parser.add_argument("--yesterday", action="store_true")
    parser.add_argument("--no-pid", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--help", action="store_true")
    parser.add_argument("--date")
    parser.add_argument("--one-processor", dest='one_processor', type=str, help="Run one named process")
    parser.add_argument("--pid")
    return parser.parse_args()

