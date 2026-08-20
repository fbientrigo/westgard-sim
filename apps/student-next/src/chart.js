// src/chart.js
// Pure renderer of a Levey-Jennings chart. No Westgard rule logic: this
// module never compares a z-value against +-2/+-3 SD. Every point already
// carries a categorical `zone` ("within_2sd" | "beyond_2sd" | "beyond_3sd")
// computed at build time by the exporter from the canonical rule functions;
// this module only maps that zone to a marker shape.

const ZONE_SHAPE = {
  within_2sd: "circle",
  beyond_2sd: "triangle",
  beyond_3sd: "square",
};

const ZONE_LABEL_ES = {
  within_2sd: "dentro de 2 DE",
  beyond_2sd: "más allá de 2 DE",
  beyond_3sd: "más allá de 3 DE",
};

function viewBoxForWidth(widthPx) {
  if (widthPx <= 480) return { w: 320, h: 200 };
  if (widthPx <= 860) return { w: 480, h: 260 };
  return { w: 720, h: 340 };
}

function formatDe(z) {
  const sign = z >= 0 ? "+" : "";
  return `${sign}${z.toFixed(1)} DE`;
}

function formatDeComma(z) {
  const sign = z >= 0 ? "+" : "\u2212";
  return `${sign}${Math.abs(z).toFixed(1)}`.replace(".", ",");
}

function shapeMarkup(shape, cx, cy, size, fill, stroke) {
  if (shape === "circle") {
    return `<circle cx="${cx}" cy="${cy}" r="${size}" fill="${fill}" stroke="${stroke}" stroke-width="2" />`;
  }
  if (shape === "triangle") {
    const h = size * 1.7;
    const p1 = `${cx},${cy - h * 0.62}`;
    const p2 = `${cx - h * 0.58},${cy + h * 0.5}`;
    const p3 = `${cx + h * 0.58},${cy + h * 0.5}`;
    return `<polygon points="${p1} ${p2} ${p3}" fill="${fill}" stroke="${stroke}" stroke-width="2" />`;
  }
  // square
  const s = size * 1.5;
  return `<rect x="${cx - s / 2}" y="${cy - s / 2}" width="${s}" height="${s}" fill="${fill}" stroke="${stroke}" stroke-width="2" />`;
}

/**
 * Render the SVG + accessible table + status text for a scenario.
 *
 * @param {object} scenario - a scenario record from practice.json (has .points, .mean, .sd)
 * @param {object} [highlight] - { evidenceRuns: number[], selectedRuns: number[], bracket: boolean }
 * @param {number} [widthPx] - viewport width used to pick the viewBox breakpoint
 * @returns {{ svg: string, table: string, status: string }}
 */
