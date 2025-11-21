// 縣市專頁 JavaScript（高雄/台南）

let analysisData = null;
let COUNTY_NAME = null;  // 全域變數，用於圖表標題

// 從 window 物件讀取縣市名稱和代碼（在 DOMContentLoaded 時重新讀取，確保已設置）
function getCountyInfo() {
    const countyName = window.COUNTY_NAME || '高雄市';
    const countyCode = window.COUNTY_CODE || 'kaohsiung';
    COUNTY_NAME = countyName;  // 設定全域變數
    console.log('讀取縣市資訊:', countyName, countyCode);
    return { name: countyName, code: countyCode };
}

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('縣市專頁 DOM 載入完成，開始初始化...');
    const countyInfo = getCountyInfo();
    console.log('使用的縣市資訊:', countyInfo);
    loadData(countyInfo.code, countyInfo.name);
});

// 如果 DOM 已經載入完成
if (document.readyState !== 'loading') {
    console.log('DOM 已載入，直接執行初始化');
    const countyInfo = getCountyInfo();
    loadData(countyInfo.code, countyInfo.name);
}

// 載入資料
async function loadData(countyCode, countyName) {
    try {
        // 如果沒有傳入參數，從 window 物件讀取
        if (!countyCode) {
            const info = getCountyInfo();
            countyCode = info.code;
            countyName = info.name;
        }
        
        // 確保 COUNTY_NAME 已設定
        COUNTY_NAME = countyName || window.COUNTY_NAME || '高雄市';
        
        console.log('開始載入縣市資料...', countyCode, countyName);
        
        const response = await fetch(`static/data/dengue_analysis.json`);
        console.log('API 回應狀態:', response.status);
        console.log('API URL:', `static/data/dengue_analysis.json`);
        
        if (!response.ok) {
            throw new Error(`無法載入資料: ${response.status}`);
        }
        
        analysisData = await response.json();
                // 如果是縣市專頁，需要過濾資料
                if (countyCode && countyCode !== 'main') {
                    // 這裡需要在前端過濾資料，或使用預先處理的 JSON
                    console.log('縣市專頁需要過濾資料:', countyCode);
                }
        console.log('縣市資料載入成功');
        console.log('資料摘要:', {
            summary: analysisData.summary,
            hasLocation: !!analysisData.location,
            hasPerson: !!analysisData.person
        });
        
        // 驗證資料是否正確
        if (analysisData.summary && analysisData.summary['縣市']) {
            console.log('資料中的縣市:', analysisData.summary['縣市']);
            if (analysisData.summary['縣市'] !== countyName) {
                console.warn('警告: 資料中的縣市名稱與請求不符!', {
                    請求: countyName,
                    實際: analysisData.summary['縣市']
                });
            }
        }
        
        // 渲染資料
        renderSummary();
        renderCharts();
        
        console.log('縣市資料渲染完成');
    } catch (error) {
        console.error('載入縣市資料錯誤:', error);
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = 'background: #fee; border: 2px solid #e63946; padding: 1rem; margin: 1rem; border-radius: 4px;';
        errorDiv.innerHTML = `
            <h3 style="color: #e63946;">無法載入資料</h3>
            <p>錯誤訊息: ${error.message}</p>
            <p>請檢查：</p>
            <ul>
                <li>Flask 伺服器是否正常運行</li>
                <li>API 端點是否正確: /api/data/${countyCode || 'tainan'}</li>
                <li>資料檔案是否存在: data/processed/dengue_analysis.json</li>
            </ul>
        `;
        document.querySelector('.main-content')?.insertBefore(errorDiv, document.querySelector('.main-content').firstChild);
    }
}

// 格式化數字
function formatNumber(num) {
    if (num === null || num === undefined) return '-';
    return num.toLocaleString('zh-TW');
}

