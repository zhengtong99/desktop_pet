# Desktop Pet 桌面宠物

A cute, always-on-top desktop companion — inspired by VS Code Pets, but it's a
real person (or people!) cut out from your favorite photos. It hops when you
poke it, chats in Chinese & English, teaches you English and friendly Chinese
language/culture cards you can hear out loud, celebrates holidays with
fireworks and falling emoji, and shows the local weather in a playful bilingual
bubble.

一个可爱的桌面小伙伴：把你喜欢的照片抠出人物，透明无边框、始终置顶。点它会跳、会
说中英文悄悄话、教你英语和简短的中文/中国文化还能点击发音、逢年过节放烟花/飘雪花，
还会用有趣的语气播报当地天气。

**100% Python • macOS & Windows • free for personal, non-commercial use.**
**无需任何编程知识，下载即用 · 仅供个人非商业使用。**

> **Disclaimer 免责声明**: Unofficial, non-commercial, fan-made — not affiliated
> with or endorsed by any artist. Photos belong to their owners; you add your
> own and are responsible for them. Rights holders may request takedown at
> **jtanpp0319@gmail.com**. See [DISCLAIMER.md](DISCLAIMER.md).
> 非官方·非商业·粉丝自制，与艺人无关；照片版权/肖像权归原权利人，用户自行
> 添加并负责；权利人可联系 **jtanpp0319@gmail.com** 删除。详见 [DISCLAIMER.md](DISCLAIMER.md)。

---

## Contents 目录

