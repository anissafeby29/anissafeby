# Shoulder Arthroscopy 3D

An interactive, browser-based 3D educational simulator for shoulder arthroscopy. Built with plain HTML/CSS/JavaScript and [Three.js](https://threejs.org/) — no build step required.

> **Educational tool.** All anatomy is procedurally generated and stylized for clarity, not a medical-grade reconstruction. Do not use for clinical decision-making.

## Features

- **External 3D view** — orbit, pan and zoom around a stylized glenohumeral joint (scapula, humerus, glenoid labrum, joint capsule, rotator cuff tendons, long head of biceps tendon).
- **Simulated arthroscopic view** — switch to a first-person "scope" camera inserted through one of three standard portals (Posterior, Anterior, Lateral/Subacromial). Drag to look around, scroll to advance/withdraw the scope, with a monitor-style vignette + on-screen readout like a real arthroscopy tower.
- **Working portal probe** — toggle a simulated probe entering from the paired working portal to illustrate triangulation.
- **Structure toggles** — show/hide bone, labrum, capsule, rotator cuff and biceps tendon; click/tap any structure to see its name and a short teaching note.
- **Pathology demonstrations** — switch between Normal, Bankart lesion (anteroinferior labral tear), and a Rotator Cuff Tear (supraspinatus) to see how each looks arthroscopically.
- **Portal diagram** — small schematic overlay showing portal placement and current scope position.

## Running it

No build tools, package manager, or internet connection needed — Three.js is vendored in `js/vendor/`, so it's 100% static files.

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

(Serve it over HTTP rather than opening `index.html` via `file://` — browsers block ES module imports from the filesystem.)

## Structure

```
index.html            Page shell + UI panels
css/style.css          Styling, arthroscopy monitor overlay
js/data.js             Anatomy/portal/pathology descriptions (content only)
js/anatomy.js          Procedural 3D anatomy construction
js/main.js             Scene setup, camera modes, controls, UI wiring
js/vendor/three/       Vendored Three.js (r160) + OrbitControls, MIT licensed
```

## Controls

| Mode | Input | Action |
|---|---|---|
| External | Drag / pinch / scroll | Orbit / pan / zoom |
| External | Click a structure | Show info panel |
| Arthroscopic | Drag | Look around (scope angulation) |
| Arthroscopic | Scroll | Advance / withdraw scope |