// 渲染摘要統計
function renderSummary() {
    const summary = analysisData.summary || {};
    
    document.getElementById('totalCases').textContent = formatNumber(summary.總病例數 || 0);
    document.getElementById('districtCount').textContent = summary.鄉鎮數 || 0;
    
    // 找出最多病例的行政區
    const townships = analysisData.location?.township || [];
    if (townships.length > 0) {
        const topDistrict = townships[0];
        document.getElementById('topDistrict').textContent = `${topDistrict.居住鄉鎮} (${formatNumber(topDistrict.病例數)}例)`;
    }
    
    // 找出疫情高峰年
    const yearlyData = analysisData.location?.county_yearly || [];
    if (yearlyData.length > 0) {
        const peakYear = yearlyData.reduce((max, item) => 
            item.病例數 > max.病例數 ? item : max, yearlyData[0]);
        document.getElementById('peakYear').textContent = `${peakYear.發病年}年 (${formatNumber(peakYear.病例數)}例)`;
    }
    
    // 更新最後更新時間
    if (analysisData.last_updated) {
        document.getElementById('lastUpdated').textContent = analysisData.last_updated;
    }
}

// 渲染所有圖表
function renderCharts() {
    renderYearlyChart();
    renderMonthlyChart();
    renderYearlyMonthlyChart();
    renderDistrictTable();
    renderDistrictChart();
    renderDistrictYearlyChart();
    renderGenderChart();
    renderAgeChart();
}

// 年度趨勢圖
function renderYearlyChart() {
    const ctx = document.getElementById('yearlyChart');
    if (!ctx) return;
    
    const yearlyData = analysisData.location?.county_yearly || [];
    if (yearlyData.length === 0) return;
    
    const labels = yearlyData.map(d => d.發病年);
    const values = yearlyData.map(d => d.病例數);
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: `${COUNTY_NAME}年度病例數`,
                data: values,
                borderColor: '#0093d5',
                backgroundColor: 'rgba(0, 147, 213, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: `${COUNTY_NAME}登革熱病例年度趨勢`,
                    font: { size: 16, weight: 'bold' }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return formatNumber(value);
                        }
                    }
                }
            }
        }
    });
}

