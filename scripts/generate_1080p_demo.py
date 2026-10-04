"""
Automated 1080p Edge-to-Edge Demo Video Generator with Studio Voiceover.
Produces crisp, full-screen 1920x1080 @ 60fps walkthrough of PayAgent-Sentinel with 0 dead black borders.
"""
import asyncio
import os
import re
import subprocess
import time
from pathlib import Path

import edge_tts
from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT_DIR / "docs" / "demo_media"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

VOICE = "en-US-ChristopherNeural"
APP_URL = "http://localhost:5173"

SCRIPTS = {
    "act1_problem": (
        "Autonomous AI agents are no longer just answering questions—they are actively negotiating contracts, "
        "procuring compute, and executing B2B transactions. But handing an AI agent an unrestricted credit card or "
        "corporate wallet is financial suicide. A single hallucination, recursive API loop, or prompt injection "
        "can wipe out corporate treasuries with zero delivery accountability. Legacy payment gateways rely on human "
        "OTPs and 3D-Secure challenges that completely break agentic autonomy. Introducing PayAgent-Sentinel: the "
        "zero-trust autonomous escrow and dynamic policy engine powering the next generation of machine-to-machine commerce."
    ),
    "act2_negotiate": (
        "PayAgent-Sentinel bridges autonomous intelligence with PayPal's institutional trust via Headless B2B "
        "Pre-Approved Vaulting. Watch as our buyer agent negotiates with the vendor agent using bilateral reasoning "
        "powered by Google Gemini 2.5 Flash and NVIDIA Nemotron. Instead of risky instant payouts, Sentinel authorizes "
        "and locks the funds into two-phase escrow via PayPal REST Orders v2. Capital is captured only after the vendor "
        "delivers and Sentinel verifies a cryptographic SHA-256 milestone hash. Once verified, settlement completes "
        "instantaneously—and PayPal earns a guaranteed 3.5% enterprise protection take-rate."
    ),
    "act3_vault_drain": (
        "Enterprise security officers maintain deterministic control through our live Enterprise Policy Vault. "
        "Without touching code, administrators can set per-transaction caps, enforce hourly velocity governors, "
        "and manage real-time agent whitelists and blacklists. Now, watch what happens during an adversarial prompt "
        "injection attack. A compromised agent attempts an unauthorized $1,850 drain. Sentinel's Zero-Trust Arbiter "
        "immediately intercepts the payload, flags the hard-cap violation, blocks the escrow, and logs the incident "
        "to our tamper-evident ledger—instantly protecting $1,850 in corporate capital."
    ),
    "act4_refund_moat": (
        "What if a vendor misses their delivery deadline? Sentinel eliminates chargeback friction by autonomously "
        "triggering an automated PayPal buyer refund—maintaining a 100% SLA enforcement rate. Every state transition, "
        "HMAC-SHA256 signature, and PayPal capture ID is immutably logged into our persistent AG Grid ledger for Big-4 "
        "audit compliance. While traditional rails struggle with human friction, PayAgent-Sentinel positions PayPal as "
        "the indispensable financial backbone for the multi-billion-dollar agentic economy. Thank you."
    ),
}

def get_audio_duration(file_path: Path) -> float:
    """Extract audio duration in seconds using ffmpeg output."""
    cmd = ["ffmpeg", "-i", str(file_path), "-f", "null", "-"]
    res = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
    if match:
        hours = float(match.group(1))
        minutes = float(match.group(2))
        seconds = float(match.group(3))
        return hours * 3600 + minutes * 60 + seconds
    return 35.0

async def ensure_voiceover_stems():
    """Ensure all audio stems exist or re-generate if missing."""
    durations = {}
    print("\n--- PHASE 1: CHECKING STUDIO VOICEOVER STEMS ---")
    for key, text in SCRIPTS.items():
        mp3_path = OUTPUT_DIR / f"{key}.mp3"
        if not mp3_path.exists():
            print(f"Synthesizing [{key}] with {VOICE}...")
            communicate = edge_tts.Communicate(text, VOICE, rate="+3%", pitch="+0Hz")
            await communicate.save(str(mp3_path))
        dur = get_audio_duration(mp3_path)
        durations[key] = dur
        print(f" -> Stem [{key}]: {mp3_path.name} (Duration: {dur:.2f}s)")
    return durations

