# Death Star Management System 仪表盘本地运行指南

## 目录结构

```
├── Phase2.html           # 主前端页面
├── gauge-server.js       # WebSocket 服务端（Node.js）
├── styles.css            # 样式文件
├── main.js               # 其它JS逻辑（如有）
```

## 运行环境要求
- Node.js（建议 16+）
- 推荐使用 VSCode + Live Server 插件 或 Python/Node 本地服务器

---

## 步骤一：启动 WebSocket 服务端

1. 安装依赖（仅首次需要）：
   ```bash
   npm install ws
   ```
2. 启动服务端：
   ```bash
   node gauge-server.js
   ```
   启动后会看到：
   ```
   WebSocket server running at ws://localhost:8080/updates
   ```

---

## 步骤二：本地启动前端页面

**不要直接用 file:// 打开 HTML 文件！**

推荐方法一：VSCode Live Server 插件
1. 安装 Live Server 插件
2. 右键 `Phase2.html`，选择"Open with Live Server"
3. 浏览器访问 `http://localhost:5500/Phase2.html`（端口可能不同）

推荐方法二：Python 本地服务器
```bash
python3 -m http.server 8000
```
然后浏览器访问：
```
http://localhost:8000/Phase2.html
```

推荐方法三：Node http-server
```bash
npx http-server .
```
然后浏览器访问：
```
http://localhost:8080/Phase2.html
```

---

## 步骤三：体验实时仪表盘

1. 打开页面后，Dashboard 区域会显示 Energy、Droid、Facilities 三个仪表盘。
2. 仪表盘会每2秒自动收到 WebSocket 推送的随机数据并实时更新。
3. 当某项数值低于阈值时，右上角会弹出红色警告 toast。

---

## 常见问题

- **页面中间一直加载？**
  > 请确认已用本地服务器打开页面，并已替换为仪表盘区域。

- **仪表盘无数据？**
  > 请确认 gauge-server.js 正常运行，且前端 WebSocket 地址为 `ws://localhost:8080/updates`。

- **端口冲突？**
  > 可修改 gauge-server.js 里的端口号，前端 WebSocket 地址也要同步修改。

---

## 其它说明
- 你可以修改 `gauge-server.js` 让其推送真实业务数据。
- 仪表盘样式和阈值可在 Phase2.html 里自定义。

---

如有问题请联系本项目维护者。 