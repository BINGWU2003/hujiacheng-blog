---
title: "Vue 3 源码笔记：Diff 算法深度解析 (patchKeyedChildren)"
date: 2026-02-13
draft: false
description: "完整解析 Vue 3 Diff 算法的 5 个核心场景，包含源码片段、逻辑图解和输入输出示例"
tags: ["Vue3", "算法", "源码分析", "Diff算法"]
categories: ["笔记"]
---

## 1. 核心策略概述

Vue 3 的 Diff 算法采用了 **双端对比 + 最长递增子序列 (LIS)** 的混合策略。

- **目标**：以最小的代价（最少的 DOM 操作）将旧的 DOM 结构更新为新的结构。
- **流程**：先处理“头”和“尾”相同的节点（预处理），缩小乱序范围；最后处理剩余的乱序节点。

## 2. 场景一：从头同步 (Sync from Start)

**逻辑**：
从两组节点的头部开始向后遍历。如果节点 `key` 和 `type` 相同（`isSameVNodeType`），则进行 patch（复用更新），并将指针 `i` 向后移动。如果不相同，立即停止循环。

- **输入示例**：
- Old: `(A, B, C)`
- New: `(A, B, D, E)`

- **执行过程**：

1. `A` vs `A` -> 相同，Patch，`i` 变为 1。
2. `B` vs `B` -> 相同，Patch，`i` 变为 2。
3. `C` vs `D` -> 不同，**Break**。

- **结果**：`i` 停留在索引 **2**。

## 3. 场景二：从尾同步 (Sync from End)

**逻辑**：
当头部对比停止后，开始从尾部向前遍历。如果尾部节点相同，进行 patch，并将尾指针 `oldEnd` 和 `newEnd` 向前移动。如果不相同，立即停止。

- **输入示例**：
- Old: `(A, B, C)`
- New: `(D, E, B, C)`

- **假设**：头部对比在 `i=0` 时就停止了。
- **执行过程**：

1. `C` vs `C` -> 相同，Patch，`oldEnd`=1, `newEnd`=2。
2. `B` vs `B` -> 相同，Patch，`oldEnd`=0, `newEnd`=1。
3. `A` vs `E` -> 不同，**Break**。

- **结果**：尾部相同部分已处理，锁定中间乱序区域。

## 4. 场景三：普通序列 - 新增挂载 (Mount New)

**逻辑**：
当头尾同步完成后，如果 **旧节点遍历完了 (`i > oldEnd`)**，但 **新节点还有剩余 (`i <= newEnd`)**，说明剩下的都是新增节点，需要挂载。

- **输入示例**：
- Old: `(A, B)`
- New: `(A, B, C)`

- **状态**：头尾同步后，`i=2`, `oldEnd=1`, `newEnd=2`。
- **判断**：`i > oldEnd` 且 `i <= newEnd`。
- **操作**：将 `C` 挂载 (Mount) 到 DOM 中。

## 5. 场景四：普通序列 - 删除多余 (Unmount Old)

**逻辑**：
当头尾同步完成后，如果 **新节点遍历完了 (`i > newEnd`)**，但 **旧节点还有剩余 (`i <= oldEnd`)**，说明剩下的都是被删掉的节点，需要卸载。

- **输入示例**：
- Old: `(A, B, C)`
- New: `(A, B)`

- **状态**：头尾同步后，`i=2`, `oldEnd=2`, `newEnd=1`。
- **判断**：`i > newEnd`。
- **操作**：将 `C` 从 DOM 中卸载 (Unmount)。

## 6. 场景五：乱序序列 (Unknown Sequence)

这是 Diff 的核心难点。当 `else` 分支触发时，意味着头尾同步后，中间还有一段 **既有新增、又有删除、还有乱序移动** 的复杂情况。

**示例输入**：

- Old: `(a, [c, d, e, f], g)`
- New: `(a, [e, c, d, h], g)`
- _注：`a` 和 `g` 已处理。核心关注乱序区间 Old: `c,d,e,f` vs New: `e,c,d,h`_

### 6.1 步骤一：构建新节点映射表 (Key Map)

**逻辑**：遍历新节点的乱序部分，生成一个 `Map<Key, Index>`。