// 月度分布圖
function renderMonthlyChart() {
    const ctx = document.getElementById('monthlyChart');
    if (!ctx) return;
    
    // 使用整體的月度數據（因為沒有縣市特定的月度數據）
    const monthlyData = analysisData.time?.monthly || [];
    if (monthlyData.length === 0) return;
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: monthlyData.map(d => d.月份),
            datasets: [{
                label: '平均月度病例數',
                data: monthlyData.map(d => d.病例數),
                backgroundColor: '#00a651',
                borderColor: '#00a651',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '登革熱病例月度分布（季節性模式）',
                    font: { size: 16, weight: 'bold' }
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// 年度-月度分布折線圖
function renderYearlyMonthlyChart() {
    const mapElement = document.getElementById('yearlyMonthlyHeatmap');
    if (!mapElement) return;
    
    // 使用整體的年度-月度數據
    const yearlyMonthlyData = analysisData.time?.yearly_monthly || [];
    if (yearlyMonthlyData.length === 0) return;
    
    const years = [...new Set(yearlyMonthlyData.map(d => d.發病年))].sort((a, b) => a - b);
    const months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
    const monthLabels = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'];
    
    const colorPalette = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
    ];
    
    const traces = years.map((year, yearIndex) => {
        const yearData = months.map(month => {
            const item = yearlyMonthlyData.find(d => d.發病年 === year && d.發病月 === month);
            return item ? item.病例數 : 0;
        });
        
        const yearTotal = yearData.reduce((sum, val) => sum + val, 0);
        
        return {
            x: monthLabels,
            y: yearData,
            name: `${year}年 (${formatNumber(yearTotal)}例)`,
            type: 'scatter',
            mode: 'lines+markers',
            line: {
                color: colorPalette[yearIndex % colorPalette.length],
                width: 2,
                shape: 'spline'
            },
            marker: {
                color: colorPalette[yearIndex % colorPalette.length],
                size: 5,
                line: { color: '#fff', width: 1 }
            },
            hovertemplate: '<b>%{fullData.name}</b><br>%{x}: %{y:,.0f}例<extra></extra>',
            hoverlabel: {
                bgcolor: 'rgba(255, 255, 255, 0.95)',
                bordercolor: colorPalette[yearIndex % colorPalette.length],
                font: { size: 13, family: 'Arial, sans-serif', color: '#333' }
            }
        };
    });
    
    const allValues = traces.flatMap(t => t.y);
    const maxValue = Math.max(...allValues);
    
    const layout = {
        title: {
            text: '不同年度登革熱病例月度分布',
            font: { size: 18, weight: 'bold' },
            x: 0.5,
            xanchor: 'center'
        },
        xaxis: {
            title: { text: '月份', font: { size: 14 } },
            tickangle: 0,
            fixedrange: true,
            showgrid: true,
            gridcolor: 'rgba(200,200,200,0.3)'
        },
        yaxis: {
            title: { text: '病例數', font: { size: 14 } },
            tickformat: ',d',
            range: [0, maxValue * 1.1],
            fixedrange: true,
            showgrid: true,
            gridcolor: 'rgba(200,200,200,0.3)'
        },
        hovermode: 'closest',
        legend: {
            orientation: 'h',
            x: 0.5,
            y: -0.15,
            xanchor: 'center',
            yanchor: 'top',
            font: { size: 9 },
            itemwidth: 30,
            tracegroupgap: 5,
            borderwidth: 1,
            bgcolor: 'rgba(255,255,255,0.9)',
            itemsizing: 'constant'
        },
        margin: { t: 60, b: 120, l: 80, r: 30 },
        autosize: true,
        height: 500,
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(245,245,245,0.5)'
    };
    
    const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d', 'zoom2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d'],
        toImageButtonOptions: {
            format: 'png',
            filename: `${COUNTY_NAME}_yearly_monthly_distribution`,
            height: 500,
            width: 1200,
            scale: 2
        }
    };
    
    try {
        Plotly.newPlot('yearlyMonthlyHeatmap', traces, layout, config);
        console.log('年度-月度折線圖繪製完成');
        
        window.addEventListener('resize', function() {
            Plotly.Plots.resize('yearlyMonthlyHeatmap');
        });
    } catch (error) {
        console.error('Plotly 繪圖錯誤:', error);
    }
}

// 渲染行政區統計表格
function renderDistrictTable() {
    const tbody = document.getElementById('districtTableBody');
    if (!tbody) return;
    
    const townshipData = analysisData.location?.township || [];
    if (townshipData.length === 0) return;
    
    const totalCases = townshipData.reduce((sum, item) => sum + item.病例數, 0);
    const sortedData = [...townshipData].sort((a, b) => b.病例數 - a.病例數);
    
    tbody.innerHTML = sortedData.map((item, index) => {
        const percentage = totalCases > 0 ? ((item.病例數 / totalCases) * 100).toFixed(2) : '0.00';
        return `
            <tr>
                <td>${index + 1}</td>
                <td>${item.居住鄉鎮}</td>
                <td class="number-cell">${formatNumber(item.病例數)}</td>
                <td class="number-cell">${percentage}%</td>
            </tr>
        `;
    }).join('');
}

// 行政區分布圖
function renderDistrictChart() {
    const ctx = document.getElementById('districtChart');
    if (!ctx) return;
    
    const townshipData = analysisData.location?.township || [];
    if (townshipData.length === 0) return;
    
    const sortedData = [...townshipData].sort((a, b) => b.病例數 - a.病例數).slice(0, 20);
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sortedData.map(d => d.居住鄉鎮),
            datasets: [{
                label: '病例數',
                data: sortedData.map(d => d.病例數),
                backgroundColor: '#0093d5'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                title: {
                    display: true,
                    text: `${COUNTY_NAME}各行政區登革熱病例分布（Top 20）`,
                    font: { size: 16, weight: 'bold' }
                }
            },
            scales: {
                x: {
                    beginAtZero: true
                }
            }
        }
    });
}

