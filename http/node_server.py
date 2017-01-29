#/usr/bin/python


import argparse
import contextlib
import errno
import os
import socket
import sys
import traceback
import urlparse
import xml.etree.cElementTree as ET

#C:\cygwin64\tmp>python -m http.node_server --bind-port 8070

from .common import constants
from .common import util
from .common import send_it
from .common import xml_func

DIRECTORY='./'


def parse_args():
    """Parse program argument."""


    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--bind-address',
        default='0.0.0.0',
        help='Bind address, default: %(default)s',
    )
    parser.add_argument(
        '--bind-port',
        default=constants.DEFAULT_HTTP_PORT,
        type=int,
        help='Bind port, default: %(default)s',
    )
    parser.add_argument(
        '--base',
        default='.',
        help='Base directory to search fils in, default: %(default)s',
    )
    args = parser.parse_args()
    args.base = os.path.normpath(os.path.realpath(args.base))
    return args
    
def check(args,s,rest) :
    req, rest = util.recv_line(s, rest)
    req_comps = req.split(' ', 2)
    if req_comps[2] != constants.HTTP_SIGNATURE:
        raise RuntimeError('Not HTTP protocol')
    if len(req_comps) != 3:
        raise RuntimeError('Incomplete HTTP protocol')

    method, uri, signature = req_comps
    if method != 'GET':
        raise RuntimeError(
            "HTTP unsupported method '%s'" % method
        )

    if not uri or uri[0] != '/':
        raise RuntimeError("Invalid URI")
    file_name = os.path.normpath(
        os.path.join(
            args.base,
            uri[1:],
        )
    )    
    return uri
    
def server():  
    args = parse_args()
    print('start')
    with contextlib.closing(
        socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
        )
    ) as sl:
        sl.bind((args.bind_address, args.bind_port))
        sl.listen(10)
        while True:
            s, addr = sl.accept()
            with contextlib.closing(s):
                status_sent = True
                try:
                    rest = bytearray()

                    uri=check(args,s,rest)
                    
                    
                    parse = urlparse.urlparse(uri)
                    param_temp = parse.query
                    param = urlparse.parse_qs(urlparse.urlparse(uri).query).values()
                    mem=mem_list()
                    normal_out=True
                    if uri[:8]=='/search?':
                        files,ids= find_name(mem,param[0][0])
                        output=xml_func.xml_form(files,ids)
                    elif uri[:15]=='/direct_search?':
                        files,ids= find_name(mem,param[0][0],True)
                        output=xml_func.xml_form(files,ids)
                    elif uri[:10]=='/get_file?':
                        normal_out=False
                        file_name = os.path.join(mem[int(param[0][0])]['root'],mem[int(param[0][0])]['filename'])
                        send_it.send_file(s,file_name)
                    else:
                        output=''

                    if normal_out:
                        send_it.send_xml(s,output)

                except IOError as e:
                    traceback.print_exc()
                    if not status_sent:
                        if e.errno == errno.ENOENT:
                            send_it.send_status(s, 404, 'File Not Found', e)
                        else:
                            send_it.send_status(s, 500, 'Internal Error', e)
                except Exception as e:
                    traceback.print_exc()
                    if not status_sent:
                        send_it.send_status(s, 500, 'Internal Error', e)
    
def mem_list():
    mem=[]
    for root, directories, filenames in os.walk(DIRECTORY):
        for filename in filenames: 
            mem.append({'root':root,'filename':filename})
    return mem
    
def find_name(mem,name,direct=False):
    files=[]
    ids=[]
    for i in range(len(mem)):
        if direct:
            if name == mem[i]['filename']:
                files.append(mem[i]['filename'])
                ids.append(i)
                break
        else:
            if name in mem[i]['filename']:
                files.append(mem[i]['filename'])
                ids.append(i)
    return files,ids

    
def main():
    server()
if __name__ == '__main__':
    main()




# vim: expandtab tabstop=4 shiftwidth=4 