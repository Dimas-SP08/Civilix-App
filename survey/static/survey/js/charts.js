// --- charts.js ---

async function initChart() {
    const loadingIndicator = document.getElementById('chartLoading');
    const url = PROJECT_CONFIG.urls.chartData;

    // Default Data Placeholder
    let chartData = {
        x: [0, 50, 100, 150],
        yGround: [100, 102, 98, 101],
        yDesign: [100, 100, 100, 100],
        labels: ['0+000', '0+050', '0+100', '0+150']
    };

    try {
        const response = await fetch(url);
        const resJson = await response.json();

        if (resJson.status === 'success' && resJson.data.distances.length > 0) {
            const d = resJson.data;
            chartData.x = d.distances;
            chartData.yGround = d.elevations;
            chartData.yDesign = d.design_elevations.map((val, i) => val !== null ? val : d.elevations[i]);
            chartData.labels = d.stations;
        }
    } catch (error) {
        console.error("Chart Data Error:", error);
    }

    // Fungsi Bantu Titik Potong
    function findIntersection(x1, y1_g, y1_d, x2, y2_g, y2_d) {
        const m_g = (y2_g - y1_g) / (x2 - x1);
        const m_d = (y2_d - y1_d) / (x2 - x1);
        if (m_g === m_d) return null;

        const x_intersect = x1 + (y1_g - y1_d) / (m_d - m_g);
        const epsilon = 1e-5;
        if (x_intersect > x1 + epsilon && x_intersect < x2 - epsilon) {
            const y_intersect = y1_g + m_g * (x_intersect - x1);
            return { x: x_intersect, y: y_intersect };
        }
        return null;
    }

    // Proses Data: Sisipkan Titik Potong
    let finalX = [], finalYGround = [], finalYDesign = [], finalLabels = [];

    if (chartData.x.length > 0) {
        for (let i = 0; i < chartData.x.length - 1; i++) {
            finalX.push(chartData.x[i]);
            finalYGround.push(chartData.yGround[i]);
            finalYDesign.push(chartData.yDesign[i]);
            finalLabels.push(chartData.labels[i]);

            const isGroundAbove1 = chartData.yGround[i] > chartData.yDesign[i];
            const isGroundAbove2 = chartData.yGround[i+1] > chartData.yDesign[i+1];

            if (isGroundAbove1 !== isGroundAbove2) {
                const intersection = findIntersection(
                    chartData.x[i], chartData.yGround[i], chartData.yDesign[i],
                    chartData.x[i+1], chartData.yGround[i+1], chartData.yDesign[i+1]
                );
                if (intersection) {
                    finalX.push(intersection.x);
                    finalYGround.push(intersection.y);
                    finalYDesign.push(intersection.y); 
                    finalLabels.push(""); 
                }
            }
        }
        finalX.push(chartData.x[chartData.x.length - 1]);
        finalYGround.push(chartData.yGround[chartData.yGround.length - 1]);
        finalYDesign.push(chartData.yDesign[chartData.yDesign.length - 1]);
        finalLabels.push(chartData.labels[chartData.labels.length - 1]);
    }

    const plotX = finalX;
    const plotYGround = finalYGround;
    const plotYDesign = finalYDesign;
    const plotLabels = finalLabels;
    const yMax = plotYGround.map((g, i) => Math.max(g, plotYDesign[i]));

    // Theme Configuration
    const CHART_THEME = {
        colors: {
            design: '#F43F5E',
            cut: 'rgba(244, 63, 94, 0.35)',
            ground: '#6366F1',
            fill: 'rgba(16, 185, 129, 0.35)',
            grid: '#F1F5F9',
            text: '#64748B',
            bg: 'rgba(0,0,0,0)'
        },
        font: { family: "'Inter', sans-serif", size: 11 }
    };

    const traces = [
        {
            x: plotX, y: plotYDesign, mode: 'lines', name: 'Design Plan',
            line: { color: CHART_THEME.colors.design, width: 2.5, dash: 'dash' }, hoverinfo: 'y+name'
        },
        {
            x: plotX, y: yMax, mode: 'lines', name: 'Cut Volume',
            line: { width: 0 }, fill: 'tonexty', fillcolor: CHART_THEME.colors.cut, hoverinfo: 'skip', showlegend: true
        },
        {
            x: plotX, y: plotYGround, mode: 'lines', name: 'Existing Ground',
            line: { color: CHART_THEME.colors.ground, width: 2.5 }, hoverinfo: 'y+name'
        },
        {
            x: plotX, y: yMax, mode: 'lines', name: 'Fill Volume',
            line: { width: 0 }, fill: 'tonexty', fillcolor: CHART_THEME.colors.fill, hoverinfo: 'skip', showlegend: true
        }
    ];

    const layout = {
        autosize: true,
        margin: { t: 30, r: 20, l: 60, b: 80 }, 
        font: { family: CHART_THEME.font.family, color: CHART_THEME.colors.text, size: CHART_THEME.font.size },
        paper_bgcolor: CHART_THEME.colors.bg,
        plot_bgcolor: CHART_THEME.colors.bg,
        legend: { orientation: 'h', yanchor: 'bottom', y: 1.02, xanchor: 'left', x: 0 },
        xaxis: {
            title: { text: 'Station (STA)', font: { weight: '600' } },
            gridcolor: CHART_THEME.colors.grid,
            linecolor: '#CBD5E1',
            showline: true,
            tickvals: plotX,
            ticktext: plotLabels,
            tickangle: -45,
        },
        yaxis: {
            title: 'Elevation (m)',
            gridcolor: CHART_THEME.colors.grid,
            zeroline: false,
            autorange: true
        },
        hovermode: 'x unified',
        hoverlabel: { bgcolor: "#FFFFFF", bordercolor: "#E2E8F0", font: { family: CHART_THEME.font.family, size: 13, color: "#0F172A" } }
    };

    const config = {
        displayModeBar: true, displaylogo: false, responsive: true,
        modeBarButtonsToRemove: ['lasso2d', 'select2d', 'autoScale2d', 'toggleSpikelines', 'hoverClosestCartesian', 'hoverCompareCartesian']
    };

    if (loadingIndicator) loadingIndicator.style.display = 'none';
    Plotly.purge('elevationChart');
    Plotly.newPlot('elevationChart', traces, layout, config);
}

document.addEventListener('DOMContentLoaded', function() {
    setTimeout(initChart, 600);
});