1. [Download & install 下载安装](#1-download--install-下载安装)
2. [How to use 使用方法](#2-how-to-use-使用方法)
3. [Use your own photos 换成你自己的照片](#3-use-your-own-photos-换成你自己的照片)
4. [Weather & privacy 天气与隐私](#4-weather--privacy-天气与隐私)
5. [Troubleshooting / FAQ 常见问题](#5-troubleshooting--faq-常见问题)
6. [Uninstall 卸载](#6-uninstall-卸载)
7. [For developers 开发者](#7-for-developers-开发者)

---

## 1. Download & install 下载安装

You do **not** need Python or any other software. 无需安装 Python 或任何专业软件。

### Step 1 — Download 下载

Go to the **[Releases](../../releases)** page and download the file for your
computer. 打开本项目的 **Releases（发布）** 页面，下载对应你系统的文件：

| Your computer 你的电脑 | Download this 下载这个 |
| --- | --- |
| 🍎 **Mac** (macOS) | `DesktopPet-macOS.zip` |
| 🪟 **Windows** (Win 10/11) | `DesktopPet-Windows.zip` |

### Step 2 — Unzip 解压

Double-click the downloaded `.zip` to unzip it. 双击下载好的压缩包解压。

### Step 3 — Open the app 打开程序

<details open>
<summary><b>🍎 On Mac</b></summary>

1. Double-click **`Desktop Pet.app`**.
2. The **first time only**, macOS protects you from apps it can't verify. If you
   see *“Desktop Pet can't be opened”*:
   - **Right-click** (or Control-click) the app → choose **Open** → click
     **Open** again in the dialog.
   - (On newer macOS you may instead go to  → **System Settings → Privacy &
     Security**, scroll down, and click **Open Anyway**.)
3. After the first time, you can just double-click it normally.

首次打开若提示“无法验证开发者/无法打开”，请 **右键点击 App → 打开 → 再点“打开”**；
或到 **系统设置 → 隐私与安全性** 里点击 **仍要打开**。之后正常双击即可。
</details>

<details>
<summary><b>🪟 On Windows</b></summary>

1. Open the unzipped **`Desktop Pet`** folder.
2. Double-click **`Desktop Pet.exe`**.
3. The **first time only**, Windows SmartScreen may pop up. Click
   **More info → Run anyway**.

首次运行若出现蓝色 SmartScreen 提示，点击 **更多信息 → 仍要运行**。
</details>

✅ **Done!** Your pet appears in a corner of the screen. 完成！桌面宠物就会出现在
屏幕角落啦。

> These security prompts appear because the app is free and unsigned — it is
> safe and source-available. 这些提示是因为程序免费未签名、源码公开，可放心使用。

---

## 2. How to use 使用方法

| Action 操作 | What happens 效果 |
| --- | --- |
| **Drag with left mouse button** 按住左键拖动 | Move the pet anywhere 移动位置 |
| **Click (tap) the pet** 左键单击 | Poke it — it jumps / squashes / shakes in turn 戳一下，轮流跳跃/压扁回弹/抖动 |
| **Mouse wheel** 鼠标滚轮 | Make the pet bigger / smaller 放大或缩小 |
| **Right-click the pet** 右键单击 | Open the menu 打开菜单 ↓ |

**Right-click menu 右键菜单：**

- **调整大小 / Size** — pick Small / Medium / Large / X-Large 选择大小
- **换一个 / Switch character** — show a different photo 换一张照片
- **陪我聊聊 / Say hi** — a random cute line 随机可爱对白
- **学个英语 / Learn English** — a daily English word/phrase 学一个英语词句
- **学中文和文化 / Learn Chinese** — short Chinese phrases, pinyin, English meaning, culture notes, and pronunciation 学简短中文、拼音、英文解释、文化小知识和发音
- **今天天气 / Weather** — show the current weather 显示天气播报
- **庆祝一下 / Celebrate** — fireworks / confetti 放个烟花彩带
- **立即同步素材 / Sync library now** — force an instant re-scan of `pic` (changes are also detected automatically within a second or two) 立刻强制按 `pic` 同步（平时改动也会在一两秒内自动同步）
- **始终置顶 / Always on top** — keep the pet above other windows 是否总在最前
- **退出 / Quit** — close the app 关闭程序

The pet also **greets you** when it starts, floats **random cute lines**,
**celebrates festivals** automatically (Spring Festival fireworks 🧨, Christmas
snow 🎄, and more), and **tells you the weather**. It also has fixed birthday
celebrations on **11/17** (Ayden) and **2/27** (Elio). 启动会打招呼、随机冒出可爱对白、节日自动庆祝、
并播报天气；并在 **11/17** (政) 与 **2/27** （瞳） 触发固定生日庆祝。

### Learn a little English 顺便学英语 🔊

Every so often (or from the right-click **Learn English** menu) the pet shows a
handy American-English **word, phrase, or everyday expression** with its Chinese
meaning. Tap the **🔊 speaker** on the bubble to hear it pronounced aloud — it
uses your computer's built-in voice, so it works offline with no setup.
宠物会时不时（或通过右键菜单“学个英语”）弹出一个地道美式英语的单词/短语/日常表达和
中文意思；点气泡上的 **🔊 小喇叭** 就能听发音，使用系统自带语音，离线也能用。

### Learn a little Chinese and culture 学中文和中国文化 🔊

Choose **学中文和文化 / Learn Chinese** from the right-click menu.
Each short card shows **Chinese characters, pinyin, a friendly English meaning,
and one small culture note**. Tap the **🔊 speaker** to hear the Chinese phrase
pronounced aloud by your computer's built-in voice.
右键选择“学中文和文化”，每张卡片会显示汉字、拼音、简短英文意思和一条文化小知识；
点击 **🔊 小喇叭** 即可听中文发音。内容简短，适合中文初学者。

The app explicitly requests a Mandarin (`zh-CN`) system voice for these cards.
A Chinese keyboard/input method is separate from a Chinese speech voice. If
your Mac still reads Chinese incorrectly, open **System Settings → Accessibility
→ Read & Speak → System Voice** and download/select a Chinese voice (for
example, the built-in **Eddy (Chinese (China mainland))** voice used by the app).
程序会为中文卡片明确请求普通话（`zh-CN`）系统语音；中文输入法和中文语音是两回事。
如果 Mac 仍然发音不正确，请到“系统设置 → 辅助功能 → 阅读与朗读 → 系统声音”下载并选择
中文（中国大陆）语音。

On Windows 10/11, the app asks Windows Speech for a `zh-CN` voice. A Chinese
keyboard is separate from a Chinese speech voice. If the pronunciation is
wrong or silent, open **Settings → Time & language → Language & region**,
install **Chinese (Simplified, China)** and its speech/language features, then
restart the app. Windows uses PowerShell/System.Speech and needs no Python.
Windows 10/11 会请求 `zh-CN` 普通话语音；中文输入法和中文语音是两回事。如果没有声音或发音
不正确，请到“设置 → 时间和语言 → 语言和区域”安装“中文（简体，中国）”及语音相关功能，
然后重启程序。Windows 版本不需要安装 Python。

### Auto-learning frequency by location 根据位置自动调整学习内容

The pet learns your **approximate location from your IP address** and adjusts
what it teaches you. **No tracking — only used to pick learning content.**

| Location | English | Chinese | Chitchat |
| --- | --- | --- | --- |
| 🇨🇳 **China IP** | 60% | 10% | 30% |
| 🌍 **Other countries** | 20% | 50% | 30% |

Example: if you're in China, you'll get mostly English lessons (60%) sprinkled
with random chat (30%) and occasional Chinese culture cards (10%) — perfect for
learning English. Outside China, you'll get mostly Chinese lessons (50%) with
some English and chat — ideal for learning Chinese!
宠物会根据你的 IP 地址推测位置，自动调整学习内容（仅用于选择教学内容，不进行追踪）。
在中国，主要弹出英语（60%）、随机闲聊（30%）、和少量中文（10%）；在其他国家，主要弹出
中文（50%）、英语（20%）、闲聊（30%）。

---

## 3. Use your own photos 换成你自己的照片

This is the fun part! You can replace the sample people with **your own photos**
— friends, family, pets, idols, anyone. The app automatically removes the
background and turns each photo into a see-through desktop character. No editing
software, no Photoshop, no coding. 这一节教你把桌面宠物换成**你自己的照片**（家人、
朋友、偶像都行）。程序会自动抠掉背景，无需任何修图软件或编程。

### 3.1 Which folder do I use? 应该放到哪个文件夹？

There are two different `pic` folders — use the right one for how you got the
app. 有两个 `pic` 文件夹，按你的使用方式选对的那个：

| How you use the app 使用方式 | Put your photos here 放照片的位置 |
| --- | --- |
| **Downloaded app** (most people) 下载的应用（大多数人） | The **`DesktopPet/pic`** folder in your **home folder** 你“个人主目录”里的 `DesktopPet/pic` |
| **Running from source** (developers) 源码运行（开发者） | The project's own **`pic/`** folder 项目自带的 `pic/` 文件夹 |

> ⚠️ For the downloaded app, do **not** look for a `/pic` folder inside the app
> itself — always use the **`DesktopPet/pic`** folder in your home folder. 下载版
> 请使用主目录里的 `DesktopPet/pic`，不要去应用内部找。

### 3.2 Find the folder 找到文件夹（详细步骤）

The `DesktopPet` folder is created **the first time you open the app**, so run
the app once first. 第一次打开程序后，`DesktopPet` 文件夹才会生成，所以请先运行一次。

<details open>
<summary><b>🍎 On Mac — step by step</b></summary>

1. Open **Finder**. 打开访达（Finder）。
2. In the top menu bar, click **Go → Home** (or press **⇧⌘H**). 点顶部菜单
   **前往 → 个人（主目录）**，或按 **⇧⌘H**。
3. Open the **`DesktopPet`** folder, then the **`pic`** folder inside it. 打开
   **`DesktopPet`** 文件夹，再进入里面的 **`pic`**。

Path 路径：`/Users/<your name>/DesktopPet/pic`
</details>

<details>
<summary><b>🪟 On Windows — step by step</b></summary>

1. Open **File Explorer** (the yellow folder icon). 打开“文件资源管理器”。
2. In the address bar at the top, type **`%USERPROFILE%\DesktopPet\pic`** and
   press **Enter**. 在顶部地址栏输入 **`%USERPROFILE%\DesktopPet\pic`** 回车。
3. That opens your picture folder directly. 就会直接打开图片文件夹。

Path 路径：`C:\Users\<your name>\DesktopPet\pic`
</details>

Inside you'll see the **sample photos** that came with the app. 里面是程序自带的
示例照片。

### 3.3 Add your own photos 放入你自己的照片

1. **Delete the samples (optional) 删除示例（可选）** — select the sample photos
   and delete them if you only want your own. 想只用自己的照片，就把示例删掉。
2. **Copy your photos in 复制照片进去** — drag or copy any
  **`.jpg` / `.jpeg` / `.png` / `.webp` / `.bmp` / `.tif` / `.tiff` / `.heic` / `.heif`**
  photos (or **`.mp4` / `.mov` / `.m4v`** live photos) into the `pic` folder.
  把 `.jpg/.jpeg/.png/.webp/.bmp/.tif/.tiff/.heic/.heif` 照片（或 `.mp4/.mov/.m4v` live 实拍）拖进 `pic`。
   - 📸 **Best results 效果最好的照片**: a clear photo where the **person stands
     out from the background** (full body or upper body). 人物清晰、和背景区分明显、
     全身或半身照效果最好。
   - You can add **as many as you like**. 想加多少张都可以。
3. **Done! 完成！** The app watches the `pic` folder and starts syncing after
  a short delay — no restart needed. AI processing may take several seconds.
  Want to start it immediately? Right-click the pet →
  **立即同步素材 / Sync library now**.
  程序会自动监测 `pic` 文件夹变化并开始同步，无需重启；AI 抠图可能需要几秒钟，想立即
  开始也可以右键宠物 → 立即同步素材。
   程序会自动抠图，新宠物就出现啦。

### 3.4 How the daily switch works 每天换一张的规则

- 🗓️ **Multiple photos 多张照片** → the app shows a **random one each day**, and
  keeps the same one for the whole day. 每天随机挑一张，当天不再变。
- 🖼️ **One photo 只有一张** → it always shows that one. 一直用这一张。
- 🔀 **Want a different one right now? 想马上换一张？** Right-click the pet →
  **换一个 / Switch character**. 右键 → 换一个。

### 3.5 Good to know 小贴士

- 👨‍👩‍👧 **Group photos work** — everyone in the picture is kept together as one
  pet. 合照也支持，会把照片里所有人一起保留成一个宠物。
- 🎬 **Live photos become animated pets** — drop in a `.mp4` / `.mov` / `.m4v` and the app cuts
  out several frames so the pet gently **loops** (still photos stay still).
  放入 `.mp4/.mov/.m4v` live 实拍，会抠出多帧让宠物**循环动起来**（普通照片仍为静态）。
- 🌐 The **first time** a brand-new photo is processed, the app downloads a small
  AI model **once** (needs internet that one time). After that it works offline.
  首次处理新照片会联网下载一次抠图模型，之后离线也能用。
- 🗑️ **Delete a photo** from the `pic` folder and its generated pet is removed
  automatically after the next sync (or immediately via **Sync library now**).
  从 `pic` 删掉照片后，程序会在下一次同步时自动清理对应宠物（也可点“立即同步素材”立刻开始）。
- ⏳ Processing a new photo takes a few seconds — the pet will let you know when a
  new friend is ready. 处理新照片需要几秒，完成后宠物会提示“新朋友准备好啦”。

---

## 4. Weather & privacy 天气与隐私

To tell you the weather, the app looks up your **approximate city** from your IP
address (via `ip-api.com`) and fetches the forecast from `open-meteo.com`. It
picks °C or °F automatically based on your country. Each report displays the
weather condition, temperature labels, and a short tip in **Chinese and
English**, for example: `现在Now 23°C，最高High 27°C / 最低Low 18°C。` 天气功能会根据
IP 获取大致城市并查询天气，自动选择摄氏或华氏；天气状态、温度标签和简短提示均为中英双语。

**Your privacy 隐私：** no account, no tracking, nothing is stored or uploaded.
If you're offline, the pet simply stays quiet about the weather. 不注册、不追踪、
不上传任何数据；离线时不播报天气。

---

## 5. Troubleshooting / FAQ 常见问题

**Q: How do I close / quit the pet? 怎么关闭程序？**
Right-click the pet → **退出 / Quit**. 右键点击宠物 → 退出。

**Q: The pet disappeared! 宠物不见了？**
It may be behind a window — it stays on top by default, but check the corners of
your screen, or other monitors. Reopen the app if needed. 可能在屏幕角落或其他显示
器；重新打开程序即可。

**Q: It's covering something I need. 挡住东西了？**
Just drag it away with the left mouse button, or make it smaller with the mouse
wheel. 用左键把它拖走，或用滚轮缩小。

**Q: Mac says the app is damaged / can't be opened. Mac 提示已损坏/无法打开？**
This is the unsigned-app warning. Right-click the app → **Open**, or allow it in
**System Settings → Privacy & Security → Open Anyway**. 见上方安装步骤的“首次打开”
说明。

**Q: Nothing happens / no pet appears. 打开后没有宠物？**
Make sure there is at least one supported photo (`.jpg/.jpeg/.png/.webp/.bmp/.tif/.tiff/.heic/.heif`) in the `DesktopPet/pic`
folder (or a live clip: `.mp4/.mov/.m4v`), then reopen. 确认 `DesktopPet/pic` 里至少有一张受支持格式照片（或 `.mp4/.mov/.m4v` live 文件），再重新打开。

**Q: I deleted photos but old pets still appear. 我删了照片但旧宠物还在？**
The app watches `pic` and starts a sync after a short delay. If you need it to
happen immediately, right-click the pet and choose
**立即同步素材 / Sync library now**.
程序会监测 `pic` 变化并自动开始同步；想立即开始，右键宠物点“立即同步素材”即可。

**Q: My settings are stored where? 设置存在哪？**
`~/.config/desktop_pet/settings.json` (Mac) or `%APPDATA%\DesktopPet` (Windows).
Delete it to reset position and size. 删除该文件可重置位置和大小。

---

## 6. Uninstall 卸载

1. Quit the pet (right-click → Quit). 退出程序。
2. Delete the app (`Desktop Pet.app` / the `Desktop Pet` folder). 删除程序。
3. (Optional) Delete the `DesktopPet` folder in your home folder and the settings
   file above to remove everything. （可选）删除主目录下的 `DesktopPet` 文件夹和上面
   的设置文件即可彻底清除。

No other files are installed anywhere. 程序不会在系统其他位置安装任何文件。

---

## 7. For developers 开发者

Run from source & use your own photos.

### 1. Set up 环境准备

```bash
git clone https://github.com/zhengtong99/desktop_pet.git
cd desktop_pet
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
```

### 2. Add your own pictures 换成你自己的照片

Drop any photos (`.jpg` / `.jpeg` / `.png` / `.webp` / `.bmp` / `.tif` / `.tiff` / `.heic` / `.heif` / `.mp4` / `.mov` / `.m4v`) into the `pic/` folder — that's it.
The running app watches `pic/` and starts syncing after a short delay; AI
processing can take several seconds. Use **Sync library now** from the pet menu
to start a sync immediately instead. If
multiple photos are present it shows a random one each day; a single photo is
always used.
把照片放进 `pic/` 即可，运行时自动抠图；多张每天随机，一张一直用。

Multi-person photos work too — everyone in the shot is kept. 合照也支持，会保留所有人。

You can also pre-generate the cut-outs manually (optional):

```bash
python tools/remove_bg.py        # AI removes backgrounds -> assets/pets/ (png or live frame folders)
```

This uses [rembg](https://github.com/danielgatis/rembg) (downloads a ~176 MB
model the first time).

### 3. Run 运行

```bash
python run.py
```

Need a snappier startup while you are working? Use:

```bash
python run.py --fast-start
```

This skips the startup weather request (all other behavior stays the same).
如果你想要更快的启动体感，可用 `--fast-start` 跳过开机天气请求（其余功能不变）。

During runtime, adding/deleting files in `pic/` starts an automatic sync after a
short delay; AI processing can take several seconds. Use **立即同步素材 / Sync
library now** to start it immediately.
运行中增删 `pic/` 内容会自动开始同步，AI 抠图可能需要几秒；点 **立即同步素材** 可立即开始。

### 4. Run tests 运行测试

```bash
python -m pytest -q
```

### 5. Optional settings 可选设置

Settings are saved automatically to a per-user file
(`~/.config/desktop_pet/settings.json`, or `%APPDATA%\DesktopPet` on Windows).

### 6. Build a distributable app 打包成可分发的应用

```bash
python tools/make_icon.py                          # make the app icon
pyinstaller build/desktop_pet.spec --noconfirm     # -> dist/
```

Or just push a `v*` git tag — the included **GitHub Actions** workflow
(`.github/workflows/build.yml`) automatically builds **both** macOS and Windows
apps and attaches them to the release. 打个 `v*` 标签即可自动构建 Mac 和 Windows 版本。

---

## Project layout 项目结构

```
pic/                    your source photos 原始照片
assets/pets/            transparent cut-outs used by the app 抠好的透明立绘
pet/                    the application (PySide6) 应用程序代码
  app.py                entry point / QApplication
  pet_window.py         the draggable, pokeable pet
  speech_bubble.py      cute speech bubbles
  phrasebook.py         offline English and Chinese learning cards
  speak.py              system text-to-speech for learning cards
  celebrations.py       fireworks / snow / emoji effects
  holidays.py           Chinese (lunar) + Western festival detection
  weather.py            IP location + weather narration
  library.py            source-photo and generated-pet synchronization
  processing.py         background cut-out and synchronization worker
  config.py             per-user settings
  animations.py         jump / squash / shake
tools/remove_bg.py      one-time background removal
tools/make_icon.py      app icon generator
build/desktop_pet.spec  PyInstaller build recipe
```

## Tech 技术

- **[PySide6](https://doc.qt.io/qtforpython/)** — cross-platform transparent,
  frameless, always-on-top window.
- **[rembg](https://github.com/danielgatis/rembg)** — AI background removal
  that turns your photos into transparent cut-outs.
- **[Open-Meteo](https://open-meteo.com/)** & **[ip-api](https://ip-api.com/)** —
  free, key-less weather + location.
- **[lunardate](https://pypi.org/project/lunardate/)** — Chinese lunar calendar
  for Spring Festival, Mid-Autumn, etc.

## License & Disclaimer 许可与免责

- **Software 软件**: PolyForm Noncommercial License 1.0.0 — free for personal,
  non-commercial use; **commercial use prohibited**. See [LICENSE](LICENSE).
  非商业许可，**禁止商用**，详见 [LICENSE](LICENSE)。
- **Photos 照片**: belong to their owners; only use images you have the right
  to, for personal use. 照片版权/肖像权归原权利人，请仅使用你有权使用的图片。
- **Unofficial fan project**; rights holders may request takedown at
  **jtanpp0319@gmail.com**. See [DISCLAIMER.md](DISCLAIMER.md).
  非官方粉丝项目；权利人可联系 **jtanpp0319@gmail.com** 删除，详见 [DISCLAIMER.md](DISCLAIMER.md)。
