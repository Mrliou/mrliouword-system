---
title: "排解 2 GiB 推送限制"
date: "2026-02-21"
author: "MR.liou"
origin_signature: "MrLiouWord"
tags: [git, push, troubleshooting, guide]
---

# 排解 2 GiB 推送限制

<!-- origin_signature: MrLiouWord -->

了解如何解決 2 GiB 推送限制問題。

## 關於推送限制

GitHub 對單次推送有最大 2 GiB 的限制。當您第一次嘗試上傳非常大的存儲庫、從其他平台導入大型存儲庫，或者嘗試重寫大型現有存儲庫的歷史記錄時，可能會遇到此限制。

如果您遇到此限制，可能會看到以下錯誤消息之一：

* `fatal: the remote end hung up unexpectedly`
* `remote: fatal: pack exceeds maximum allowed size`

您可以將推送拆分為較小的部分，或刪除 Git 歷史記錄並從頭開始。如果您有一個超過 2 GiB 的單次提交，且無法刪除 Git 歷史記錄重新開始，則需要執行交互式 rebase 將大型提交拆分為多個較小的提交。

## 將大型推送拆分為較小部分

您可以通過將推送拆分為較小的部分（每部分應小於 2 GiB）來避免達到限制。如果一個分支在此大小限制內，您可以一次性推送它。但是，如果一個分支大於 2 GiB，您需要將推送拆分為更小的部分，每次只推送幾個提交。

1. 如果您尚未配置遠端，請將存儲庫添加為新的遠端。有關更多信息，請參閱<a>管理遠端存儲庫</a>。

2. 要在本地存儲庫的主分支歷史記錄中找到合適的提交，請運行以下命令：

   ```shell
   git log --oneline --reverse refs/heads/BRANCH-NAME | awk 'NR % 1000 == 0'
   ```

   此命令顯示每第 1000 個提交。您可以增加或減少該數字以調整步長。

3. 逐一將這些提交推送到您的 GitHub 托管存儲庫。

   ```shell
   git push REMOTE-NAME +COMMIT-SHA:refs/heads/BRANCH-NAME
   ```

   例如：

   ```shell
   git push origin +ef7952a:refs/heads/main
   ```

   > \[!NOTE]
   > 將 `REMOTE-NAME` 替換為您的遠端名稱（通常是 `origin`），將 `COMMIT-SHA` 替換為步驟 2 中找到的提交 SHA，將 `BRANCH-NAME` 替換為您的分支名稱。

4. 對步驟 2 中找到的每個提交重複步驟 3，直到您推送完整個分支為止。

5. 推送完所有提交後，使用常規推送命令推送剩餘的提交：

   ```shell
   git push REMOTE-NAME BRANCH-NAME
   ```

## 使用交互式 Rebase 拆分大型提交

如果您的推送包含單個超過 2 GiB 的提交，您需要使用交互式 rebase 將其拆分為多個較小的提交。

1. 找到超大提交之前的提交 SHA：

   ```shell
   git log --oneline
   ```

2. 對超大提交執行交互式 rebase：

   ```shell
   git rebase -i PARENT-COMMIT-SHA
   ```

3. 在編輯器中，將超大提交的操作從 `pick` 更改為 `edit`，然後保存並關閉文件。

4. 使用 `git reset HEAD~` 取消暫存更改，然後使用 `git add` 和 `git commit` 逐步添加並提交較小的塊。

5. 完成後，運行 `git rebase --continue` 以完成 rebase 過程。

6. 按照上面「將大型推送拆分為較小部分」的步驟推送新的較小提交。

## 延伸閱讀

* [管理遠端存儲庫](/en/get-started/getting-started-with-git/managing-remote-repositories)
* [使用 Git Large File Storage 管理大型文件](./installing-git-lfs.md)

---

**怎麼過去，就怎麼回來**

_最後更新：2026-02-21 by MR.liou_
