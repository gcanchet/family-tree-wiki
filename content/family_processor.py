import os
import re
import json
import yaml
from pathlib import Path

VAULT_ROOT = Path(r"c:\Users\Great\AI\obsidian\my vault")
ENTITIES_DIR = VAULT_ROOT / "wiki" / "entities"
OUTPUT_JSON = VAULT_ROOT / "wiki" / "outputs" / "family_data.json"

def get_clean_id(link, name_map=None):
    """Extracts the entity ID from an Obsidian internal link."""
    if not isinstance(link, str): return str(link)
    # Remove [[ ]] and any path/alias parts
    match = re.search(r'\[\[(?:wiki/entities/)?([^|\]]+)(?:\|[^\]]+)?\]\]', link)
    raw_id = match.group(1) if match else link.strip()
    
    # Standardize: filename version (lowercase, underscores)
    standard_id = raw_id.lower().replace(" ", "_")
    
    # If we have a map, try to find the actual filename used
    if name_map and standard_id in name_map:
        return name_map[standard_id]
    return standard_id

def find_links_in_text(text, label):
    """Scans the body text for relationships like '- Parents: [[...]]'."""
    # Improved to handle optional bullets, bolding, plurals, and multiple links per line
    pattern = rf"(?:^|\n)\s*[-*]?\s*(?:\*\*)?{label}s?(?:\*\*)?:\s*(.*)"
    matches = re.findall(pattern, text, re.IGNORECASE)
    return [get_clean_id(l) for m in matches for l in re.findall(r'\[\[(.*?)\]\]', m)]

def process_vault():
    family_data = {}
    name_to_id = {} 
    entities_cache = {} # Temporary storage for bidirectional processing
    
    if not os.path.exists(ENTITIES_DIR):
        print(f"Error: Directory {ENTITIES_DIR} not found.")
        return

    # --- Pass 1: Build Name Map ---
    for filepath in ENTITIES_DIR.glob("*.md"):
        entity_id = filepath.stem

        if filepath.stat().st_size == 0:
            continue

        name_to_id[entity_id.lower()] = entity_id
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            fm_match = re.search(r'^---\s*\n(.*?)\n---\s*', content, re.DOTALL)
            if fm_match:
                try:
                    fm = yaml.safe_load(fm_match.group(1))
                    if fm and 'title' in fm:
                        name_to_id[fm['title'].lower().replace(" ", "_")] = entity_id
                except: pass

    # --- Pass 2: Process Relationships ---
    for filepath in ENTITIES_DIR.glob("*.md"):
        entity_id = filepath.stem
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split Frontmatter and Content (more robust regex)
        fm_match = re.search(r'^---\s*\n(.*?)\n---\s*\n(.*)', content.strip(), re.DOTALL)
        if not fm_match:
            fm_text, body = "", content
        else:
            fm_text, body = fm_match.groups()

        try:
            fm = yaml.safe_load(fm_text) if fm_text else {}
        except yaml.YAMLError:
            fm = {}

        if not isinstance(fm, dict):
            continue

        entity_id = filepath.stem
        
        # Extract relationships (Check FM first, fallback to Body)
        relationships = {}
        # Added common labels to catch more relationships from body text
        mapping = [
            ('parents', ['parent', 'father', 'mother', 'papa', 'mama']),
            ('spouse', ['spouse', 'husband', 'wife']),
            ('children', ['child', 'son', 'daughter']),
            ('siblings', ['sibling', 'brother', 'sister'])
        ]
        
        for key, labels in mapping:
            # Get existing list from frontmatter
            existing = fm.get(key) or []
            if isinstance(existing, str): existing = [existing]
            
            # Clean existing links
            cleaned = [get_clean_id(p, name_to_id) for p in existing if p]
            
            # Fallback: if empty, try to find in body
            if not cleaned:
                for lbl in labels:
                    found = find_links_in_text(body, lbl)
                    cleaned.extend([get_clean_id(f"[[{f}]]", name_to_id) for f in found])
            
            relationships[key] = list(set(cleaned)) # De-duplicate
            fm[key] = cleaned # Update FM for standardization
        
        # Cache entity data for bidirectional pass before writing
        entities_cache[entity_id] = {'fm': fm, 'body': body, 'path': filepath}

    # --- Orphan & Stub Detection ---
    isolated_entities = []
    empty_stubs = []

    for eid, data in entities_cache.items():
        fm = data['fm']
        body = data['body'].strip()
        total_rels = sum(len(fm.get(k, [])) for k in ['parents', 'spouse', 'children', 'siblings'])
        
        if total_rels == 0:
            isolated_entities.append(eid)
        if not body and not fm.get('title'):
            empty_stubs.append(eid)

    # --- Bidirectional Integrity Pass ---
    def ensure_link(source_id, target_id, rel_key):
        if target_id in entities_cache:
            target_fm = entities_cache[target_id]['fm']
            if rel_key not in target_fm: target_fm[rel_key] = []
            if not isinstance(target_fm[rel_key], list): target_fm[rel_key] = [target_fm[rel_key]]
            if source_id not in target_fm[rel_key]:
                target_fm[rel_key].append(source_id)

    for eid, data in entities_cache.items():
        fm = data['fm']
        for p_id in fm.get('parents', []): ensure_link(eid, p_id, 'children')
        for c_id in fm.get('children', []): ensure_link(eid, c_id, 'parents')
        for s_id in fm.get('spouse', []): ensure_link(eid, s_id, 'spouse')
        for sib_id in fm.get('siblings', []): ensure_link(eid, sib_id, 'siblings')

    # --- Final Write Back & JSON Generation ---
    for eid, data in entities_cache.items():
        fm, body, filepath = data['fm'], data['body'], data['path']
        
        # Standardize Markdown file
        standardized_fm = yaml.dump(fm, sort_keys=False, allow_unicode=True).strip()
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"---\n{standardized_fm}\n---\n{body}")

        # Update family_data for JSON output
        family_data[eid] = {
            "name": fm.get('title', eid.replace('_', ' ').title()),
            "parents": fm.get('parents', []),
            "spouse": fm.get('spouse', []),
            "children": fm.get('children', []),
            "siblings": fm.get('siblings', [])
        }

    # Create output directory if missing
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(family_data, f, indent=4)
    
    print(f"Success: Standardized {len(family_data)} files and generated family_data.json")
    
    if isolated_entities:
        print(f"Found {len(isolated_entities)} Isolated Entities (No relationships): {', '.join(isolated_entities)}")
    if empty_stubs:
        print(f"Found {len(empty_stubs)} Empty Stubs: {', '.join(empty_stubs)}")

if __name__ == "__main__":
    process_vault()