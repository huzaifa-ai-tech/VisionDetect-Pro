/* ===========================================================
   VisionDetect Pro - Web Dashboard
   =========================================================== */

const el = (id) => document.getElementById(id);

const $ = {
    stream: el("stream"),
    status: el("status-badge"),
    rec: el("rec-badge"),
    clock: el("clock"),
    sourceType: el("source-type"),
    sourcePick: el("source-pick"),
    btnStart: el("btn-start"),
    btnStop: el("btn-stop"),
    btnRecord: el("btn-record"),
    btnShot: el("btn-shot"),
    fps: el("stat-fps"),
    infer: el("stat-infer"),
    active: el("stat-active"),
    unique: el("stat-unique"),
    persons: el("stat-persons"),
    vehicles: el("stat-vehicles"),
    objects: el("object-list"),
    chart: el("fps-chart"),
    sessDetections: el("sess-detections"),
    sessAvgFps: el("sess-avgfps"),
    sessFrames: el("sess-frames"),
    sessUptime: el("sess-uptime"),
    sessSource: el("sess-source"),
    sessModel: el("sess-model"),
    streamSource: el("stream-source"),
    streamRes: el("stream-res"),
    toast: el("toast"),
};

const API = {
    sources: "/api/sources",
    stats: "/api/stats",
    start: "/api/start",
    stop: "/api/stop",
    record: "/api/record",
    screenshot: "/api/screenshot",
};

let sourcesCache = { camera: [], video: [], image: [] };
let running = false;
let recording = false;
let toastTimer = null;

/* ---------------- Clock ---------------- */

function tickClock() {
    const now = new Date();
    $.clock.textContent = now.toLocaleTimeString("en-GB");
}
setInterval(tickClock, 1000);
tickClock();

/* ---------------- Toast ---------------- */

function toast(message, isError = false) {
    $.toast.textContent = message;
    $.toast.classList.remove("hidden");
    $.toast.classList.toggle("error", isError);
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => $.toast.classList.add("hidden"), 2800);
}

/* ---------------- Source loading ---------------- */

async function loadSources() {
    try {
        const res = await fetch(API.sources);
        sourcesCache = await res.json();
        renderSourcePick();
    } catch {
        toast("Failed to load sources", true);
    }
}

function renderSourcePick() {
    const type = $.sourceType.value;
    const options = sourcesCache[type] || [];
    $.sourcePick.innerHTML = "";
    if (!options.length) {
        const opt = document.createElement("option");
        opt.value = "";
        opt.textContent = "No sources found";
        opt.disabled = true;
        $.sourcePick.appendChild(opt);
        return;
    }
    options.forEach((src) => {
        const opt = document.createElement("option");
        opt.value = src;
        opt.textContent = formatSource(src);
        $.sourcePick.appendChild(opt);
    });
}

function formatSource(src) {
    if (typeof src === "number") return `Webcam ${src}`;
    const parts = src.replace(/\\/g, "/").split("/");
    return parts[parts.length - 1];
}

function resolveSourceValue() {
    const type = $.sourceType.value;
    const raw = $.sourcePick.value;
    if (!raw) return null;
    if (type === "camera") return Number(raw);
    return raw;
}

$.sourceType.addEventListener("change", renderSourcePick);

/* ---------------- Controls ---------------- */

async function apiPost(url, body = {}) {
    const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });
    return res.json();
}

async function startPipeline() {
    const source = resolveSourceValue();
    if (source === null) {
        toast("Pick a source first", true);
        return;
    }
    if (running) {
        await apiPost(API.stop);
        running = false;
        recording = false;
        $.btnRecord.classList.remove("recording");
        $.btnRecord.textContent = "Record";
        $.rec.classList.add("hidden");
    }
    $.btnStart.disabled = true;
    const data = await apiPost(API.start, { source, tracking: true });
    $.btnStart.disabled = false;
    if (data.success) {
        running = true;
        $.stream.src = "/video";
        setStatus("live");
        toast("Detection started");
    } else {
        toast("Start failed: " + data.message, true);
    }
}async function stopPipeline() {
    await apiPost(API.stop);
    running = false;
    recording = false;
    $.stream.removeAttribute("src");
    setStatus("idle");
    $.btnRecord.classList.remove("recording");
    $.btnRecord.textContent = "Record";
    $.rec.classList.add("hidden");
    toast("Detection stopped");
}

async function toggleRecord() {
    if (!running) {
        toast("Start detection first", true);
        return;
    }
    const data = await apiPost(API.record);
    recording = data.message === "recording";
    $.btnRecord.classList.toggle("recording", recording);
    $.btnRecord.textContent = recording ? "Stop Rec" : "Record";
    $.rec.classList.toggle("hidden", !recording);
    toast(recording ? "Recording started" : "Recording saved");
}

async function takeScreenshot() {
    if (!running) {
        toast("Start detection first", true);
        return;
    }
    const data = await apiPost(API.screenshot);
    if (data.success) toast("Screenshot saved: " + formatSource(data.path));
    else toast("Screenshot failed", true);
}

$.btnStart.addEventListener("click", startPipeline);
$.btnStop.addEventListener("click", stopPipeline);
$.btnRecord.addEventListener("click", toggleRecord);
$.btnShot.addEventListener("click", takeScreenshot);

