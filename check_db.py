import pymysql

# 连接数据库
try:
    connection = pymysql.connect(
        host='8.138.190.109',
        port=3306,
        user='root',
        password='123456',
        database='shared_documents',
        charset='utf8mb4'
    )
    
    print("✅ 数据库连接成功！\n")
    
    with connection.cursor() as cursor:
        # 查看所有表
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        print("📊 数据库中的表：")
        for table in tables:
            print(f"  - {table[0]}")
        print()
        
        # 查看 users 表结构
        if tables:
            cursor.execute("DESCRIBE users;")
            columns = cursor.fetchall()
            print("📋 users 表结构：")
            for col in columns:
                print(f"  {col[0]:20} {col[1]:20} {col[2]:10} {col[3]:10}")
            print()
            
            # 查看 users 表数据
            cursor.execute("SELECT id, username, email, created_at, is_active FROM users;")
            users = cursor.fetchall()
            print(f"👥 users 表数据（共 {len(users)} 条）：")
            if users:
                for user in users:
                    print(f"  ID: {user[0]}, 用户名: {user[1]}, 邮箱: {user[2]}, 创建时间: {user[3]}, 状态: {user[4]}")
            else:
                print("  （暂无数据）")
    
    connection.close()
    print("\n✅ 检查完成！")
    
except Exception as e:
    print(f"❌ 错误: {e}")
