#!/usr/bin/env python3
"""Import existing analyzer CSVs and print SQL reports; no additional dependencies."""
import argparse
import json
import sqlite3
import sys

from src.data.sqlite_store import DEFAULT_DB, REPORTS, audit, import_csv, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', default=str(DEFAULT_DB))
    commands = parser.add_subparsers(dest='command', required=True)
    load = commands.add_parser('import')
    load.add_argument('csv')
    load.add_argument('--observed-on', required=True, help='Date the input snapshot represents, YYYY-MM-DD')
    load.add_argument('--source-kind', choices=['user-provided', 'synthetic'], default='user-provided')
    load.add_argument('--skip-invalid', action='store_true', help='Explicitly permit partial imports')
    query = commands.add_parser('report')
    query.add_argument('name', choices=sorted(REPORTS))
    query.add_argument('--observed-on')
    query.add_argument('--zip-code', default='')
    query.add_argument('--min-score', type=float, default=0)
    query.add_argument('--max-price', type=float)
    commands.add_parser('audit')
    args = parser.parse_args()
    try:
        if args.command == 'import':
            result = import_csv(args.csv, args.db, args.observed_on, args.source_kind, args.skip_invalid)
        elif args.command == 'audit':
            result = audit(args.db)
        else:
            result = report(args.name, args.db, observed_on=args.observed_on, zip_code=args.zip_code,
                            min_score=args.min_score, max_price=args.max_price)
        print(json.dumps(result, indent=2, allow_nan=False))
        return 2 if isinstance(result, dict) and result.get('status') == 'rejected' else 0
    except (OSError, ValueError, sqlite3.Error) as exc:
        print('Error: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
