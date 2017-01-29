# -*- coding: utf-8 -*-

import tempfile
import argparse
import contextlib
import errno
import os
import socket
import sys
import traceback
import urlparse
import xml.etree.cElementTree as ET

#C:\cygwin64\tmp>python -m http.front_server --url http://localhost:8070/\ --bind-port 8080 --node-port 8070

from .common import constants
from .common import util
from .common import send_it
from .common import xml_func

HTML_SEARCH='search_form.html'
URI_SEARCH='/search?Search='
URI_ID='/get_file?id='
  

def parse_args():
    """Parse program argument."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--base',
        default='.',
        help='Base directory to search fils in, default: %(default)s',
    )
    parser.add_argument(
        '--bind-address',
        default='0.0.0.0',
        help='Bind address, default: %(default)s',
    )
    parser.add_argument(
        '--bind-port',
        default=0,
        type=int,
        help='Bind port, default: %(default)s',
    )
    parser.add_argument(
        '--node-port',
        default=0,
        type=int,
        help='Bind port, default: %(default)s',
    )
    parser.add_argument(
        '--url',
        required=True,
        help='URL to use',
    )
    return parser.parse_args()

def check(args,s,rest) :
    #check http ask
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
                    
                    if uri[:15]==URI_SEARCH:
                        if len(uri) != len(URI_SEARCH):
                            output=client(URI_SEARCH,param[0][0],True) 
                    elif uri[:11]=='/view_file?':
                        output=client(URI_ID,param[0][0],False)
                    elif uri[:15]=='/download_file?':
                        output=client(URI_ID,param[0][0],False)
                        send_it.download(s,output)
                        
                    elif uri[:6]=='/form?':                
                        send_it.send_file(s,HTML_SEARCH)       
                       
                    else :
                        output =''
                    send_it.send(s,output)

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


                        
def client(uri_beg,search,xml_status):
    args = parse_args()
    url = util.spliturl(args.url)
    if url.scheme != 'http':
        raise RuntimeError("Invalid URL scheme '%s'" % url.scheme)

    with contextlib.closing(
        socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
        )
    ) as s:
        s.connect((
            url.hostname,
            url.port if url.port else constants.DEFAULT_HTTP_PORT,
        ))
        uri=uri_beg+search
        util.send_all(
            s,
            (
                (
                    'GET %s HTTP/1.1\r\n'
                    'Host: %s\r\n'
                    '\r\n'
                ) % (
                    uri,
                    args.url+uri,
                )
            ).encode('utf-8'),
        )

        rest = bytearray()

        #
        # Parse status line
        #
        status, rest = util.recv_line(s, rest)
        status_comps = status.split(' ', 2)
        if status_comps[0] != constants.HTTP_SIGNATURE:
            raise RuntimeError('Not HTTP protocol')
        if len(status_comps) != 3:
            raise RuntimeError('Incomplete HTTP protocol')

        signature, code, message = status_comps
        if code != '200':
            raise RuntimeError('HTTP failure %s: %s' % (code, message))

        #
        # Parse headers
        #
        content_length = None
        for i in range(constants.MAX_NUMBER_OF_HEADERS):
            line, rest = util.recv_line(s, rest)
            if not line:
                break

            name, value = util.parse_header(line)
            if name == 'Content-Length':
                content_length = int(value)
        else:
            raise RuntimeError('Too many headers')

        try:
            if content_length is None:

                buf=''
                while True:
                    buf += s.recv(constants.BLOCK_SIZE)
                    if not buf:
                        break
                if xml_status:
                    output=xml_func.xml_to_html(buf)
                else:
                    output=buf
                return output
            else:
                buff=''
                
                left_to_read = content_length
                while left_to_read > 0:
                    if not rest:
                        t = s.recv(constants.BLOCK_SIZE)
                        if not t:
                            raise RuntimeError(
                                'Disconnected while waiting for content'
                            )
                        rest += t
                    buf, rest = rest[:left_to_read], rest[left_to_read:]
                    buff+=buf
                    left_to_read -= len(buf)
                if xml_status:
                    output=xml_func.xml_to_html(buff)
                else:
                    output=buff
                
                return output

            # Commit
            name = None
        finally:
            if name is not None:
                try:
                    os.remove(name)
                except Exception:
                    print("Cannot remove temp file '%s'" % name)

    
def main():
    server()

if __name__ == '__main__':
    main()


# vim: expandtab tabstop=4 shiftwidth=4
