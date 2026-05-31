document.addEventListener("DOMContentLoaded", () => {

    // ==========================================
    // 1. SPA Navigation Logic
    // ==========================================
    const navLinks = document.querySelectorAll(".sidebar .nav-link");
    const sections = document.querySelectorAll(".spa-section");

    navLinks.forEach(link => {
        link.addEventListener("click", (e) => {
            e.preventDefault();
            navLinks.forEach(l => l.classList.remove("active"));
            link.classList.add("active");

            const targetId = link.getAttribute("data-target");
            sections.forEach(sec => {
                if (sec.id === targetId) {
                    sec.classList.add("active");
                    // Trigger data load on section active
                    if (targetId === 'dashboard') { loadDashboardData(); }
                    else if (targetId === 'dataImport') { /* 无需自动加载，但可以清空预览区域 */ }
                    else if (targetId === 'clusteringAnalysis') { loadClusteringData(); }
                    else if (targetId === 'dataView') { loadDataView(); }
                    else if (targetId === 'predict') { /* 无需自动加载 */ }
                    else if (targetId === 'associationRules'){ /* 无需自动加载 */ }
                } else {
                    sec.classList.remove("active");
                }
            });
        });
    });

    // ==========================================
    // 2. Global ECharts Instances
    // ==========================================
    let chartAge, chartSex, chartCP, chartFBS, chartCluster;

    function initCharts() {
        if (document.getElementById("chart-age") && !chartAge) {
            chartAge = echarts.init(document.getElementById("chart-age"));
            chartSex = echarts.init(document.getElementById("chart-sex"));
            chartCP = echarts.init(document.getElementById("chart-cp"));
            chartFBS = echarts.init(document.getElementById("chart-fbs"));
        }

        window.addEventListener("resize", () => {
            if (chartAge) chartAge.resize();
            if (chartSex) chartSex.resize();
            if (chartCP) chartCP.resize();
            if (chartFBS) chartFBS.resize();
            if (chartCluster) chartCluster.resize();
        });
    }

    // ==========================================
    // 3. Load Dashboard Data (AJAX)
    // ==========================================
    window.loadDashboardData = function () {
        initCharts();

        fetch('/api/dashboard')
            .then(res => res.json())
            .then(data => {
                // Update KPIs
                document.getElementById('kpi-total').innerText = data.kpis.total;
                document.getElementById('kpi-rate').innerText = data.kpis.heart_disease_rate;
                document.getElementById('kpi-age').innerText = data.kpis.avg_age;

                // Age Distribution Chart (Bar)
                chartAge.setOption({
                    tooltip: { trigger: 'axis' },
                    xAxis: {
                        type: 'category',
                        data: data.charts.age_dist.map(item => item.age_group)
                    },
                    yAxis: { type: 'value' },
                    series: [{
                        data: data.charts.age_dist.map(item => item.count),
                        type: 'bar',
                        itemStyle: { color: '#3498db' }
                    }]
                });

                // Sex Distribution Chart (Pie)
                chartSex.setOption({
                    tooltip: { trigger: 'item' },
                    series: [{
                        type: 'pie',
                        radius: '50%',
                        data: data.charts.sex_dist,
                        emphasis: {
                            itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.5)' }
                        }
                    }]
                });

                // Chest Pain Chart (Bar)
                chartCP.setOption({
                    tooltip: { trigger: 'axis' },
                    xAxis: {
                        type: 'category',
                        data: data.charts.cp_dist.map(item => "类型 " + item.cp_type)
                    },
                    yAxis: { type: 'value' },
                    series: [{
                        data: data.charts.cp_dist.map(item => item.count),
                        type: 'bar',
                        itemStyle: { color: '#e74c3c' }
                    }]
                });

                // Fasting Blood Sugar Chart (Pie)
                chartFBS.setOption({
                    tooltip: { trigger: 'item' },
                    series: [{
                        type: 'pie',
                        radius: ['40%', '70%'],
                        data: data.charts.fbs_dist
                    }]
                });
            })
            .catch(err => console.error("Error loading dashboard data:", err));
    };

    // ==========================================
    // 4. Predict Form Submission Logic
    // ==========================================
    const predictForm = document.getElementById("predict-form");
    if (predictForm) {
        predictForm.addEventListener("submit", (e) => {
            e.preventDefault();
            const formData = new FormData(predictForm);
            const data = Object.fromEntries(formData.entries());

            fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
                .then(res => res.json())
                .then(resData => {
                    const resDiv = document.getElementById('result-container');
                    if (resData.prediction === 1) {
                        resDiv.innerHTML = `<div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle fa-3x mb-3"></i><br>
                        <h4>高风险</h4>
                        <p>模型预测此患者存在心脏病风险，请尽快安排详细诊断。</p>
                        </div>`;
                    } else {
                        resDiv.innerHTML = `<div class="alert alert-success">
                        <i class="fas fa-check-circle fa-3x mb-3"></i><br>
                        <h4>低风险</h4>
                        <p>模型预测此患者目前风险较低。</p>
                        </div>`;
                    }
                })
                .catch(err => console.error("Error in prediction:", err));
        });
    }

    // ==========================================
    // 5. 数据导入预览 + 确认/撤销
    // ==========================================
    const uploadForm = document.getElementById("upload-form");
    const previewArea = document.getElementById("preview-area");
    const previewStatsDiv = document.getElementById("preview-stats");
    const previewTableBody = document.querySelector("#preview-table tbody");

    if (uploadForm) {
        uploadForm.addEventListener("submit", (e) => {
            e.preventDefault();
            const formData = new FormData(uploadForm);
            const btn = document.getElementById("upload-btn");
            const originalHtml = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 处理中...';
            btn.disabled = true;

            fetch('/api/upload/preview', {
                method: 'POST',
                body: formData
            })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        previewArea.style.display = 'block';
                        const p = data.preview;
                        previewStatsDiv.innerHTML = `
                    <div class="col-md-2"><div class="card p-2"><h6>总记录数</h6><h4>${p.total}</h4></div></div>
                    <div class="col-md-2"><div class="card p-2"><h6>患病率</h6><h4>${(p.disease_rate * 100).toFixed(1)}%</h4></div></div>
                    <div class="col-md-2"><div class="card p-2"><h6>男性比例</h6><h4>${(p.male_ratio * 100).toFixed(1)}%</h4></div></div>
                    <div class="col-md-2"><div class="card p-2"><h6>平均年龄</h6><h4>${p.avg_age}</h4></div></div>
                    <div class="col-md-2"><div class="card p-2"><h6>平均血压</h6><h4>${p.avg_trestbps}</h4></div></div>
                    <div class="col-md-2"><div class="card p-2"><h6>平均胆固醇</h6><h4>${p.avg_chol}</h4></div></div>
                `;
                        let rowsHtml = '';
                        p.data_preview.forEach((row, idx) => {
                            rowsHtml += `<td>
                        <td>${idx + 1}</td>
                        <td>${row.age}</td>
                        <td>${row.sex === 1 ? '男' : '女'}</td>
                        <td>${row.trestbps}</td>
                        <td>${row.chol}</td>
                        <td>${row.target === 1 ? '患病' : '健康'}</td>
                    </tr>`;
                        });
                        previewTableBody.innerHTML = rowsHtml;
                        document.getElementById('upload-result').innerHTML = '<div class="alert alert-info">文件已清洗，请确认导入。</div>';
                    } else {
                        document.getElementById('upload-result').innerHTML = `<div class="alert alert-danger">上传失败: ${data.error}</div>`;
                        previewArea.style.display = 'none';
                    }
                })
                .catch(err => {
                    document.getElementById('upload-result').innerHTML = '<div class="alert alert-danger">网络错误</div>';
                    previewArea.style.display = 'none';
                })
                .finally(() => {
                    btn.innerHTML = originalHtml;
                    btn.disabled = false;
                });
        });
    }

    // 确认导入按钮
    document.getElementById("confirm-import")?.addEventListener("click", () => {
        fetch('/api/upload/confirm', { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert("导入成功，数据已更新！");
                    previewArea.style.display = 'none';
                    loadDashboardData();
                    loadDataView();
                    loadClusteringData();
                    document.getElementById('upload-result').innerHTML = '<div class="alert alert-success">导入成功！</div>';
                } else {
                    alert("导入失败: " + data.error);
                }
            });
    });

    // 取消导入按钮
    document.getElementById("cancel-import")?.addEventListener("click", () => {
        fetch('/api/upload/cancel', { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    previewArea.style.display = 'none';
                    document.getElementById('upload-result').innerHTML = '<div class="alert alert-warning">已取消导入。</div>';
                }
            });
    });

    // 撤销上次导入按钮
    document.getElementById("rollback-import")?.addEventListener("click", () => {
        if (confirm("撤销将恢复上一次导入前的所有数据，确定吗？")) {
            fetch('/api/upload/rollback', { method: 'POST' })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        alert("已撤销导入，数据已回滚。");
                        loadDashboardData();
                        loadDataView();
                        loadClusteringData();
                    } else {
                        alert("撤销失败: " + data.error);
                    }
                });
        }
    });

    window.loadClusteringData = function () {
        const clusterContainer = document.getElementById("chart-cluster");
        if (!clusterContainer) return;

        if (!chartCluster) chartCluster = echarts.init(clusterContainer);

        chartCluster.showLoading();
        fetch('/api/clustering')
            .then(res => res.json())
            .then(resData => {
                chartCluster.hideLoading();
                if (!resData.success) {
                    console.error("Clustering error:", resData.error);
                    return;
                }

                const data = resData.data;
                const colors = ['#e74c3c', '#3498db', '#2ecc71', '#f1c40f', '#9b59b6'];

                const seriesData = [];
                for (let i = 0; i < data.cluster_centers.length; i++) {
                    const clusterPoints = data.scatter_data.filter(item => item[2] === i);
                    seriesData.push({
                        name: '人群分类 ' + (i + 1),
                        type: 'scatter',
                        data: clusterPoints,
                        itemStyle: { color: colors[i % colors.length] },
                        symbolSize: 8
                    });
                }

                chartCluster.setOption({
                    title: { text: "患者特征分布 (年龄 vs 胆固醇)", left: 'center', textStyle: { fontSize: 14 } },
                    tooltip: {
                        formatter: function (obj) {
                            return `年龄: ${obj.value[0]}<br>胆固醇: ${obj.value[1]}`;
                        }
                    },
                    legend: { top: 'bottom' },
                    xAxis: { name: '年龄 (Age)', splitLine: { show: false } },
                    yAxis: { name: '胆固醇 (Chol)', splitLine: { show: true } },
                    series: seriesData
                }, true);
            })
            .catch(err => {
                chartCluster.hideLoading();
                console.error(err);
            });
    };

    // Auto-load main dashboard on init
    loadDashboardData();

    // ==== Data View Implementation ====
    function loadDataView() {
        fetch('/api/data')
            .then(res => res.json())
            .then(data => {
                const tbody = document.getElementById('dataTableBody');
                tbody.innerHTML = '';

                if (data.success === true || data.status === 'success') {
                    data.data.forEach(row => {
                        const tr = document.createElement('tr');

                        // Age, Sex (1=Male, 0=Female)
                        const sexName = row.sex === 1 ? '男' : '女';

                        // Target (1=Heart Disease, 0=Normal)
                        const targetBadge = row.target === 1
                            ? '<span class="badge bg-danger">有疾病</span>'
                            : '<span class="badge bg-success">正常</span>';

                        tr.innerHTML = `
                            <td>${row.ID}</td>
                            <td>${row.age}</td>
                            <td>${sexName}</td>
                            <td>${row.cp}</td>
                            <td>${row.trestbps}</td>
                            <td>${row.chol}</td>
                            <td>${row.fbs}</td>
                            <td>${row.restecg}</td>
                            <td>${row.thalach}</td>
                            <td>${row.exang}</td>
                            <td>${row.oldpeak}</td>
                            <td>${row.slope}</td>
                            <td>${row.ca}</td>
                            <td>${row.thal}</td>
                            <td>${targetBadge}</td>
                        `;
                        tbody.appendChild(tr);
                    });
                }
            })
            .catch(err => console.error("Error loading data table:", err));
    }

    // Bind refresh button
    const refreshDataBtn = document.getElementById('refreshDataBtn');
    if (refreshDataBtn) {
        refreshDataBtn.addEventListener('click', loadDataView);
    }

});

