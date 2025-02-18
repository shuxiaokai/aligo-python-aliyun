"""文件相关"""
import os
from typing import List, Union, overload

from aligo.core import *
from aligo.request import *
from aligo.response import *
from aligo.types import *
from aligo.types.Enum import *


class File(Core):
    """..."""

    @overload
    def get_file(self, file_id: str, drive_id: str = None) -> BaseFile:
        """
        获取文件
        :param file_id: [str] 文件ID
        :param drive_id: Optional[str] 存储桶ID
        :return: [BaseFile] 文件对象

        用法示例:
        >>> from aligo import Aligo, BaseFile
        >>> ali = Aligo()
        >>> file = ali.get_file('file_id')
        >>> assert isinstance(file, BaseFile)
        >>> print(file)
        """

    @overload
    def get_file(self, body: GetFileRequest) -> BaseFile:
        """
        获取文件
        :param body: [GetFileRequest] 获取文件请求体
        :return: [BaseFile] 文件对象

        用法示例:
        >>> from aligo import Aligo, BaseFile, GetFileRequest
        >>> ali = Aligo()
        >>> file = ali.get_file(body=GetFileRequest(file_id='file_id'))
        >>> assert isinstance(file, BaseFile)
        >>> print(file)
        """

    def get_file(self,
                 file_id: str = None,
                 drive_id: str = None,
                 body: GetFileRequest = None,
                 **kwargs) -> BaseFile:
        """get_file"""
        if body is None:
            body = GetFileRequest(
                file_id=file_id, drive_id=drive_id,
                **kwargs
            )
        return self._core_get_file(body)

    @overload
    def get_file_list(self, parent_file_id: str = 'root', drive_id: str = None, **kwargs) -> List[BaseFile]:
        """
        获取文件列表
        :param parent_file_id: Optional[str] 文件夹ID，默认为根目录
        :param drive_id: Optional[str] 存储桶ID
        :param kwargs: [dict] 其他参数
        :return: [List[BaseFile]] 文件列表

        用法示例:
        >>> from aligo import Aligo
        >>> ali = Aligo()
        >>> file_list = ali.get_file_list('<parent_file_id>')
        >>> assert isinstance(file_list, list)
        >>> print(file_list)
        """

    @overload
    def get_file_list(self, body: GetFileListRequest) -> List[BaseFile]:
        """
        获取文件列表
        :param body: [GetFileListRequest] 获取文件列表请求体
        :return: [List[BaseFile]] 文件列表

        用法示例:
        >>> from aligo import Aligo, BaseFile, GetFileListRequest
        >>> ali = Aligo()
        >>> file_list = ali.get_file_list(body=GetFileListRequest(parent_file_id='<parent_file_id>'))
        >>> assert isinstance(file_list, list)
        >>> print(file_list)
        """

    def get_file_list(self, parent_file_id: str = 'root', drive_id: str = None, body: GetFileListRequest = None,
                      **kwargs) -> List[BaseFile]:
        """get_file_list"""
        if body is None:
            body = GetFileListRequest(drive_id=drive_id, parent_file_id=parent_file_id, **kwargs)
        result = self._core_get_file_list(body)
        return [i for i in result]

    def batch_get_files(self, file_id_list: List[str], drive_id: str = None) -> List[BatchSubResponse]:
        """
        批量获取文件
        :param file_id_list: [List[str]] 文件ID列表
        :param drive_id: [str] 存储桶ID
        :return: [List[BatchSubResponse]] 批量获取文件响应列表

        用法示例:
        >>> from aligo import Aligo, Null
        >>> ali = Aligo()
        >>> file_list = ali.batch_get_files(['file_id1', 'file_id2'])
        >>> assert isinstance(file_list, list)
        >>> # 实际使用中一般不需要判断，这里写出来只是提供一个判断示例
        >>> if isinstance(file_list[-1], Null):
        >>>     print('出现错误')
        >>> for e in file_list:
        >>>     assert isinstance(e, BatchSubResponse)
        >>> print(file_list)
        """
        body = BatchGetFileRequest(file_id_list=file_id_list, drive_id=drive_id)
        result = self._core_batch_get_files(body)
        return [i for i in result]

    def get_folder_by_path(self, path: str = '/', parent_file_id: str = 'root',
                           check_name_mode: CheckNameMode = 'refuse', drive_id: str = None
                           ) -> Union[BaseFile, CreateFileResponse]:
        """
        根据路径获取（无则创建）文件夹对象
        :param path: [str] 路径，无需以'/'开头
        :param parent_file_id: Optional[str] 父文件夹ID，默认为根目录，意思是基于根目录查找
        :param check_name_mode: Optional[CheckNameMode] 检查名称模式，默认为refuse
        :param drive_id: Optional[str] 存储桶ID
        :return: [BaseFile] 文件对象

        用法示例:
        >>> from aligo import Aligo
        >>> ali = Aligo()
        >>> folder = ali.get_folder_by_path('path/to/folder')
        >>> assert isinstance(folder, BaseFile)
        >>> print(folder)
        """
        path = path.strip('/')
        if path == '':
            return self.get_file(file_id=parent_file_id, drive_id=drive_id)
        folder = None
        for name in path.split('/'):
            folder = self._core_create_folder(CreateFolderRequest(
                name=name, parent_file_id=parent_file_id, check_name_mode=check_name_mode, drive_id=drive_id
            ))
            parent_file_id = folder.file_id
        return folder

    def get_file_by_path(self, path: str = '/', parent_file_id: str = 'root',
                         check_name_mode: CheckNameMode = 'refuse',
                         drive_id: str = None) -> Union[BaseFile, CreateFileResponse]:
        """
        根据路径获取文件或文件夹, 先找到啥就返回啥，不存在就创建文件夹并返回
        :param path: [str] 路径，无需以'/'开头
        :param parent_file_id: Optional[str] 父文件夹ID，默认为根目录，意思是基于根目录查找
        :param check_name_mode: Optional[CheckNameMode] 检查名称模式，默认为refuse
        :param drive_id: Optional[str] 存储桶ID
        :return: [BaseFile] 文件对象

        用法示例:
        >>> from aligo import Aligo
        >>> ali = Aligo()
        >>> file = ali.get_file_by_path('path/to/file')
        >>> assert isinstance(file, BaseFile)
        >>> print(file)
        """
        path = path.strip('/')
        folder_path, file_name = os.path.split(path)
        if folder_path != '':
            parent_file_id = self.get_folder_by_path(folder_path, parent_file_id=parent_file_id,
                                                     check_name_mode=check_name_mode, drive_id=drive_id).file_id
        if file_name == '':
            return self.get_file(file_id=parent_file_id, drive_id=drive_id)

        file_list = self._core_get_file_list(
            GetFileListRequest(parent_file_id=parent_file_id, drive_id=drive_id)
        )

        for file in file_list:
            if file_name == file.name:
                return file

        return self._core_create_folder(CreateFolderRequest(
            name=file_name, parent_file_id=parent_file_id, check_name_mode=check_name_mode, drive_id=drive_id
        ))
