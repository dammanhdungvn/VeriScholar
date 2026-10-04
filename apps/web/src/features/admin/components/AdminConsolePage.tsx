import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  Users,
  HardDrive,
  Cpu,
  DollarSign,
  Activity,
  ArrowLeft,
  Loader2,
  Edit,
  CheckCircle2,
  XCircle,
  Search,
} from "lucide-react";
import { AcademicLogo } from "@/components/shared/AcademicLogo";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog } from "@/components/ui/dialog";
import { adminApi } from "../api/adminApi";
import type {
  AdminDashboardMetrics,
  AdminUserListItem,
  AdminUsageLogItem,
  AdminSystemHealth,
} from "@/types/admin";

export function AdminConsolePage() {
  const [metrics, setMetrics] = useState<AdminDashboardMetrics | null>(null);
  const [users, setUsers] = useState<AdminUserListItem[]>([]);
  const [usageLogs, setUsageLogs] = useState<AdminUsageLogItem[]>([]);
  const [health, setHealth] = useState<AdminSystemHealth | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState<string>("");

  // Edit User Quota Modal State
  const [editingUser, setEditingUser] = useState<AdminUserListItem | null>(null);
  const [newQuotaTokens, setNewQuotaTokens] = useState<number>(200000);
  const [newQuotaStorageMb, setNewQuotaStorageMb] = useState<number>(1024);
  const [newRole, setNewRole] = useState<"admin" | "researcher" | "member">("researcher");
  const [newIsActive, setNewIsActive] = useState<boolean>(true);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const loadData = async () => {
    try {
      setIsLoading(true);
      const [m, u, logs, h] = await Promise.all([
        adminApi.getDashboardMetrics().catch(() => null),
        adminApi.listUsers({ per_page: 50 }).catch(() => ({ data: [], meta: { total: 0 } })),
        adminApi.listUsageLogs({ per_page: 15 }).catch(() => ({ data: [], meta: { total: 0 } })),
        adminApi.getSystemHealth().catch(() => null),
      ]);
      setMetrics(m);
      setUsers(u.data);
      setUsageLogs(logs.data);
      setHealth(h);
    } catch (err) {
      console.error("Failed to load admin console data:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const openEditModal = (user: AdminUserListItem) => {
    setEditingUser(user);
    setNewQuotaTokens(user.token_quota);
    setNewQuotaStorageMb(Math.round(user.storage_quota_bytes / (1024 * 1024)));
    setNewRole(user.role);
    setNewIsActive(user.is_active);
  };

  const handleUpdateQuota = async () => {
    if (!editingUser) return;
    try {
      setIsSubmitting(true);
      await adminApi.updateUserQuota(editingUser.id, {
        token_quota: newQuotaTokens,
        storage_quota_bytes: newQuotaStorageMb * 1024 * 1024,
        role: newRole,
        is_active: newIsActive,
      });
      setEditingUser(null);
      await loadData();
    } catch (err) {
      console.error("Failed to update user quota:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const filteredUsers = users.filter((u) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return u.email.toLowerCase().includes(q) || u.full_name.toLowerCase().includes(q);
  });

  return (
    <div className="min-h-screen bg-[#faf8f4] dark:bg-[#161513] text-ink dark:text-zinc-100 flex flex-col font-sans">
      {/* Header */}
      <header className="h-14 border-b border-[#e8e4dc] dark:border-[#2a2824] bg-white dark:bg-[#1c1b18] px-6 flex items-center justify-between sticky top-0 z-30">
        <div className="flex items-center gap-3">
          <Link
            to="/dashboard"
            className="w-8 h-8 rounded-lg flex items-center justify-center text-muted hover:text-ink hover:bg-[#f2ece1] dark:hover:bg-[#282522] transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <AcademicLogo size="sm" showWordmark={false} />
          <div className="h-4 w-px bg-[#e8e4dc] dark:border-[#2a2824]" />
          <h1 className="text-sm font-semibold font-serif">Bảng điều khiển Quản trị (Admin Console)</h1>
        </div>

        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 text-xs font-mono font-medium px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-600 border border-emerald-500/20">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Hệ thống: {metrics?.system_status || "Healthy"}
          </span>
        </div>
      </header>

      {/* Main Body */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 md:p-8 space-y-8">
        {isLoading && !metrics ? (
          <div className="py-20 flex flex-col items-center justify-center text-muted">
            <Loader2 className="w-8 h-8 animate-spin text-coral-500 mb-2" />
            <p className="text-sm">Đang tải dữ liệu quản trị...</p>
          </div>
        ) : (
          <>
            {/* 1. Metrics Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-5 rounded-2xl bg-white dark:bg-[#201e1b] border border-[#e8e4dc] dark:border-[#2a2824] shadow-2xs space-y-2">
                <div className="flex items-center justify-between text-muted">
                  <span className="text-xs font-mono uppercase">Tài khoản</span>
                  <Users className="w-4 h-4 text-coral-600" />
                </div>
                <div className="text-2xl font-bold font-serif">{metrics?.total_users ?? 0}</div>
                <p className="text-[11px] text-muted">{metrics?.active_users ?? 0} đang hoạt động</p>
              </div>

              <div className="p-5 rounded-2xl bg-white dark:bg-[#201e1b] border border-[#e8e4dc] dark:border-[#2a2824] shadow-2xs space-y-2">
                <div className="flex items-center justify-between text-muted">
                  <span className="text-xs font-mono uppercase">CAS Lưu trữ</span>
                  <HardDrive className="w-4 h-4 text-amber-600" />
                </div>
                <div className="text-2xl font-bold font-serif">
                  {metrics?.total_storage_formatted ?? "0 MB"}
                </div>
                <p className="text-[11px] text-muted">{metrics?.total_documents ?? 0} tài liệu đã index</p>
              </div>

              <div className="p-5 rounded-2xl bg-white dark:bg-[#201e1b] border border-[#e8e4dc] dark:border-[#2a2824] shadow-2xs space-y-2">
                <div className="flex items-center justify-between text-muted">
                  <span className="text-xs font-mono uppercase">LLM Tokens</span>
                  <Cpu className="w-4 h-4 text-indigo-600" />
                </div>
                <div className="text-2xl font-bold font-serif">
                  {(metrics?.total_tokens_consumed ?? 0).toLocaleString()}
                </div>
                <p className="text-[11px] text-muted">{metrics?.active_sessions ?? 0} phiên chat active</p>
              </div>

              <div className="p-5 rounded-2xl bg-white dark:bg-[#201e1b] border border-[#e8e4dc] dark:border-[#2a2824] shadow-2xs space-y-2">
                <div className="flex items-center justify-between text-muted">
                  <span className="text-xs font-mono uppercase">Chi phí ước tính</span>
                  <DollarSign className="w-4 h-4 text-emerald-600" />
                </div>
                <div className="text-2xl font-bold font-serif">
                  ${(metrics?.total_cost_estimated_usd ?? 0).toFixed(2)}
                </div>
                <p className="text-[11px] text-muted">{metrics?.total_labs ?? 0} phòng lab nghiên cứu</p>
              </div>
            </div>

            {/* 2. User Accounts Management Table */}
            <div className="bg-white dark:bg-[#201e1b] border border-[#e8e4dc] dark:border-[#2a2824] rounded-2xl p-6 shadow-2xs space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <h2 className="text-base font-semibold font-serif">Quản trị Người dùng & Hạn mức Quota</h2>
                  <p className="text-xs text-muted">
                    Phân bổ Token LLM, dung lượng lưu trữ CAS và vai trò quản trị.
                  </p>
                </div>
                <div className="relative w-64">
                  <Search className="w-3.5 h-3.5 text-muted absolute left-3 top-3" />
                  <Input
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Tìm theo tên, email..."
                    className="h-9 pl-8 text-xs rounded-xl"
                  />
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left">
                  <thead className="bg-[#fbf9f5] dark:bg-[#1a1917] border-y border-[#ece8df] dark:border-[#2a2824] font-mono uppercase text-muted text-[10px]">
                    <tr>
                      <th className="py-2.5 px-3">Người dùng</th>
                      <th className="py-2.5 px-3">Vai trò</th>
                      <th className="py-2.5 px-3">Token Quota</th>
                      <th className="py-2.5 px-3">Storage Quota</th>
                      <th className="py-2.5 px-3">Trạng thái</th>
                      <th className="py-2.5 px-3 text-right">Thao tác</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#ece8df] dark:divide-[#2a2824]">
                    {filteredUsers.length === 0 ? (
                      <tr>
                        <td colSpan={6} className="py-8 text-center text-muted">
                          Không tìm thấy người dùng phù hợp.
                        </td>
                      </tr>
                    ) : (
                      filteredUsers.map((u) => {
                        const tokenPercent = Math.min(
                          100,
                          Math.round((u.tokens_used / (u.token_quota || 1)) * 100)
                        );
                        return (
                          <tr key={u.id} className="hover:bg-surface-cream dark:hover:bg-[#252320]">
                            <td className="py-3 px-3">
                              <p className="font-semibold text-ink dark:text-zinc-200">{u.full_name}</p>
                              <p className="text-muted font-mono text-[11px]">{u.email}</p>
                            </td>
                            <td className="py-3 px-3">
                              <span
                                className={`px-2 py-0.5 rounded font-mono font-medium text-[10px] ${
                                  u.role === "admin"
                                    ? "bg-purple-500/10 text-purple-600 dark:text-purple-400"
                                    : "bg-surface-cream text-muted"
                                }`}
                              >
                                {u.role}
                              </span>
                            </td>
                            <td className="py-3 px-3">
                              <div className="space-y-1">
                                <div className="flex justify-between font-mono text-[10px]">
                                  <span>{u.tokens_used.toLocaleString()}</span>
                                  <span className="text-muted">/ {u.token_quota.toLocaleString()}</span>
                                </div>
                                <div className="h-1.5 w-24 bg-zinc-200 dark:bg-zinc-700 rounded-full overflow-hidden">
                                  <div
                                    className={`h-full ${
                                      tokenPercent > 90 ? "bg-rose-500" : "bg-coral-500"
                                    }`}
                                    style={{ width: `${tokenPercent}%` }}
                                  />
                                </div>
                              </div>
                            </td>
                            <td className="py-3 px-3 font-mono text-[11px]">
                              {Math.round(u.storage_used_bytes / (1024 * 1024))} MB /{" "}
                              {Math.round(u.storage_quota_bytes / (1024 * 1024))} MB
                            </td>
                            <td className="py-3 px-3">
                              {u.is_active ? (
                                <span className="inline-flex items-center gap-1 text-emerald-600 font-medium">
                                  <CheckCircle2 className="w-3.5 h-3.5" />
                                  Active
                                </span>
                              ) : (
                                <span className="inline-flex items-center gap-1 text-rose-500 font-medium">
                                  <XCircle className="w-3.5 h-3.5" />
                                  Blocked
                                </span>
                              )}
                            </td>
                            <td className="py-3 px-3 text-right">
                              <Button
                                onClick={() => openEditModal(u)}
                                variant="ghost"
                                size="sm"
                                className="h-7 text-xs gap-1"
                              >
                                <Edit className="w-3 h-3" />
                                <span>Sửa</span>
                              </Button>
                            </td>
                          </tr>
                        );
                      })
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* 3. Real-time Audit Usage Logs */}
            <div className="bg-white dark:bg-[#201e1b] border border-[#e8e4dc] dark:border-[#2a2824] rounded-2xl p-6 shadow-2xs space-y-4">
              <h2 className="text-base font-semibold font-serif">Nhật ký Sử dụng Compute (Audit Trail)</h2>
              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left">
                  <thead className="bg-[#fbf9f5] dark:bg-[#1a1917] border-y border-[#ece8df] dark:border-[#2a2824] font-mono uppercase text-muted text-[10px]">
                    <tr>
                      <th className="py-2 px-3">Thời gian</th>
                      <th className="py-2 px-3">Người dùng</th>
                      <th className="py-2 px-3">Hành động</th>
                      <th className="py-2 px-3">Model</th>
                      <th className="py-2 px-3">Tokens</th>
                      <th className="py-2 px-3">Chi phí (cents)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#ece8df] dark:divide-[#2a2824] font-mono text-[11px]">
                    {usageLogs.length === 0 ? (
                      <tr>
                        <td colSpan={6} className="py-6 text-center text-muted font-sans">
                          Chưa có nhật ký ghi nhận.
                        </td>
                      </tr>
                    ) : (
                      usageLogs.map((log) => (
                        <tr key={log.id} className="hover:bg-surface-cream dark:hover:bg-[#252320]">
                          <td className="py-2.5 px-3 text-muted">
                            {new Date(log.created_at).toLocaleTimeString("vi-VN")}
                          </td>
                          <td className="py-2.5 px-3 font-sans font-medium">{log.user_email}</td>
                          <td className="py-2.5 px-3">{log.activity_type}</td>
                          <td className="py-2.5 px-3 text-muted">{log.model_name || "—"}</td>
                          <td className="py-2.5 px-3 font-semibold">
                            {log.total_tokens.toLocaleString()}
                          </td>
                          <td className="py-2.5 px-3">{log.cost_cents.toFixed(2)}¢</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* 4. Infrastructure Health Probes */}
            {health && (
              <div className="p-4 rounded-2xl bg-white dark:bg-[#201e1b] border border-[#e8e4dc] dark:border-[#2a2824] text-xs flex flex-wrap items-center justify-between gap-4 font-mono">
                <div className="flex items-center gap-2">
                  <Activity className="w-4 h-4 text-coral-600" />
                  <span>PostgreSQL: {health.database_connected ? "Connected" : "Disconnected"}</span>
                </div>
                <div>CAS Blobs: {health.total_storage_blobs} files</div>
                <div>Storage Free: {Math.round(health.storage_free_bytes / (1024 * 1024 * 1024))} GB</div>
                <div>Latency: {health.average_latency_ms.toFixed(1)} ms</div>
              </div>
            )}
          </>
        )}
      </main>

      {/* Edit Quota Dialog */}
      {editingUser && (
        <Dialog open={true} onOpenChange={() => setEditingUser(null)}>
          <div className="fixed inset-0 bg-black/50 backdrop-blur-xs z-50 flex items-center justify-center p-4">
            <div className="bg-white dark:bg-[#201e1b] rounded-2xl border border-[#e8e4dc] dark:border-[#2a2824] p-6 max-w-md w-full shadow-2xl space-y-4">
              <h3 className="text-base font-semibold font-serif">Điều chỉnh Quota & Phân quyền</h3>
              <p className="text-xs text-muted">
                Cập nhật hạn mức cho <span className="font-semibold">{editingUser.email}</span>
              </p>

              <div className="space-y-3 text-xs">
                <div>
                  <label className="block text-muted mb-1">Token Quota (Tokens)</label>
                  <Input
                    type="number"
                    value={newQuotaTokens}
                    onChange={(e) => setNewQuotaTokens(parseInt(e.target.value) || 0)}
                    className="h-8 font-mono"
                  />
                </div>

                <div>
                  <label className="block text-muted mb-1">Dung lượng CAS Quota (MB)</label>
                  <Input
                    type="number"
                    value={newQuotaStorageMb}
                    onChange={(e) => setNewQuotaStorageMb(parseInt(e.target.value) || 0)}
                    className="h-8 font-mono"
                  />
                </div>

                <div>
                  <label className="block text-muted mb-1">Vai trò hệ thống</label>
                  <select
                    value={newRole}
                    onChange={(e) => setNewRole(e.target.value as any)}
                    className="w-full h-8 px-2 rounded-lg border border-[#e8e4dc] dark:border-[#2a2824] bg-transparent text-xs"
                  >
                    <option value="researcher">Researcher</option>
                    <option value="admin">Admin</option>
                    <option value="member">Member</option>
                  </select>
                </div>

                <div className="flex items-center gap-2 pt-1">
                  <input
                    type="checkbox"
                    id="isActiveCheck"
                    checked={newIsActive}
                    onChange={(e) => setNewIsActive(e.target.checked)}
                    className="rounded text-coral-500"
                  />
                  <label htmlFor="isActiveCheck">Tài khoản được phép đăng nhập (Active)</label>
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <Button variant="ghost" size="sm" onClick={() => setEditingUser(null)}>
                  Hủy
                </Button>
                <Button
                  onClick={handleUpdateQuota}
                  disabled={isSubmitting}
                  size="sm"
                  className="bg-coral-500 hover:bg-coral-600 text-white"
                >
                  {isSubmitting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : "Lưu thay đổi"}
                </Button>
              </div>
            </div>
          </div>
        </Dialog>
      )}
    </div>
  );
}
