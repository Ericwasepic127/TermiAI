#!/usr/bin/env python3
# Made by @Ericwasepic127

import os
from termilib import tools

def main():
    confirm = input("Are you sure you want to delete ALL TermiAI data? (y/n): ")
    if confirm.lower() != 'y':
        print("Aborted.")
        return
    for x in os.listdir(tools.DATA):
        os.remove(tools.JOIN(tools.DATA, x)) if os.path.isfile(tools.JOIN(tools.DATA, x)) else print("Directory in DATA folder named:", x)
    for x in os.listdir(tools.CONFIGS):
        os.remove(tools.JOIN(tools.CONFIGS, x)) if os.path.isfile(tools.JOIN(tools.CONFIGS, x)) else print("Directory in CONFIG folder named:", x)
    os.rmdir(tools.DATA) if not os.listdir(tools.DATA) else print("Directory inside DATA folder (look above)")
    os.rmdir(tools.CONFIGS) if not os.listdir(tools.CONFIGS) else print("Directory inside CONFIG folder (look above)")

if __name__ == '__main__':
    main()