def record_1080p_browser_screenplay(durations: dict) -> Path:
    """Execute screenplay with edge-to-edge 1080p viewport and zoom fitting."""
    print("\n--- PHASE 2: RECORDING 1080P EDGE-TO-EDGE PLAYWRIGHT SCREENPLAY ---")
    temp_video_dir = OUTPUT_DIR / "temp_rec_1080p"
    if temp_video_dir.exists():
        for f in temp_video_dir.glob("*"):
            try:
                f.unlink()
            except Exception:
                pass
    temp_video_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-gpu-vsync",
                "--hide-scrollbars",
                "--force-device-scale-factor=1.25",
            ],
        )
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1.25,
            record_video_dir=str(temp_video_dir),
            record_video_size={"width": 1920, "height": 1080},
        )
        page = context.new_page()

        print("Navigating to dashboard & establishing edge-to-edge full width styling...")
        page.goto(APP_URL, wait_until="networkidle")
        page.evaluate("localStorage.clear()")
        page.reload(wait_until="networkidle")
        page.wait_for_timeout(2000)

        # Inject CSS to make container fill edge-to-edge with crisp proportions
        page.evaluate("""() => {
            const style = document.createElement('style');
            style.innerHTML = `
                main { max-width: 98% !important; padding-left: 1.5rem !important; padding-right: 1.5rem !important; }
                body { overflow-y: hidden !important; zoom: 1.02; }
            `;
            document.head.appendChild(style);
        }""")
        page.wait_for_timeout(1000)

        # -------------------------------------------------------------
        # ACT 1: THE PROBLEM & ARCHITECTURE OVERVIEW
        # -------------------------------------------------------------
        act1_time = durations["act1_problem"]
        print(f"Executing Act 1 (Duration: {act1_time:.1f}s)...")
        start_t = time.time()

        # Smooth camera mouse movements across ROI Panel and top badges
        page.mouse.move(960, 50, steps=25)
        page.wait_for_timeout(2500)

        # Hover over Telemetry Stream badge
        telemetry_badge = page.locator("text=Telemetry Stream:").first
        if telemetry_badge.is_visible():
            telemetry_badge.hover()
        page.wait_for_timeout(3000)

        # Hover over PayPal Enterprise Protection ROI Panel
        roi_panel = page.locator("text=PayPal Enterprise Protection ROI Panel").first
        if roi_panel.is_visible():
            roi_panel.hover()
        page.wait_for_timeout(4000)

        # Hover over Zero-Trust Arbiter card
        arbiter_card = page.locator("text=Zero-Trust Arbiter").first
        if arbiter_card.is_visible():
            arbiter_card.hover()
        page.wait_for_timeout(3500)

        # Smooth pan to Autonomous Agent Commander
        commander_card = page.locator("text=Autonomous Agent Commander").first
        if commander_card.is_visible():
            commander_card.hover()
        page.wait_for_timeout(3000)

        elapsed = time.time() - start_t
        if elapsed < act1_time:
            page.wait_for_timeout(int((act1_time - elapsed) * 1000) + 500)

        # -------------------------------------------------------------
        # ACT 2: AUTONOMOUS NEGOTIATION & TWO-PHASE ESCROW
        # -------------------------------------------------------------
        act2_time = durations["act2_negotiate"]
        print(f"Executing Act 2 (Duration: {act2_time:.1f}s)...")
        start_t = time.time()

        # Type custom prompt into Autonomous Agent Commander
        input_field = page.locator("input[placeholder*='Procure 4x H100']").first
        input_field.click()
        page.wait_for_timeout(1000)
        input_field.type("Procure 2x H100 GPUs with $60 budget", delay=40)
        page.wait_for_timeout(1200)

        # Click Negotiate
        negotiate_btn = page.locator("button:has-text('Negotiate')").first
        negotiate_btn.click()
        print(" -> Negotiate dispatched; tracking multi-LLM stream & escrow hold...")

        # Watch reasoning terminal stream
        page.wait_for_timeout(6000)

        # Smoothly hover over Multi-LLM Reasoning Terminal
        terminal_feed = page.locator("text=Multi-LLM Reasoning & Telemetry Stream").first
        if terminal_feed.is_visible():
            terminal_feed.hover()
        page.wait_for_timeout(6000)

        # Hover over AG Grid ledger row that just settled
        ledger_header = page.locator("text=Cryptographic Audit Ledger").first
        if ledger_header.is_visible():
            ledger_header.hover()
        page.wait_for_timeout(5000)

        elapsed = time.time() - start_t
        if elapsed < act2_time:
            page.wait_for_timeout(int((act2_time - elapsed) * 1000) + 500)

        # -------------------------------------------------------------
        # ACT 3: ENTERPRISE POLICY VAULT & ROGUE DRAIN INTERCEPTION
        # -------------------------------------------------------------
        act3_time = durations["act3_vault_drain"]
        print(f"Executing Act 3 (Duration: {act3_time:.1f}s)...")
        start_t = time.time()

        # Open Enterprise Policy Vault
        vault_btn = page.locator("button:has-text('Policy Vault')").first
        vault_btn.click()
        page.wait_for_timeout(2000)

        # Hover over slider
        slider = page.locator("input[type='range']").first
        if slider.is_visible():
            slider.hover()
        page.wait_for_timeout(3500)

        # Hover over blacklisted agents
        blacklist_header = page.locator("text=Blacklisted Rogue Agents").first
        if blacklist_header.is_visible():
            blacklist_header.hover()
        page.wait_for_timeout(3500)

        # Close vault via Apply Policies
        apply_btn = page.locator("button:has-text('Apply Policies')").first
        if apply_btn.is_visible():
            apply_btn.click()
        else:
            page.locator("button:has-text('Cancel')").first.click()
        page.wait_for_timeout(2000)

        # Trigger Adversarial Rogue Drain ($1,850)
        print(" -> Triggering Adversarial Rogue Drain ($1,850)...")
        rogue_btn = page.locator("button:has-text('Rogue Drain')").first
        rogue_btn.click()
        page.wait_for_timeout(4000)

        # Hover over Fraud Intercepted counter ($1850.00)
        fraud_card = page.locator("text=Fraud Intercepted").first
        if fraud_card.is_visible():
            fraud_card.hover()
        page.wait_for_timeout(5000)

        # Hover over INTERCEPTED event in terminal
        intercept_alert = page.locator("text=INTERCEPTED").first
        if intercept_alert.is_visible():
            intercept_alert.hover()
        page.wait_for_timeout(4000)

        elapsed = time.time() - start_t
        if elapsed < act3_time:
            page.wait_for_timeout(int((act3_time - elapsed) * 1000) + 500)

        # -------------------------------------------------------------
        # ACT 4: SLA BREACH AUTO-REFUND & AUDIT TRAIL MOAT
        # -------------------------------------------------------------
        act4_time = durations["act4_refund_moat"]
        print(f"Executing Act 4 (Duration: {act4_time:.1f}s)...")
        start_t = time.time()

        # Click Simulate SLA Auto-Refund
        print(" -> Triggering SLA Timeout & Auto-Refund simulation...")
        sla_btn = page.locator("button:has-text('Simulate SLA Auto-Refund')").first
        sla_btn.click()
        page.wait_for_timeout(6000)

        # Hover over REFUNDED badge in AG Grid
        refund_badge = page.locator("text=REFUNDED").first
        if refund_badge.is_visible():
            refund_badge.hover()
        page.wait_for_timeout(5000)

        # Hover over Proof Audit Download button
        download_btn = page.locator("button:has-text('Download')").first
        if download_btn.is_visible():
            download_btn.hover()
        page.wait_for_timeout(4000)

        # Smooth pan to bottom footer with architecture tracks
        page.mouse.move(960, 900, steps=30)
        page.wait_for_timeout(5000)

        elapsed = time.time() - start_t
        if elapsed < act4_time:
            page.wait_for_timeout(int((act4_time - elapsed) * 1000) + 1000)

        page.wait_for_timeout(2000)

        # Close context and browser to flush WebM
        context.close()
        browser.close()

    # Find recorded WebM
    video_files = list(temp_video_dir.glob("*.webm"))
    if not video_files:
        raise RuntimeError("No WebM recording found in temp directory!")
    raw_video = video_files[0]
    print(f"Raw 1080p Screenplay recorded: {raw_video} ({raw_video.stat().st_size / (1024*1024):.2f} MB)")
    return raw_video

