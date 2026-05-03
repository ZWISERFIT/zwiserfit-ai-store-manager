# DeepSeek 聊天记录导出指南（5 分钟版）

> 写给 Shuyu 总指挥 · 2026-05-03 · ⚙️ Tristan 编制

---

## 方法一：浏览器扩展（推荐，2 分钟）

最简单，一键导出，支持 Markdown / JSON / HTML。

### 步骤

| # | 操作 | 说明 |
|---|------|------|
| 1 | 打开 Chrome 或 Edge 浏览器 | 必须用电脑操作 |
| 2 | 访问 Chrome 应用商店，搜索 **"DeepSeek Chat Exporter"** | 或直接搜 `DeepSeek export` |
| 3 | 点击 **"添加到 Chrome"** | 免费，无需注册 |
| 4 | 打开 chat.deepseek.com，登录您的账号 | |
| 5 | 点击浏览器右上角 🧩 扩展图标 → 点击刚装的扩展 | |
| 6 | 选择导出格式 → **Markdown**（推荐）或 **JSON** | Markdown 我处理最方便 |
| 7 | 点击 **"Export All"** 或 **"导出全部"** | 等待几秒即可 |
| 8 | 把下载的文件发给我 | 拖到对话框就行 ✅ |

---

## 方法二：浏览器控制台脚本（3 分钟，无需安装任何东西）

如果您不想装扩展，直接在浏览器里跑一段代码就行。

### 步骤

| # | 操作 |
|---|------|
| 1 | 打开 Chrome/Edge，访问 **chat.deepseek.com** 并登录 |
| 2 | 按键盘 **F12**（或 `Ctrl+Shift+I`），打开开发者工具 |
| 3 | 点击顶部 **Console**（控制台）标签 |
| 4 | 把下面的代码**完整复制**，粘贴到控制台，按 **回车** |
| 5 | 等待几秒，浏览器会自动下载一个 `.json` 文件 |
| 6 | 把下载的 `deepseek-chats.json` 文件发给我 |

### 复制以下全部代码：

```javascript
(async () => {
  // DeepSeek 聊天记录一键导出脚本
  const DB_NAME = 'deepseek-chat';
  const STORE_NAME = 'conversations';
  
  const req = indexedDB.open(DB_NAME);
  req.onsuccess = (event) => {
    const db = event.target.result;
    const tx = db.transaction(STORE_NAME, 'readonly');
    const store = tx.objectStore(STORE_NAME);
    const getAll = store.getAll();
    getAll.onsuccess = () => {
      const data = getAll.result;
      const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'deepseek-chats.json';
      a.click();
      URL.revokeObjectURL(url);
      console.log('✅ 导出完成！共 ' + data.length + ' 条对话');
    };
    getAll.onerror = () => {
      console.log('⚠️ 方法1失败，尝试备用方案...');
      // 备用：尝试从 localStorage 读取
      const keys = Object.keys(localStorage).filter(k => k.includes('chat') || k.includes('conversation'));
      const chats = keys.map(k => ({key: k, value: localStorage.getItem(k)}));
      const blob2 = new Blob([JSON.stringify(chats, null, 2)], {type: 'application/json'});
      const url2 = URL.createObjectURL(blob2);
      const a2 = document.createElement('a');
      a2.href = url2;
      a2.download = 'deepseek-chats-backup.json';
      a2.click();
      URL.revokeObjectURL(url2);
      console.log('✅ 备用方案完成！共 ' + chats.length + ' 条数据');
    };
  };
  req.onerror = () => console.error('❌ 无法访问 DeepSeek 数据库，请确认已登录 chat.deepseek.com');
})();
```

---

## 方法三：手动导出（兜底方案）

如果以上都不行：

1. 在 DeepSeek 网页端，逐条打开对话
2. 点击对话右上角的 **"..."** 或 **分享按钮**
3. 选择 **"复制"** 或 **"导出"**
4. 粘贴到记事本，保存为 `.txt`，发给我

---

## 📋 我收到文件后会做什么

1. **格式解析** → 将 JSON/Markdown 转为结构化对话数据
2. **去重清洗** → 去除重复、空对话、系统消息
3. **角色标注** → 区分「你说的话」和「DeepSeek 的回复」
4. **归档入库** → 存入 铸魂 任务数据目录 `data/soul-casting/`
5. **生成报告** → 输出对话画像摘要，供您审阅

---

> ⚙️ 有问题随时叫我。文件拖过来我就开始处理。