export function renderChart(scenario, highlight = {}, widthPx = 900) {
  const points = scenario.points;
  const evidenceRuns = new Set(highlight.evidenceRuns || []);
  const selectedRuns = new Set(highlight.selectedRuns || []);
  const bracket = highlight.bracket || null; // { runs: [a,b], label } or null

  const { w, h } = viewBoxForWidth(widthPx);
  const margin = { top: 18, right: 14, bottom: 30, left: widthPx <= 480 ? 30 : 40 };
  const plotW = w - margin.left - margin.right;
  const plotH = h - margin.top - margin.bottom;

  const n = points.length;
  const x = (i) => margin.left + (i / (n - 1)) * plotW;
  // Fixed axis: -4 .. +4 SD
  const y = (z) => margin.top + ((4 - z) / 8) * plotH;

  const fontSize = widthPx <= 480 ? 11 : 12;
  const showOneSdLabels = widthPx > 480;

  const gridZs = [-3, -2, -1, 0, 1, 2, 3];
  const gridLines = gridZs
    .map((z) => {
      const isMean = z === 0;
      const is2 = Math.abs(z) === 2;
      const is3 = Math.abs(z) === 3;
      if (Math.abs(z) === 1 && !showOneSdLabels) {
        return `<line x1="${margin.left}" y1="${y(z)}" x2="${w - margin.right}" y2="${y(z)}" stroke="#dce2eb" stroke-width="1" />`;
      }
      const dash = is2 ? 'stroke-dasharray="5 5"' : is3 ? 'stroke-dasharray="2 5"' : "";
      const stroke = isMean ? "#77839a" : "#dce2eb";
      const strokeWidth = isMean ? 1.6 : 1;
      const label = isMean ? "Media" : `${z > 0 ? "+" : "\u2212"}${Math.abs(z)} DE`;
      const showLabel = isMean || is2 || is3;
      const labelMarkup = showLabel
        ? `<text x="${margin.left - 6}" y="${y(z) + 4}" text-anchor="end" fill="#657086" font-size="${fontSize}">${label}</text>`
        : "";
      return `<line x1="${margin.left}" y1="${y(z)}" x2="${w - margin.right}" y2="${y(z)}" stroke="${stroke}" stroke-width="${strokeWidth}" ${dash} />${labelMarkup}`;
    })
    .join("");

  // Emphasised solid threshold line(s) after reveal (evidence runs' governing threshold)
  let emphasisLines = "";
  if (evidenceRuns.size) {
    const sides = new Set();
    for (const run of evidenceRuns) {
      const p = points.find((pt) => pt.run === run);
      if (!p) continue;
      sides.add(p.z >= 0 ? "positive" : "negative");
    }
    for (const side of sides) {
      const thresholdZ = side === "positive" ? 2 : -2;
      // If any evidence point is beyond 3 SD, emphasise the 3 SD line instead for that side.
      const beyond3 = [...evidenceRuns].some((run) => {
        const p = points.find((pt) => pt.run === run);
        return p && p.zone === "beyond_3sd" && (p.z >= 0 ? "positive" : "negative") === side;
      });
      const z = beyond3 ? (side === "positive" ? 3 : -3) : thresholdZ;
      const label = `${z > 0 ? "+" : "\u2212"}${Math.abs(z)} DE`;
      emphasisLines += `<line x1="${margin.left}" y1="${y(z)}" x2="${w - margin.right}" y2="${y(z)}" stroke="#172033" stroke-width="2.2" />`;
      emphasisLines += `<text x="${w - margin.right}" y="${y(z) - 6}" text-anchor="end" fill="#172033" font-size="${fontSize}" font-weight="700">${label}</text>`;
    }
  }

  const path = points
    .map((p, i) => `${i === 0 ? "M" : "L"} ${x(i)} ${y(p.z)}`)
    .join(" ");

  let connectors = "";
  let bracketMarkup = "";
  if (bracket && bracket.runs && bracket.runs.length === 2) {
    const [a, b] = bracket.runs;
    const pa = points.find((pt) => pt.run === a);
    const pb = points.find((pt) => pt.run === b);
    if (pa && pb) {
      const xa = x(pa.run - 1);
      const xb = x(pb.run - 1);
      const yTop = Math.min(y(pa.z), y(pb.z)) - 16;
      bracketMarkup = `
        <path d="M ${xa} ${yTop + 6} L ${xa} ${yTop} L ${xb} ${yTop} L ${xb} ${yTop + 6}" fill="none" stroke="#172033" stroke-width="1.6" />
        <text x="${(xa + xb) / 2}" y="${yTop - 6}" text-anchor="middle" fill="#172033" font-size="${fontSize}" font-weight="700">${bracket.label}</text>
      `;
    }
  }

  const pointsMarkup = points
    .map((p) => {
      const i = p.run - 1;
      const isEvidence = evidenceRuns.has(p.run);
      const isSelected = selectedRuns.has(p.run);
      const shape = ZONE_SHAPE[p.zone] || "circle";
      const baseSize = widthPx <= 480 ? 5 : 6;
      const fill = isEvidence ? "#3157d5" : "#ffffff";
      const stroke = isEvidence ? "#172033" : "#3157d5";

      let ring = "";
      if (isEvidence) {
        const ringSize = baseSize + 5;
        ring =
          shape === "circle"
            ? `<circle cx="${x(i)}" cy="${y(p.z)}" r="${ringSize}" fill="none" stroke="#172033" stroke-width="3" />`
            : shapeMarkup(shape, x(i), y(p.z), ringSize, "none", "#172033").replace(
                'stroke-width="2"',
                'stroke-width="3"'
              );
      }

      if (isEvidence && connectors !== null) {
        const thresholdZ = p.zone === "beyond_3sd" ? (p.z >= 0 ? 3 : -3) : p.z >= 0 ? 2 : -2;
        connectors += `<line x1="${x(i)}" y1="${y(p.z)}" x2="${x(i)}" y2="${y(thresholdZ)}" stroke="#172033" stroke-width="1.2" stroke-dasharray="2 3" />`;
      }

      const marker = shapeMarkup(shape, x(i), y(p.z), baseSize, fill, stroke);
      const runLabelWeight = isEvidence ? "700" : "400";
      const runLabel = `<text x="${x(i)}" y="${h - margin.bottom + 16}" text-anchor="middle" fill="#657086" font-size="${fontSize}" font-weight="${runLabelWeight}">${p.run}</text>`;
      const caret = isSelected
        ? `<text x="${x(i)}" y="${h - margin.bottom + 28}" text-anchor="middle" fill="#3157d5" font-size="${fontSize}">^</text>`
        : "";

      return `${ring}${marker}${runLabel}${caret}`;
    })
    .join("");

  const svg = `
    <svg viewBox="0 0 ${w} ${h}" aria-hidden="true" focusable="false">
      ${gridLines}
      ${emphasisLines}
      <path d="${path}" fill="none" stroke="#3157d5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" opacity="0.55" />
      ${connectors}
      ${bracketMarkup}
      ${pointsMarkup}
    </svg>
  `;

  const tableRows = points
    .map(
      (p) =>
        `<tr><td>${p.run}</td><td>${formatDe(p.z)}</td><td>${ZONE_LABEL_ES[p.zone]}</td></tr>`
    )
    .join("");
  const table = `
    <table class="visually-hidden">
      <caption>Serie de control, valores en desviaciones estándar</caption>
      <thead><tr><th>Control</th><th>Desviación en DE</th><th>Zona</th></tr></thead>
      <tbody>${tableRows}</tbody>
    </table>
  `;

  const deList = points.map((p) => formatDeComma(p.z)).join("; ");
  let status = `Serie de ${n} controles. Desviaciones en DE: ${deList}.`;
  const triggeredRules = highlight.triggeredRules || [];
  if (triggeredRules.length) {
    const summaries = triggeredRules.map((rule) => {
      const runs = rule.evidenceRuns.join(" y ");
      return `${rule.display} en los controles ${runs}`;
    });
    status += ` Reglas que se cumplen: ${summaries.join("; ")}.`;
  } else if (highlight.locked) {
    status += " No se cumple ninguna de las reglas evaluadas.";
  }

  return { svg, table, status };
}

