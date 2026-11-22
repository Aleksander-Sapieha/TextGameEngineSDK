
import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

sys.path.insert(0, str(PROJECT_ROOT))

from TextGameEngineSDK.exporter.linux.builder import Builder


def main():
    parser = argparse.ArgumentParser(
        prog="sourcepack",
        description="Python project packager"
    )

    parser.add_argument("source", help="Project directory")
    parser.add_argument("--runtime", required=True)
    parser.add_argument("--entry", default="main.py")
    parser.add_argument("-o", "--output", default="dist")

    args = parser.parse_args()

    builder = Builder(
        source=args.source,
        runtime=args.runtime,
        output=args.output,
        entry=args.entry
    )

    builder.build()


if __name__ == "__main__":
    main()
