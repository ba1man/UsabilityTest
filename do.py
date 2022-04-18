'''
This script aims to run automated usability test on selected dependency exraction tools.

This script depends on:
    Git (through environment)
    SciTools Understand (through environment path)
    Java >= 15 (through environment path)

This script has only been tested on Windows 10.
'''

import logging
from os import path, rename
import sys
import csv
import subprocess
import time
import argparse
from datetime import datetime
import re


def harmony_print(raw, source):
    try:
        print(raw.decode('utf-8'))
    except UnicodeDecodeError:
        logging.warning(
            f'Metting utf-8 decode error for understand in project {source}')
        print(raw)


def create_udb(lang, project_root, udb_path):
    if lang == 'cpp':
        ulang = 'C++'
    elif lang == 'java':
        ulang = 'Java'
    else:
        ulang = 'Python'

    try:
        output = subprocess.check_output(
            f'und create -db {udb_path} -languages {ulang}',
            shell=True)
        harmony_print(output, project_root)
        output = subprocess.check_output(
            f'und add -db {udb_path} {project_root} analyze -all', shell=True)
        harmony_print(output, project_root)
    except subprocess.CalledProcessError as e:
        logging.exception(f'Failed to create udb {e.output.decode("utf-8")}')


if __name__ == '__main__':
    timestamp = datetime.now().strftime("%y%m%d%H%M")

    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            logging.FileHandler(
                f'./logs/{timestamp}.log'),
            logging.StreamHandler()
        ]
    )

    # Usage
    parser = argparse.ArgumentParser()
    parser.add_argument('lang', help='Sepcify the target language')
    parser.add_argument('range', help='Specify the start line from csv file')
    parser.add_argument('only', help='Specify the only tool to run', nargs='?')
    args = parser.parse_args()

    lang = args.lang
    try:
        ['cpp', 'java', 'python'].index(lang)
    except:
        raise f'Invalid lang {lang}, only support cpp / java / python'

    range = args.range.split('-')
    if len(range) == 1:
        from_line = int(range[0])
        end_line = int(range[0])
    elif len(range) == 2:
        from_line = int(range[0])
        end_line = int(range[1])
    else:
        raise f'Invalid range format {args.range}, only support x or x-x'

    only = args.only.lower() if args.only is not None else ''
    try:
        ['clone', 'enre', 'depends', 'understand', ''].index(only)
    except:
        raise f'Invalid tool {only}, only support enre / depends / understand / clone'

    logging.info(
        f'Working on {from_line}-{end_line} for {lang} with {"all tools" if only == "" else f"{only} only"}')

    outfile_path = f'./records/{timestamp}-{lang}-{from_line}-{end_line}.csv'

    project_clone_url_list = dict()
    try:
        with open(f'./lists/{args.lang} project list final.csv', 'r', encoding='utf-8') as file:
            project_list = csv.reader(file)
            count = 0
            for row in project_list:
                if (count >= from_line) & (count <= end_line):
                    project_name = row[0].split("/")[-1]
                    # Some project's git url is in 3rd column, rather than 4th column,
                    # which is weird. (Encoding problem) This handles that situation.
                    if lang == 'cpp':
                        project_clone_url_list[project_name] = row[4] if row[4] != '' else row[3]
                    else:
                        project_clone_url_list[project_name] = row[3] if row[3] != '' else row[2]
                count += 1
    except EnvironmentError:
        logging.error(f'Can not find project list for {args.lang}')
        sys.exit()

    # Cloning (or reusing) repository from GitHub
    for project_name in project_clone_url_list.keys():
        expected = f'./repo/{project_name}'
        if not path.exists(expected):
            logging.info(f'Cloning \'{project_name}\'')
            fail_count = 0

            jump = False
            while not path.exists(expected):
                # Depth 1 for only current revison
                cmd = f'git clone --depth 1 {project_clone_url_list[project_name]} {expected}'
                proc = subprocess.Popen(
                    cmd, shell=True, stdout=subprocess.PIPE)
                while proc.poll() is None:
                    out = proc.stdout.readline().strip()
                    harmony_print(out, project_name)
                proc.kill()
                if not path.exists(expected):
                    logging.warning(
                        f'Failed cloning with return code {proc.poll()}, retry in 2 mins')
                    fail_count += 1
                    if fail_count < 4:
                        # If fails cloning, retry after cooldown
                        time.sleep(2*60)
                    else:
                        logging.fatal(
                            f'Unable to clone {project_clone_url_list[project_name]} after 3 tries, go to next')
                        jump = True
                        break
            if jump is True:
                continue
        else:
            logging.info(
                f'Reusing existed local repository for {project_name}')

        records = dict()

        # Obtain LoC (only when process all tools)
        if only == '':
            print('Counting line of code')
            LoC = 0
            cmd = f'.\\utils\\cloc-1.92.exe ./repo/{project_name} --csv --quiet'
            try:
                proc = subprocess.check_output(cmd, shell=True)
                outs = proc.strip().decode('utf-8').splitlines()
                for out in outs:
                    out = out.split(',')
                    if len(out) == 5:
                        if lang == 'java':
                            if out[1] == 'Java':
                                LoC += int(out[-1])
                        elif lang == 'cpp':
                            try:
                                ['C++', 'C/C++ Header'].index(out[1])
                                LoC += int(out[-1])
                            except:
                                pass
                        else:
                            if out[1] == 'Python':
                                LoC += int(out[-1])
                logging.info(f'LoC for {project_name} is {LoC}')
            except subprocess.CalledProcessError:
                logging.exception(
                    f'Failed couting line of code for project \'{project_name}\'')
            records['LoC'] = LoC
        else:
            records['LoC'] = 0

        # Run ENRE
        if only == 'enre' or only == '':
            print('Starting ENRE')
            if args.lang == 'java':
                cmd = f'java -jar {path.join(path.dirname(__file__), "./tools/enre/enre-java.jar")} java {path.join(path.dirname(__file__), "./repo")}/{project_name} {project_name}'
            elif args.lang == 'cpp':
                # FIXME: Change / to \ as a workaround for an ENRE-cpp issue regarding to path handling
                cmd = f'java -jar {path.abspath(path.join(path.dirname(__file__), "./tools/enre/enre-cpp.jar"))} cpp {path.abspath(path.join(path.dirname(__file__), "./repo"))}\{project_name} {project_name} {project_name}'
            else:
                cmd = f'{path.join(path.dirname(__file__), "./tools/enre/enre-python.exe")} {path.join(path.dirname(__file__), "./repo")}/{project_name}'
            time_start = time.time()
            # Let ENREs output in sandbox
            proc = subprocess.Popen(
                cmd, shell=True, stdout=subprocess.PIPE, cwd=f'./out/enre-{lang}')

            while proc.poll() is None:
                harmony_print(proc.stdout.readline().strip(), project_name)
            time_end = time.time()
            proc.kill()
            logging.info(
                f'Running ENRE-{args.lang} on {project_name} costs {time_end - time_start}')
            records['ENRE'] = time_end - time_start
        else:
            records['ENRE'] = 0

        if only == 'depends' or only == '':
            # Run Depends
            print('starting Depends')
            cmd = f'java -jar {path.join(path.dirname(__file__), "./tools/depends.jar")} {lang} {path.join(path.dirname(__file__), "./repo")}/{project_name} {project_name}'
            time_start = time.time()
            if lang == 'java':
                # Depends always save output at the cwd, so change cwd to ./out
                proc = subprocess.Popen(
                    cmd, shell=True, stdout=subprocess.PIPE, cwd='./out/depends')
            else:
                proc = subprocess.Popen(
                    cmd, shell=True, stdout=subprocess.PIPE)
            while proc.poll() is None:
                harmony_print(proc.stdout.readline().strip(), project_name)
            time_end = time.time()
            proc.kill()
            logging.info(
                f'Running Depends on {project_name} costs {time_end - time_start}')
            records['Depends'] = time_end - time_start
        else:
            records['Depends'] = 0

        if only == 'understand' or only == '':
            # Run Understand
            print('Starting Understand')
            time_start = time.time()
            create_udb(lang, f'./repo/{project_name}',
                       f'./out/understand/{project_name}.und')
            time_end = time.time()
            logging.info(
                f'Running Understand on {project_name} costs {time_end - time_start}')
            records["Understand"] = time_end - time_start
        else:
            records['Understand'] = 0

        # Instantly save time info whenever a project is finished analizing
        # to prevent from crashing.
        with open(f'{outfile_path}.pending', 'a+') as f:
            f.write(
                f'{project_name},{records["LoC"]},{records["ENRE"]},{records["Depends"]},{records["Understand"]}\n')

    try:
        # Remove `.pending` identifier to indicates to whole process succeeded
        # After the finishing of this script, if `.pending` still exists,
        # you might want to check out log files since it's a sign of some exception
        # has taken place.
        rename(f'{outfile_path}.pending', outfile_path)
    except:
        logging.error(f'Lost output file {outfile_path}!')

    logging.info('Run has completed')
