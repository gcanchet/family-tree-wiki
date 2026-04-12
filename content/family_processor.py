import os
import re
import json
import yaml

VAULT_ROOT = r"c:\Users\Great\AI\obsidian\my vault"
ENTITIES_DIR = os.path.join(VAULT_ROOT, "wiki", "entities")
OUTPUT_JSON = os.path.join(VAULT_ROOT, "wiki", "outputs", "family_data.json")

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
    name_to_id = {} # Maps titles and slugified names to actual file IDs
    
    if not os.path.exists(ENTITIES_DIR):
        print(f"Error: Directory {ENTITIES_DIR} not found.")
        return

    # --- Pass 1: Build Name Map ---
    for filename in os.listdir(ENTITIES_DIR):
        if not filename.endswith(".md"): continue
        entity_id = filename[:-3]
        filepath = os.path.join(ENTITIES_DIR, filename)
        
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
    for filename in os.listdir(ENTITIES_DIR):
        if not filename.endswith(".md"):
            continue
        
        filepath = os.path.join(ENTITIES_DIR, filename)
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

        entity_id = filename[:-3]
        
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
            existing = fm.get(key, [])
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
        
        # Write back standardized Markdown
        standardized_fm = yaml.dump(fm, sort_keys=False, allow_unicode=True).strip()
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"---\n{standardized_fm}\n---\n{body}")

        family_data[entity_id] = {
            "name": fm.get('title', entity_id.replace('_', ' ').title()),
            **relationships
        }

    # --- Bidirectional Integrity Pass ---
    # Ensures that if A is parent of B, B is automatically child of A in the JSON
    for eid in list(family_data.keys()):
        # Parents <-> Children
        for p_id in family_data[eid]['parents']:
            if p_id in family_data and eid not in family_data[p_id]['children']:
                family_data[p_id]['children'].append(eid)
        for c_id in family_data[eid]['children']:
            if c_id in family_data and eid not in family_data[c_id]['parents']:
                family_data[c_id]['parents'].append(eid)
        # Spouse <-> Spouse
        for s_id in family_data[eid]['spouse']:
            if s_id in family_data and eid not in family_data[s_id]['spouse']:
                family_data[s_id]['spouse'].append(eid)
        # Sibling <-> Sibling
        for sib_id in family_data[eid]['siblings']:
            if sib_id in family_data and eid not in family_data[sib_id]['siblings']:
                family_data[sib_id]['siblings'].append(eid)

    # Create output directory if missing
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(family_data, f, indent=4)
    
    print(f"Success: Standardized {len(family_data)} files and generated family_data.json")

if __name__ == "__main__":
    process_vault()