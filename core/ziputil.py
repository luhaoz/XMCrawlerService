from zipfile import ZipFile, ZIP_LZMA
from io import BytesIO


class ZipUtil(object):

    def __init__(self, path):
        self.__path = path
        self.__tasks = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.build()

    def build(self):
        _zip_file = ZipFile(self.__path, mode="a", compression=ZIP_LZMA, compresslevel=9)
        # if zinfo_or_arcname in _zip_file.namelist():
        _diff = set(_zip_file.namelist()).intersection(set(self.__tasks.keys()))
        __memory = None
        if len(_diff) > 0:
            # rebuild
            pass
            __memory = BytesIO()
            _temp_zip = ZipFile(__memory, 'w', compression=ZIP_LZMA, compresslevel=9)
            for _zip_info in _zip_file.infolist():
                if _zip_info.filename in _diff:
                    continue
                _temp_zip.writestr(_zip_info, _zip_file.read(_zip_info.filename))
            _zip_file.close()
            _zip_file = _temp_zip
        for _task_name, _task_data in self.__tasks.items():
            _zip_file.writestr(_task_name, _task_data)
        _zip_file.close()
        if __memory is not None:
            with open(self.__path, 'wb') as _new_file:
                __memory.seek(0)
                _new_file.write(__memory.getbuffer())

    def replace(self, zinfo_or_arcname, data):
        self.__tasks[zinfo_or_arcname] = data

        # self.__current = ZipFile(self.__path, mode="a", compression=ZIP_LZMA, compresslevel=9)
        # if zinfo_or_arcname in self.__current.namelist():
        #     self.__rebuild(zinfo_or_arcname)
        # self.__current.writestr(zinfo_or_arcname, data)

    def __rebuild(self, zinfo_or_arcname):
        pass
        # if self.__memory is None:
        #     self.__memory = BytesIO()
        # _temp_zip = ZipFile(self.__memory, 'a', compression=ZIP_LZMA, compresslevel=9)
        # _zip_infos = self.__current.infolist()
        # for _zip_info in _zip_infos:
        #     if zinfo_or_arcname == _zip_info.filename:
        #         continue
        #     _temp_zip.writestr(_zip_info, self.__current.read(_zip_info.filename))
        # # close old file
        # self.__current.close()
        # self.__current = _temp_zip
