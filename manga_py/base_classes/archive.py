from zipfile import ZipFile, ZIP_DEFLATED

# from PIL import Image as PilImage
from manga_py.image import Image
from os import path

from manga_py.fs import is_file, make_dirs, basename, dirname, unlink, get_temp_path


class Archive:
    _archive = None
    _writes = None
    files = None
    not_change_files_extension = False

    def __init__(self):
        self.files = []
        self._writes = {}

    def write_file(self, data, in_arc_name):
        self._writes[in_arc_name] = data

    def add_file(self, file, in_arc_name=None):
        if in_arc_name is None:
            in_arc_name = basename(file)
        self.files.append((file, in_arc_name))

    def set_files_list(self, files):
        self.files = files

    def add_book_info(self, data):
        self.write_file('comicbook.xml', data)

    def __add_files(self):
        for file in self.files:
            if is_file(file[0]):
                self._archive.write(file[0], file[1])

    def __add_writes(self):
        for file in self._writes:
            self._archive.writestr(file, self._writes[file])

    def add_info(self, data):
        self.write_file(data, 'info.txt')

    def make(self, dst):
        if not len(self.files) and not len(self._writes):
            return

        make_dirs(dirname(dst))

        self._archive = ZipFile(dst, 'w', ZIP_DEFLATED)
        self.__add_files()
        self.__add_writes()
        self._archive.close()
        self._maked()

    def _maked(self):
        for file in self.files:
            unlink(file[0])

    def __update_image_extension(self, filename) -> tuple:
        fn, extension = path.splitext(filename)
        if not self.not_change_files_extension:
            ext = Image.real_extension(get_temp_path(filename))
            if ext:
                extension = ext
        return basename(fn + extension)

    def lazy_add(self, _path):
        self.add_file(_path, self.__update_image_extension(_path))