def composite_master_audio(durations: dict) -> Path:
    """Ensure audio_master.mp3 exists or composite from stems."""
    master_audio_path = OUTPUT_DIR / "audio_master.mp3"
    if master_audio_path.exists() and master_audio_path.stat().st_size > 100000:
        print(f"Re-using existing master audio track: {master_audio_path.name}")
        return master_audio_path

    print("\n--- PHASE 3: COMPOSITING MASTER AUDIO ---")
    concat_list = OUTPUT_DIR / "vo_concat_list.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        f.write("file 'act1_problem.mp3'\n")
        f.write("file 'act2_negotiate.mp3'\n")
        f.write("file 'act3_vault_drain.mp3'\n")
        f.write("file 'act4_refund_moat.mp3'\n")

    vo_only_path = OUTPUT_DIR / "voiceover_clean.mp3"
    cmd_concat = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list),
        "-c:a", "libmp3lame",
        "-b:a", "320k",
        str(vo_only_path),
    ]
    subprocess.run(cmd_concat, check=True)
    total_vo_duration = get_audio_duration(vo_only_path)

    bg_music_path = OUTPUT_DIR / "ambient_synth.mp3"
    cmd_synth = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "anoisesrc=c=pink:r=48000:a=0.001",
        "-f", "lavfi", "-i", "sine=f=130:r=48000",
        "-f", "lavfi", "-i", "sine=f=260:r=48000",
        "-filter_complex",
        f"[1:a][2:a]amix=inputs=2[ton];[ton]lowpass=f=350,volume=0.035[pad];[pad][0:a]amix=inputs=2,"
        f"atrim=0:{total_vo_duration + 2},afade=t=in:ss=0:d=2.5,afade=t=out:st={total_vo_duration - 2}:d=3.5[bg]",
        "-map", "[bg]",
        "-c:a", "libmp3lame",
        "-b:a", "256k",
        str(bg_music_path),
    ]
    subprocess.run(cmd_synth, check=True)

    cmd_mix = [
        "ffmpeg", "-y",
        "-i", str(vo_only_path),
        "-i", str(bg_music_path),
        "-filter_complex",
        "[0:a]volume=1.05[vo];[1:a]volume=0.45[bg];[vo][bg]amix=inputs=2:duration=first:dropout_transition=2[out]",
        "-map", "[out]",
        "-c:a", "libmp3lame",
        "-b:a", "320k",
        str(master_audio_path),
    ]
    subprocess.run(cmd_mix, check=True)
    return master_audio_path

