import csv
import os
import json
from datetime import datetime

def generate_dashboard(csv_path=None, output_path=None):
    # Determine base directory (project root)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    if csv_path is None:
        csv_path = os.path.join(base_dir, "logs/results.csv")
    if output_path is None:
        output_path = os.path.join(base_dir, "index.html")
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    results = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                row['Latency(s)'] = float(row['Latency(s)'])
                row['EfficiencyScore'] = float(row['EfficiencyScore'])
                row['Tokens/sec'] = float(row['Tokens/sec'])
                row['CPU(%)'] = float(row['CPU(%)'])
                row['RAM(%)'] = float(row['RAM(%)'])
                results.append(row)
            except (ValueError, KeyError):
                continue

    if not results:
        print("Error: No data in results.csv")
        return

    # Filter for the latest session (last 12 runs if user runs 6+6)
    # Alternatively, just use all for averages but show latest accurately
    latest_unopt = [r for r in results if r['Mode'] == 'Unoptimized']
    latest_opt = [r for r in results if r['Mode'] == 'Optimized']
    
    def get_avg(data_list):
        if not data_list: return None
        # Use last 6 for average if possible to represent a "session"
        session_data = data_list[-6:]
        count = len(session_data)
        return {
            'Latency(s)': round(sum(r['Latency(s)'] for r in session_data) / count, 2),
            'EfficiencyScore': round(sum(r['EfficiencyScore'] for r in session_data) / count, 2),
            'Tokens/sec': round(sum(r['Tokens/sec'] for r in session_data) / count, 2),
            'CPU(%)': round(sum(r['CPU(%)'] for r in session_data) / count, 1),
            'RAM(%)': round(sum(r['RAM(%)'] for r in session_data) / count, 1),
            'Model': session_data[-1]['Model'] # Show the switched model
        }

    avg_unopt = get_avg(latest_unopt)
    avg_opt = get_avg(latest_opt)

    # Trend data (Last 24 to accommodate 6+6 safely with history)
    trend_results = results[-24:]
    labels = [f"#{len(results)-len(trend_results)+i+1}" for i in range(len(trend_results))]
    latency_data = [r['Latency(s)'] for r in trend_results]
    efficiency_data = [r['EfficiencyScore'] for r in trend_results]
    tokens_data = [r['Tokens/sec'] for r in trend_results]
    modes = [r['Mode'] for r in trend_results]

    total_runs = len(results)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inference Insights Pro | Performance Audit</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg: #08090d;
            --card: #11141b;
            --border: rgba(255, 255, 255, 0.05);
            --accent: #00e5ff;
            --baseline: #ff4d4d;
            --text: #ffffff;
            --text-dim: #8a8f98;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Outfit', sans-serif; }}

        body {{
            background-color: var(--bg);
            color: var(--text);
            padding: 30px;
            display: flex;
            justify-content: center;
            height: 100vh;
        }}

        .layout {{
            width: 100%;
            max-width: 1600px;
            display: grid;
            grid-template-areas: 
                "header header header"
                "avgs chart chart"
                "table table table";
            grid-template-columns: 420px 1fr 1fr;
            grid-template-rows: auto 450px 1fr;
            gap: 25px;
        }}

        header {{
            grid-area: header;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            border-bottom: 2px solid var(--border);
            padding-bottom: 15px;
        }}

        header h1 {{ font-size: 2.2rem; font-weight: 700; color: var(--accent); }}

        .avgs-panel {{
            grid-area: avgs;
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 30px;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}

        .avg-card {{
            padding: 20px;
            border-radius: 18px;
            background: rgba(255,255,255,0.02);
            border: 1px solid var(--border);
            position: relative;
        }}

        .avg-card.opt {{ border-left: 5px solid var(--accent); }}
        .avg-card.base {{ border-left: 5px solid var(--baseline); }}

        .label-row {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 12px;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-dim);
        }}

        .val-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
        }}

        .metric-box span:first-child {{ font-size: 0.75rem; color: var(--text-dim); }}
        .metric-box span:last-child {{ font-size: 1.5rem; font-weight: 700; display: block; }}

        .chart-box {{
            grid-area: chart;
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 30px;
            display: flex;
            flex-direction: column;
        }}

        .table-box {{
            grid-area: table;
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 35px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }}

        .table-container {{
            flex: 1;
            overflow-y: auto;
            margin-top: 20px;
            border-radius: 12px;
            border: 1px solid var(--border);
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        th {{
            position: sticky;
            top: 0;
            background: #1c1f26;
            padding: 18px 24px;
            text-align: left;
            font-weight: 600;
            color: var(--text-dim);
            font-size: 0.9rem;
            border-bottom: 2px solid var(--border);
            z-index: 10;
        }}

        td {{
            padding: 18px 24px;
            border-bottom: 1px solid var(--border);
            font-size: 1rem;
        }}

        tr:hover {{ background: rgba(255,255,255,0.01); }}

        .badge {{
            padding: 6px 14px;
            border-radius: 8px;
            font-size: 0.8rem;
            font-weight: 700;
        }}

        .b-opt {{ background: rgba(0, 229, 255, 0.1); color: var(--accent); }}
        .b-base {{ background: rgba(255, 77, 77, 0.1); color: var(--baseline); }}

        @media (max-width: 1200px) {{
            .layout {{
                grid-template-areas: "header" "avgs" "chart" "table";
                grid-template-columns: 1fr;
                grid-template-rows: auto auto 400px 1fr;
                height: auto;
            }}
            body {{ height: auto; }}
        }}
    </style>
</head>
<body>
    <div class="layout">
        <header>
            <h1>Session Audit Report</h1>
            <div style="color: var(--text-dim); font-size: 0.9rem;">
                Monitoring {total_runs} Inference cycles | System Active
            </div>
        </header>

        <section class="avgs-panel">
            <h3 style="font-size: 1.1rem; color: var(--accent);">Average Session Stats</h3>
            
            <div class="avg-card base">
                <div class="label-row">
                    <span>Baseline (Unoptimized)</span>
                    <span style="color:var(--text);">{avg_unopt['Model'] if avg_unopt else 'N/A'}</span>
                </div>
                {render_val_grid(avg_unopt)}
            </div>

            <div class="avg-card opt">
                <div class="label-row">
                    <span>Elite (Optimized)</span>
                    <span style="color:var(--accent); font-weight:700;">{avg_opt['Model'] if avg_opt else 'N/A'}</span>
                </div>
                {render_val_grid(avg_opt)}
            </div>

            <div style="margin-top: auto; padding: 20px; background: rgba(0,229,255,0.04); border-radius: 15px;">
                <h4 style="font-size: 0.8rem; color: var(--accent); margin-bottom: 10px;">AVERAGE GAIN</h4>
                <div style="font-size: 1.1rem; font-weight: 600;">
                    {calculate_gain(avg_unopt, avg_opt)}
                </div>
            </div>
        </section>

        <section class="chart-box">
            <h3 style="margin-bottom: 20px;">Trend Analysis (Last 24 Runs)</h3>
            <div style="flex: 1; min-height: 0;">
                <canvas id="trendChart"></canvas>
            </div>
        </section>

        <section class="table-box">
            <h3 style="font-size: 1.2rem;">Full Performance Journal</h3>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Sequence</th>
                            <th>Mode</th>
                            <th>Model Used</th>
                            <th>Latency (s)</th>
                            <th>Tokens/sec</th>
                            <th>System Load (C/R)</th>
                            <th>Efficiency</th>
                        </tr>
                    </thead>
                    <tbody>
                        {generate_table_body(results)}
                    </tbody>
                </table>
            </div>
        </section>
    </div>

    <script>
        const ctx = document.getElementById('trendChart').getContext('2d');
        const labels = {json.dumps(labels)};
        
        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: labels,
                datasets: [
                    {{
                        label: 'Throughput',
                        data: {json.dumps(tokens_data)},
                        backgroundColor: {json.dumps(['rgba(255, 77, 77, 0.6)' if m == 'Unoptimized' else 'rgba(0, 229, 255, 0.6)' for m in modes])},
                        borderRadius: 6
                    }},
                    {{
                        label: 'Efficiency Index',
                        data: {json.dumps(efficiency_data)},
                        type: 'line',
                        borderColor: '#ffffff',
                        borderWidth: 2,
                        fill: false,
                        pointRadius: 4,
                        yAxisID: 'y1'
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }}, ticks: {{ color: '#8a8f98' }} }},
                    y1: {{ position: 'right', grid: {{ display: false }}, ticks: {{ color: '#00e5ff' }} }},
                    x: {{ grid: {{ display: false }}, ticks: {{ color: '#8a8f98' }} }}
                }},
                plugins: {{
                    legend: {{ position: 'bottom', labels: {{ color: '#8a8f98', boxWidth: 15 }} }}
                }}
            }}
        }});
    </script>
