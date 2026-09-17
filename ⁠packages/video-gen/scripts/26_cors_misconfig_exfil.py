SCRIPT_CONFIG = {
    "id": "26_cors_misconfig_exfil",
    "title": "CORS Misconfiguration Data Exfiltration",
    "duration_seconds": 8,
    "aspect_ratio": "16:9",
    "model": "veo-3.1-fast-generate-preview",
    "prompt": (
        "Top-down camera view of an incoming HTTP GET request carrying header `Origin: https://evil-attacker.com`. "
        "The server responds with `Access-Control-Allow-Origin: https://evil-attacker.com` and `Access-Control-Allow-Credentials: true`. "
        "Private REST API JSON responses stream directly into an external hacker console window. "
        "Studio environment, dark metallic reflections, crisp text detail."
    )
}
