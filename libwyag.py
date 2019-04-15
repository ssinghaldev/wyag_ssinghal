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

class GitRepository:
    """ A git repository """
    worktree          = None
    gitdir            = None
    config_parser     = None

    def __init__(self, path, force=False):
        self.worktree = path
        self.gitdir   = os.path.join(path, '.git')

        if not (force or os.path.isdir(self.gitdir)):
            raise Exception("Not a Git repository %s" % path)
        
        #Read configuration file in .git/config
        self.config_parser = configparser.ConfigParser()
        config_file = repo_file(self, "config")

        if config_file and os.path.exists(config_file):
            self.config_parser.read([config_file])
        elif not force:
            raise Exception("Configuration file missing")
        
        if not force:
            version = int(self.config_parser.get("core", "repositoryformatversion"))
            if version != 0:
                raise Exception("Unsupported repositoryformatversion %s" % version")

def main(argv=sys.argv[1:]):
    arg_parser = argparse.ArgumentParser(description="My Git")

    arg_sub_parsers = arg_parser.add_subparsers(title="Commands", dest="command")
    arg_sub_parsers.required = True
    
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