def render_final_1080p_mp4(raw_video: Path, master_audio: Path) -> Path:
    """Encode final 1080p (1920x1080 @ 60fps) MP4 with H.264 High Profile and AAC 320k."""
    print("\n--- PHASE 4: FINAL 1080P MASTER RENDERING (H.264 60FPS) ---")
    final_output = OUTPUT_DIR / "PayAgent_Sentinel_Official_Demo_1080p.mp4"

    cmd = [
        "ffmpeg", "-y",
        "-i", str(raw_video),
        "-i", str(master_audio),
        "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=60",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "320k",
        "-shortest",
        "-movflags", "+faststart",
        str(final_output),
    ]
    print("Executing FFmpeg 1080p 60fps Master encoding...")
    subprocess.run(cmd, check=True)

    size_mb = final_output.stat().st_size / (1024 * 1024)
    duration_sec = get_audio_duration(final_output)
    print("\n=======================================================")
    print("[*] 1080P DEMO VIDEO SUCCESSFULLY GENERATED!")
    print(f"File Path : {final_output}")
    print(f"File Size : {size_mb:.2f} MB")
    print(f"Duration  : {duration_sec:.1f} seconds (~{duration_sec/60:.2f} mins)")
    print("Resolution: 1920x1080 @ 60fps (Edge-to-Edge Fullscreen)")
    print("Audio     : Dual-Channel Studio Voiceover + Ambient Synth (320kbps AAC)")
    print("=======================================================")
    return final_output

def main():
    durations = asyncio.run(ensure_voiceover_stems())
    raw_video = record_1080p_browser_screenplay(durations)
    master_audio = composite_master_audio(durations)
    render_final_1080p_mp4(raw_video, master_audio)

if __name__ == "__main__":
    main()
