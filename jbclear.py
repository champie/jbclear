#!/usr/bin/env python
import glob
import os
import re
import argparse
import plistlib
import shutil
try:
    import send2trash_
    have_send2trash = True
except ImportError:
    send2trash = None
    have_send2trash = False

args = None


def should_remove(dir_to_check):
    if args.delete_all:
        return True
    if dir_to_check == args.logs_dir and not args.keep_logs:
        return True
    if dir_to_check == args.caches_dir and not args.keep_caches:
        return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version='%(prog)s 0.1')
    parser.add_argument('-a', '--apps-dir', action='store', default="~/Library/Application Support/JetBrains/Toolbox/apps",
                        help="Directory where apps are installed")
    parser.add_argument('-l', '--logs-dir', action='store', default="~/Library/Logs/JetBrains",
                        help="Directory where apps are installed")
    parser.add_argument('-c', '--caches-dir', action='store', default="~/Library/Caches/JetBrains",
                        help="Directory where apps are installed")
    parser.add_argument('-o', '--config-dir', action='store', default="~/Library/Application Support/JetBrains",
                        help="Directory where apps are installed")
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help="Don't do anything, just show what directories would be removed")
    parser.add_argument('--keep-logs', action='store_true', help="Don't remove log files for installed apps")
    parser.add_argument('--keep-caches', action='store_true', help="Don't remove cache files for installed apps")
    parser.add_argument('--delete-configs', action='store_true', help="Delete configs for installed apps")
    parser.add_argument('--delete-all', action='store_true', help="Delete all files, even for installed apps")
    if have_send2trash:
        parser.add_argument('-d', '--delete', action='store_true', help="Delete files directly, don't move them to trash")
    else:
        print("*** Your system does not have send2trash module so files will be completely deleted ***")
        print("If this is not OK, select N and then run 'pip install send2trash'")
        response = raw_input("\nProceed? (y/N)")
        if response is None or len(response) == 0 or response[0].upper() != "Y":
            exit(4)
    args = parser.parse_args()
    if not have_send2trash:
        args.delete = True
    installed_apps = []
    for dir_path, dir_names, files in os.walk(os.path.expanduser(args.apps_dir)):
        if re.match(".*/Contents", dir_path) and not re.match(".*/Contents/.*", dir_path):
            plist = plistlib.readPlist(dir_path + '/Info.plist')
            app_name = plist['CFBundleGetInfoString'].split(",")[0]
            app_name = re.sub(r"(JetBrains )*([A-Za-z]*) ([0-9]*)\.([0-9]*).*", r"\2\3.\4", app_name)
            installed_apps.append(app_name)
    if args.dry_run:
        print("*** Dry run only, full run would do the following: ***")
    if args.delete:
        print("  Delete:")
    else:
        print("  Trash:")
    for top_dir in [args.config_dir, args.caches_dir, args.logs_dir]:
        full_dir = os.path.expanduser(top_dir)
        for app_dir in glob.glob(full_dir + '/*202[0-9].[0-9]'):
            if should_remove(top_dir):
                print("    " + app_dir)
                if not args.dry_run:
                    if args.delete:
                        shutil.rmtree(app_dir)
                    else:
                        send2trash.send2trash(app_dir)
