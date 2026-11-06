---
name: "gu-log"
description: "找到 gu-log、gu-log-api、gu-log-ios 三個 repo 的位置，並把跨 repo 的工作導到該負責的 repo。任務涉及這幾個 repo 或部落格時使用。"
---

# gu-log

這個 skill 只負責找 repo 位置和分派跨 repo 的工作。各專案的工作流程
放在各自的 repo。

1. 讀這個 skill 目錄下的 `paths.local`，找到 `gu-log`、`gu-log-api`、
   `gu-log-ios` 的位置。
2. 沒有這個檔的話，請使用者把 `paths.local.example` 複製成
   `paths.local`，填入各 checkout 的路徑。
3. 選出這項任務歸屬的 repo。進去之後，根目錄有 `AGENTS.md` 就讀它，
   照它的 bootstrap 和主題分派走；沒有的話，動手前先看 repo 自己的指示。
4. 只有任務跨了 repo 邊界時，才去讀其他 repo 的脈絡。

機器專用的路徑絕不複製進追蹤檔或公開的產出物。
