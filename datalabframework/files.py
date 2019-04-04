import os
import sys

import re
import json
import requests

import ipykernel
from notebook.notebookapp import list_running_servers

_filename = None

def extract_filename(f):
    """
    Return the full path of the jupyter notebook.
    """

    # check provided filename (if exists)
    try:
        os.stat(f)
        return os.path.abspath(f)
    except:
        pass

    # fallback 1: interactive shell (ipynb notebook)
    try:
        kernel_filename = ipykernel.connect.get_connection_file()
        kernel_id = re.search('kernel-(.*).json', kernel_filename).group(1)

        for s in list_running_servers():
            url = requests.compat.urljoin(s['url'], 'api/sessions')
            params = {'token': s.get('token', '')}
            response = requests.get(url, params)
            for nn in json.loads(response.text):
                if nn['kernel']['id'] == kernel_id:
                    relative_path = nn['notebook']['path']
                    f = os.path.join(s['notebook_dir'], relative_path)
                    return os.path.abspath(f)
    except:
        pass

    # fallback 2: main file name (python files)
    filename = os.path.abspath(sys.argv[0]) if sys.argv[0] else None
    if filename:
        return filename

    # check if running an interactive ipython sessions
    try:
        __IPYTHON__
        return os.path.join(os.getcwd(), '<ipython-session>')
    except NameError:
        pass

    try:
        __DATALABFRAMEWORK__
        return os.path.join(os.getcwd(), '<datalabframework>')
    except NameError:
        pass

    # nothing found. Use <unknown>
    return os.path.join(os.getcwd(), '<unknown>')


def set_current_filename(f=None):
    global _filename
    _filename = extract_filename(f)

def get_current_filename():
    if _filename is None:
        set_current_filename()
        
    return _filename

def get_files(ext, rootdir, exclude_dirs=None, ignore_dir_with_file=''):
    if exclude_dirs is None:
        exclude_dirs = []

    lst = list()
    rootdir = os.path.abspath(rootdir)
    for root, dirs, files in os.walk(rootdir, topdown=True):
        for d in exclude_dirs:
            if d in dirs:
                dirs.remove(d)

        if ignore_dir_with_file in files:
            dirs[:] = []
            next
        else:
            for file in files:
                if file.endswith(ext):
                    path = os.path.join(root, file)
                    relative_path = os.path.relpath(path, rootdir)
                    lst.append(relative_path)

    return lst

def get_metadata_files(rootdir):
    return get_files('metadata.yml', rootdir, ignore_dir_with_file='metadata.ignore.yml')

def get_python_files(rootdir):
    return get_files('.py', rootdir)

def get_jupyter_notebook_files(rootdir):
    return get_files('.ipynb', rootdir, exclude_dirs=['.ipynb_checkpoints'])

def get_dotenv_file(rootdir):
    filepath = os.path.join(rootdir, '.env')
    
    if os.path.isfile(filepath):
        return filepath
    else:
        return filepath