/* ---------------- Status ---------------- */

function setStatus(state) {
    $.status.textContent = state === "live" ? "LIVE" : "STOPPED";
    $.status.classList.toggle("badge-live", state === "live");
    $.status.classList.toggle("badge-idle", state !== "live");
}

/* ---------------- Stats polling ---------------- */

const fpsHistory = [];
const MAX_POINTS = 48;

async function pollStats() {
    try {
        const res = await fetch(API.stats);
        const stats = await res.json();
        renderStats(stats);
    } catch {
        /* server briefly unavailable */
    }
}

function renderStats(s) {
    $.fps.textContent = s.fps != null ? s.fps.toFixed(1) : "0";
    $.infer.innerHTML = (s.inference_ms != null ? s.inference_ms.toFixed(1) : "0") + '<span class="unit">ms</span>';
    $.active.textContent = s.active_tracks ?? 0;
    $.unique.textContent = s.unique_ids ?? 0;
    $.persons.textContent = s.persons ?? 0;
    $.vehicles.textContent = s.vehicles ?? 0;

    $.sessDetections.textContent = s.total_detections ?? 0;
    $.sessAvgFps.textContent = s.avg_fps ?? 0;
    $.sessFrames.textContent = s.frames ?? 0;
    $.sessUptime.textContent = s.session ?? "00:00:00";
    $.sessSource.textContent = s.source_type ?? "-";
    $.sessModel.textContent = s.model ? formatSource(s.model) : "-";

    if (s.source) $.streamSource.textContent = formatSource(s.source);

    if (s.fps != null) {
        fpsHistory.push(s.fps);
        if (fpsHistory.length > MAX_POINTS) fpsHistory.shift();
        drawChart();
    }

    renderObjects(s.objects, s.class_colors);

    if (s.status === "running" || s.status === "finished") {
        if (!$.stream.src) $.stream.src = "/video";
        setStatus(s.status === "running" ? "live" : "idle");
        running = s.status === "running";
    } else if (s.running && !running) {
        running = true;
        $.stream.src = "/video";
        setStatus("live");
    } else if (!s.running && running && s.status === "finished") {
        running = false;
        setStatus("idle");
        toast("Source finished");
    }

    if (s.recording !== recording) {
        recording = s.recording;
        $.btnRecord.classList.toggle("recording", recording);
        $.btnRecord.textContent = recording ? "Stop Rec" : "Record";
        $.rec.classList.toggle("hidden", !recording);
    }

    if (s.error) toast("Error: " + s.error, true);
}

/* ---------------- Object list ---------------- */

function renderObjects(objects, colorMap) {
    $.objects.innerHTML = "";
    const entries = Object.entries(objects || {}).sort((a, b) => b[1] - a[1]);
    if (!entries.length) {
        $.objects.innerHTML = '<p class="muted">No detections yet</p>';
        return;
    }
    entries.forEach(([name, count]) => {
        const row = document.createElement("div");
        row.className = "object-row";
        const chip = document.createElement("span");
        chip.className = "object-chip";
        const rgb = colorMap && colorMap[name];
        chip.style.background = rgb ? `rgb(${rgb.join(",")})` : "#888";
        const label = document.createElement("span");
        label.className = "object-name";
        label.textContent = name;
        const badge = document.createElement("span");
        badge.className = "object-badge";
        badge.textContent = count;
        row.appendChild(chip);
        row.appendChild(label);
        row.appendChild(badge);
        $.objects.appendChild(row);
    });
}

/* ---------------- FPS chart ---------------- */

function drawChart() {
    const canvas = $.chart;
    const ctx = canvas.getContext("2d");
    const dpr = window.devicePixelRatio || 1;
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    if (width === 0 || height === 0) return;

    canvas.width = width * dpr;
    canvas.height = height * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    ctx.clearRect(0, 0, width, height);

    const pad = 4;
    const max = Math.max(30, ...fpsHistory) * 1.1;

    // grid lines
    ctx.strokeStyle = "#262b33";
    ctx.lineWidth = 1;
    for (let i = 1; i <= 4; i++) {
        const y = pad + (height - pad * 2) * (i / 4);
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
    }

    if (fpsHistory.length < 2) return;

    const stepX = width / (MAX_POINTS - 1);
    const plot = (i) => {
        const x = i * stepX;
        const y = height - pad - (fpsHistory[i] / max) * (height - pad * 2);
        return [x, y];
    };

    // fill
    ctx.beginPath();
    fpsHistory.forEach((_, i) => {
        const [x, y] = plot(i);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });
    ctx.lineTo(width, height - pad);
    ctx.lineTo(0, height - pad);
    ctx.closePath();
    ctx.fillStyle = "rgba(0,229,255,0.12)";
    ctx.fill();

    // line
    ctx.beginPath();
    fpsHistory.forEach((_, i) => {
        const [x, y] = plot(i);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });
    ctx.strokeStyle = "#00e5ff";
    ctx.lineWidth = 2;
    ctx.lineJoin = "round";
    ctx.stroke();
}

window.addEventListener("resize", drawChart);

/* ---------------- Boot ---------------- */

loadSources();
setInterval(pollStats, 500);
pollStats();