- **目的**：让后续查找的时间复杂度从 `O(n²)` 降为 `O(n)`。
- **结果 (keyToNewIndexMap)**：`{ e:0, c:1, d:2, h:3 }` (索引为相对位置)

### 6.2 步骤二：清理旧节点 (Patch or Unmount)

**逻辑**：遍历旧节点，判断是删除还是复用，并构建 `newIndexToOldIndexMap`（用于计算 LIS）。

- **操作细节**：

1. **查找**：拿旧节点的 key 去 Map 里找。
2. **删除**：没找到（如 `f`），直接 `unmount`。
3. **复用**：找到了（如 `c, d, e`），执行 `patch` 更新内容。
4. **记录**：填充数组 `newIndexToOldIndexMap`。

- **结果 (newIndexToOldIndexMap)**：`[3, 1, 2, 0]`
  - `e` (new 0) <- old 2 (值3)
  - `c` (new 1) <- old 0 (值1)
  - `d` (new 2) <- old 1 (值2)
  - `h` (new 3) <- old 无 (值0)

### 6.3 步骤三：移动与挂载 (LIS & Move)

**逻辑**：计算最长递增子序列 (LIS)，并倒序遍历进行最终的 DOM 操作。

- **LIS 结果**：对于数组 `[3, 1, 2, 0]` (忽略0)，LIS 是 `[1, 2]` (即 `c, d`)。这意味着 `c` 和 `d` 不需要动。
- **倒序遍历逻辑**：
  1. **处理 h (idx 3)**: 值是 0 -> **Mount** (插入到 g 前)。
  2. **处理 d (idx 2)**: 在 LIS `[1, 2]` 中 -> **跳过**。
  3. **处理 c (idx 1)**: 在 LIS `[1, 2]` 中 -> **跳过**。
  4. **处理 e (idx 0)**: 不在 LIS 中 -> **Move** (插入到 c 前)。

{{< article link="/posts/vue3-patch-keyed-children-deep-dive/" showSummary=true compactSummary=true >}}

## 7. 附录：完整源码 (Annotated Source Code)

以下是 `patchKeyedChildren` 的完整源码，附带详细注释以便对照学习。

