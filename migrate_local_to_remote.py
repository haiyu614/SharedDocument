"""
将本地uploads目录中的文件迁移到远程服务器
"""
import sys
import os
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def migrate_files():
    """迁移本地文件到远程服务器"""
    print("=" * 70)
    print("本地文件迁移到远程服务器")
    print("=" * 70)
    
    from config import Config
    import paramiko
    
    local_upload_dir = Config.UPLOAD_FOLDER
    remote_upload_dir = Config.REMOTE_UPLOAD_DIR
    
    print(f"\n本地目录: {local_upload_dir}")
    print(f"远程目录: {remote_upload_dir}")
    print(f"服务器: {Config.REMOTE_HOST}\n")
    
    # 检查本地目录是否存在
    if not os.path.exists(local_upload_dir):
        print(f"✗ 本地目录不存在: {local_upload_dir}")
        return False
    
    # 获取本地文件列表
    local_files = []
    for item in os.listdir(local_upload_dir):
        item_path = os.path.join(local_upload_dir, item)
        if os.path.isfile(item_path) and item != '.gitkeep':
            local_files.append(item)
    
    if not local_files:
        print("本地目录为空，没有文件需要迁移。")
        return True
    
    print(f"找到 {len(local_files)} 个文件需要上传:\n")
    
    try:
        # 连接服务器
        print("正在连接到远程服务器...")
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
        print("✓ 连接成功！\n")
        
        # 确保远程目录存在
        try:
            sftp.stat(remote_upload_dir)
        except FileNotFoundError:
            print(f"远程目录不存在，正在创建...")
            # 递归创建目录
            dirs = []
            dir_path = remote_upload_dir
            while dir_path != '/':
                dirs.append(dir_path)
                dir_path = os.path.dirname(dir_path)
            dirs.reverse()
            for dir_item in dirs:
                try:
                    sftp.stat(dir_item)
                except FileNotFoundError:
                    sftp.mkdir(dir_item)
            print(f"✓ 目录创建完成\n")
        
        # 上传文件
        success_count = 0
        fail_count = 0
        total_size = 0
        
        for i, filename in enumerate(local_files, 1):
            local_path = os.path.join(local_upload_dir, filename)
            remote_path = os.path.join(remote_upload_dir, filename).replace('\\', '/')
            
            try:
                # 获取文件大小
                file_size = os.path.getsize(local_path)
                
                # 格式化文件大小
                if file_size < 1024:
                    size_str = f"{file_size} B"
                elif file_size < 1024 * 1024:
                    size_str = f"{file_size / 1024:.2f} KB"
                elif file_size < 1024 * 1024 * 1024:
                    size_str = f"{file_size / (1024 * 1024):.2f} MB"
                else:
                    size_str = f"{file_size / (1024 * 1024 * 1024):.2f} GB"
                
                # 检查远程文件是否已存在
                file_exists = False
                try:
                    sftp.stat(remote_path)
                    file_exists = True
                except FileNotFoundError:
                    pass
                
                if file_exists:
                    print(f"[{i}/{len(local_files)}] ⊙ {filename} ({size_str}) - 已存在，跳过")
                else:
                    print(f"[{i}/{len(local_files)}] ↑ 正在上传 {filename} ({size_str})...", end='')
                    
                    # 上传文件
                    sftp.put(local_path, remote_path)
                    
                    # 验证上传
                    try:
                        remote_stat = sftp.stat(remote_path)
                        if remote_stat.st_size == file_size:
                            print(" ✓ 成功")
                            success_count += 1
                            total_size += file_size
                        else:
                            print(f" ✗ 失败 (大小不匹配)")
                            fail_count += 1
                    except:
                        print(" ✗ 验证失败")
                        fail_count += 1
                
            except Exception as e:
                print(f"[{i}/{len(local_files)}] ✗ {filename} - 失败: {e}")
                fail_count += 1
        
        sftp.close()
        client.close()
        
        # 总结
        print("\n" + "=" * 70)
        print("迁移完成！")
        print(f"  成功: {success_count} 个文件")
        if fail_count > 0:
            print(f"  失败: {fail_count} 个文件")
        
        # 格式化总大小
        if total_size < 1024:
            total_str = f"{total_size} B"
        elif total_size < 1024 * 1024:
            total_str = f"{total_size / 1024:.2f} KB"
        elif total_size < 1024 * 1024 * 1024:
            total_str = f"{total_size / (1024 * 1024):.2f} MB"
        else:
            total_str = f"{total_size / (1024 * 1024 * 1024):.2f} GB"
        
        if success_count > 0:
            print(f"  总大小: {total_str}")
        print("=" * 70)
        
        if fail_count == 0:
            print("\n提示: 现在可以安全删除本地uploads目录中的文件了")
            print("      (建议先验证远程文件完整性)")
        
        return fail_count == 0
        
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        return False

if __name__ == '__main__':
    success = migrate_files()
    sys.exit(0 if success else 1)
