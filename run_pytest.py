#!/usr/bin/env python3

"""
    Helper to start pytest with arguments
"""
import subprocess
import sys

print("sys.real_prefix:", getattr(sys, "real_prefix", "-"))
print("sys.prefix:", sys.prefix)

if __name__ == "__main__":
    # sys.stderr = sys.stdout #
    args = sys.argv
    args[0] = "pytest"
    print("_"*79)
    print(" ".join(args))
    returncode = subprocess.call(args)
    sys.exit(returncode)
