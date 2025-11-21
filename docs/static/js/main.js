// 登革熱監測系統主要 JavaScript

let analysisData = null;

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM 載入完成，開始初始化...');
    console.log('analysisData 初始值:', analysisData);
    loadData();
});

// 如果 DOM 已經載入完成
if (document.readyState === 'loading') {
    // DOM 還在載入中，等待 DOMContentLoaded 事件
    console.log('等待 DOM 載入...');
} else {
    // DOM 已經載入完成，直接執行
    console.log('DOM 已載入，直接執行初始化');
    loadData();
}

// 載入資料
async function loadData() {
    try {
        console.log('開始載入資料...');
        
        // 顯示載入訊息
        const loadingMsg = document.createElement('div');
        loadingMsg.id = 'loading-message';
        loadingMsg.style.cssText = 'text-align: center; padding: 2rem; color: #666;';
        loadingMsg.innerHTML = '<p>正在載入資料...</p>';
        document.body.insertBefore(loadingMsg, document.body.firstChild);
        
        const response = await fetch('./static/data/dengue_analysis.json');
        console.log('API 回應狀態:', response.status, response.statusText);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('API 錯誤回應:', errorText);
            throw new Error(`無法載入資料: ${response.status} ${response.statusText}`);
        }
        
        analysisData = await response.json();
        console.log('資料載入成功');
        console.log('資料結構:', {
            hasSummary: !!analysisData.summary,
            hasTime: !!analysisData.time,
            hasLocation: !!analysisData.location,
            hasPerson: !!analysisData.person
        });
        
        if (!analysisData) {
            throw new Error('資料為空');
        }
        
        if (!analysisData.summary) {
            console.warn('警告: 缺少 summary 資料');
        }
        
        // 移除載入訊息
        const loadingEl = document.getElementById('loading-message');
        if (loadingEl) loadingEl.remove();
        
        // 渲染資料
        if (analysisData.summary) {
            renderSummary();
        } else {
            console.error('無法渲染摘要：缺少 summary 資料');
        }
        
        renderCharts();
        
        console.log('資料渲染完成');
    } catch (error) {
        console.error('載入資料錯誤:', error);
        const errorMsg = error.message || '未知錯誤';
        
        // 移除載入訊息
        const loadingEl = document.getElementById('loading-message');
        if (loadingEl) loadingEl.remove();
        
        // 顯示錯誤訊息（不覆蓋整個頁面）
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = 'background: #fee; border: 2px solid #e63946; padding: 1rem; margin: 1rem; border-radius: 4px;';
        errorDiv.innerHTML = `
            <h3 style="color: #e63946; margin: 0 0 0.5rem 0;">無法載入資料</h3>
            <p style="margin: 0.5rem 0; color: #666;">錯誤訊息: ${errorMsg}</p>
            <p style="margin: 0.5rem 0; font-size: 0.9rem; color: #999;">
                請確認：<br/>
                1. 已執行資料分析腳本: python src/analyze_dengue.py<br/>
                2. 資料檔案存在: data/processed/dengue_analysis.json<br/>
                3. 檢查瀏覽器控制台 (F12) 查看詳細錯誤訊息
            </p>
        `;
        const mainContent = document.querySelector('.main-content');
        if (mainContent) {
            mainContent.insertBefore(errorDiv, mainContent.firstChild);
        } else {
            document.body.appendChild(errorDiv);
        }
    }
}