/**
 * Render a small 96x48 mini-pattern SVG for the Learn view, from authored
 * mini_pattern data (already z-values, no rule evaluation happens here).
 */
export function renderMiniPattern(miniPattern) {
  const w = 96;
  const h = 48;
  const seriesList = miniPattern.series;
  const highlightList = miniPattern.highlight || [];
  const margin = { top: 6, right: 6, bottom: 6, left: 6 };
  const plotW = w - margin.left - margin.right;
  const plotH = h - margin.top - margin.bottom;

  const allValues = seriesList.flat();
  const maxAbs = Math.max(3.5, ...allValues.map((v) => Math.abs(v)));
  const y = (z) => margin.top + ((maxAbs - z) / (2 * maxAbs)) * plotH;

  const twoSdLines = [2, -2]
    .map(
      (z) =>
        `<line x1="${margin.left}" y1="${y(z)}" x2="${w - margin.right}" y2="${y(z)}" stroke="#dce2eb" stroke-width="1" stroke-dasharray="3 3" />`
    )
    .join("");
  const meanLine = `<line x1="${margin.left}" y1="${y(0)}" x2="${w - margin.right}" y2="${y(0)}" stroke="#a8b2c4" stroke-width="1" />`;

  let seriesMarkup = "";
  seriesList.forEach((series, seriesIndex) => {
    const n = series.length;
    const x = (i) => margin.left + (n === 1 ? plotW / 2 : (i / (n - 1)) * plotW);
    const hollow = seriesIndex === 1; // R_4s second level renders hollow
    const highlighted = new Set(highlightList[seriesIndex] || []);
    const path = series.map((v, i) => `${i === 0 ? "M" : "L"} ${x(i)} ${y(v)}`).join(" ");
    const pts = series
      .map((v, i) => {
        const isHi = highlighted.has(i + 1);
        const r = isHi ? 3.6 : 2.6;
        const fill = hollow ? "#ffffff" : isHi ? "#3157d5" : "#ffffff";
        const stroke = "#3157d5";
        const ring = isHi
          ? `<circle cx="${x(i)}" cy="${y(v)}" r="${r + 2}" fill="none" stroke="#172033" stroke-width="1.6" />`
          : "";
        return `${ring}<circle cx="${x(i)}" cy="${y(v)}" r="${r}" fill="${fill}" stroke="${stroke}" stroke-width="1.4" />`;
      })
      .join("");
    seriesMarkup += `<path d="${path}" fill="none" stroke="#3157d5" stroke-width="1.3" opacity="0.6" />${pts}`;
  });

  // Vertical connector between run-1 points for two-series mini patterns (R_4s)
  let connector = "";
  if (seriesList.length === 2) {
    const n0 = seriesList[0].length;
    const x0 = margin.left + (n0 === 1 ? plotW / 2 : 0);
    connector = `<line x1="${x0}" y1="${y(seriesList[0][0])}" x2="${x0}" y2="${y(seriesList[1][0])}" stroke="#172033" stroke-width="1.4" stroke-dasharray="2 2" />`;
  }

  return `<svg viewBox="0 0 ${w} ${h}" aria-hidden="true" focusable="false" width="96" height="48">${twoSdLines}${meanLine}${seriesMarkup}${connector}</svg>`;
}

export { ZONE_SHAPE, viewBoxForWidth };
