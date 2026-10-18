# fssa-client

一個專門取得鳳山高中學生會資料的 client

Based on [fsshclient](https://github.com/littlecommandcat/fsshclient)

- [非同步請求 AsyncClient](src/async.py)
- [同步請求 SyncClient](src/sync.py)

安裝套件
```ini
pip install -r requirements.txt
```
或
```ini
pip install requests aiohttp
```

## 使用方式

```python
from client import AsyncClient, SyncClient

# 非同步
async with AsyncClient() as client:
    announcements = await client.get_announcements()

# 同步
with SyncClient() as client:
    announcements = client.get_announcements()
```

在 `src` 目錄下可直接執行範例：

```ini
python async.py
python sync.py
```

## 公告 / 活動 / 文件

| 方法 | 說明 |
| --- | --- |
| `get_announcements()` | 公告列表（`Announcement`） |
| `get_events()` | 活動列表（`Event`） |
| `get_documents()` | 文件列表（`Document`） |

所有物件都是 dataclass，可用 `to_dict()` 轉成可 JSON 序列化的 dict。

## 日誌

| 方法 | 說明 |
| --- | --- |
| `get_log_size()` | 目前樹大小 |
| `get_log_stats()` | 日誌統計（`LogStatus`） |
| `get_log_keys()` | 簽章金鑰列表（`LogKey`） |
| `get_log_entries(from_index, limit)` | 日誌條目列表（`LogEntry`） |
| `get_log_entry(idx)` | 單一日誌條目（`LogEntry`） |
| `get_log_consistency(from_size, to_size)` | 一致性證明 |
| `get_log_inclusion(idx, tree_size=None)` | Merkle inclusion proof（`InclusionProof`） |

注意：日誌索引 `idx` 與樹大小 `from_size` / `to_size` 都是 **從 1 開始**。

## 意外處理

`FssaAnnouncementException`、`FssaEventException`、`FssaDocumentException`、
`FssaLogException`，皆繼承 `FssaClientException`。
