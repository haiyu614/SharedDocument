import socket

# 目标主机和端口
host = 'www.people.com.cn'
port = 80

# 创建 socket 对象
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # 连接到目标主机
    client_socket.connect((host, port))
    print(f"成功连接到 {host}:{port}")

    # 构造 HTTP GET 请求
    get_request = f"GET / HTTP/1.1\r\nHost: {host}\r\n\r\n"
    client_socket.send(get_request.encode('utf-8'))

    # 接收并保存网页内容
    web_content = b""
    while True:
        chunk = client_socket.recv(4096)
        if not chunk:
            break
        web_content += chunk

    # 将网页内容以字符串形式保存到 txt 文件
    with open('people_web_content.txt', 'w', encoding='utf-8') as f:
        f.write(web_content.decode('utf-8', errors='ignore'))
    print("网页文本内容已保存到 people_web_content.txt")

finally:
    # 关闭 socket 连接
    client_socket.close()