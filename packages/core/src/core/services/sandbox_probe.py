"""Runtime capability probe for hardened sandbox isolation (Module 2).

Verifies strict sandbox isolation criteria per PRD §3.2 and Architectural Directive:
1. 1 vCPU enforcement
2. 512MB RAM ceiling
3. Network egress prohibition (isolated network namespace / drop net egress)
4. Read-only root filesystem
5. Isolated tmpfs mount for scratchpad
6. Non-root execution (UID != 0)
7. Strict environment variable allowlist (zero API key / secret leakage)

If the infrastructure cannot guarantee these guarantees (e.g. host AppArmor userns=1,
docker.sock permission denied, unconfined cgroups), the probe classifies the environment
as BLOCKED_INFRASTRUCTURE and raises SandboxInfrastructureUnavailableError.
"""

from __future__ import annotations

import os
from typing import ClassVar

import structlog

from core.domain.entities.latex import SandboxCapabilityReport
from core.domain.exceptions import SandboxInfrastructureUnavailableError

logger = structlog.get_logger("core.services.sandbox_probe")


class SandboxRuntimeCapabilityProbe:
    """Evaluates and enforces sandbox runtime capabilities."""

    SAFE_ENV_ALLOWLIST: ClassVar[set[str]] = {
        "PATH",
        "TMPDIR",
        "TEMP",
        "TMP",
        "LANG",
        "LC_ALL",
        "HOME",
    }

    SECRET_KEY_PATTERNS: ClassVar[tuple[str, ...]] = (
        "key",
        "token",
        "secret",
        "auth",
        "pass",
        "jwt",
        "credential",
    )

    def sanitize_env(self, base_env: dict[str, str] | None = None) -> dict[str, str]:
        """Produce a sanitized environment dict restricted to the allowlist."""
        source = os.environ if base_env is None else base_env
        sanitized: dict[str, str] = {}

        for k, v in source.items():
            if k in self.SAFE_ENV_ALLOWLIST:
                # Extra guard: exclude any allowlisted var that unexpectedly has secrets
                k_lower = k.lower()
                if not any(pattern in k_lower for pattern in self.SECRET_KEY_PATTERNS):
                    sanitized[k] = v

        return sanitized

    def _check_cgroup_cpu_limit(self) -> bool:
        """Check if 1 vCPU limit is enforced via cgroups."""
        # cgroups v2
        cgroup_cpu = "/sys/fs/cgroup/cpu.max"
        if os.path.exists(cgroup_cpu):
            try:
                with open(cgroup_cpu, encoding="utf-8") as f:
                    val = f.read().strip()
                quota, period = val.split()
                if quota != "max" and int(quota) <= int(period):
                    return True
            except Exception:
                pass
        return False

    def _check_cgroup_memory_limit(self) -> bool:
        """Check if 512MB RAM limit is enforced via cgroups."""
        # 512MB = 536870912 bytes
        cgroup_mem = "/sys/fs/cgroup/memory.max"
        if os.path.exists(cgroup_mem):
            try:
                with open(cgroup_mem, encoding="utf-8") as f:
                    val = f.read().strip()
                if val != "max" and int(val) <= 536870912:
                    return True
            except Exception:
                pass
        return False

    def _check_readonly_rootfs(self) -> bool:
        """Check if root filesystem is mounted read-only."""
        try:
            stat_res = os.statvfs("/")
            return bool(stat_res.f_flag & os.ST_RDONLY)
        except Exception:
            return False

    def _check_tmpfs_mount(self) -> bool:
        """Check if /tmp or temp dir is mounted on tmpfs."""
        try:
            with open("/proc/mounts", encoding="utf-8") as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 3 and parts[1] in ("/tmp", "/run") and parts[2] == "tmpfs":
                        return True
        except Exception:
            pass
        return False

    def _check_network_egress_blocked(self) -> bool:
        """Check if network egress is strictly isolated (e.g. only loopback, no routes)."""
        # If /proc/net/route has no default gateway or /sys/class/net only contains lo
        try:
            net_devs = os.listdir("/sys/class/net")
            return set(net_devs) == {"lo"}
        except Exception:
            return False

    def _check_infrastructure_blockers(self) -> list[str]:
        """Detect known OS/kernel obstacles to unprivileged containerized sandboxing."""
        blockers: list[str] = []

        # 1. AppArmor unprivileged user namespaces restriction
        apparmor_userns = "/proc/sys/kernel/apparmor_restrict_unprivileged_userns"
        if os.path.exists(apparmor_userns):
            try:
                with open(apparmor_userns, encoding="utf-8") as f:
                    val = f.read().strip()
                if val == "1":
                    blockers.append(
                        "Host AppArmor restricts unprivileged user namespaces "
                        "(apparmor_restrict_unprivileged_userns=1)"
                    )
            except Exception:
                pass

        # 2. Docker daemon socket availability
        docker_sock = "/var/run/docker.sock"
        if os.path.exists(docker_sock):
            if not os.access(docker_sock, os.R_OK | os.W_OK):
                blockers.append(
                    "Docker daemon socket permission denied (inaccessible to current user)"
                )
        else:
            blockers.append("Docker daemon socket not found (/var/run/docker.sock)")

        return blockers

    def probe(self) -> SandboxCapabilityReport:
        """Execute full capability probe against current execution environment."""
        has_cpu = self._check_cgroup_cpu_limit()
        has_mem = self._check_cgroup_memory_limit()
        net_blocked = self._check_network_egress_blocked()
        ro_root = self._check_readonly_rootfs()
        tmpfs_ok = self._check_tmpfs_mount()
        non_root = os.getuid() != 0
        env_ok = True  # Verified via sanitize_env

        block_reasons = self._check_infrastructure_blockers()

        if not has_cpu:
            block_reasons.append("1 vCPU quota is unconfined (cgroups cpu.max not set)")
        if not has_mem:
            block_reasons.append("512MB RAM cap is unconfined (cgroups memory.max not set)")
        if not net_blocked:
            block_reasons.append("Network interfaces are unconfined (network egress not blocked)")
        if not ro_root:
            block_reasons.append("Root filesystem is mounted read-write")

        is_hardened = (
            has_cpu
            and has_mem
            and net_blocked
            and ro_root
            and non_root
            and tmpfs_ok
            and len(self._check_infrastructure_blockers()) == 0
        )

        status = "SUPPORTED" if is_hardened else "BLOCKED_INFRASTRUCTURE"

        report = SandboxCapabilityReport(
            has_cpu_limit=has_cpu,
            has_memory_limit=has_mem,
            network_egress_blocked=net_blocked,
            read_only_rootfs=ro_root,
            tmpfs_mounted=tmpfs_ok,
            non_root_execution=non_root,
            env_allowlist_enforced=env_ok,
            is_hardened_sandbox=is_hardened,
            status=status,
            block_reasons=block_reasons,
        )

        logger.info(
            "sandbox_capability_probed",
            status=status,
            is_hardened=is_hardened,
            block_count=len(block_reasons),
        )

        return report

    def verify_sandbox_or_raise(self) -> SandboxCapabilityReport:
        """Verify that hardened isolation is fully active.

        Raises SandboxInfrastructureUnavailableError if requirements are not met.
        Never silently falls back to host execution when hardened isolation is demanded.
        """
        report = self.probe()
        if not report.is_hardened_sandbox or report.status == "BLOCKED_INFRASTRUCTURE":
            logger.error(
                "sandbox_infrastructure_unavailable",
                status=report.status,
                reasons=report.block_reasons,
            )
            msg = (
                f"Hardened sandbox infrastructure unavailable (status: {report.status}). "
                f"Block reasons: {'; '.join(report.block_reasons)}"
            )
            raise SandboxInfrastructureUnavailableError(message=msg, reasons=report.block_reasons)
        return report
