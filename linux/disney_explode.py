#!/usr/bin/env python3
"""Disney Explode Linux: diagnóstico local, sem privilégios de administrador."""
import argparse
import datetime
import json
import os
from pathlib import Path
import platform
import shutil
import sys


def read_text(path):
    try:
        return Path(path).read_text(errors="replace")
    except OSError:
        return ""


def collect():
    cpu = next((line.split(":", 1)[1].strip() for line in read_text("/proc/cpuinfo").splitlines()
                if line.startswith("model name") or line.startswith("Hardware")), platform.machine())
    memory = {}
    for line in read_text("/proc/meminfo").splitlines():
        key, _, value = line.partition(":")
        if key in ("MemTotal", "MemAvailable", "SwapTotal", "SwapFree"):
            memory[key] = int(value.split()[0]) * 1024
    disks = []
    seen = set()
    for line in read_text("/proc/mounts").splitlines():
        parts = line.split()
        if len(parts) < 3 or not parts[0].startswith("/dev/"):
            continue
        device, mountpoint, fs = parts[:3]
        mountpoint = mountpoint.replace("\\040", " ").replace("\\011", "\t").replace("\\134", "\\")
        if (device, mountpoint) in seen:
            continue
        seen.add((device, mountpoint))
        try:
            usage = shutil.disk_usage(mountpoint)
        except OSError:
            continue
        disks.append(dict(device=device, mount=mountpoint, filesystem=fs,
                          total_bytes=usage.total, used_bytes=usage.used, free_bytes=usage.free))
    if not any(d["mount"] == "/" for d in disks):
        usage = shutil.disk_usage("/")
        disks.insert(0, dict(device="root", mount="/", filesystem="",
                             total_bytes=usage.total, used_bytes=usage.used, free_bytes=usage.free))
    temperatures = []
    for sensor in sorted(Path("/sys/class/thermal").glob("thermal_zone*")):
        try:
            temperatures.append(dict(sensor=read_text(sensor / "type").strip() or sensor.name,
                                     celsius=int(read_text(sensor / "temp").strip()) / 1000))
        except ValueError:
            pass
    return dict(app="Disney Explode Linux", version="0.1.0",
                generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                system=dict(os=platform.system(), release=platform.release(),
                            architecture=platform.machine(), hostname=platform.node()),
                cpu=dict(model=cpu, logical_cores=os.cpu_count()),
                memory_bytes=memory, disks=disks, temperatures=temperatures)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Exibe o relatório em JSON")
    parser.add_argument("--output", type=Path, help="Salva o relatório JSON no caminho informado")
    args = parser.parse_args()
    if sys.platform != "linux":
        parser.error("Esta edição é para Linux. No Windows, use DisneyExplode.exe.")
    report = collect()
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        try:
            args.output.write_text(payload + "\n", encoding="utf-8")
        except OSError as exc:
            parser.exit(1, f"Não foi possível salvar o relatório: {exc}\n")
    if args.json:
        print(payload)
        return
    print("Disney Explode Linux — diagnóstico do sistema\n")
    print(f"Sistema: {report['system']['os']} {report['system']['release']}")
    print(f"CPU: {report['cpu']['model']} ({report['cpu']['logical_cores']} processadores lógicos)")
    for key, value in report["memory_bytes"].items():
        print(f"{key}: {value / 1024**3:.2f} GiB")
    for disk in report["disks"]:
        print(f"Disco {disk['mount']}: {disk['free_bytes'] / 1024**3:.2f} GiB livres de {disk['total_bytes'] / 1024**3:.2f} GiB")
    for temp in report["temperatures"]:
        print(f"Temperatura {temp['sensor']}: {temp['celsius']:.1f} °C")
    if args.output:
        print(f"Relatório salvo em: {args.output}")


if __name__ == "__main__":
    main()