// 渲染摘要統計
function renderSummary() {
    try {
        if (!analysisData) {
            console.error('analysisData 不存在');
            return;
        }
        
        const summary = analysisData.summary;
        
        if (!summary) {
            console.error('缺少 summary 資料');
            console.log('analysisData 內容:', analysisData);
            return;
        }
        
        console.log('開始渲染摘要統計，summary 內容:', summary);
        
        const totalCasesEl = document.getElementById('totalCases');
        const dateRangeEl = document.getElementById('dateRange');
        const topCountyEl = document.getElementById('topCounty');
        const peakYearEl = document.getElementById('peakYear');
        const localCasesEl = document.getElementById('localCases');
        const importedCasesEl = document.getElementById('importedCases');
        const lastUpdatedEl = document.getElementById('lastUpdated');
        
        if (!totalCasesEl) {
            console.error('找不到 totalCases 元素');
            return;
        }
        
        if (totalCasesEl) {
            totalCasesEl.textContent = formatNumber(summary.total_cases || 0);
            console.log('設定總病例數:', summary.total_cases);
        }
        if (dateRangeEl) dateRangeEl.textContent = summary.date_range || '-';
        if (topCountyEl) topCountyEl.textContent = `${summary.top_county || '-'} (${formatNumber(summary.top_county_cases || 0)} 例)`;
        if (peakYearEl) peakYearEl.textContent = `${summary.peak_year || '-'} 年 (${formatNumber(summary.peak_year_cases || 0)} 例)`;
        if (localCasesEl) localCasesEl.textContent = `${formatNumber(summary.local_cases || 0)} (${summary.local_percentage || 0}%)`;
        if (importedCasesEl) importedCasesEl.textContent = `${formatNumber(summary.imported_cases || 0)} (${summary.imported_percentage || 0}%)`;
        if (lastUpdatedEl) lastUpdatedEl.textContent = analysisData.last_updated || '-';
        
        console.log('摘要統計渲染完成');
    } catch (error) {
        console.error('渲染摘要統計錯誤:', error);
        console.error('錯誤堆疊:', error.stack);
    }
}

// 渲染所有圖表
function renderCharts() {
    try {
        console.log('開始渲染圖表...');
        
        // 檢查必要資料是否存在
        if (!analysisData) {
            console.error('analysisData 不存在');
            return;
        }
        
        if (analysisData.location) {
            renderTaiwanMap();
            renderCountyTable();
        }
        
        if (analysisData.time) {
            renderYearlyChart();
            renderMonthlyChart();
            renderYearlyMonthlyHeatmap();
            renderRecentTrendChart();
        }
        
        if (analysisData.location) {
            renderCountyChart();
            renderCountyYearlyChart();
        }
        
        if (analysisData.person) {
            renderGenderChart();
            renderAgeChart();
            renderGenderYearlyChart();
            renderImportStatusChart();
            renderImportYearlyChart();
        }
        
        console.log('所有圖表渲染完成');
    } catch (error) {
        console.error('渲染圖表錯誤:', error);
    }
}

