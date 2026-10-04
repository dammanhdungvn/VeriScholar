import { useState, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import {
  Building2,
  Plus,
  ArrowLeft,
  Loader2,
  UserPlus,
  Trash2,
  HardDrive,
  Cpu,
} from "lucide-react";
import { AcademicLogo } from "@/components/shared/AcademicLogo";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog } from "@/components/ui/dialog";
import { organizationsApi } from "../api/organizationsApi";
import type {
  OrganizationItem,
  OrganizationDetail,
} from "@/types/organization";

export function OrganizationsPage() {
  const [labs, setLabs] = useState<OrganizationItem[]>([]);
  const [selectedLab, setSelectedLab] = useState<OrganizationDetail | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isDetailLoading, setIsDetailLoading] = useState<boolean>(false);

  // Create Lab Modal
  const [isCreateOpen, setIsCreateOpen] = useState<boolean>(false);
  const [newLabName, setNewLabName] = useState<string>("");
  const [newLabSlug, setNewLabSlug] = useState<string>("");
  const [newLabDesc, setNewLabDesc] = useState<string>("");
  const [isCreating, setIsCreating] = useState<boolean>(false);

  // Invite Member Modal
  const [isInviteOpen, setIsInviteOpen] = useState<boolean>(false);
  const [inviteEmail, setInviteEmail] = useState<string>("");
  const [inviteRole, setInviteRole] = useState<"admin" | "member" | "guest">("member");
  const [isInviting, setIsInviting] = useState<boolean>(false);

  const loadLabDetail = useCallback(async (id: string) => {
    try {
      setIsDetailLoading(true);
      const detail = await organizationsApi.getOrganization(id);
      setSelectedLab(detail);
    } catch (err) {
      console.error("Failed to load lab detail:", err);
    } finally {
      setIsDetailLoading(false);
    }
  }, []);

  const loadLabs = useCallback(async () => {
    try {
      setIsLoading(true);
      const res = await organizationsApi.listOrganizations();
      setLabs(res.data);
      if (res.data.length > 0) {
        await loadLabDetail(res.data[0].id);
      }
    } catch (err) {
      console.error("Failed to load organizations:", err);
    } finally {
      setIsLoading(false);
    }
  }, [loadLabDetail]);

  useEffect(() => {
    loadLabs();
  }, [loadLabs]);

  const handleCreateLab = async () => {
    if (!newLabName.trim() || !newLabSlug.trim()) return;
    try {
      setIsCreating(true);
      const created = await organizationsApi.createOrganization({
        name: newLabName.trim(),
        slug: newLabSlug.trim().toLowerCase(),
        description: newLabDesc.trim() || undefined,
      });
      setIsCreateOpen(false);
      setNewLabName("");
      setNewLabSlug("");
      setNewLabDesc("");
      await loadLabs();
      await loadLabDetail(created.id);
    } catch (err) {
      console.error("Failed to create lab:", err);
    } finally {
      setIsCreating(false);
    }
  };

  const handleAddMember = async () => {
    if (!selectedLab || !inviteEmail.trim()) return;
    try {
      setIsInviting(true);
      await organizationsApi.addMember(selectedLab.id, {
        email: inviteEmail.trim(),
        role: inviteRole,
      });
      setIsInviteOpen(false);
      setInviteEmail("");
      await loadLabDetail(selectedLab.id);
    } catch (err) {
      console.error("Failed to invite member:", err);
    } finally {
      setIsInviting(false);
    }
  };

  const handleRemoveMember = async (userId: string) => {
    if (!selectedLab) return;
    try {
      await organizationsApi.removeMember(selectedLab.id, userId);
      await loadLabDetail(selectedLab.id);
    } catch (err) {
      console.error("Failed to remove member:", err);
    }
  };

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
          <h1 className="text-sm font-semibold font-serif">Phòng Lab & Nhóm Nghiên cứu Cộng tác</h1>
        </div>

        <Button
          onClick={() => setIsCreateOpen(true)}
          size="sm"
          className="bg-coral-500 hover:bg-coral-600 text-white text-xs gap-1.5"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Tạo Lab Mới</span>
        </Button>
      </header>

      {/* Main Body */}
      <div className="flex-1 flex max-w-7xl w-full mx-auto p-6 md:p-8 gap-6 overflow-hidden">
        {/* Left: Labs List */}
        <aside className="w-72 bg-white dark:bg-[#201e1b] border border-[#e8e4dc] dark:border-[#2a2824] rounded-2xl p-4 flex flex-col shrink-0">
          <div className="flex items-center justify-between mb-3 px-1">
            <span className="text-xs font-mono font-semibold uppercase text-muted">Danh sách Lab</span>
            <span className="text-xs font-mono text-muted">{labs.length}</span>
          </div>

          <div className="flex-1 overflow-y-auto space-y-1.5">
            {isLoading ? (
              <div className="py-12 text-center text-xs text-muted">
                <Loader2 className="w-4 h-4 animate-spin mx-auto mb-2 text-coral-500" />
                Đang tải phòng lab...
              </div>
            ) : labs.length === 0 ? (
              <div className="py-12 text-center text-xs text-muted px-2">
                Bạn chưa tham gia phòng lab nào. Hãy bấm &quot;Tạo Lab Mới&quot;.
              </div>
            ) : (
              labs.map((lab) => (
                <button
                  key={lab.id}
                  onClick={() => loadLabDetail(lab.id)}
                  className={`w-full text-left p-3 rounded-xl transition-colors flex items-center justify-between ${
                    selectedLab?.id === lab.id
                      ? "bg-coral-500/10 text-coral-700 dark:text-coral-400 font-semibold border border-coral-500/20"
                      : "hover:bg-surface-cream dark:hover:bg-[#282522] text-ink dark:text-zinc-200"
                  }`}
                >
                  <div className="truncate pr-2">
                    <p className="text-xs truncate font-serif font-medium">{lab.name}</p>
                    <p className="text-[10px] text-muted font-mono">/{lab.slug}</p>
                  </div>
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-surface-cream dark:bg-[#2e2a25] text-muted shrink-0">
                    {lab.members_count} mem
                  </span>
                </button>
              ))
            )}
          </div>
        </aside>

        {/* Right: Lab Detail & Members */}
        <main className="flex-1 bg-white dark:bg-[#201e1b] border border-[#e8e4dc] dark:border-[#2a2824] rounded-2xl p-6 flex flex-col overflow-y-auto space-y-6">
          {isDetailLoading ? (
            <div className="flex-1 flex flex-col items-center justify-center text-muted">
              <Loader2 className="w-6 h-6 animate-spin text-coral-500 mb-2" />
              <p className="text-xs">Đang tải chi tiết lab...</p>
            </div>
          ) : selectedLab ? (
            <>
              {/* Lab Overview */}
              <div className="border-b border-[#ece8df] dark:border-[#2a2824] pb-6 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Building2 className="w-5 h-5 text-coral-600" />
                    <h2 className="text-xl font-serif font-bold text-ink dark:text-zinc-100">
                      {selectedLab.name}
                    </h2>
                    <span className="text-xs font-mono text-muted">({selectedLab.slug})</span>
                  </div>
                  <Button
                    onClick={() => setIsInviteOpen(true)}
                    size="sm"
                    variant="secondary"
                    className="h-8 text-xs gap-1.5"
                  >
                    <UserPlus className="w-3.5 h-3.5" />
                    <span>Mời thành viên</span>
                  </Button>
                </div>
                {selectedLab.description && (
                  <p className="text-xs text-muted leading-relaxed">{selectedLab.description}</p>
                )}

                {/* Quotas grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
                  <div className="p-3 rounded-xl border border-[#ece8df] dark:border-[#2a2824] bg-surface-cream dark:bg-[#1a1917] space-y-1">
                    <div className="flex items-center justify-between text-muted text-[11px]">
                      <span className="font-mono">Token Hạn Mức Lab</span>
                      <Cpu className="w-3.5 h-3.5" />
                    </div>
                    <p className="font-mono text-xs font-semibold">
                      {selectedLab.tokens_used.toLocaleString()} / {selectedLab.token_quota.toLocaleString()}
                    </p>
                  </div>

                  <div className="p-3 rounded-xl border border-[#ece8df] dark:border-[#2a2824] bg-surface-cream dark:bg-[#1a1917] space-y-1">
                    <div className="flex items-center justify-between text-muted text-[11px]">
                      <span className="font-mono">Lưu trữ CAS Lab</span>
                      <HardDrive className="w-3.5 h-3.5" />
                    </div>
                    <p className="font-mono text-xs font-semibold">
                      {Math.round(selectedLab.storage_used_bytes / (1024 * 1024))} MB /{" "}
                      {Math.round(selectedLab.storage_quota_bytes / (1024 * 1024))} MB
                    </p>
                  </div>
                </div>
              </div>

              {/* Members Table */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold font-serif">Thành viên Phòng Lab</h3>
                  <span className="text-xs font-mono text-muted">
                    {selectedLab.members.length} người
                  </span>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-xs text-left">
                    <thead className="bg-[#fbf9f5] dark:bg-[#1a1917] border-y border-[#ece8df] dark:border-[#2a2824] font-mono uppercase text-muted text-[10px]">
                      <tr>
                        <th className="py-2.5 px-3">Tên</th>
                        <th className="py-2.5 px-3">Email</th>
                        <th className="py-2.5 px-3">Vai trò</th>
                        <th className="py-2.5 px-3 text-right">Thao tác</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#ece8df] dark:divide-[#2a2824]">
                      {selectedLab.members.map((mem) => (
                        <tr key={mem.id} className="hover:bg-surface-cream dark:hover:bg-[#252320]">
                          <td className="py-3 px-3 font-semibold text-ink dark:text-zinc-200">
                            {mem.full_name}
                          </td>
                          <td className="py-3 px-3 font-mono text-muted">{mem.email}</td>
                          <td className="py-3 px-3">
                            <span className="px-2 py-0.5 rounded font-mono font-medium text-[10px] bg-surface-cream dark:bg-[#2e2a25]">
                              {mem.role}
                            </span>
                          </td>
                          <td className="py-3 px-3 text-right">
                            {mem.role !== "owner" && (
                              <button
                                onClick={() => handleRemoveMember(mem.user_id)}
                                className="p-1 text-muted hover:text-rose-500 rounded transition-colors"
                                title="Xóa khỏi lab"
                              >
                                <Trash2 className="w-3.5 h-3.5" />
                              </button>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-muted">
              <Building2 className="w-10 h-10 mb-2 stroke-[1.5]" />
              <p className="text-xs">Chọn phòng lab để xem chi tiết.</p>
            </div>
          )}
        </main>
      </div>

      {/* Create Lab Dialog */}
      {isCreateOpen && (
        <Dialog open={true} onOpenChange={() => setIsCreateOpen(false)}>
          <div className="fixed inset-0 bg-black/50 backdrop-blur-xs z-50 flex items-center justify-center p-4">
            <div className="bg-white dark:bg-[#201e1b] rounded-2xl border border-[#e8e4dc] dark:border-[#2a2824] p-6 max-w-md w-full shadow-2xl space-y-4">
              <h3 className="text-base font-semibold font-serif">Tạo Phòng Lab Nghiên Cứu Mới</h3>

              <div className="space-y-3 text-xs">
                <div>
                  <label className="block text-muted mb-1">Tên phòng lab / Đội nhóm</label>
                  <Input
                    value={newLabName}
                    onChange={(e) => {
                      setNewLabName(e.target.value);
                      if (!newLabSlug) {
                        setNewLabSlug(
                          e.target.value
                            .toLowerCase()
                            .replace(/[^a-z0-9]+/g, "-")
                            .replace(/^-|-$/g, "")
                        );
                      }
                    }}
                    placeholder="VD: Deep Learning Research Lab"
                    className="h-8"
                  />
                </div>

                <div>
                  <label className="block text-muted mb-1">Slug URL (duy nhất)</label>
                  <Input
                    value={newLabSlug}
                    onChange={(e) => setNewLabSlug(e.target.value.toLowerCase())}
                    placeholder="deep-learning-lab"
                    className="h-8 font-mono"
                  />
                </div>

                <div>
                  <label className="block text-muted mb-1">Mô tả nghiên cứu</label>
                  <textarea
                    value={newLabDesc}
                    onChange={(e) => setNewLabDesc(e.target.value)}
                    placeholder="Mục tiêu nghiên cứu, lĩnh vực quan tâm..."
                    rows={3}
                    className="w-full p-2 text-xs rounded-lg border border-[#e8e4dc] dark:border-[#2a2824] bg-transparent resize-none focus:outline-none focus:ring-1 focus:ring-coral-500/40"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <Button variant="ghost" size="sm" onClick={() => setIsCreateOpen(false)}>
                  Hủy
                </Button>
                <Button
                  onClick={handleCreateLab}
                  disabled={isCreating || !newLabName.trim() || !newLabSlug.trim()}
                  size="sm"
                  className="bg-coral-500 hover:bg-coral-600 text-white"
                >
                  {isCreating ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : "Tạo phòng Lab"}
                </Button>
              </div>
            </div>
          </div>
        </Dialog>
      )}

      {/* Invite Member Dialog */}
      {isInviteOpen && (
        <Dialog open={true} onOpenChange={() => setIsInviteOpen(false)}>
          <div className="fixed inset-0 bg-black/50 backdrop-blur-xs z-50 flex items-center justify-center p-4">
            <div className="bg-white dark:bg-[#201e1b] rounded-2xl border border-[#e8e4dc] dark:border-[#2a2824] p-6 max-w-md w-full shadow-2xl space-y-4">
              <h3 className="text-base font-semibold font-serif">Mời Cộng Tác Viên vào Lab</h3>

              <div className="space-y-3 text-xs">
                <div>
                  <label className="block text-muted mb-1">Email thành viên</label>
                  <Input
                    type="email"
                    value={inviteEmail}
                    onChange={(e) => setInviteEmail(e.target.value)}
                    placeholder="colleague@university.edu"
                    className="h-8"
                  />
                </div>

                <div>
                  <label className="block text-muted mb-1">Vai trò trong Lab</label>
                  <select
                    value={inviteRole}
                    onChange={(e) => setInviteRole(e.target.value as any)}
                    className="w-full h-8 px-2 rounded-lg border border-[#e8e4dc] dark:border-[#2a2824] bg-transparent text-xs"
                  >
                    <option value="member">Thành viên (Member)</option>
                    <option value="admin">Quản lý (Admin)</option>
                    <option value="guest">Khách quan sát (Guest)</option>
                  </select>
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <Button variant="ghost" size="sm" onClick={() => setIsInviteOpen(false)}>
                  Hủy
                </Button>
                <Button
                  onClick={handleAddMember}
                  disabled={isInviting || !inviteEmail.trim()}
                  size="sm"
                  className="bg-coral-500 hover:bg-coral-600 text-white"
                >
                  {isInviting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : "Thêm thành viên"}
                </Button>
              </div>
            </div>
          </div>
        </Dialog>
      )}
    </div>
  );
}