// 加载数据概览统计卡片
function loadDataOverview() {
    fetch('/api/data/overview')
        .then(res => res.json())
        .then(stats => {
            document.getElementById('stat-total').innerText = stats.total || 0;
            document.getElementById('stat-disease').innerText = stats.disease_rate ? (stats.disease_rate * 100).toFixed(1) + '%' : '0%';
            document.getElementById('stat-male').innerText = stats.male_ratio ? (stats.male_ratio * 100).toFixed(1) + '%' : '0%';
            document.getElementById('stat-age').innerText = stats.avg_age || '--';
            document.getElementById('stat-bp').innerText = stats.avg_trestbps || '--';
            document.getElementById('stat-chol').innerText = stats.avg_chol || '--';
        })
        .catch(err => console.error("加载概览统计失败:", err));
}

// 修改原有的 loadDataView 函数，使其同时刷新统计卡片和表格
function loadDataView() {
    loadDataOverview();  // 新增
    // 原有表格加载逻辑保持不变
    fetch('/api/data')
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById('dataTableBody');
            tbody.innerHTML = '';
            if (data.success === true || data.status === 'success') {
                data.data.forEach(row => {
                    const tr = document.createElement('tr');
                    const sexName = row.sex === 1 ? '男' : '女';
                    const targetBadge = row.target === 1
                        ? '<span class="badge bg-danger">有疾病</span>'
                        : '<span class="badge bg-success">正常</span>';
                    tr.innerHTML = `
                        <td>${row.ID}</td><td>${row.age}</td><td>${sexName}</td>
                        <td>${row.cp}</td><td>${row.trestbps}</td><td>${row.chol}</td>
                        <td>${row.fbs}</td><td>${row.restecg}</td><td>${row.thalach}</td>
                        <td>${row.exang}</td><td>${row.oldpeak}</td><td>${row.slope}</td>
                        <td>${row.ca}</td><td>${row.thal}</td><td>${targetBadge}</td>
                    `;
                    tbody.appendChild(tr);
                });
            } else {
                tbody.innerHTML = '<tr><td colspan="15" class="text-center">暂无数据</td></tr>';
            }
        })
        .catch(err => console.error("Error loading data table:", err));
}

