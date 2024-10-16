import argparse
import subprocess


def compile(args):
    encode_po2mo = f'"{args.msgfmt}" "{args.po}" -o "{args.mo}"'
    subprocess.run(encode_po2mo, shell=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-po", type=str)
    parser.add_argument("-mo", type=str)
    parser.add_argument("-msgfmt", type=str)
    args = parser.parse_args()
    compile(args)
