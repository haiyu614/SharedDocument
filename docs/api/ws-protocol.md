# WebSocket 消息格式（MVP）

Endpoint: `ws://{host}/ws/{documentId}?token=<JWT>&clientId=<uuid>`

## 客户端 → 服务端

### `edit_operation`
```json
{
  "type": "edit_operation",
  "version": 12,
  "operations": [
    { "op": "retain", "count": 5 },
    { "op": "insert", "text": "Hello" }
  ],
  "cursor": { "position": 10, "selection": [10, 15] }
}
```

### `cursor_update`
```json
{
  "type": "cursor_update",
  "cursor": { "position": 20, "selection": [20, 25], "color": "#ff7f50" }
}
```

### `heartbeat`
```json
{ "type": "heartbeat" }
```

## 服务端 → 客户端

### `user_joined`
```json
{ "type": "user_joined", "clientId": "abc123", "username": "Alice" }
```

### `cursor_update`
```json
{ "type": "cursor_update", "clientId": "abc123", "cursor": { "position": 20 } }
```

### `edit_operation`
```json
{ "type": "edit_operation", "clientId": "abc123", "operations": [...] }
```

### `user_left`
```json
{ "type": "user_left", "clientId": "abc123" }
```

### `error`
```json
{ "type": "error", "message": "Token 无效" }
```

> 后续可扩展 `save_result`、`session_snapshot` 等消息类型。

