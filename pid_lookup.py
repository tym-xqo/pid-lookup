#!/usr/bin/env python
# -*- coding: utf-8 -

# tym@benchprep.com 2019-07-25
""" Module to display activity stats for a given PID value
"""

import argparse
import os

# activate virtualenv for outer interpreter
activate_this = (
    f"{os.path.dirname(os.path.realpath(__file__))}/.venv/bin/activate_this.py"
)
exec(open(activate_this).read(), {"__file__": activate_this})

# virtualenv imports after activation
import psycopg2  # noqa E402
import yaml  # noqa E402
from dotenv import load_dotenv  # noqa E402
from psycopg2.extras import RealDictCursor  # noqa E402
from sshtunnel import SSHTunnelForwarder  # noqa E402

# load config from .env
load_dotenv(f"{os.path.dirname(os.path.realpath(__file__))}/.env")


def result(pid=0):
    """ Connect to database via ssh bastion & submit query with :pid parameter
    set to `pid` argument

    arg: `pid` integer
    returns: YAML string with selected  pg_stat_activity results
    """
    # TODO: Maybe don't hard-code username and key path
    with SSHTunnelForwarder(
        (os.getenv("BASTION_ADDR"), 22),
        ssh_username="deploy",
        ssh_pkey="~/.ssh/identity",
        ssh_private_key_password=os.getenv("PASSPHRASE"),
        remote_bind_address=(os.getenv("POSTGRES_ADDR"), 5432),
        local_bind_address=("0.0.0.0", 7532),
    ):
        db_url = os.getenv("DATABASE_URL")
        sql = (
            "select query_age::text"
            "     , xact_age::text"
            "     , pid"
            "     , application_name"
            "     , query"
            "     , query_start"
            "     , state"
            "     , wait_event_type"
            "     , wait_event"
            "  from pid_lookup(%s)"
        )

        conn = psycopg2.connect(db_url)
        db = conn.cursor(cursor_factory=RealDictCursor)

        # DBAPI expects SQL bind parameter values in a tuple,
        # even when there's only one.
        db.execute(sql, (pid,))
        dat = db.fetchone()
        conn.close()

        if not dat:
            return f"PID {pid} not found"
        return yaml.safe_dump(dict(dat))


if __name__ == "__main__":
    """ Get pid from command line arg, pass to result(), and print to stdout
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("pid")
    args = parser.parse_args()
    result = result(int(args.pid))
    print(result)