// 台灣地圖視覺化（使用 Plotly Choropleth Map）
function renderTaiwanMap() {
    const mapElement = document.getElementById('taiwanMap');
    if (!mapElement) {
        console.error('找不到地圖元素');
        return;
    }
    
    console.log('開始渲染 Plotly 地圖...');
    
    const countyData = analysisData.location.county;
    
    // 建立縣市名稱對應（處理「台」vs「臺」的差異）
    // 資料中使用「台」，GeoJSON 中可能使用「臺」
    const nameMapping = {
        '台北市': '臺北市',
        '台中市': '臺中市',
        '台南市': '臺南市',
        '台東縣': '臺東縣'
    };
    
    // 反向對應（從「臺」到「台」）
    const reverseMapping = {
        '臺北市': '台北市',
        '臺中市': '台中市',
        '臺南市': '台南市',
        '臺東縣': '台東縣'
    };
    
    // 建立完整的縣市名稱對應表（包含所有可能的變體）
    const allNameVariants = {};
    Object.entries(nameMapping).forEach(([key, value]) => {
        allNameVariants[key] = value;
        allNameVariants[value] = key;
    });
    
    // 建立病例數對應表（同時支援「台」和「臺」）
    const casesMap = {};
    const countyNames = [];
    const casesValues = [];
    
    countyData.forEach(item => {
        if (item.居住縣市 === '未知') return;
        const originalName = item.居住縣市;
        const standardName = nameMapping[originalName] || originalName;
        
        // 同時儲存兩種名稱格式，以便匹配
        casesMap[originalName] = item.病例數;
        if (standardName !== originalName) {
            casesMap[standardName] = item.病例數;
        }
        
        // 也儲存反向對應（如果有的話）
        if (reverseMapping[standardName]) {
            casesMap[reverseMapping[standardName]] = item.病例數;
        }
        
        countyNames.push(standardName);
        casesValues.push(item.病例數);
    });
    
    console.log('建立的病例數對應表（所有鍵）:', Object.keys(casesMap));
    
    const maxCases = Math.max(...casesValues);
    
    console.log('病例數對應表:', casesMap);
    
    // 載入台灣縣市 GeoJSON - 使用更可靠的來源
    const geoJsonUrls = [
        'https://raw.githubusercontent.com/g0v/twgeojson/master/json/twCounty2010.geo.json',
        'https://raw.githubusercontent.com/kiang/pharmacies/master/json/taiwan.json'
    ];
    
    async function loadGeoJSON() {
        for (const url of geoJsonUrls) {
            try {
                console.log(`嘗試載入: ${url}`);
                const response = await fetch(url);
                if (response.ok) {
                    const geoJson = await response.json();
                    console.log('GeoJSON 載入成功');
                    console.log('GeoJSON features 數量:', geoJson.features?.length);
                    if (geoJson.features && geoJson.features.length > 0) {
                        console.log('第一個 feature 的屬性:', geoJson.features[0].properties);
                    }
                    return geoJson;
                }
            } catch (e) {
                console.log(`無法載入 ${url}，嘗試下一個...`, e);
                continue;
            }
        }
        return null;
    }
    
    loadGeoJSON().then(geoJson => {
        if (!geoJson || !geoJson.features || geoJson.features.length === 0) {
            console.error('無法載入任何 GeoJSON 檔案或檔案為空');
            mapElement.innerHTML = `
                <div style="display: flex; align-items: center; justify-content: center; height: 100%; background: #f0f0f0; border-radius: 4px;">
                    <div style="text-align: center; padding: 20px;">
                        <p style="font-size: 16px; color: #666;">無法載入地圖資料</p>
                        <p style="font-size: 14px; color: #999; margin-top: 10px;">請查看下方縣市統計表格</p>
                    </div>
                </div>
            `;
            return;
        }
        
        console.log('GeoJSON features 總數:', geoJson.features.length);
        
        // 找出 GeoJSON 中使用的縣市名稱屬性
        const firstFeature = geoJson.features[0];
        const props = firstFeature.properties;
        console.log('GeoJSON 屬性名稱:', Object.keys(props));
        
        let countyKey = null;
        if (props.COUNTYNAME) countyKey = 'COUNTYNAME';
        else if (props.COUNTY) countyKey = 'COUNTY';
        else if (props.name) countyKey = 'name';
        else if (props.縣市) countyKey = '縣市';
        else if (props.NAME_2014) countyKey = 'NAME_2014';
        
        console.log('使用的縣市屬性名稱:', countyKey);
        
        if (!countyKey) {
            console.error('找不到縣市名稱屬性');
            mapElement.innerHTML = `
                <div style="display: flex; align-items: center; justify-content: center; height: 100%; background: #f0f0f0; border-radius: 4px;">
                    <div style="text-align: center; padding: 20px;">
                        <p style="font-size: 16px; color: #666;">地圖資料格式不正確</p>
                        <p style="font-size: 14px; color: #999; margin-top: 10px;">請查看下方縣市統計表格</p>
                    </div>
                </div>
            `;
            return;
        }
        
        // 準備 Plotly 資料
        const locations = [];
        const z = [];
        const text = [];
        const customdata = [];
        
        geoJson.features.forEach(feature => {
            let geoCountyName = feature.properties[countyKey];
            if (!geoCountyName) return;
            
            // 處理名稱差異（台 vs 臺）
            // 嘗試多種匹配方式
            let cases = 0;
            let displayName = geoCountyName;
            
            // 1. 直接匹配（最優先）
            if (casesMap[geoCountyName] !== undefined) {
                cases = casesMap[geoCountyName];
                displayName = geoCountyName;
            }
            // 2. 嘗試標準化名稱（台 -> 臺）
            else if (nameMapping[geoCountyName]) {
                const standardName = nameMapping[geoCountyName];
                if (casesMap[standardName] !== undefined) {
                    cases = casesMap[standardName];
                    displayName = standardName;
                }
            }
            // 3. 嘗試反向對應（臺 -> 台）
            else if (reverseMapping[geoCountyName]) {
                const originalName = reverseMapping[geoCountyName];
                if (casesMap[originalName] !== undefined) {
                    cases = casesMap[originalName];
                    displayName = originalName;
                }
            }
            // 4. 嘗試部分匹配（移除「市」「縣」等後綴）
            else {
                const nameWithoutSuffix = geoCountyName.replace(/[市縣]$/, '');
                for (const [key, value] of Object.entries(casesMap)) {
                    const keyWithoutSuffix = key.replace(/[市縣]$/, '');
                    if (keyWithoutSuffix === nameWithoutSuffix) {
                        cases = value;
                        displayName = key;
                        break;
                    }
                }
            }
            
            // 如果還是找不到，嘗試模糊匹配（處理「台」和「臺」的差異）
            if (cases === 0) {
                // 將「臺」替換為「台」再試一次
                const nameWithTai = geoCountyName.replace(/臺/g, '台');
                if (casesMap[nameWithTai] !== undefined) {
                    cases = casesMap[nameWithTai];
                    displayName = nameWithTai;
                }
                // 將「台」替換為「臺」再試一次
                else {
                    const nameWithTaiTraditional = geoCountyName.replace(/台/g, '臺');
                    if (casesMap[nameWithTaiTraditional] !== undefined) {
                        cases = casesMap[nameWithTaiTraditional];
                        displayName = nameWithTaiTraditional;
                    }
                }
            }
            
            locations.push(geoCountyName);
            z.push(cases);
            text.push(`${displayName}<br>病例數: ${formatNumber(cases)} 例`);
            customdata.push(displayName);
            
            if (cases > 0) {
                console.log(`✓ 配對成功: ${geoCountyName} -> ${displayName} = ${cases} 例`);
            } else {
                console.warn(`⚠ 無法配對: ${geoCountyName} (GeoJSON 中的名稱)`);
            }
        });
        
        console.log('成功配對縣市數:', locations.length);
        console.log('Locations:', locations);
        console.log('病例數:', z);
        
        if (locations.length === 0) {
            console.error('沒有成功配對任何縣市');
            mapElement.innerHTML = `
                <div style="display: flex; align-items: center; justify-content: center; height: 100%; background: #f0f0f0; border-radius: 4px;">
                    <div style="text-align: center; padding: 20px;">
                        <p style="font-size: 16px; color: #666;">無法配對縣市資料</p>
                        <p style="font-size: 14px; color: #999; margin-top: 10px;">請查看下方縣市統計表格</p>
                    </div>
                </div>
            `;
            return;
        }
        
        // 建立 Plotly Choropleth
        const data = [{
            type: 'choropleth',
            geojson: geoJson,
            locations: locations,
            z: z,
            text: text,
            featureidkey: `properties.${countyKey}`,
            hovertemplate: '<b>%{text}</b><extra></extra>',
            colorscale: [
                [0, '#e0f2fe'],
                [0.2, '#7dd3fc'],
                [0.4, '#38bdf8'],
                [0.6, '#0284c7'],
                [0.8, '#0369a1'],
                [1, '#075985']
            ],
            zmin: 0,
            zmax: maxCases,
            marker: {
                line: {
                    color: 'white',
                    width: 1.5
                }
            },
            colorbar: {
                title: {
                    text: '病例數',
                    font: { size: 14, color: '#333' }
                },
                tickformat: ',d',
                len: 0.6,
                y: 0.5,
                yanchor: 'middle',
                bgcolor: 'rgba(255,255,255,0.9)',
                bordercolor: '#ccc',
                borderwidth: 1,
                thickness: 20
            }
        }];
        
        const layout = {
            geo: {
                scope: 'asia',
                fitbounds: 'geojson',  // 自動適應 GeoJSON 範圍
                visible: true,
                showcountries: false,
                showframe: false,
                showcoastlines: false,
                showlakes: false,
                showocean: false,
                showland: false,
                projection: {
                    type: 'mercator'
                },
                bgcolor: 'rgba(0,0,0,0)',
                // 設定台灣的初始視圖（確保顯示完整台灣）
                center: {
                    lon: 120.5,
                    lat: 23.5
                },
                lonaxis: {
                    range: [119, 122]
                },
                lataxis: {
                    range: [21.5, 25.5]
                }
            },
            margin: { t: 0, b: 0, l: 0, r: 100 },  // 右側留空間給 colorbar
            height: 600,
            autosize: true,
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)'
        };
        
        const config = {
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d'],
            toImageButtonOptions: {
                format: 'png',
                filename: 'taiwan_dengue_map',
                height: 600,
                width: 1200,
                scale: 2
            }
        };
        
        // 繪製地圖
        try {
            Plotly.newPlot('taiwanMap', data, layout, config);
            console.log('Plotly 地圖繪製完成');
            
            // 調整地圖大小以適應容器
            window.addEventListener('resize', function() {
                Plotly.Plots.resize('taiwanMap');
            });
        } catch (error) {
            console.error('Plotly 繪圖錯誤:', error);
            console.error('錯誤詳情:', error.stack);
            mapElement.innerHTML = `
                <div style="display: flex; align-items: center; justify-content: center; height: 100%; background: #f0f0f0; border-radius: 4px;">
                    <div style="text-align: center; padding: 20px;">
                        <p style="font-size: 16px; color: #666;">地圖繪製失敗</p>
                        <p style="font-size: 14px; color: #999; margin-top: 10px;">錯誤: ${error.message}</p>
                    </div>
                </div>
            `;
        }
    }).catch(error => {
        console.error('載入 GeoJSON 錯誤:', error);
        mapElement.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 100%; background: #f0f0f0; border-radius: 4px;">
                <div style="text-align: center; padding: 20px;">
                    <p style="font-size: 16px; color: #666;">無法載入地圖資料</p>
                    <p style="font-size: 14px; color: #999; margin-top: 10px;">請查看下方縣市統計表格</p>
                </div>
            </div>
        `;
    });
}

// 渲染縣市統計表格
function renderCountyTable() {
    const tbody = document.getElementById('countyTableBody');
    if (!tbody) return;
    
    const countyData = analysisData.location.county.filter(item => item.居住縣市 !== '未知');
    const totalCases = countyData.reduce((sum, item) => sum + item.病例數, 0);
    
    // 按病例數排序
    const sortedData = [...countyData].sort((a, b) => b.病例數 - a.病例數);
    
    tbody.innerHTML = sortedData.map((item, index) => {
        const percentage = ((item.病例數 / totalCases) * 100).toFixed(2);
        return `
            <tr>
                <td>${index + 1}</td>
                <td>${item.居住縣市}</td>
                <td class="number-cell">${formatNumber(item.病例數)}</td>
                <td class="number-cell">${percentage}%</td>
            </tr>
        `;
    }).join('');
}

// 年度趨勢圖
function renderYearlyChart() {
    const ctx = document.getElementById('yearlyChart').getContext('2d');
    const data = analysisData.time.yearly;
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => d.年份),
            datasets: [{
                label: '年度病例數',
                data: data.map(d => d.病例數),
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
                    text: '登革熱病例年度趨勢',
                    font: { size: 16, weight: 'bold' }
                },
                legend: {
                    display: true
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
    const ctx = document.getElementById('monthlyChart').getContext('2d');
    const data = analysisData.time.monthly;
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.月份),
            datasets: [{
                label: '平均月度病例數',
                data: data.map(d => d.病例數),
                backgroundColor: '#00a651',
                borderColor: '#00a651',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            // 關鍵：調整 layout padding 來匹配 Plotly
            layout: {
                padding: {
                    left: 50,
                    right: 50,  // 增加右側 padding 來匹配 Plotly
                    top: 0,
                    bottom: 0
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: '登革熱病例月度分布（季節性模式）',
                    font: { size: 16, weight: 'bold' }
                },
                legend: {
                    display: false  // 可選：隱藏圖例節省空間
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        // 對齊左側 Y 軸
                        padding: 5
                    }
                },
                x: {
                    // 確保 X 軸刻度對齊
                    grid: {
                        offset: false
                    },
                    ticks: {
                        padding: 5
                    }
                }
            }
        }
    });
}

// 年度-月度分布折線圖(使用 Plotly,簡單折線圖)
function renderYearlyMonthlyHeatmap() {
    const mapElement = document.getElementById('yearlyMonthlyHeatmap');
    if (!mapElement) {
        console.error('找不到年度-月度圖表元素');
        return;
    }
    
    const yearlyMonthlyData = analysisData.time.yearly_monthly;
    
    // 取得所有年份和月份
    const years = [...new Set(yearlyMonthlyData.map(d => d.發病年))].sort((a, b) => a - b);
    const months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
    const monthLabels = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'];
    
    // 定義高對比度顏色調色盤
    const colorPalette = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
        '#0093d5', '#00a651', '#e63946', '#ffb703', '#fb5607',
        '#06ffa5', '#3a86ff', '#ff006e', '#4cc9f0', '#f72585',
        '#1d3557', '#7209b7', '#560bad', '#480ca8', '#3a0ca3',
        '#2d00f7', '#6a00f4', '#8900f2', '#b100e8', '#bc00dd'
    ];
    
    // 準備資料 - 關鍵改動:使用自定義 hovertemplate
    const traces = years.map((year, yearIndex) => {
        const yearData = months.map(month => {
            const item = yearlyMonthlyData.find(d => d.發病年 === year && d.發病月 === month);
            return item ? item.病例數 : 0;
        });
        
        // 計算該年度總病例數
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
                line: {
                    color: '#fff',
                    width: 1
                }
            },
            // 關鍵:自定義 hover 模板,只顯示該年份的資料
            hovertemplate: '<b>%{fullData.name}</b><br>%{x}: %{y:,.0f}例<extra></extra>',
            // 設定 hoverlabel 樣式
            hoverlabel: {
                bgcolor: 'rgba(255, 255, 255, 0.95)',
                bordercolor: colorPalette[yearIndex % colorPalette.length],
                font: {
                    size: 13,
                    family: 'Arial, sans-serif',
                    color: '#333'
                }
            }
        };
    });
    
    // 計算資料範圍
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
            title: {
                text: '月份',
                font: { size: 14 }
            },
            tickangle: 0,
            fixedrange: true,
            showgrid: true,
            gridcolor: 'rgba(200,200,200,0.3)'
        },
        yaxis: {
            title: {
                text: '病例數',
                font: { size: 14 }
            },
            tickformat: ',d',
            range: [0, maxValue * 1.1],
            fixedrange: true,
            showgrid: true,
            gridcolor: 'rgba(200,200,200,0.3)'
        },
        // 關鍵改動:使用 'closest' 模式,每次只顯示最近的一條線
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
        margin: { 
            t: 60, 
            b: 120,
            l: 80, 
            r: 30
        },
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
            filename: 'yearly_monthly_distribution',
            height: 500,
            width: 1200,
            scale: 2
        }
    };
    
    try {
        Plotly.newPlot('yearlyMonthlyHeatmap', traces, layout, config);
        console.log('年度-月度折線圖繪製完成');
        
        // 響應式調整
        window.addEventListener('resize', function() {
            Plotly.Plots.resize('yearlyMonthlyHeatmap');
        });
        
    } catch (error) {
        console.error('Plotly 繪圖錯誤:', error);
        mapElement.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 100%; background: #f0f0f0; border-radius: 4px;">
                <div style="text-align: center; padding: 20px;">
                    <p style="font-size: 16px; color: #666;">圖表繪製失敗</p>
                    <p style="font-size: 14px; color: #999; margin-top: 10px;">錯誤: ${error.message}</p>
                </div>
            </div>
        `;
    }
}

