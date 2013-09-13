__author__ = 'headradio'
#Some utilities to set up a mongdb instance with all the images
# from the collection of tar files available for download
import os
import tarfile
from joblib import Parallel, delayed
import pymongo as pm
import gridfs

def get_tar_filenames(path=None):
    if path is None:
        path = os.getcwd()
    return [filename for filename in os.listdir(path) if filename.endswith('.tar')]


db = pm.MongoClient('dicarlo5').gridfs_example
default_fs = gridfs.GridFS(db)

def put_tar_file_contents_on_gridfs(tar_file_name, fs=default_fs, force=True):
    tar_file = tarfile.open(tar_file_name, mode='r|')
    filenames = []
    for member in tar_file:
        file = tar_file.extractfile(member)
        filename = member.name
        filenames.append(filename)
        if force and fs.exists(filename):
            fs.delete(filename)
            print 'Overwriting '+ filename
        fs.put(file, _id=filename)
    return filenames


def parallel_upload_tar_folder(path=None, n_jobs=-1):
    if path is None:
        path = os.getcwd()
    tar_filenames = get_tar_filenames(path)
    ids = Parallel(n_jobs=n_jobs)(delayed(put_tar_file_contents_on_gridfs)(tar_filename)
                                      for tar_filename in tar_filenames)
    return tar_filenames, ids

