# -*- coding: utf-8 -*-
# @Author: wangwh8
# @Date:   2017-01-19 10:26:46
# @Last Modified by:   wangwh8
# @Last Modified time: 2017-01-19 12:49:37
import requests
import tempfile
import zipfile
import os

GITHUB_API_HOST = 'api.github.com'

def make_url(path, **kwargs):
    for key, val in kwargs.items():
        path = path.replace(':' + key, val)
    if ':' in path:
        raise ValueError('invalid path:' + path)
    return "http://%s%s" % (GITHUB_API_HOST, path)

def getLatestRelease(owner, repo):
    """
    param: owner
    param: repo
    """
    path = '/repos/:owner/:repo/releases/latest'
    requestURI =  make_url(**locals())
    resp = requests.get(requestURI)
    return resp.json()

def downloadZipBall(zipball_url):
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
    print 'Finished 100 %'
    extract(tf, '.')

def extract(zip_file, output_dir):
  f_zip = zipfile.ZipFile(zip_file, 'r')
 
  # 解压所有文件到指定目录
  f_zip.extractall(output_dir)
 
  # 逐个解压文件到指定目录
  for f in f_zip.namelist():
    f_zip.extract(f, os.path.join(output_dir, 'bak'))
if __name__ == '__main__':
    lr =  getLatestRelease("edwardw1987", "tool")
    # print lr["tag_name"]
    downloadZipBall(lr["zipball_url"])