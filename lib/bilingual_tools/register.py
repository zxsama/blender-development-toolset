import os
import argparse


def register(args):
    with open(args.file, "a+", encoding="utf-8") as f:
        lang_data = f.read()
        if not (args.data in lang_data):
            f.write(args.data)

    if not os.path.exists(args.mo_floder):
        os.makedirs(args.mo_floder)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-file", type=str)
    parser.add_argument("-data", type=str)
    parser.add_argument("-mo_floder", type=str)
    args = parser.parse_args()
    register(args)
