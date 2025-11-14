# 协同算法策略（MVP）

## 目标

- 支持多人实时编辑文本内容。
- 保障操作顺序一致与最终一致性。
- 为后续引入表格/图片等复杂元素预留空间。

## MVP 实现路线

1. **OT（Operational Transformation）思路**
   - 客户端生成操作（insert/delete/retain），携带本地版本号，经 WebSocket 发送。
   - 服务端按顺序接收，若版本不一致，对操作执行 transform 后再应用。
   - 服务端广播转换后的操作，客户端将本地未确认操作与之再次 transform。
   - 会话内维护最新版本号、历史操作列表，可定期落盘至 `edit_logs`。

2. **数据结构**
   - `operations`: OT 操作数组。
   - `version`: 当前文档版本号。
   - `cursor`: 协作者光标信息（位置、选区、颜色）。

3. **保存策略**
   - 客户端主动触发 `save_request` 或服务端定时（如 30s）落地。
   - 服务器将当前文档内容写入 `document_versions`，并生成 diff。

4. **扩展方向**
   - 引入 CRDT（如 Yjs）以支持离线/冲突自动合并。
   - 将会话状态托管至 Redis，支持多节点扩缩容。
   - 记录富文本格式（Delta 格式）以便表格/图片扩展。

## 当前仓库中的实现留白

- `backend/app/services/collab_service.py`: 维护会话状态的占位逻辑，可替换为专业协同引擎。
- `backend/app/api/routes/collab.py`: WebSocket 消息处理骨架，预留 `cursor_update` / `edit_operation` / `heartbeat`。
- 前端 `EditorPage.vue`: 建立 WebSocket 连接并发送占位消息，后续可引入 yjs/quill-delta 同步。

