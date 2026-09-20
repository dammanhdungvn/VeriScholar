export function TaskbarSessionsSkeleton() {
  return (
    <div className="space-y-2 p-2" aria-label="Đang tải phiên nghiên cứu">
      {[1, 2, 3, 4].map((i) => (
        <div
          key={i}
          className="h-10 w-full rounded-lg bg-[#e8e0d2]/60 dark:bg-[#262420]/70 animate-pulse"
        />
      ))}
    </div>
  );
}

export function ChatThreadSkeleton() {
  return (
    <div className="space-y-6 max-w-3xl mx-auto w-full py-8 px-4" aria-label="Đang tải nội dung">
      {/* User message skeleton */}
      <div className="flex justify-end">
        <div className="h-12 w-64 rounded-2xl rounded-tr-sm bg-[#e8e0d2]/60 dark:bg-[#262420]/70 animate-pulse" />
      </div>

      {/* Assistant message skeleton */}
      <div className="space-y-3">
        <div className="h-4 w-48 rounded bg-[#e8e0d2]/80 dark:bg-[#262420]/80 animate-pulse" />
        <div className="h-20 w-full rounded-2xl bg-[#e8e0d2]/40 dark:bg-[#262420]/50 animate-pulse" />
        <div className="h-4 w-32 rounded-full bg-coral-500/10 animate-pulse" />
      </div>
    </div>
  );
}
