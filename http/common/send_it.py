# -*- coding: utf-8 -*-

import os

# MIME_MAPPING = {
    # 'html': 'text/html',
    # 'xml': 'text/xml',
    # 'png': 'image/png',
    # 'txt': 'text/plain',
# }

from . import constants
from . import util

def download(s,output):
    util.send_all(
    s,
    (
        (
            '%s 200 OK\r\n'
            'Content-Length: %s\r\n'
            'Content-Type: %s\r\n'
            'Content-Disposition: attachment; filename=b.txt;'
            '\r\n'
        ) % (
            constants.HTTP_SIGNATURE,
            len(output),
            constants.MIME_MAPPING.get('html'),
        )
    ).encode('utf-8')

    )


    #
    # Send content
    #
    util.send_all(s,output)
    
def send_file(s,file_name):

    with open(file_name, 'rb') as f:

        util.send_all(
            s,
            (
                (
                    '%s 200 OK\r\n'
                    'Content-Length: %s\r\n'
                    'Content-Type: %s\r\n'
                    '\r\n'
                ) % (
                    constants.HTTP_SIGNATURE,
                    os.fstat(f.fileno()).st_size,
                    constants.MIME_MAPPING.get(
                        os.path.splitext(
                            file_name
                        )[1].lstrip('.'),
                        'application/octet-stream',
                    ),
                )
            ).encode('utf-8')
        )


    #
    # Send content
    #
        buf=''
        while True:
            buf += f.read(constants.BLOCK_SIZE)
            if not buf:
                break
            util.send_all(s, buf)
            
def send(s,output):
    util.send_all(
    s,
    (
        (
            '%s 200 OK\r\n'
            'Content-Length: %s\r\n'
            'Content-Type: %s\r\n'
            '\r\n'
        ) % (
            constants.HTTP_SIGNATURE,
            len(output),
            constants.MIME_MAPPING.get('html'),
        )
    ).encode('utf-8')

    )


    #
    # Send content
    #
    util.send_all(s,output)
def send_xml(s,output):
    util.send_all(
        s,
        (
            (
                '%s 200 OK\r\n'
                'Content-Length: %s\r\n'
                'Content-Type: %s\r\n'
                '\r\n'
            ) % (
                constants.HTTP_SIGNATURE,
                len(output),
                constants.MIME_MAPPING.get('xml'),
            )
        ).encode('utf-8')

    )

    util.send_all(s,output)

def send_status(s, code, message, extra):
    util.send_all(
        s,
        (
            (
                '%s %s %s\r\n'
                'Content-Type: text/plain\r\n'
                '\r\n'
                'Error %s %s\r\n'
                '%s'
            ) % (
                constants.HTTP_SIGNATURE,
                code,
                message,
                code,
                message,
                extra,
            )
        ).encode('utf-8')
    )
# vim: expandtab tabstop=4 shiftwidth=4