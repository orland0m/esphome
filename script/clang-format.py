#!/usr/bin/env python

from __future__ import print_function

import multiprocessing
import os
import re
import subprocess
import sys

import argparse
import click
import threading

is_py2 = sys.version[0] == '2'

if is_py2:
    import Queue as queue
else:
    import queue as queue

root_path = os.path.abspath(os.path.normpath(os.path.join(__file__, '..', '..')))
basepath = os.path.join(root_path, 'esphome')
rel_basepath = os.path.relpath(basepath, os.getcwd())


def run_format(args, queue, lock):
    """Takes filenames out of queue and runs clang-tidy on them."""
    while True:
        path = queue.get()
        invocation = ['clang-format-7']
        if args.inplace:
            invocation.append('-i')
        invocation.append(path)

        proc = subprocess.Popen(invocation, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        output, err = proc.communicate()
        with lock:
            if proc.returncode != 0:
                print(' '.join(invocation))
                print(output.decode('utf-8'))
                print(err.decode('utf-8'))
        queue.task_done()


def progress_bar_show(value):
    if value is None:
        return ''
    return value


def walk_files(path):
    for root, _, files in os.walk(path):
        for name in files:
            yield os.path.join(root, name)


def get_output(*args):
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = proc.communicate()
    return output.decode('utf-8')


def splitlines_no_ends(string):
    return [s.strip() for s in string.splitlines()]


def filter_changed(files):
    for remote in ('upstream', 'origin'):
        command = ['git', 'merge-base', '{}/dev'.format(remote), 'HEAD']
        try:
            merge_base = splitlines_no_ends(get_output(*command))[0]
            break
        except:
            pass
    else:
        return files
    command = ['git', 'diff', merge_base, '--name-only']
    changed = splitlines_no_ends(get_output(*command))
    changed = {os.path.relpath(f, os.getcwd()) for f in changed}
    print("Changed Files:")
    files = [p for p in files if p in changed]
    for p in files:
        print("  {}".format(p))
    if not files:
        print("  No changed files")
    return files


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-j', '--jobs', type=int,
                        default=multiprocessing.cpu_count(),
                        help='number of tidy instances to be run in parallel.')
    parser.add_argument('files', nargs='*', default=[],
                        help='files to be processed (regex on path)')
    parser.add_argument('-i', '--inplace', action='store_true',
                        help='apply fix-its')
    parser.add_argument('-q', '--quiet', action='store_false',
                        help='Run clang-tidy in quiet mode')
    parser.add_argument('-c', '--changed', action='store_true',
                        help='Only run on changed files')
    args = parser.parse_args()

    try:
        get_output('clang-format-7', '-version')
    except:
        print("""
        Oops. It looks like clang-format is not installed. 
        
        Please check you can run "clang-format-7 -version" in your terminal and install
        clang-format (v7) if necessary.
        
        Note you can also upload your code as a pull request on GitHub and see the CI check
        output to apply clang-format.
        """)
        return 1

    files = []
    for path in walk_files(basepath):
        filetypes = ('.cpp', '.h', '.tcc')
        ext = os.path.splitext(path)[1]
        if ext in filetypes:
            path = os.path.relpath(path, os.getcwd())
            files.append(path)
    # Match against re
    file_name_re = re.compile('|'.join(args.files))
    files = [p for p in files if file_name_re.search(p)]

    if args.changed:
        files = filter_changed(files)

    files.sort()

    return_code = 0
    try:
        task_queue = queue.Queue(args.jobs)
        lock = threading.Lock()
        for _ in range(args.jobs):
            t = threading.Thread(target=run_format,
                                 args=(args, task_queue, lock))
            t.daemon = True
            t.start()

        # Fill the queue with files.
        with click.progressbar(files, width=30, file=sys.stderr,
                               item_show_func=progress_bar_show) as bar:
            for name in bar:
                task_queue.put(name)

        # Wait for all threads to be done.
        task_queue.join()

    except KeyboardInterrupt:
        print()
        print('Ctrl-C detected, goodbye.')
        os.kill(0, 9)

    sys.exit(return_code)


if __name__ == '__main__':
    main()