// 最近5年趨勢
function renderRecentTrendChart() {
    const ctx = document.getElementById('recentTrendChart').getContext('2d');
    const data = analysisData.time.recent_yearly_monthly;
    
    // 按年月分組
    const grouped = {};
    data.forEach(d => {
        if (!grouped[d.年月]) {
            grouped[d.年月] = 0;
        }
        grouped[d.年月] += d.病例數;
    });
    
    const labels = Object.keys(grouped).sort();
    const values = labels.map(label => grouped[label]);
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: '最近5年月度病例數',
                data: values,
                borderColor: '#e63946',
                backgroundColor: 'rgba(230, 57, 70, 0.1)',
                borderWidth: 2,
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
                    text: '最近5年登革熱病例趨勢',
                    font: { size: 16, weight: 'bold' }
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                },
                x: {
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            }
        }
    });
}

// 縣市分布圖
function renderCountyChart() {
    const ctx = document.getElementById('countyChart').getContext('2d');
    const data = analysisData.location.county_top20;
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.居住縣市),
            datasets: [{
                label: '病例數',
                data: data.map(d => d.病例數),
                backgroundColor: '#0093d5',
                borderColor: '#0077b6',
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '各縣市登革熱病例數（Top 20）',
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

// 縣市年度趨勢
function renderCountyYearlyChart() {
    const ctx = document.getElementById('countyYearlyChart').getContext('2d');
    const data = analysisData.location.county_yearly;
    
    // 按縣市分組
    const counties = [...new Set(data.map(d => d.居住縣市))];
    const years = [...new Set(data.map(d => d.發病年.toString()))].sort();
    
    const datasets = counties.map((county, index) => {
        const colors = ['#0093d5', '#00a651', '#e63946', '#ffb703', '#1d3557', '#7209b7', '#f72585', '#06ffa5', '#ff006e', '#8338ec'];
        return {
            label: county,
            data: years.map(year => {
                const item = data.find(d => d.居住縣市 === county && d.發病年.toString() === year);
                return item ? item.病例數 : 0;
            }),
            borderColor: colors[index % colors.length],
            backgroundColor: colors[index % colors.length] + '40',
            borderWidth: 2,
            fill: false,
            tension: 0.4
        };
    });
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: years,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '主要縣市登革熱病例年度趨勢',
                    font: { size: 16, weight: 'bold' }
                },
                legend: {
                    display: true,
                    position: 'right'
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
    const ctx = document.getElementById('genderChart').getContext('2d');
    const data = analysisData.person.gender;
    
    // 性別標籤和顏色對應（傳統顏色：男藍、女紅）
    const genderConfig = {
        'M': { label: '男性', color: '#0093d5' },  // 男性：藍色
        'F': { label: '女性', color: '#e63946' },  // 女性：紅色
        'U': { label: '未知', color: '#6c757d' },  // 未知：灰色
        '男': { label: '男性', color: '#0093d5' },
        '女': { label: '女性', color: '#e63946' },
        '未知': { label: '未知', color: '#6c757d' }
    };
    
    // 排序：男性、女性、未知
    const genderOrder = ['M', 'F', 'U', '男', '女', '未知'];
    const sortedData = [];
    genderOrder.forEach(key => {
        const item = data.find(d => d.性別 === key);
        if (item) {
            const config = genderConfig[key] || { label: key, color: '#6c757d' };
            sortedData.push({
                ...item,
                label: config.label,
                color: config.color
            });
        }
    });
    
    // 如果還有其他性別值
    data.forEach(item => {
        if (!genderOrder.includes(item.性別)) {
            const config = genderConfig[item.性別] || { label: item.性別, color: '#6c757d' };
            sortedData.push({
                ...item,
                label: config.label,
                color: config.color
            });
        }
    });
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: sortedData.map(d => d.label),
            datasets: [{
                data: sortedData.map(d => d.病例數),
                backgroundColor: sortedData.map(d => d.color),
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '登革熱病例性別分布',
                    font: { size: 16, weight: 'bold' }
                },
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// 年齡層分布圖（固定排序，從小到大）
function renderAgeChart() {
    const ctx = document.getElementById('ageChart').getContext('2d');
    const data = analysisData.person.age; // 已經在後端按固定順序排序
    
    // 定義年齡層的固定排序順序
    const ageOrder = [
        '0-4', '5-9', '10-14', '15-19', '20-24', '25-29', 
        '30-34', '35-39', '40-44', '45-49', '50-54', '55-59',
        '60-64', '65-69', '70-74', '75-79', '80-84', '85+', '未知'
    ];
    
    // 確保資料按固定順序排列
    const sortedData = ageOrder.map(age => {
        const found = data.find(d => d.年齡層 === age || d.年齡層.startsWith(age.split('-')[0]));
        return found || { 年齡層: age, 病例數: 0 };
    }).filter(d => d.病例數 > 0 || d.年齡層 === '未知'); // 只顯示有資料的年齡層
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sortedData.map(d => d.年齡層),
            datasets: [{
                label: '病例數',
                data: sortedData.map(d => d.病例數),
                backgroundColor: '#00a651',
                borderColor: '#00a651',
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '登革熱病例年齡層分布（按年齡排序）',
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

// 性別年度趨勢
function renderGenderYearlyChart() {
    const ctx = document.getElementById('genderYearlyChart').getContext('2d');
    const data = analysisData.person.gender_yearly;
    
    // 性別標籤和顏色對應（傳統顏色：男藍、女紅）
    const genderConfig = {
        'M': { label: '男性', color: '#0093d5' },  // 男性：藍色
        'F': { label: '女性', color: '#e63946' },  // 女性：紅色
        'U': { label: '未知', color: '#6c757d' },  // 未知：灰色
        '男': { label: '男性', color: '#0093d5' },
        '女': { label: '女性', color: '#e63946' },
        '未知': { label: '未知', color: '#6c757d' }
    };
    
    const genders = [...new Set(data.map(d => d.性別))];
    const years = [...new Set(data.map(d => d.發病年.toString()))].sort();
    
    // 確保順序：男性、女性、未知
    const genderOrder = ['M', 'F', 'U', '男', '女', '未知'];
    const sortedGenders = [];
    genderOrder.forEach(key => {
        if (genders.includes(key)) {
            sortedGenders.push(key);
        }
    });
    // 加入其他未排序的性別
    genders.forEach(gender => {
        if (!genderOrder.includes(gender)) {
            sortedGenders.push(gender);
        }
    });
    
    const datasets = sortedGenders.map((gender) => {
        const config = genderConfig[gender] || { label: gender, color: '#6c757d' };
        return {
            label: config.label,
            data: years.map(year => {
                const item = data.find(d => d.性別 === gender && d.發病年.toString() === year);
                return item ? item.病例數 : 0;
            }),
            borderColor: config.color,
            backgroundColor: config.color + '40',
            borderWidth: 2,
            fill: false,
            tension: 0.4
        };
    });
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: years,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '登革熱病例性別年度趨勢',
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

// 境外移入狀態圖
function renderImportStatusChart() {
    const ctx = document.getElementById('importStatusChart').getContext('2d');
    const data = analysisData.person.import_status;
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.map(d => d.是否境外移入 === '是' ? '境外移入' : '本土病例'),
            datasets: [{
                data: data.map(d => d.病例數),
                backgroundColor: ['#e63946', '#00a651'],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '登革熱病例來源分布',
                    font: { size: 16, weight: 'bold' }
                },
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// 境外移入年度趨勢
function renderImportYearlyChart() {
    const ctx = document.getElementById('importYearlyChart').getContext('2d');
    const data = analysisData.person.import_yearly;
    
    const statuses = [...new Set(data.map(d => d.是否境外移入))];
    const years = [...new Set(data.map(d => d.發病年.toString()))].sort();
    
    const datasets = statuses.map((status, index) => {
        const colors = ['#00a651', '#e63946'];
        return {
            label: status === '是' ? '境外移入' : '本土病例',
            data: years.map(year => {
                const item = data.find(d => d.是否境外移入 === status && d.發病年.toString() === year);
                return item ? item.病例數 : 0;
            }),
            borderColor: colors[index % colors.length],
            backgroundColor: colors[index % colors.length] + '40',
            borderWidth: 2,
            fill: false,
            tension: 0.4
        };
    });
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: years,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '登革熱病例來源年度趨勢',
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

// 格式化數字（千分位）
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

