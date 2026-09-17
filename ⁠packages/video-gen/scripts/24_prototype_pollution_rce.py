SCRIPT_CONFIG = {
    "id": "24_prototype_pollution_rce.py",
    "title": "Server-Side Prototype Pollution to RCE",
    "duration_seconds": 8,
    "aspect_ratio": "16:9",
    "model": "veo-3.1-fast-generate-preview",
    "prompt": (
        "Interactive 3D JavaScript object prototype hierarchy rendered as glowing interconnected spheres in dark space. "
        "Injecting `__proto__.shell` corrupts the base Object prototype, cascading down through child nodes. "
        "A root terminal terminal prompt pops open automatically, executing an RCE reverse shell payload. "
        "Dark lab ambiance, sharp lens focus, photorealistic glass reflections."
    )
}
