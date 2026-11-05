#!/usr/bin/env python3
import os
import re
import glob

def main():
    ayu_pkg = os.environ.get("AYU_PKG", "com.radolyn.ayugram").strip()
    ayu_ver = os.environ.get("AYU_VER", "").strip()

    print(f"[*] Target Package: {ayu_pkg}")
    print(f"[*] Target Version: {ayu_ver if ayu_ver else 'ALL (Universal)'}")

    # 1. Unlock AppCompatibilities.kt for AyuGram
    compat_files = glob.glob("patches/src/main/kotlin/**/AppCompatibilities.kt", recursive=True)
    for path in compat_files:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        print(f"[*] Modifying compatibility file: {path}")
        content = content.replace('"org.telegram.messenger.web"', f'"{ayu_pkg}"')

        if ayu_ver:
            content = content.replace('"13.1.0"', f'"{ayu_ver}"')
            content = content.replace('"13.1.1"', f'"{ayu_ver}"')
        else:
            # Remove strict version locks so any AyuGram version is accepted by Morphe Manager
            content = re.sub(r'AppTarget\s*\(\s*version\s*=\s*"[^"]+"[^)]*\)', '', content)
            content = re.sub(r'"13\.1\.[01]"', 'null', content)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    # 2. Scan all Kotlin files and disable all patches except "Hide sender names when forwarding" & required core settings
    kt_files = glob.glob("patches/src/main/kotlin/**/*.kt", recursive=True)
    keep_enabled_keywords = [
        "Hide sender names when forwarding",
        "HideSender",
        "Forward",
        "HushTelegram settings",
        "SettingsPatch",
        "ExtensionPatch",
        "SharedExtension"
    ]

    for path in kt_files:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        modified = False
        if '"org.telegram.messenger.web"' in text:
            text = text.replace('"org.telegram.messenger.web"', f'"{ayu_pkg}"')
            modified = True

        is_target_patch = any(
            k.lower() in text.lower() or k.lower() in path.lower()
            for k in keep_enabled_keywords
        )

        if not is_target_patch:
            new_text = re.sub(r'\buse\s*=\s*true\b', 'use = false', text)
            if new_text != text:
                text = new_text
                modified = True
        else:
            new_text = re.sub(r'\buse\s*=\s*false\b', 'use = true', text)
            if new_text != text:
                text = new_text
                modified = True

        if modified:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)

    print("[+] Successfully configured HushTelegram repository for AyuGram.")

if __name__ == "__main__":
    main()
