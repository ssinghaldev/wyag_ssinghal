# This project we are writing our own git. 
# Basically I am just implementing this : https://wyag.thb.lt/
# Implementing is a 'big' word, just suplicating the above thing is more 
# accurate description. But I will not just copy-paste. I will type out the commands.
# I am confident I will learn a lot while doing this.

import argparse
import collections
import configparser
import hashlib
import os
import re
import sys
import zlib

arg_parser = argparse.ArgumentParser(description="My Git")
arg_sub_parsers = arg_parser.add_subparsers(title="Commands", dest="command")
arg_sub_parsers.required = True

def main(argv=sys.argv[1:]):
    args = arg_parser.parse_args(argv)

    if args.command == "add":
        cmd_add(args)
    elif args.command == "cat-file":
        cmd_cat_file(args)
    elif args.command == "checkout":
        cmd_checkout(args)
    elif args.command == "commit":
        cmd_commit(args)
    elif args.command == "hash-object":
        cmd_hash_object(args)
    elif args.command == "init":
        cmd_init(args)
    elif args.command == "log":
        cmd_log(args)
    elif args.command == "ls-tree":
        cmd_ls_tree(args)
    elif args.command == "merge":
        cmd_merge(args)
    elif args.command == "rebase":
        cmd_rebase(args)
    elif args.command == "rev-parse":
        cmd_rev_parse(args)
    elif args.command == "rm":
        cmd_rm(args)
    elif args.command == "show-ref":
        cmd_show_ref(args)
    elif args.command == "tag":
        cmd_tag(args)
    