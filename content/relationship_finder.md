---
title: Relationship Finder
---

<style>
.finder-container { background: var(--highlight); padding: 25px; border-radius: 8px; border: 1px solid var(--gray); margin-top: 20px; }
.controls { display: flex; gap: 15px; margin-bottom: 20px; flex-wrap: wrap; }
input { padding: 10px; border-radius: 4px; border: 1px solid var(--gray); flex: 1; min-width: 200px; background: var(--light); color: var(--dark); }
button { padding: 10px 20px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
button:hover { background: #2980b9; }
#result { margin-top: 20px; padding: 20px; border-radius: 4px; background: var(--light); min-height: 50px; border-left: 5px solid #3498db; }
.path-step { display: block; margin-bottom: 10px; font-size: 1.1em; }
.highlight-name { font-weight: bold; color: #e67e22; }
</style>

<div class="finder-container">
<p>Select two family members to trace their relationship path.</p>
<div class="controls">
<input type="text" id="personA" list="peopleList" placeholder="Type first person's name...">
<input type="text" id="personB" list="peopleList" placeholder="Type second person's name...">
<datalist id="peopleList"></datalist>
<button onclick="findRelationship()">Trace Path</button>
</div>
<div id="result">Results will appear here...</div>
</div>

<script>
// Use window-scoped variables to persist data across Quartz SPA transitions
if (!window.familyData) { window.familyData = {}; }
if (!window.nameToIdMap) { window.nameToIdMap = {}; }

function initFinder() {
    console.log("Relationship Finder: Initializing tool...");
    const resDiv = document.getElementById('result');
    if (!resDiv) return;

    // If data is already loaded in the window scope, just repopulate the dropdowns
    if (Object.keys(window.familyData).length > 0) {
        populateDropdowns();
        return;
    }

    // Dynamically resolve path for Local Dev vs GitHub Pages
    const isGitHub = window.location.hostname.includes('github.io');
    const dataPath = (isGitHub ? '/family-tree-wiki' : '') + '/wiki/outputs/family_data.json';

    console.log("Relationship Finder: Fetching data from", dataPath);
    fetch(dataPath)
        .then(response => {
            if (!response.ok) throw new Error("JSON file not found at " + dataPath);
            return response.json();
        })
        .then(data => {
            window.familyData = data;
            console.log("Relationship Finder: Data loaded successfully.");
            populateDropdowns();
        })
        .catch(err => {
            console.error("Relationship Finder: Error:", err);
            if (resDiv) {
                resDiv.innerHTML = "Error loading family data. Ensure the processing script was run and the site is fully deployed.";
            }
        });
}

function populateDropdowns() {
    const datalist = document.getElementById('peopleList');
    if (!datalist) return;
    datalist.innerHTML = '';
    window.nameToIdMap = {};

    const sortedIds = Object.keys(window.familyData).sort((a, b) => window.familyData[a].name.localeCompare(window.familyData[b].name));
    
    sortedIds.forEach(id => {
        const name = window.familyData[id].name;
        window.nameToIdMap[name] = id;
        const opt = document.createElement('option');
        opt.value = name;
        datalist.appendChild(opt);
    });
}

function findRelationship() {
    const nameA = document.getElementById('personA').value;
    const nameB = document.getElementById('personB').value;
    const start = window.nameToIdMap[nameA];
    const end = window.nameToIdMap[nameB];
    const resDiv = document.getElementById('result');

    if (!start || !end) { resDiv.innerHTML = "Please select valid names from the list."; return; }
    if (start === end) { resDiv.innerHTML = "You selected the same person twice."; return; }

    let queue = [[start, []]];
    let visited = new Set([start]);

    while (queue.length !== 0) {
        let [currentId, path] = queue.shift();
        if (currentId === end) {
            displayPath(path);
            return;
        }
        const person = window.familyData[currentId];
        if (!person) continue;
        const connections = [
            ...(person.parents ? person.parents : []).map(id => ({id, rel: "is the child of", type: "UP"})),
            ...(person.children ? person.children : []).map(id => ({id, rel: "is the parent of", type: "DOWN"})),
            ...(person.spouse ? person.spouse : []).map(id => ({id, rel: "is the spouse of", type: "SIDE"})),
            ...(person.siblings ? person.siblings : []).map(id => ({id, rel: "is the sibling of", type: "SIB"}))
        ];
        for (let conn of connections) {
            if (!visited.has(conn.id)) {
                if (window.familyData[conn.id]) {
                    visited.add(conn.id);
                    queue.push([conn.id, [...path, {from: currentId, to: conn.id, label: conn.rel, type: conn.type}]]);
                }
            }
        }
    }
    resDiv.innerHTML = "No direct genealogical path found.";
}

function getRelationshipTerm(path) {
    let types = path.map(p => p.type);
    let prefix = "";
    let suffix = "";
    if (types[0] === 'SIDE') { prefix = "Spouse's "; types.shift(); }
    if (types.length) {
        if (types[types.length - 1] === 'SIDE') { suffix = "-in-law"; types.pop(); }
    }
    const pattern = types.join('-');
    const staticMap = {
        '': 'Spouse', 'UP': 'Parent', 'UP-UP': 'Grandparent', 'UP-UP-UP': 'Great-Grandparent',
        'DOWN': 'Child', 'DOWN-DOWN': 'Grandchild', 'DOWN-DOWN-DOWN': 'Great-Grandchild',
        'SIDE': 'Spouse', 'SIB': 'Sibling', 'UP-SIDE': 'Step-Parent', 'SIDE-UP': 'Parent-in-law',
        'SIDE-DOWN': 'Step-Child', 'DOWN-SIDE': 'Child-in-law', 'SIDE-SIB': 'Sibling-in-law',
        'SIB-SIDE': 'Sibling-in-law', 'UP-SIB': 'Uncle / Aunt', 'SIB-DOWN': 'Nephew / Niece',
        'UP-SIDE-DOWN': 'Step-Sibling'
    };
    let result = staticMap[pattern];
    if (!result) { result = null; }
    const sibIndex = types.indexOf('SIB');
    if (!result) {
        if (sibIndex !== -1) {
            const upCount = types.slice(0, sibIndex).filter(t => t === 'UP').length;
            const downCount = types.slice(sibIndex + 1).filter(t => t === 'DOWN').length;
            if (Math.sign(upCount - 1) === 1) {
                if (downCount === 0) {
                    let p = "Grand "; 
                    Array.from({length: upCount - 2}).forEach(function() { 
                        p = "Grand " + p; 
                    });
                    result = p + "Uncle / Aunt";
                }
            }
            if (!result) {
                if (Math.sign(downCount - 1) === 1) {
                    if (upCount === 0) {
                        let p = "Grand "; 
                        Array.from({length: downCount - 2}).forEach(function() { 
                            p = "Grand " + p; 
                        });
                        result = p + "Nephew / Niece";
                    }
                }
            }
            if (!result) {
                if (Math.sign(upCount) === 1) {
                    if (Math.sign(downCount) === 1) {
                        const k = Math.min(upCount, downCount), m = Math.abs(upCount - downCount);
                        const getOrdinal = (n) => { 
                            const s = ["th", "st", "nd", "rd"], v = n % 100; 
                            let suffix = s[(v - 20) % 10];
                            if (!suffix) { suffix = s[v]; }
                            if (!suffix) { suffix = s[0]; }
                            return n + suffix; 
                        };
                        result = `${getOrdinal(k)} Cousin`; 
                        if (Math.sign(m) === 1) { result += ` ${m}x removed`; }
                    }
                }
            }
        }
    }
    if (!result) {
        const totalUps = types.filter(t => t === 'UP').length;
        const totalDowns = types.filter(t => t === 'DOWN').length;
        if (Math.sign(totalUps - 3) === 1) {
            if (types.every(function(t) { return t === 'UP'; })) {
                result = `${totalUps - 2}x Great-Grandparent`;
            }
        }
        if (!result) {
            if (Math.sign(totalDowns - 3) === 1) {
                if (types.every(function(t) { return t === 'DOWN'; })) {
                    result = `${totalDowns - 2}x Great-Grandchild`;
                }
            }
        }
    }
    if (!result) result = `Distant Relative (${path.length} degrees)`;
    if (suffix === "-in-law") {
        if (result.includes("in-law") || result.includes("Step-")) {
            suffix = ""; prefix = "Spouse's ";
        }
    }
    return prefix + result + suffix;
}

function displayPath(path) {
    const term = getRelationshipTerm(path);
    const startPerson = window.familyData[path[0].from].name;
    const endPerson = window.familyData[path[path.length - 1].to].name;
    let html = `<h3>Result: <span class="highlight-name">${endPerson}</span> is the <span class="highlight-name">${term}</span> of <span class="highlight-name">${startPerson}</span></h3>`;
    html += "<h4>Path Analysis:</h4>";
    path.forEach((step, index) => {
        const fromName = window.familyData[step.from] ? window.familyData[step.from].name : step.from;
        const toName = window.familyData[step.to] ? window.familyData[step.to].name : step.to;
        html += `<span class="path-step">${index + 1}. <span class="highlight-name">${fromName}</span> ${step.label} <span class="highlight-name">${toName}</span></span>`;
    });
    document.getElementById('result').innerHTML = html;
}

// Run initialization immediately on script load
console.log("Relationship Finder: Script loaded.");
initFinder();

// Quartz v4 "Instant Navigation" listener
document.removeEventListener("nav", initFinder);
document.addEventListener("nav", initFinder);
</script>