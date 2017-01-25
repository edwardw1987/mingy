# -*- coding: utf-8 -*-
# @Author: wangwh8
# @Date:   2017-01-19 10:26:46
# @Last Modified by:   wangwh8
# @Last Modified time: 2017-01-25 17:15:45
import requests
import tempfile
import zipfile
import os
from requests.exceptions import ConnectTimeout
import shutil


GITHUB_API_HOST = 'api.github.com'
GITHUB_OWNER = 'edwardw1987'
GITHUB_REPO = 'mingy'

def make_url(path, **kwargs):
    for key, val in kwargs.items():
        path = path.replace(':' + key, val)
    if ':' in path:
        raise ValueError('invalid path:' + path)
    return "http://%s%s" % (GITHUB_API_HOST, path)

def getLatestRelease(owner=GITHUB_OWNER, repo=GITHUB_REPO):
    """
    param: owner
    param: repo
    """
    path = '/repos/:owner/:repo/releases/latest'
    requestURI =  make_url(**locals())
    ret = {}
    try:
        resp = requests.get(requestURI)
        ret.update(resp.json())
    except ConnectTimeout:
        ret["errMsg"] = ConnectTimeout.__name__
    except Exception as e:
        ret["errMsg"] = e
    return ret


def updateByZipball(zipball_url):
    resp = requests.get(zipball_url, stream=True)
    contentLen = int(resp.headers["Content-Length"])
    remains = contentLen
    print 'Content-length:', contentLen
    tf = tempfile.NamedTemporaryFile(suffix=".zip")
    print tf.name
    for _b in resp.iter_content(chunk_size=1024):
        print 'Remains:', "%.2f" % ((contentLen -remains)*100/float(contentLen)), '%'
        tf.write(_b)
        remains -= 1024
    replaceSourceWith(tf, '.')
    print 'Finished 100 %'

def replaceSourceWith(zip_file, root_dir):
    f_zip = zipfile.ZipFile(zip_file, 'r')
    # 解压所有文件到指定目录
    # f_zip.extractall()
    # shutil.copytree()
    # print members
    # shutil.copytree(os.path.join(root_dir,))
    # 逐个解压文件到指定目录
    members = []
    src_dir = None
    for f in f_zip.namelist():
        if 'module' in f:
            members.append(f)
        if f.endswith('/module/'):
            src_dir = f
    bak_dir = os.path.join(root_dir, 'bak')
    to_copy_src_dir = os.path.join(bak_dir, src_dir)
    f_zip.extractall(path= bak_dir, members=members)
    dest_dir = root_dir
    print dest_dir
    for i in os.listdir(to_copy_src_dir):
        shutil.copy(i, root_dir + '\\' + i.rsplit('\\')[-1])
    # shutil.copytree(to_copy_src_dir, dest_dir)
    #   f_zip.extract(f, os.path.join(output_dir, 'bak'))
if __name__ == '__main__':
    lr =  getLatestRelease()
    # print lr["tag_name"]
    updateByZipball(lr["zipball_url"])
