#!/usr/bin/env python
# -*- coding: utf-8 -
import argparse
import os

activate_this = (
    f"{os.path.dirname(os.path.realpath(__file__))}/.venv/bin/activate_this.py"
)
exec(open(activate_this).read(), {"__file__": activate_this})

import psycopg2  # noqa E402
import yaml  # noqa E402
from dotenv import load_dotenv  # noqa E402
from psycopg2.extras import RealDictCursor  # noqa E402
from sshtunnel import SSHTunnelForwarder  # noqa E402


load_dotenv(f"{os.path.dirname(os.path.realpath(__file__))}/.env")


def result(pid=0):
    with SSHTunnelForwarder(
        (os.getenv("BASTION_ADDR"), 22),
        remote_bind_address=(os.getenv("POSTGRES_ADDR"), 5432),
        ssh_pkey="~/.ssh/identity",
        ssh_private_key_password=os.getenv("PASSPHRASE"),
        ssh_username="deploy",
        local_bind_address=("0.0.0.0", 7532),
    ) as tunnel:  # noqa F841
        db_url = os.getenv("DATABASE_URL")
        conn = psycopg2.connect(db_url)
        db = conn.cursor(cursor_factory=RealDictCursor)
        # db = _db()
        sql = (
            "select extract(epoch from query_age) as query_age_secs"
            "     , extract(epoch from xact_age) as xact_age_secs"
            "     , pid"
            "     , application_name"
            "     , query"
            "     , query_start"
            "     , state"
            "     , wait_event_type"
            "     , wait_event"
            "  from pid_lookup(%s)"
        )
        db.execute(sql, (pid,))
        dat = db.fetchone()
        conn.close()
        if not dat:
            return f"PID {pid} not found"
        return yaml.safe_dump(dict(dat))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pid")
    args = parser.parse_args()
    result = result(int(args.pid))
    print(result)
