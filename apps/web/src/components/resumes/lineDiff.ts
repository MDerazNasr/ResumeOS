export type DiffLine = {
  type: "added" | "removed" | "unchanged";
  text: string;
};

export function buildLineDiff(previousSource: string, currentSource: string): DiffLine[] {
  const previousLines = previousSource.split("\n");
  const currentLines = currentSource.split("\n");
  const lcs = buildLcsTable(previousLines, currentLines);
  const diff: DiffLine[] = [];

  let previousIndex = previousLines.length;
  let currentIndex = currentLines.length;

  while (previousIndex > 0 || currentIndex > 0) {
    if (
      previousIndex > 0 &&
      currentIndex > 0 &&
      previousLines[previousIndex - 1] === currentLines[currentIndex - 1]
    ) {
      diff.push({ type: "unchanged", text: currentLines[currentIndex - 1] });
      previousIndex -= 1;
      currentIndex -= 1;
      continue;
    }

    if (currentIndex > 0 && (previousIndex === 0 || lcs[previousIndex][currentIndex - 1] >= lcs[previousIndex - 1][currentIndex])) {
      diff.push({ type: "added", text: currentLines[currentIndex - 1] });
      currentIndex -= 1;
      continue;
    }

    diff.push({ type: "removed", text: previousLines[previousIndex - 1] });
    previousIndex -= 1;
  }

  return diff.reverse();
}

function buildLcsTable(previousLines: string[], currentLines: string[]): number[][] {
  const table = Array.from({ length: previousLines.length + 1 }, () =>
    Array.from({ length: currentLines.length + 1 }, () => 0)
  );

  for (let previousIndex = 1; previousIndex <= previousLines.length; previousIndex += 1) {
    for (let currentIndex = 1; currentIndex <= currentLines.length; currentIndex += 1) {
      if (previousLines[previousIndex - 1] === currentLines[currentIndex - 1]) {
        table[previousIndex][currentIndex] = table[previousIndex - 1][currentIndex - 1] + 1;
      } else {
        table[previousIndex][currentIndex] = Math.max(
          table[previousIndex - 1][currentIndex],
          table[previousIndex][currentIndex - 1]
        );
      }
    }
  }

  return table;
}
