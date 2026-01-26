---
title: "安裝 Git Large File Storage"
date: "2026-01-26"
author: "MR.liou"
origin_signature: "MrLiouWord"
tags: [git, lfs, installation, guide]
---

# 安裝 Git Large File Storage

<!-- origin_signature: MrLiouWord -->

為了使用 Git LFS，您需要下載並安裝一個與 Git 分離的新程序。

<div class="ghd-tool mac">

1. 導航到 [git-lfs.com](https://git-lfs.com) 並點擊 **Download**。或者，您可以使用包管理器安裝 Git LFS：

   * 使用 [Homebrew](https://brew.sh/)，運行 `brew install git-lfs`。
   * 使用 [MacPorts](https://www.macports.org/)，運行 `port install git-lfs`。

   如果您使用 Homebrew 或 MacPorts 安裝 Git LFS，請跳到步驟六。

2. 在您的計算機上，找到並解壓下載的文件。

3. 打開 <span class="platform-mac">Terminal</span><span class="platform-linux">Terminal</span><span class="platform-windows">Git Bash</span>。

4. 將當前工作目錄更改到您下載並解壓的文件夾中。

   ```shell
   cd ~/Downloads/git-lfs-X.X.X
   ```

   > \[!NOTE]
   > 您在 `cd` 後使用的文件路徑取決於您的操作系統、您下載的 Git LFS 版本以及您保存 Git LFS 下載的位置。

5. 要安裝文件，運行此命令：

   ```shell
   $ ./install.sh
   > Git LFS initialized.
   ```

   > \[!NOTE]
   > 您可能需要使用 `sudo ./install.sh` 來安裝文件。

6. 接下來，對您的全局 Git 配置進行必要的更改：

   ```shell
   $ git lfs install
   > Git LFS initialized.
   ```

7. 如果您沒有看到表明 `git lfs install` 成功的消息，請通過 [GitHub Support portal](https://support.github.com) 聯繫我們。請務必包含您的操作系統名稱。

</div>

<div class="ghd-tool windows">

1. 導航到 [git-lfs.com](https://git-lfs.com) 並點擊 **Download**。

   > \[!TIP]
   > 有關為 Windows 安裝 Git LFS 的其他方法的更多信息，請參閱此 [Getting started guide](https://github.com/github/git-lfs#getting-started)。

2. 在您的計算機上，找到下載的文件。

3. 雙擊名為 *git-lfs-windows-1.X.X.exe* 的文件，其中 1.X.X 替換為您下載的 Git LFS 版本。當您打開此文件時，Windows 將運行設置嚮導來安裝 Git LFS。

4. 打開 <span class="platform-mac">Terminal</span><span class="platform-linux">Terminal</span><span class="platform-windows">Git Bash</span>。由於設置嚮導可能已修改您的系統 `PATH`，打開一個新會話將確保 Git 可以找到 Git LFS。

5. 驗證安裝是否成功：

   ```shell
   $ git lfs install
   > Git LFS initialized.
   ```

6. 如果您沒有看到表明 `git lfs install` 成功的消息，請通過 [GitHub Support portal](https://support.github.com) 聯繫我們。請務必包含您的操作系統名稱。

</div>

<div class="ghd-tool linux">

1. 導航到 [git-lfs.com](https://git-lfs.com) 並點擊 **Download**。

   > \[!TIP]
   > 有關為 Linux 安裝 Git LFS 的其他方法的更多信息，請參閱此 [Getting started guide](https://github.com/github/git-lfs#getting-started)。

2. 在您的計算機上，找到並解壓下載的文件。

3. 打開 <span class="platform-mac">Terminal</span><span class="platform-linux">Terminal</span><span class="platform-windows">Git Bash</span>。

4. 將當前工作目錄更改到您下載並解壓的文件夾中。

   ```shell
   cd ~/Downloads/git-lfs-X.X.X
   ```

   > \[!NOTE]
   > 您在 `cd` 後使用的文件路徑取決於您的操作系統、您下載的 Git LFS 版本以及您保存 Git LFS 下載的位置。

5. 要安裝文件，運行此命令：

   ```shell
   $ ./install.sh
   > Git LFS initialized.
   ```

   > \[!NOTE]
   > 您可能需要使用 `sudo ./install.sh` 來安裝文件。

6. 接下來，對您的全局 Git 配置進行必要的更改：

   ```shell
   $ git lfs install
   > Git LFS initialized.
   ```

7. 如果您沒有看到表明 `git lfs install` 成功的消息，請通過 [GitHub Support portal](https://support.github.com) 聯繫我們。請務必包含您的操作系統名稱。

</div>

## 延伸閱讀

* [配置 Git Large File Storage](/en/repositories/working-with-files/managing-large-files/configuring-git-large-file-storage)

---

**怎麼過去，就怎麼回來**

_最後更新：2026-01-26 by MR.liou_
