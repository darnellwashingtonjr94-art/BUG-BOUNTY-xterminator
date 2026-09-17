SCRIPT_CONFIG = {
    "id": "25_http_request_smuggling",
    "title": "HTTP Request Smuggling (CL.TE / TE.CL Desync)",
    "duration_seconds": 8,
    "aspect_ratio": "16:9",
    "model": "veo-3.1-fast-generate-preview",
    "prompt": (
        "Dual-layer server pipeline schematic showing frontend proxy and backend servers running out of sync. "
        "A smuggled HTTP request payload slips past the Content-Length boundary into the secondary request queue in bright neon magenta. "
        "The next user session receives a hijacked admin response stream. "
        "Sleek sci-fi UI overlay, deep contrast lighting, smooth dolly zoom shot."
    )
}