// 绑定刷新概览按钮（如果存在）
const refreshOverviewBtn = document.getElementById('refreshOverviewBtn');
if (refreshOverviewBtn) {
    refreshOverviewBtn.addEventListener('click', loadDataOverview);
}

// 加载模型性能数据
function loadModelPerformance() {
    fetch('/api/model_performance')
        .then(res => res.json())
        .then(data => {
            if (!data.success) {
                document.getElementById('classification-report').innerHTML = `<div class="alert alert-warning">${data.error}</div>`;
                return;
            }
            const perf = data.performance;
            // 1. 分类报告表格
            const report = perf.classification_report;
            let reportHtml = `<table class="table table-sm table-bordered">
                <thead><tr><th></th><th>精确率</th><th>召回率</th><th>F1分数</th><th>支持数</th></tr></thead>
                <tbody>`;
            for (let label of ['0', '1']) {
                if (report[label]) {
                    reportHtml += `<tr>
                        <td>${label === '0' ? '健康' : '患病'}</td>
                        <td>${report[label].precision.toFixed(3)}</td>
                        <td>${report[label].recall.toFixed(3)}</td>
                        <td>${report[label]['f1-score'].toFixed(3)}</td>
                        <td>${report[label].support}</td>
                    </tr>`;
                }
            }
            reportHtml += `<tr><td><strong>准确率</strong></td><td colspan="4">${perf.accuracy.toFixed(3)}</td></tr>`;
            reportHtml += `</tbody></table>`;
            document.getElementById('classification-report').innerHTML = reportHtml;

            // 2. 混淆矩阵热力图
            const cm = perf.confusion_matrix;
            const cmChart = echarts.init(document.getElementById('confusion-matrix-chart'));
            cmChart.setOption({
                tooltip: { trigger: 'item' },
                xAxis: { type: 'category', data: ['预测:健康', '预测:患病'] },
                yAxis: { type: 'category', data: ['真实:健康', '真实:患病'], inverse: true },
                visualMap: { min: 0, max: Math.max(...cm.flat()), calculable: true, orient: 'horizontal', left: 'center', bottom: -10 },
                series: [{
                    type: 'heatmap',
                    data: [
                        [0, 0, cm[0][0]], // 预健康，真健康
                        [1, 0, cm[0][1]], // 预患病，真健康
                        [0, 1, cm[1][0]], // 预健康，真患病
                        [1, 1, cm[1][1]]  // 预患病，真患病
                    ],
                    label: { show: true },
                    emphasis: { itemStyle: { shadowBlur: 10 } }
                }]
            });

            // 3. 特征重要性条形图
            const features = perf.feature_names;
            const importance = perf.feature_importance;
            const pairs = features.map((f, i) => ({ name: f, value: importance[i] })).sort((a,b) => b.value - a.value);
            const impChart = echarts.init(document.getElementById('feature-importance-chart'));
            impChart.setOption({
                tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
                grid: { left: '15%', containLabel: true },
                xAxis: { type: 'value', name: '重要性' },
                yAxis: { type: 'category', data: pairs.map(p => p.name), axisLabel: { rotate: 30 } },
                series: [{ type: 'bar', data: pairs.map(p => p.value), itemStyle: { color: '#3498db' } }]
            });
        })
        .catch(err => console.error("加载模型性能失败:", err));
}

