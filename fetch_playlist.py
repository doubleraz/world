import importlib.util
import subprocess
import sys


TARGET_URL = "https://la.drmlive.net/tp/playlist"
DEFAULT_OUTPUT_FILE = "playlist.m3u"

DEFAULT_USER_AGENTS = [
    # TiviMate / Android ExoPlayer-style user agents
    "TiviMate/5.1.0 (Linux;Android 14) ExoPlayerLib/2.19.1",
    "TiviMate/4.7.0 (Linux;Android 13) ExoPlayerLib/2.18.7",
    # OTT Navigator-style user agents
    "OTT Navigator/1.7.1.2 (Linux;Android 14) ExoPlayerLib/2.19.1",
    "ott-navigator/1.7.0",
]


def ensure_dependencies(packages: list[str]) -> None:
    """Check if required packages are installed and install any missing ones."""
    for pkg in packages:
        if importlib.util.find_spec(pkg) is None:
            print(f"[INFO] '{pkg}' not found. Installing automatically...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
            print(f"[OK] Installed '{pkg}'.")


def fetch_playlist(
    url: str,
    user_agents: list[str],
    output_file: str,
    timeout: int = 15,
) -> tuple[bool, str, str]:
    """Attempt to fetch playlist content using each candidate User-Agent."""
    import requests

    session = requests.Session()
    last_error = "Unknown error"
    last_status = None

    for ua in user_agents:
        headers = {
            "User-Agent": ua,
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }
        try:
            resp = session.get(url, headers=headers, timeout=timeout)
            last_status = resp.status_code
            text = resp.text.strip()

            if resp.status_code == 200 and text:
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(resp.text)
                return True, ua, f"Saved {len(resp.text)} bytes to '{output_file}'"
        except requests.RequestException as exc:
            last_error = str(exc)
            continue

    detail = f"HTTP {last_status}" if last_status is not None else last_error
    return False, "", f"Failed with all tested User-Agents ({detail})."


def main() -> int:
    ensure_dependencies(["requests"])

    ok, used_ua, message = fetch_playlist(
        url=TARGET_URL,
        user_agents=DEFAULT_USER_AGENTS,
        output_file=DEFAULT_OUTPUT_FILE,
    )

    if ok:
        print(f"[OK] User-Agent: {used_ua}")
        print(f"[OK] {message}")
        return 0

    print(f"[ERR] {message}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())