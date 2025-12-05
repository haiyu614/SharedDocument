"""
远程存储服务模块 - 使用SFTP将文件存储到云服务器
"""
import paramiko
import os
import io
from flask import current_app


class RemoteStorage:
    """远程SFTP存储服务"""
    
    def __init__(self):
        self.client = None
        self.sftp = None
        
    def connect(self):
        """连接到远程SFTP服务器"""
        if self.sftp is not None:
            return self.sftp
            
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            self.client.connect(
                hostname=current_app.config['REMOTE_HOST'],
                port=current_app.config.get('REMOTE_PORT', 22),
                username=current_app.config['REMOTE_USERNAME'],
                password=current_app.config['REMOTE_PASSWORD'],
                timeout=10
            )
            
            self.sftp = self.client.open_sftp()
            
            # 确保远程目录存在
            remote_dir = current_app.config['REMOTE_UPLOAD_DIR']
            try:
                self.sftp.stat(remote_dir)
            except FileNotFoundError:
                # 递归创建目录
                self._mkdir_p(remote_dir)
                
            return self.sftp
        except Exception as e:
            print(f"SFTP连接失败: {e}")
            self.close()
            raise
    
    def _mkdir_p(self, remote_directory):
        """递归创建远程目录"""
        dirs = []
        dir_path = remote_directory
        
        while dir_path != '/':
            dirs.append(dir_path)
            dir_path = os.path.dirname(dir_path)
        
        dirs.reverse()
        
        for dir_item in dirs:
            try:
                self.sftp.stat(dir_item)
            except FileNotFoundError:
                try:
                    self.sftp.mkdir(dir_item)
                except:
                    pass
    
    def close(self):
        """关闭SFTP连接"""
        if self.sftp:
            try:
                self.sftp.close()
            except:
                pass
            self.sftp = None
            
        if self.client:
            try:
                self.client.close()
            except:
                pass
            self.client = None
    
    def upload_file(self, local_path, remote_filename):
        """
        上传文件到远程服务器
        
        Args:
            local_path: 本地文件路径
            remote_filename: 远程文件名
            
        Returns:
            bool: 上传是否成功
        """
        try:
            sftp = self.connect()
            remote_path = os.path.join(
                current_app.config['REMOTE_UPLOAD_DIR'], 
                remote_filename
            ).replace('\\', '/')
            
            sftp.put(local_path, remote_path)
            
            # 验证文件是否上传成功
            try:
                sftp.stat(remote_path)
                return True
            except:
                return False
                
        except Exception as e:
            print(f"文件上传失败: {e}")
            return False
        finally:
            self.close()
    
    def upload_fileobj(self, file_obj, remote_filename):
        """
        上传文件对象到远程服务器
        
        Args:
            file_obj: 文件对象（如Flask的request.files['file']）
            remote_filename: 远程文件名
            
        Returns:
            bool: 上传是否成功
        """
        try:
            sftp = self.connect()
            remote_path = os.path.join(
                current_app.config['REMOTE_UPLOAD_DIR'], 
                remote_filename
            ).replace('\\', '/')
            
            # 将文件对象内容读取到BytesIO
            file_data = file_obj.read()
            file_obj.seek(0)  # 重置指针以便后续可能的使用
            
            # 使用putfo上传
            sftp.putfo(io.BytesIO(file_data), remote_path)
            
            # 验证文件是否上传成功
            try:
                sftp.stat(remote_path)
                return True
            except:
                return False
                
        except Exception as e:
            print(f"文件对象上传失败: {e}")
            return False
        finally:
            self.close()
    
    def download_file(self, remote_filename, local_path):
        """
        从远程服务器下载文件
        
        Args:
            remote_filename: 远程文件名
            local_path: 本地保存路径
            
        Returns:
            bool: 下载是否成功
        """
        try:
            sftp = self.connect()
            remote_path = os.path.join(
                current_app.config['REMOTE_UPLOAD_DIR'], 
                remote_filename
            ).replace('\\', '/')
            
            # 确保本地目录存在
            local_dir = os.path.dirname(local_path)
            if not os.path.exists(local_dir):
                os.makedirs(local_dir)
            
            sftp.get(remote_path, local_path)
            return os.path.exists(local_path)
            
        except Exception as e:
            print(f"文件下载失败: {e}")
            return False
        finally:
            self.close()
    
    def download_fileobj(self, remote_filename):
        """
        从远程服务器下载文件到内存
        
        Args:
            remote_filename: 远程文件名
            
        Returns:
            BytesIO: 文件内容的BytesIO对象，失败返回None
        """
        try:
            sftp = self.connect()
            remote_path = os.path.join(
                current_app.config['REMOTE_UPLOAD_DIR'], 
                remote_filename
            ).replace('\\', '/')
            
            file_obj = io.BytesIO()
            sftp.getfo(remote_path, file_obj)
            file_obj.seek(0)
            return file_obj
            
        except Exception as e:
            print(f"文件下载到内存失败: {e}")
            return None
        finally:
            self.close()
    
    def delete_file(self, remote_filename):
        """
        删除远程服务器上的文件
        
        Args:
            remote_filename: 远程文件名
            
        Returns:
            bool: 删除是否成功
        """
        try:
            sftp = self.connect()
            remote_path = os.path.join(
                current_app.config['REMOTE_UPLOAD_DIR'], 
                remote_filename
            ).replace('\\', '/')
            
            try:
                sftp.remove(remote_path)
                return True
            except FileNotFoundError:
                # 文件不存在也算成功
                return True
            except Exception as e:
                print(f"删除文件失败: {e}")
                return False
                
        except Exception as e:
            print(f"连接服务器失败: {e}")
            return False
        finally:
            self.close()
    
    def file_exists(self, remote_filename):
        """
        检查远程文件是否存在
        
        Args:
            remote_filename: 远程文件名
            
        Returns:
            bool: 文件是否存在
        """
        try:
            sftp = self.connect()
            remote_path = os.path.join(
                current_app.config['REMOTE_UPLOAD_DIR'], 
                remote_filename
            ).replace('\\', '/')
            
            try:
                sftp.stat(remote_path)
                return True
            except FileNotFoundError:
                return False
                
        except Exception as e:
            print(f"检查文件存在性失败: {e}")
            return False
        finally:
            self.close()
    
    def get_file_size(self, remote_filename):
        """
        获取远程文件大小
        
        Args:
            remote_filename: 远程文件名
            
        Returns:
            int: 文件大小（字节），失败返回0
        """
        try:
            sftp = self.connect()
            remote_path = os.path.join(
                current_app.config['REMOTE_UPLOAD_DIR'], 
                remote_filename
            ).replace('\\', '/')
            
            stat = sftp.stat(remote_path)
            return stat.st_size
            
        except Exception as e:
            print(f"获取文件大小失败: {e}")
            return 0
        finally:
            self.close()


# 创建全局实例
def get_remote_storage():
    """获取远程存储实例"""
    return RemoteStorage()
