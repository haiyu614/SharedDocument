"""
测试远程存储连接
"""
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_connection():
    """测试SFTP连接"""
    print("=" * 50)
    print("测试远程存储连接")
    print("=" * 50)
    
    # 导入配置
    from config import Config
    
    print(f"\n配置信息:")
    print(f"  服务器: {Config.REMOTE_HOST}:{Config.REMOTE_PORT}")
    print(f"  用户名: {Config.REMOTE_USERNAME}")
    print(f"  远程目录: {Config.REMOTE_UPLOAD_DIR}")
    print(f"  启用远程存储: {Config.USE_REMOTE_STORAGE}")
    
    # 测试连接
    print("\n正在连接到远程服务器...")
    
    try:
        import paramiko
        
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        client.connect(
            hostname=Config.REMOTE_HOST,
            port=Config.REMOTE_PORT,
            username=Config.REMOTE_USERNAME,
            password=Config.REMOTE_PASSWORD,
            timeout=10
        )
        
        print("✓ SSH连接成功！")
        
        # 测试SFTP
        sftp = client.open_sftp()
        print("✓ SFTP连接成功！")
        
        # 检查远程目录
        try:
            sftp.stat(Config.REMOTE_UPLOAD_DIR)
            print(f"✓ 远程目录存在: {Config.REMOTE_UPLOAD_DIR}")
        except FileNotFoundError:
            print(f"✗ 远程目录不存在: {Config.REMOTE_UPLOAD_DIR}")
            print(f"  正在创建目录...")
            
            # 递归创建目录
            dirs = []
            dir_path = Config.REMOTE_UPLOAD_DIR
            
            while dir_path != '/':
                dirs.append(dir_path)
                dir_path = os.path.dirname(dir_path)
            
            dirs.reverse()
            
            for dir_item in dirs:
                try:
                    sftp.stat(dir_item)
                except FileNotFoundError:
                    try:
                        sftp.mkdir(dir_item)
                        print(f"  ✓ 创建目录: {dir_item}")
                    except Exception as e:
                        print(f"  ✗ 创建目录失败: {e}")
            
            print(f"✓ 目录创建完成")
        
        # 测试写入权限
        test_file = os.path.join(Config.REMOTE_UPLOAD_DIR, '.test_write').replace('\\', '/')
        try:
            import io
            test_content = b"test"
            sftp.putfo(io.BytesIO(test_content), test_file)
            print(f"✓ 写入权限测试成功")
            
            # 清理测试文件
            try:
                sftp.remove(test_file)
                print(f"✓ 删除权限测试成功")
            except:
                pass
        except Exception as e:
            print(f"✗ 写入权限测试失败: {e}")
        
        # 关闭连接
        sftp.close()
        client.close()
        
        print("\n" + "=" * 50)
        print("✓ 所有测试通过！远程存储配置正确。")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"\n✗ 连接失败: {e}")
        print("\n请检查:")
        print("  1. 服务器地址和端口是否正确")
        print("  2. 用户名和密码是否正确")
        print("  3. 网络连接是否正常")
        print("  4. 防火墙是否允许SSH连接")
        print("=" * 50)
        return False

if __name__ == '__main__':
    success = test_connection()
    sys.exit(0 if success else 1)
