import os
import shutil
import argparse


def remove(args):
    if os.path.exists(args.file):
        with open(args.file, "r", encoding="utf-8") as f:
            lang_data = f.read()
            lang_data = lang_data.replace(args.data, "")
        with open(args.file, "w", encoding="utf-8") as f:
            f.writelines(lang_data)

    mo_floder = os.path.dirname(args.mo_floder)
    if os.path.exists(mo_floder):
        shutil.rmtree(mo_floder)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-file", type=str)
    parser.add_argument("-data", type=str)
    parser.add_argument("-mo_floder", type=str)
    args = parser.parse_args()
    remove(args)
