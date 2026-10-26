export function ScholarlySkeletonList() {
  return (
    <div
      data-testid="scholarly-skeleton-list"
      className="w-full mt-6 space-y-3"
    >
      {[1, 2, 3].map((idx) => (
        <div
          key={idx}
          className="p-5 rounded-xl border border-hairline bg-white dark:bg-[#1c1b18] shadow-xs flex flex-col justify-between gap-4 animate-pulse"
        >
          <div className="space-y-3">
            {/* Khung badge & năm */}
            <div className="flex items-center justify-between gap-2">
              <div className="h-5 w-32 rounded-full bg-zinc-200 dark:bg-zinc-800" />
              <div className="h-4 w-12 rounded bg-zinc-200 dark:bg-zinc-800" />
            </div>

            {/* Tiêu đề 2 dòng giả lập */}
            <div className="space-y-2 pt-1">
              <div className="h-4.5 w-11/12 rounded bg-zinc-200 dark:bg-zinc-800" />
              <div className="h-4.5 w-3/4 rounded bg-zinc-200 dark:bg-zinc-800" />
            </div>

            {/* Tác giả 1 dòng giả lập */}
            <div className="h-3.5 w-1/2 rounded bg-zinc-200 dark:bg-zinc-800" />

            {/* Tóm tắt 2 dòng giả lập */}
            <div className="space-y-1.5 pt-1">
              <div className="h-3 w-full rounded bg-zinc-200 dark:bg-zinc-800" />
              <div className="h-3 w-4/5 rounded bg-zinc-200 dark:bg-zinc-800" />
            </div>
          </div>

          {/* Nút hành động góc dưới */}
          <div className="pt-3 border-t border-hairline flex items-center justify-end">
            <div className="h-8 w-28 rounded-lg bg-zinc-200 dark:bg-zinc-800" />
          </div>
        </div>
      ))}
    </div>
  );
}
