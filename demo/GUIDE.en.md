# Start with a material card

Open `materials.k`. Feel free to edit it. Refreshing the page keeps your current session's changes.

1. In the first data card under `*MAT_PIECEWISE_LINEAR_PLASTICITY`, place the cursor in E. Press Tab to select PR, change `0.3` to `0.31`, and press Tab to move to SIGY. Wait until the field is selected before typing.
2. Inspect the hover help for PR. Open its manual chapter and try English, Chinese and bilingual reading. Search for `*DEFINE_CURVE`, then switch to full-text search and search for “曲线”.
3. With the material card active, open the command palette and run `LS-DYNA: Open Keyword Manager`. Change PR, apply it, and inspect the value in the document. Closing the manager does not undo document changes.
4. Save the file and run `LS-DYNA: Diff: Changes Since Opened`. Compare the values, return to the source file, undo the edit, and save again.
5. Open `main.k` and scan the include tree. Find `parts.k`. Use Find Entity to query `mat 1`, then open the material definition and its reference in Part 6. If indexing is still in progress, wait before treating the results as complete.
6. Create a blank file, select LS-Dyna language mode, type `*DEFINE_CUR`, and accept `*DEFINE_CURVE`. Completion inserts a card template. Undo to restore the blank file. Try this in a new file rather than over an existing card header.

Command titles follow the editor's display language. Field help and parts of the plugin UI also follow `lsdyna.language`. The current tested editor uses English command titles.

The example comes from the [DYNAmore Drop Test](https://www.dynaexamples.com/show-cases/drop-test). Changes affect only your own session's copy.
