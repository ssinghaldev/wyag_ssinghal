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
                raise Exception("Unsupported repositoryformatversion %s" % version)


class GitObject(object):
    repo = None

    def __init__(self, repo, data=None):
        self.repo  = repo

        if data != None:
            self.deserialize(data)
    
    def serialize(self):
        """This function must be implemented by subclasses
           It must read the object's content from self.data a byte string,
           and do whatever it takes to convert it into  a meaningful reprentation.
           What exactly that means depends on each subclass"""
        raise Exception("Unimplemented")
    
    def deserialize(self):
        raise Exception("Unimplemented")



def repo_path(repo, *path):
    """Compute path under repo's gitdir"""
    return os.path.join(repo.gitdir, *path)

def repo_file(repo, *path, mkdir=False):
    """Same as repo_path but create dirname(*path) if absent"""
    if repo_dir(repo, *path[:-1], mkdir=mkdir):
        return repo_path(repo, *path)
    
def repo_dir(repo, *path, mkdir=False):
    """Same as repo_path, but mkdir *path if absent if mkdir"""
    path = repo_path(repo, *path)

    if os.path.exists(path):
        if os.path.isdir(path):
            return path
        else:
            raise Exception("Not a directory %s" % path)
    
    if mkdir:
        os.makedirs(path)
        return path
    else:
        return None

def repo_create(path):
    """Create a new repository at path"""
    repo = GitRepository(path, True)

    #First we make sure that path doesn't exist or is an empty dir
    if os.path.exists(repo.worktree):
        if not os.path.isdir(repo.worktree):
            raise Exception("%s is not a directory!" % path)
        if os.listdir(repo.worktree):
            raise Exception("%s is not empty!" % path)
    else:
        os.makedirs(repo.worktree)
    
    #Next create all important dirs
    assert(repo_dir(repo, "branches", mkdir=True))
    assert(repo_dir(repo, "objects", mkdir=True))
    assert(repo_dir(repo, "refs", "tags", mkdir=True))
    assert(repo_dir(repo, "refs", "heads", mkdir=True))

    #create all important files
    with open(repo_path(repo, "description", "w")) as f:
        f.write("Unnamed repository; edit this file 'description' to name the repository.\n")
    with open(repo_path(repo, "HEAD"), "w") as f:
        f.write("ref: refs/heads/master\n")
    with open(repo_path(repo, "config"), "w") as f:
        config = repo_default_config()
        config.write(f)

    return repo

def repo_default_config():
    ret = configparser.ConfigParser()

    ret.add_section("core")
    ret.set("core", "repositoryformatversion", "0")
    ret.set("core", "filemode", "false")
    ret.set("core", "bare", "false")

    return ret

def repo_find(path='.', required=True):
    path = os.path.realpath(path)

    if os.path.isdir(os.path.join(path, ".git")):
        return GitRepository(path)
    
    # recurse in parents as we didn't find in current dir
    parent = os.path.realpath(os.path.join(path, ".."))

    # base case when we reach root (/)
    if parent == path:
        if required:
            raise Exception("Not a git directory.")
        else:
            return None

    return repo_find(parent, required)

def object_read(repo, sha):
    """Read object object_id from git repository repo.
       Return a GitObject whose exact type depends on the object"""
    
    path = repo_file(repo, "objects", sha[0:2], sha[2:])

    with open(path, "rb") as f:
        raw = zlib.decompress(f.read())

        # Read object type
        x = raw.find(b' ')
        fmt = raw[0:x]

        #read and validate object size
        y = raw.find(b'\x00', x)
        size = int(raw[x:y].decode(ascii))
        if size != len(raw) - y - 1:
            raise Exception("Malformed object {0}: bad length".format(sha))
        
        if   fmt == b'commit' : c = GitCommit
        elif fmt == b'tree'   : c = GitTree
        elif fmt == b'tag'    : c = GitTag
        elif fmt == b'blob'   : c = GitBlob
        else:
            raise Exception("Unknown type %s for object %s".format(fmt.decode(ascii),sha))
        
        return c(repo, raw[y+1:])

def object_write(obj, actually_write=True):
    #Serialize object data
    data = obj.serialize()

    #Add header
    result = obj.fmt + b' ' + str(len(data)).encode() + b'\x00' + data
    
    #Compute hash
    sha = hashlib.sha1(result).hexdigest()

    if actually_write:
        #Compute path
        path = repo_file(obj.repo, "objects", sha[0:2],sha[2:], mkdir=actually_write)

        with open(path, 'wb') as f:
            f.write(zlib.compress(result))
        
    return sha

def object_find(repo, name, fmt=None, follow=True):
    return name

 def main(argv=sys.argv[1:]):
    arg_parser = argparse.ArgumentParser(description="My Git")

    arg_sub_parsers = arg_parser.add_subparsers(title="Commands", dest="command")
    arg_sub_parsers.required = True

    # adding all subparsers
    argsp = arg_sub_parsers.add_parser("init", help="Initialize a new, empty repository.")
    argsp.add_argument("path", metavar="directory", nargs="?", default=".", help="Where to create the repository.")

    
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

# All commands BRIDGE functions
def cmd_init(args):
    repo_create(args.path)