// 绑定模态框显示事件
const perfModal = document.getElementById('performanceModal');
if (perfModal) {
    perfModal.addEventListener('shown.bs.modal', loadModelPerformance);
}

// 关联规则功能
const minSupportSlider = document.getElementById('min-support');
const minConfidenceSlider = document.getElementById('min-confidence');
const supportValue = document.getElementById('support-value');
const confidenceValue = document.getElementById('confidence-value');
const mineBtn = document.getElementById('mine-rules-btn');
const rulesResultDiv = document.getElementById('rules-result');
const rulesLoadingDiv = document.getElementById('rules-loading');
const exportBtn = document.getElementById('export-rules-btn');

if (minSupportSlider) {
    minSupportSlider.addEventListener('input', function() {
        supportValue.innerText = this.value;
    });
    minConfidenceSlider.addEventListener('input', function() {
        confidenceValue.innerText = this.value;
    });
}

async function mineRules() {
    const minSupport = parseFloat(minSupportSlider.value);
    const minConfidence = parseFloat(minConfidenceSlider.value);
    rulesLoadingDiv.style.display = 'block';
    rulesResultDiv.innerHTML = '';
    exportBtn.style.display = 'none';
    try {
        const response = await fetch('/api/rules', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ min_support: minSupport, min_confidence: minConfidence })
        });
        const data = await response.json();
        rulesLoadingDiv.style.display = 'none';
        if (data.success) {
            if (data.rules.length === 0) {
                rulesResultDiv.innerHTML = '<div class="alert alert-info">未找到符合条件的规则，请降低支持度或置信度。</div>';
                return;
            }
            // 构建表格
            let html = '<div class="table-responsive"><table class="table table-bordered table-striped"><thead><tr>';
            html += '<th>前提 (Antecedents)</th><th>结论 (Consequents)</th><th>支持度</th><th>置信度</th><th>提升度</th></tr></thead><tbody>';
            data.rules.forEach(rule => {
                html += `<tr>
                    <td>${rule.antecedents}</td>
                    <td>${rule.consequents}</td>
                    <td>${rule.support.toFixed(3)}</td>
                    <td>${rule.confidence.toFixed(3)}</td>
                    <td>${rule.lift.toFixed(2)}</td>
                </tr>`;
            });
            html += '</tbody></table></div>';
            rulesResultDiv.innerHTML = html;
            exportBtn.style.display = 'inline-block';
            // 存储规则数据以供导出
            window.currentRules = data.rules;
        } else {
            rulesResultDiv.innerHTML = `<div class="alert alert-danger">挖掘失败: ${data.error}</div>`;
        }
    } catch (err) {
        rulesLoadingDiv.style.display = 'none';
        rulesResultDiv.innerHTML = '<div class="alert alert-danger">网络错误，请重试。</div>';
    }
}

if (mineBtn) {
    mineBtn.addEventListener('click', mineRules);
}

// 导出 CSV
function exportRulesToCSV() {
    if (!window.currentRules || window.currentRules.length === 0) return;
    const headers = ['antecedents', 'consequents', 'support', 'confidence', 'lift'];
    const rows = window.currentRules.map(rule => [rule.antecedents, rule.consequents, rule.support, rule.confidence, rule.lift]);
    let csvContent = headers.join(',') + '\n';
    rows.forEach(row => {
        csvContent += row.map(cell => `"${cell}"`).join(',') + '\n';
    });
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.href = url;
    link.setAttribute('download', 'association_rules.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

if (exportBtn) {
    exportBtn.addEventListener('click', exportRulesToCSV);
}