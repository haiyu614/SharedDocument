"""
列出远程存储中的所有文件
"""
import sys
import os
from datetime import datetime

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def list_remote_files():
    """列出远程存储中的所有文件"""
    print("=" * 70)
    print("远程存储文件列表")
    print("=" * 70)
    
    from config import Config
    import paramiko
    
    print(f"\n服务器: {Config.REMOTE_HOST}")
    print(f"目录: {Config.REMOTE_UPLOAD_DIR}\n")
    
    try:
        # 连接服务器
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        client.connect(
            hostname=Config.REMOTE_HOST,
            port=Config.REMOTE_PORT,
            username=Config.REMOTE_USERNAME,
            password=Config.REMOTE_PASSWORD,
            timeout=10
        )
        
        sftp = client.open_sftp()
        
        # 列出文件
        try:
            files = sftp.listdir_attr(Config.REMOTE_UPLOAD_DIR)
            
            if not files:
                print("目录为空，还没有上传任何文件。")
            else:
                print(f"共找到 {len(files)} 个文件:\n")
                print(f"{'文件名':<40} {'大小':<15} {'修改时间':<20}")
                print("-" * 70)
                
                total_size = 0
                for file_attr in sorted(files, key=lambda x: x.st_mtime, reverse=True):
                    filename = file_attr.filename
                    size = file_attr.st_size
                    mtime = datetime.fromtimestamp(file_attr.st_mtime)
                    
                    # 格式化文件大小
                    if size < 1024:
                        size_str = f"{size} B"
                    elif size < 1024 * 1024:
                        size_str = f"{size / 1024:.2f} KB"
                    elif size < 1024 * 1024 * 1024:
                        size_str = f"{size / (1024 * 1024):.2f} MB"
                    else:
                        size_str = f"{size / (1024 * 1024 * 1024):.2f} GB"
                    
                    # 截断过长的文件名
                    display_name = filename if len(filename) <= 38 else filename[:35] + "..."
                    
                    print(f"{display_name:<40} {size_str:<15} {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
                    total_size += size
                
                print("-" * 70)
                
                # 格式化总大小
                if total_size < 1024:
                    total_str = f"{total_size} B"
                elif total_size < 1024 * 1024:
                    total_str = f"{total_size / 1024:.2f} KB"
                elif total_size < 1024 * 1024 * 1024:
                    total_str = f"{total_size / (1024 * 1024):.2f} MB"
                else:
                    total_str = f"{total_size / (1024 * 1024 * 1024):.2f} GB"
                
                print(f"总大小: {total_str}")
                
        except FileNotFoundError:
            print(f"✗ 目录不存在: {Config.REMOTE_UPLOAD_DIR}")
        
        sftp.close()
        client.close()
        
        print("\n" + "=" * 70)
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False
    
    return True

if __name__ == '__main__':
    success = list_remote_files()
    sys.exit(0 if success else 1)
