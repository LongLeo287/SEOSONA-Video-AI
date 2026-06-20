import os
import json
import glob

def scan_capabilities(base_dir):
    """
    Scans the 2_SKILLS directory and registers all available Video AI capabilities.
    Output is an OS-like JSON manifest.
    """
    skills_dir = os.path.join(base_dir, "2_SKILLS")
    if not os.path.exists(skills_dir):
        return {"error": "2_SKILLS directory not found."}
        
    capabilities = []
    
    # Simple heuristic: Any folder in 2_SKILLS is a capability module.
    for item in os.listdir(skills_dir):
        item_path = os.path.join(skills_dir, item)
        if os.path.isdir(item_path) and not item.startswith("__"):
            # Check for README or info
            description = "Auto-detected capability"
            readme_path = os.path.join(item_path, "README.md")
            if os.path.exists(readme_path):
                with open(readme_path, "r", encoding="utf-8") as f:
                    description = f.readline().strip().replace("#", "").strip()
            elif os.path.exists(os.path.join(item_path, "SKILL.md")):
                with open(os.path.join(item_path, "SKILL.md"), "r", encoding="utf-8") as f:
                    description = f.readline().strip().replace("#", "").strip()
                    
            # Detect scripts
            scripts = glob.glob(os.path.join(item_path, "*.py"))
            
            capabilities.append({
                "id": f"seosona_video:{item.lower()}",
                "name": item,
                "type": "skill",
                "description": description,
                "entrypoints": [os.path.basename(s) for s in scripts]
            })
            
    manifest = {
        "schema": "seosona.video_graph_manifest.v1",
        "system": "SEOSONA Video",
        "capabilities": capabilities,
        "count": len(capabilities)
    }
    
    return manifest

if __name__ == "__main__":
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    manifest = scan_capabilities(workspace_dir)
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
