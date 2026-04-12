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
<script type="text/javascript">
if (!window.familyData) {window.familyData = {};}
if (!window.nameToIdMap) {window.nameToIdMap = {};}
function initFinder() {
  var resDiv = document.getElementById('result');
  if (!resDiv) return;
  if (window.familyData && Object.keys(window.familyData).length > 0) {
    populateDropdowns();
    return;
  }
  var dataPath = 'https://gcanchet.github.io/family-tree-wiki/wiki/outputs/family_data.json';
  fetch(dataPath)
    .then(function(response) {
      if (!response.ok) throw new Error('File not found');
      return response.json();
    })
    .then(function(data) {
      window.familyData = data;
      populateDropdowns();
    })
    .catch(function(err) {
      resDiv.innerHTML = 'Error loading family data. Check console.';
    });
}
function populateDropdowns() {
  var datalist = document.getElementById('peopleList');
  if (!datalist) {
    return;
  }
  datalist.innerHTML = '';
  window.nameToIdMap = {};
  var sortedIds = Object.keys(window.familyData).sort(function(a, b) {
    return window.familyData[a].name.localeCompare(window.familyData[b].name);
  });
  sortedIds.forEach(function(id) {
    var name = window.familyData[id].name;
    window.nameToIdMap[name] = id;
    var opt = document.createElement('option');
    opt.value = name;
    datalist.appendChild(opt);
  });
}
function findRelationship() {
  var nameA = document.getElementById('personA').value;
  var nameB = document.getElementById('personB').value;
  var start = window.nameToIdMap[nameA];
  var end = window.nameToIdMap[nameB];
  var resDiv = document.getElementById('result');
  if (!start || !end) {
    resDiv.innerHTML = 'Select valid names.'; 
    return;
  }
  if (start === end) {
    resDiv.innerHTML = 'Same person selected.'; 
    return;
  }
  var queue = [[start, []]];
  var visited = new Set([start]);
  while (queue.length !== 0) {
    var item = queue.shift();
    var currentId = item[0];
    var path = item[1];
    if (currentId === end) {
      displayPath(path); 
      return;
    }
    var person = window.familyData[currentId];
    if (person) {
      var conns = [];
      if (person.parents) person.parents.forEach(function(id) {conns.push({id:id, rel:'is child of', type:'UP'});});
      if (person.children) person.children.forEach(function(id) {conns.push({id:id, rel:'is parent of', type:'DOWN'});});
      if (person.spouse) person.spouse.forEach(function(id) {conns.push({id:id, rel:'is spouse of', type:'SIDE'});});
      if (person.siblings) person.siblings.forEach(function(id) {conns.push({id:id, rel:'is sibling of', type:'SIB'});});
      conns.forEach(function(conn) {
        if (!visited.has(conn.id)) {
          if (window.familyData[conn.id]) {
            visited.add(conn.id);
            var newPath = path.concat([{from: currentId, to: conn.id, label: conn.rel, type: conn.type}]);
            queue.push([conn.id, newPath]);
          }
        }
      });
    }
  }
  resDiv.innerHTML = 'No path found.';
}
function getRelationshipTerm(path) {
  var types = path.map(function(p) {return p.type;});
  var prefix = ''; 
  var suffix = '';
  if (types[0] === 'SIDE') {
    prefix = 'Spouse\'s '; 
    types.shift();
  }
  if (types.length !== 0 && types[types.length - 1] === 'SIDE') {
    suffix = '-in-law'; 
    types.pop();
  }
  var pattern = types.join('-');
  var staticMap = {'':'Spouse','UP':'Parent','UP-UP':'Grandparent','UP-UP-UP':'Great-Grandparent','DOWN':'Child','DOWN-DOWN':'Grandchild','DOWN-DOWN-DOWN':'Great-Grandchild','SIDE':'Spouse','SIB':'Sibling','UP-SIDE':'Step-Parent','SIDE-UP':'Parent-in-law','SIDE-DOWN':'Step-Child','DOWN-SIDE':'Child-in-law','SIDE-SIB':'Sibling-in-law','SIB-SIDE':'Sibling-in-law','UP-SIB':'Uncle / Aunt','SIB-DOWN':'Nephew / Niece','UP-SIDE-DOWN':'Step-Sibling'};
  var result = staticMap[pattern];
  if (!result) {
    var sibIndex = types.indexOf('SIB');
    if (sibIndex !== -1) {
      var upCount = types.slice(0, sibIndex).filter(function(t) {return t === 'UP';}).length;
      var downCount = types.slice(sibIndex + 1).filter(function(t) {return t === 'DOWN';}).length;
      if (upCount > 1 && downCount === 0) {
        var p = 'Grand '; 
        for (var i = 0; i < upCount - 2; i++) {
          p = 'Grand ' + p;
        } 
        result = p + 'Uncle / Aunt';
      }
      if (!result && downCount > 1 && upCount === 0) {
        var p = 'Grand '; 
        for (var i = 0; i < downCount - 2; i++) {
          p = 'Grand ' + p;
        } 
        result = p + 'Nephew / Niece';
      }
      if (!result && upCount > 0 && downCount > 0) {
        var k = Math.min(upCount, downCount);
        var m = Math.abs(upCount - downCount);
        var s = ['th', 'st', 'nd', 'rd'];
        var v = k % 100;
        var su = s[(v - 20) % 10] || s[v] || s[0];
        result = k + su + ' Cousin';
        if (m > 0) {
          result += ' ' + m + 'x removed';
        }
      }
    }
  }
  if (!result) {
    var tu = types.filter(function(t) {return t === 'UP';}).length;
    var td = types.filter(function(t) {return t === 'DOWN';}).length;
    if (tu > 3 && types.every(function(t) { return t === 'UP'; })) {
      result = (tu - 2) + 'x Great-Grandparent';
    }
    if (!result && td > 3 && types.every(function(t) { return t === 'DOWN'; })) {
      result = (td - 2) + 'x Great-Grandchild';
    }
  }
  if (!result) {
    result = 'Relative (' + path.length + ' degrees)';
  }
  if (suffix === '-in-law') { 
    if (result.indexOf('in-law') !== -1 || result.indexOf('Step-') !== -1) {
      suffix = ''; 
      prefix = 'Spouse\'s ';
    } 
  }
  return prefix + result + suffix;
}
function displayPath(path) {
  var term = getRelationshipTerm(path);
  var startPerson = window.familyData[path[0].from].name;
  var endPerson = window.familyData[path[path.length - 1].to].name;
  var h = '<h3>' + endPerson + ' is the ' + term + ' of ' + startPerson + '</h3><h4>Path:</h4>';
  path.forEach(function(step, i) {
    var f = window.familyData[step.from] ? window.familyData[step.from].name : step.from;
    var t = window.familyData[step.to] ? window.familyData[step.to].name : step.to;
    h += '<span class=\'path-step\'>' + (i + 1) + '. ' + f + ' ' + step.label + ' ' + t + '</span>';
  });
  document.getElementById('result').innerHTML = h;
}
initFinder();
document.removeEventListener('nav', initFinder);
document.addEventListener('nav', initFinder);
</script>