// 行政區年度趨勢圖
function renderDistrictYearlyChart() {
    const ctx = document.getElementById('districtYearlyChart');
    if (!ctx) return;
    
    // 使用縣市年度趨勢（因為沒有行政區年度趨勢數據）
    const yearlyData = analysisData.location?.county_yearly || [];
    if (yearlyData.length === 0) return;
    
    const years = yearlyData.map(d => d.發病年.toString());
    const values = yearlyData.map(d => d.病例數);
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: years,
            datasets: [{
                label: `${COUNTY_NAME}年度病例數`,
                data: values,
                borderColor: '#0093d5',
                backgroundColor: 'rgba(0, 147, 213, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: `${COUNTY_NAME}登革熱病例年度趨勢`,
                    font: { size: 16, weight: 'bold' }
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// 性別分布圖
function renderGenderChart() {
    const ctx = document.getElementById('genderChart');
    if (!ctx) return;
    
    // 使用該縣市的性別數據
    const genderData = analysisData.person?.gender || [];
    if (genderData.length === 0) return;
    
    // 性別標籤對應（F=女性, M=男性, U=未知）
    const genderLabelMap = {
        'F': '女性',
        'M': '男性',
        'U': '未知',
        '女': '女性',
        '男': '男性',
        '未知': '未知'
    };
    
    // 準備資料，確保順序：男性、女性、未知
    const sortedGenderData = [];
    const genderOrder = ['M', 'F', 'U', '男', '女', '未知'];
    const colors = {
        'M': '#0093d5',      // 男性：藍色
        '男': '#0093d5',     // 男性：藍色
        'F': '#e63946',      // 女性：紅色
        '女': '#e63946',     // 女性：紅色
        'U': '#6c757d',      // 未知：灰色
        '未知': '#6c757d'    // 未知：灰色
    };
    
    genderOrder.forEach(genderKey => {
        const item = genderData.find(d => d.性別 === genderKey);
        if (item) {
            sortedGenderData.push({
                ...item,
                label: genderLabelMap[genderKey] || genderKey,
                color: colors[genderKey] || '#6c757d'
            });
        }
    });
    
    // 如果還有其他性別值，也加入
    genderData.forEach(item => {
        if (!genderOrder.includes(item.性別)) {
            sortedGenderData.push({
                ...item,
                label: genderLabelMap[item.性別] || item.性別,
                color: '#6c757d'
            });
        }
    });
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: sortedGenderData.map(d => d.label),
            datasets: [{
                data: sortedGenderData.map(d => d.病例數),
                backgroundColor: sortedGenderData.map(d => d.color)
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: `${COUNTY_NAME}性別分布`,
                    font: { size: 16, weight: 'bold' }
                },
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// 年齡分布圖
function renderAgeChart() {
    const ctx = document.getElementById('ageChart');
    if (!ctx) return;
    
    // 使用整體的年齡數據
    const ageData = analysisData.person?.age || [];
    if (ageData.length === 0) return;
    
    // 固定年齡層排序
    const ageOrder = ['0-4', '5-9', '10-14', '15-19', '20-24', '25-29', '30-34', 
                      '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', 
                      '65-69', '70-74', '75-79', '80-84', '85+', '未知'];
    
    const sortedAgeData = ageOrder.map(age => {
        const item = ageData.find(d => d.年齡層 === age);
        return item || { 年齡層: age, 病例數: 0 };
    });
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sortedAgeData.map(d => d.年齡層),
            datasets: [{
                label: '病例數',
                data: sortedAgeData.map(d => d.病例數),
                backgroundColor: '#00a651'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '年齡層分布',
                    font: { size: 16, weight: 'bold' }
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

