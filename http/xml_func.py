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

HTML_TABLE_HEADER='''<!DOCTYPE html><html><body><table style="width:35%" ; border= "2px solid #dddddd">  <tr>    <th align="left"> Filename </th>    <th align="left">Option</th>   </tr>'''
HTML_END='''</table></body></html>'''

def xml_to_html(st):
    st=str(st)
    root=ET.fromstring(st)
    html=HTML_TABLE_HEADER
    for result in root.findall('result'):
        name = result.get('name')
        id=result.get('id')
        html+='  <tr> <td>%s</td> <td align="middle"> <a href="/download_file?id=%s">&lt;download&gt;</a> <a href="/view_file?id=%s">&lt;view&gt;</a></td>  </tr>' %(name,id,id)
    html+='<a href="/form?">&lt;Back&gt;</a>'+HTML_END
    return html
    
def xml_form(files,ids):
    root = ET.Element('root')
    
    if len(files)>0:
        for file,i in zip(files,ids):
            ET.SubElement(root, 'result', name=file, id=str(i))
       
    return ET.tostring(root)

# vim: expandtab tabstop=4 shiftwidth=4 