```typescript
const patchKeyedChildren = (
  oldChildren: any[],
  newChildren: any[],
  container: Element,
  parentAnchor?: Element | null,
) => {
  let i = 0;
  const oldLen = oldChildren.length;
  const newLen = newChildren.length;
  let oldEnd = oldLen - 1;
  let newEnd = newLen - 1;

  // -------------------------------------------------------------
  // 1. 从头同步 (Sync from Start)
  // -------------------------------------------------------------
  while (i <= oldEnd && i <= newEnd) {
    const oldVNode = (oldChildren[i] = normalizeVNode(oldChildren[i]));
    const newVNode = (newChildren[i] = normalizeVNode(newChildren[i]));

    if (isSameVNodeType(oldVNode, newVNode)) {
      patch(oldVNode, newVNode, container);
    } else {
      break;
    }
    i++;
  }

  // -------------------------------------------------------------
  // 2. 从尾同步 (Sync from End)
  // -------------------------------------------------------------
  while (i <= oldEnd && i <= newEnd) {
    const oldVNode = (oldChildren[oldEnd] = normalizeVNode(
      oldChildren[oldEnd],
    ));
    const newVNode = (newChildren[newEnd] = normalizeVNode(
      newChildren[newEnd],
    ));
    if (isSameVNodeType(oldVNode, newVNode)) {
      patch(oldVNode, newVNode, container);
    } else {
      break;
    }
    oldEnd--;
    newEnd--;
  }

  // -------------------------------------------------------------
  // 3. 普通序列 - 新增挂载 (Mount New)
  // -------------------------------------------------------------
  if (i > oldEnd) {
    // 新节点多于旧节点（挂载）
    // 此时 oldEnd < i
    if (i <= newEnd) {
      // 计算锚点：如果后面还有节点，插在它前面；否则插在 container 末尾
      const anchor = newEnd + 1 < newLen ? newChildren[newEnd + 1].el : null;
      while (i <= newEnd) {
        patch(
          null,
          (newChildren[i] = normalizeVNode(newChildren[i])),
          container,
          anchor,
        );
        i++;
      }
    }
  }
  // -------------------------------------------------------------
  // 4. 普通序列 - 删除多余 (Unmount Old)
  // -------------------------------------------------------------
  else if (i > newEnd) {
    // 旧节点多于新节点（卸载）
    // 此时 newEnd < i
    while (i <= oldEnd) {
      unmount(oldChildren[i]);
      i++;
    }
  }
  // -------------------------------------------------------------
  // 5. 乱序序列 (Unknown Sequence) - 核心难点
  // -------------------------------------------------------------
  else {
    // 旧子节点的开始索引
    const oldStartIndex = i;
    // 新子节点的开始索引
    const newStartIndex = i;

    // -----------------------------------------------------------
    // 5.1 构建 Map: { newKey : newIndex }
    // -----------------------------------------------------------
    const keyToNewIndexMap = new Map();
    for (i = newStartIndex; i <= newEnd; i++) {
      const nextChild = normalizeVNode(newChildren[i]);
      if (nextChild.key != null) {
        keyToNewIndexMap.set(nextChild.key, i);
      }
    }

    // -----------------------------------------------------------
    // 5.2 遍历旧节点: Patch 或 Unmount
    // -----------------------------------------------------------
    let j;
    let patched = 0; // 已复用数量
    const toBePatched = newEnd - newStartIndex + 1; // 待处理总数
    let moved = false; // 是否需要移动
    let maxNewIndexSoFar = 0; // 记录遇到的最大新索引，判断是否递增

    // newIndexToOldIndexMap: 索引是新位置，值是 oldIndex + 1
    const newIndexToOldIndexMap = new Array(toBePatched);
    for (i = 0; i < toBePatched; i++) newIndexToOldIndexMap[i] = 0;

    for (i = oldStartIndex; i <= oldEnd; i++) {
      const prevChild = oldChildren[i];

      // 优化：如果新节点已经找齐了，剩下的旧节点直接删
      if (patched >= toBePatched) {
        unmount(prevChild);
        continue;
      }

      let newIndex;
      if (prevChild.key != null) {
        newIndex = keyToNewIndexMap.get(prevChild.key);
      } else {
        // 无 key 查找逻辑 (尝试寻找相同 type 的无 key 节点)
        for (j = newStartIndex; j <= newEnd; j++) {
          if (
            newIndexToOldIndexMap[j - newStartIndex] === 0 &&
            isSameVNodeType(prevChild, newChildren[j])
          ) {
            newIndex = j;
            break;
          }
        }
      }

      // 没找到 -> 删除
      if (newIndex === undefined) {
        unmount(prevChild);
      }
      // 找到了 -> 复用 Patch
      else {
        newIndexToOldIndexMap[newIndex - newStartIndex] = i + 1;

        // 检查是否递增
        if (newIndex >= maxNewIndexSoFar) {
          maxNewIndexSoFar = newIndex;
        } else {
          moved = true; // 乱序了
        }

        patch(prevChild, newChildren[newIndex], container, null);
        patched++;
      }
    }

    // -----------------------------------------------------------
    // 5.3 移动与挂载 (LIS Algorithm)
    // -----------------------------------------------------------
    // 计算最长递增子序列
    const increasingNewIndexSequence = moved
      ? getSequence(newIndexToOldIndexMap)
      : [];
    j = increasingNewIndexSequence.length - 1;

    // 倒序遍历
    for (i = toBePatched - 1; i >= 0; i--) {
      const nextIndex = newStartIndex + i;
      const nextChild = newChildren[nextIndex];
      // 计算锚点：插在后一个节点前面
      const anchor =
        nextIndex + 1 < newLen ? newChildren[nextIndex + 1].el : parentAnchor;

      // 情况 A: 是新节点 (值为0) -> 挂载
      if (newIndexToOldIndexMap[i] === 0) {
        patch(null, nextChild, container, anchor);
      }
      // 情况 B: 需要移动
      else if (moved) {
        // 如果不在 LIS 中，或者 LIS 已用完 -> 移动
        if (j < 0 || i !== increasingNewIndexSequence[j]) {
          move(nextChild, container, anchor);
        } else {
          // 在 LIS 中 -> 不动
          j--;
        }
      }
    }
  }
};
```