</body>
</html>"""
    
    with open(output_path, "w", encoding='utf-8') as f:
        f.write(html)
    print(f"Professional Dashboard generated at {os.path.abspath(output_path)}")

def render_val_grid(avg):
    if not avg:
        return "<div class='val-grid'><div class='metric-box'><span>Latency</span><span>No Data</span></div></div>"
    return f"""
    <div class="val-grid">
        <div class="metric-box"><span>LATENCY</span><span>{avg['Latency(s)']}s</span></div>
        <div class="metric-box"><span>SPEED</span><span>{avg['Tokens/sec']}</span></div>
        <div class="metric-box"><span>SCORE</span><span>{avg['EfficiencyScore']}</span></div>
    </div>
    """

def calculate_gain(unopt, opt):
    if not unopt or not opt: return "Collecting data..."
    improvement = round((opt['Tokens/sec'] / unopt['Tokens/sec'] - 1) * 100, 1) if unopt['Tokens/sec'] > 0 else 0
    return f"🚀 {improvement}% faster through dynamic scaling."

def generate_table_body(results):
    rows = ""
    for i, r in enumerate(reversed(results)):
        badge = "b-opt" if r['Mode'] == 'Optimized' else "b-base"
        rows += f"""
        <tr>
            <td style="color:var(--text-dim);">#{len(results)-i}</td>
            <td><span class="badge {badge}">{r['Mode']}</span></td>
            <td style="font-weight:600;">{r['Model']}</td>
            <td>{r['Latency(s)']}s</td>
            <td><strong>{r['Tokens/sec']}</strong></td>
            <td style="color:var(--text-dim);">{r['CPU(%)']}% / {r['RAM(%)']}%</td>
            <td style="color:var(--accent); font-weight:bold;">{r['EfficiencyScore']}</td>
        </tr>
        """
    return rows

if __name__ == "__main__":
    generate_dashboard()
