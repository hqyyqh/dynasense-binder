# 从一张材料卡开始

打开 `materials.k`。可以自由修改；刷新页面会保留当前会话里的内容。

1. 找到 `*MAT_PIECEWISE_LINEAR_PLASTICITY` 的第一张数据卡，将光标放到 E 字段，按 Tab 选中 PR。把 `0.3` 改为 `0.31`，再按 Tab 进入 SIGY。等待字段选中后再输入。
2. 查看 PR 的悬停帮助。打开对应手册章节，切换中文、英文和双语阅读；在搜索栏查找 `*DEFINE_CURVE`，再切换全文搜索，搜索“曲线”。
3. 在该材料卡中打开命令面板，运行 `LS-DYNA: Open Keyword Manager`。修改 PR，应用到文档，检查实际字段。关闭管理器不会代替撤销文档修改。
4. 保存文件，运行 `LS-DYNA: Diff: Changes Since Opened`，查看修改前后的数值。回到源文件，使用撤销恢复，再保存。
5. 打开 `main.k`，扫描引用文件树；找到 `parts.k`。用 Find Entity 查询 `mat 1`，打开材料定义和 Part 6 的材料引用。若结果显示仍在索引，等待完成后再判断是否查全。
6. 新建一个空白文件，选择 LS-Dyna 语言模式，输入 `*DEFINE_CUR`，接受 `*DEFINE_CURVE` 候选。它会创建卡片模板；用撤销恢复。不要在已有卡片的卡头上体验模板插入。

命令标题跟随编辑器显示语言；字段帮助和部分插件界面还受 `lsdyna.language` 控制。当前实测宿主为英文，所以这里保留可直接搜索的英文命令名。

案例来自 [DYNAmore Drop Test](https://www.dynaexamples.com/show-cases/drop-test)。当前会话中的修改只影响自己的副本。
