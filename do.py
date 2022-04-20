'''
This script aims to run automated usability test on selected dependency exraction tools.

This script depends on:
    Git (through environment)
    SciTools Understand (through environment path)
    Java >= 15 (through environment path)

This script has only been tested on Windows 10.
'''

import re
import io
import logging
from os import path, rename
import sys
import csv
import subprocess
import time
import argparse
from datetime import datetime
from threading import Timer


def harmony_print(raw, source):
    try:
        decode = raw.decode('utf-8')
        print(decode)
        return decode
    except UnicodeDecodeError:
        logging.warning(
            f'Metting utf-8 decode error for understand in project {source}')
        print(raw)
        return ''


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
    parser.add_argument('-t',
                        '--timeout',
                        help='Specify the maximum duration of a single process',
                        type=int)
    args = parser.parse_args()

    lang = args.lang
    try:
        ['cpp', 'java', 'python'].index(lang)
    except:
        raise ValueError(
            f'Invalid lang {lang}, only support cpp / java / python')

    range = args.range.split('-')
    if len(range) == 1:
        from_line = int(range[0])
        end_line = int(range[0])
    elif len(range) == 2:
        from_line = int(range[0])
        end_line = int(range[1])
    else:
        raise ValueError(
            f'Invalid range format {args.range}, only support x or x-x')

    only = args.only.lower() if args.only is not None else ''
    try:
        ['clone', 'loc', 'enre', 'depends', 'understand', ''].index(only)
    except:
        raise ValueError(
            f'Invalid tool {only}, only support enre / depends / understand / clone / loc')

    # Feature set
    timeout = args.timeout  # None, or positive int
    if timeout is not None:
        if timeout < 0 or timeout > 3600:
            raise ValueError(
                f'Invalid timeout value {timeout}, only range(300, 3600) are valid')

    logging.info(
        f'Working on {from_line}-{end_line} for {lang} with {"all tools" if only == "" else f"{only} only"}{f" and timeout limit to {timeout}" if timeout is not None else ""}')

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
        repo_path = f'./repo/{project_name}'
        abs_repo_path = path.join(path.dirname(__file__), repo_path)
        if not path.exists(repo_path):
            logging.info(f'Cloning \'{project_name}\'')
            fail_count = 0

            jump = False
            while not path.exists(repo_path):
                # Depth 1 for only current revison
                cmd = f'git clone --depth 1 {project_clone_url_list[project_name]} {repo_path}'

                proc = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                for line in io.TextIOWrapper(proc.stdout):
                    print(line, end='')

                if not path.exists(repo_path):
                    logging.warning(
                        f'Failed cloning with return code {proc.poll()}, retry in 2 mins')
                    fail_count += 1
                    if fail_count < 4:
                        # If fails cloning, retry after cooldown
                        time.sleep(2*60)
                        continue
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
        if only == 'loc' or only == '':
            print('Counting line of code')
            LoC = 0
            cmd = f'.\\utils\\cloc-1.92.exe {repo_path} --csv --quiet'
            try:
                # A fixed timeout threshold
                proc = subprocess.check_output(
                    cmd, timeout=2)
            except subprocess.TimeoutExpired:
                logging.exception(
                    f'Counting LoC for {project_name} timed out')
                records['LoC'] = -1
            except subprocess.CalledProcessError:
                logging.exception(
                    f'Failed couting line of code for {project_name}')
                records['LoC'] = -1
            else:
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
            records['LoC'] = LoC
        else:
            records['LoC'] = 0

        # Run ENRE
        if only == 'enre' or only == '':
            print('Starting ENRE')
            if args.lang == 'java':
                cmd = f'java -jar {path.join(path.dirname(__file__), "./tools/enre/enre-java.jar")} java {abs_repo_path} {project_name}'
            elif args.lang == 'cpp':
                cmd = f'java -jar {path.join(path.dirname(__file__), "./tools/enre/enre-cpp.jar")} cpp {abs_repo_path} {project_name} {project_name}'
            else:
                cmd = f'{path.join(path.dirname(__file__), "./tools/enre/enre-python.exe")} {abs_repo_path}'

            time_start = time.time()
            proc = subprocess.Popen(
                cmd,
                # Do not use shell, which will create shell->jvm, a sub-subprocess, which
                # won't be killed just by calling shell's `.kill()`; whereas,
                # without shell, the jvm subprocess is directly returned, which can be killed then.
                # shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=f'./out/enre-{lang}')

            killed = False
            if timeout is not None:
                def handle_timeout():
                    global killed
                    killed = True
                    proc.kill()
                    logging.warning(
                        f'Running ENRE-{lang} on {project_name} timed out')
                    records['ENRE'] = -1

                timer = Timer(timeout, handle_timeout)
                timer.start()

            for line in io.TextIOWrapper(proc.stdout):
                print(line, end='')
            time_end = time.time()

            if not killed:
                records['ENRE'] = time_end - time_start
                logging.info(
                    f'Running ENRE-{lang} on {project_name} costs {records["ENRE"]}')
        else:
            records['ENRE'] = 0

        if only == 'depends' or only == '':
            # Run Depends
            print('starting Depends')
            cmd = f'java -jar {path.join(path.dirname(__file__), "./tools/depends.jar")} {lang} {abs_repo_path} {project_name}'

            time_start = time.time()
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd='./out/depends')

            killed = False
            if timeout is not None:
                def handle_timeout():
                    global killed
                    killed = True
                    proc.kill()
                    logging.warning(
                        f'Running Depends on {project_name} timed out')
                    records['Depends'] = -1

                timer = Timer(timeout, handle_timeout)
                timer.start()

            for line in io.TextIOWrapper(proc.stdout):
                print(line, end='')
            time_end = time.time()

            if not killed:
                records['Depends'] = time_end - time_start
                logging.info(
                    f'Running Depends on {project_name} costs {records["Depends"]}')
        else:
            records['Depends'] = 0

        if only == 'understand' or only == '':
            # Run Understand
            print('Starting Understand')
            upath = f'./out/understand/{project_name}.und'
            if lang == 'cpp':
                ulang = 'C++'
            elif lang == 'java':
                ulang = 'Java'
            else:
                ulang = 'Python'
            cmd = f'und create -db {upath} -languages {ulang} add {abs_repo_path} analyze -all'

            time_start = time.time()
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd='./out/understand')

            killed = False
            if timeout is not None:
                def handle_timeout():
                    global killed
                    killed = True
                    proc.kill()
                    logging.warning(
                        f'Running Understand on {project_name} timed out')
                    records['Understand'] = -1

                timer = Timer(timeout, handle_timeout)
                timer.start()

            for line in io.TextIOWrapper(proc.stdout):
                print(line, end='')
            time_end = time.time()

            if not killed:
                records['Understand'] = time_end - time_start
                logging.info(
                    f'Running Understand on {project_name} costs {records["Understand"]}')
        else:
            records['Understand'] = 0

        # Instantly save duration info whenever a project is finished analizing
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
