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
        
        const response = await fetch(`/api/data/${countyCode}`);
        console.log('API 回應狀態:', response.status);
        console.log('API URL:', `/api/data/${countyCode}`);
        
        if (!response.ok) {
            throw new Error(`無法載入資料: ${response.status}`);
        }
        
        analysisData = await response.json();
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
    renderCountyMap();
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

// 縣市地圖視覺化（顯示該縣市內各行政區）
function renderCountyMap() {
    const mapElement = document.getElementById('countyMap');
    if (!mapElement) {
        console.log('找不到地圖元素，跳過地圖渲染');
        return;
    }
    
    console.log('開始渲染縣市地圖...', COUNTY_NAME);
    
    const townshipData = analysisData.location?.township || analysisData.location?.township_top30 || [];
    if (townshipData.length === 0) {
        console.log('沒有行政區資料，跳過地圖渲染');
        mapElement.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 100%; background: #f0f0f0; border-radius: 4px;">
                <div style="text-align: center; padding: 20px;">
                    <p style="font-size: 16px; color: #666;">暫無行政區地圖資料</p>
                </div>
            </div>
        `;
        return;
    }
    
    // 建立行政區病例數對應表
    const casesMap = {};
    const districtNames = [];
    const casesValues = [];
    
    townshipData.forEach(item => {
        const districtName = item.居住鄉鎮 || item.鄉鎮 || item.行政區;
        if (!districtName || districtName === '未知') return;
        casesMap[districtName] = item.病例數;
        districtNames.push(districtName);
        casesValues.push(item.病例數);
    });
    
    const maxCases = Math.max(...casesValues, 1);
    
    console.log('行政區病例數對應表:', casesMap);
    console.log('行政區數量:', districtNames.length);
    
    // 根據縣市載入對應的 GeoJSON
    // 優先使用本地檔案（通過 Flask 路由），然後嘗試線上來源
    const geoJsonUrls = {
        '高雄市': [
            // 本地檔案（優先，通過 Flask 路由）
            '/static/data/taiwan_township.geojson', // 優先：直接使用鄉鎮檔案
            '/static/data/TOWN_MOI_1090415.json',  // 備用：全台鄉鎮市區（會自動過濾）
            '/static/data/kaohsiung_districts.geojson',
            // 線上來源（備用，可能無法訪問）
            'https://raw.githubusercontent.com/kiang/pharmacies/master/json/geo/64000.json',
            'https://raw.githubusercontent.com/g0v/twgeojson/master/json/town/64000.json'
        ],
        '台南市': [
            // 本地檔案（優先，通過 Flask 路由）
            '/static/data/taiwan_township.geojson', // 優先：直接使用鄉鎮檔案
            '/static/data/TOWN_MOI_1090415.json',  // 備用：全台鄉鎮市區（會自動過濾）
            '/static/data/tainan_districts.geojson',
            // 線上來源（備用，可能無法訪問）
            'https://raw.githubusercontent.com/kiang/pharmacies/master/json/geo/63000.json',
            'https://raw.githubusercontent.com/g0v/twgeojson/master/json/town/63000.json'
        ]
    };
    
    const urls = geoJsonUrls[COUNTY_NAME] || [];
    
    async function loadGeoJSON() {
        for (const url of urls) {
            try {
                console.log(`嘗試載入: ${url}`);
                const response = await fetch(url);
                if (response.ok) {
                    const geoJson = await response.json();
                    console.log('GeoJSON 載入成功');
                    if (geoJson.features && geoJson.features.length > 0) {
                        return geoJson;
                    }
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
            console.error('無法載入任何 GeoJSON 檔案');
            mapElement.innerHTML = `
                <div style="display: flex; align-items: center; justify-content: center; height: 100%; background: #f0f0f0; border-radius: 4px;">
                    <div style="text-align: center; padding: 20px; max-width: 600px;">
                        <p style="font-size: 16px; color: #666; font-weight: bold; margin-bottom: 10px;">無法載入地圖資料</p>
                        <p style="font-size: 14px; color: #999; margin-bottom: 15px;">請查看下方行政區統計表格以查看資料</p>
                        <div style="background: #fff; padding: 15px; border-radius: 4px; border: 1px solid #ddd; margin-top: 15px;">
                            <p style="font-size: 13px; color: #666; margin-bottom: 10px;"><strong>如何啟用地圖功能：</strong></p>
                            <ol style="text-align: left; font-size: 12px; color: #666; padding-left: 20px; margin: 0;">
                                <li>前往 <a href="https://data.gov.tw/dataset/7442" target="_blank" style="color: #0093d5;">政府資料開放平台</a></li>
                                <li>下載「TOWN_MOI_1090415.json」檔案</li>
                                <li>將檔案放置於：<code style="background: #f5f5f5; padding: 2px 6px; border-radius: 3px;">website/static/data/</code></li>
                                <li>重新整理頁面即可顯示地圖</li>
                            </ol>
                        </div>
                    </div>
                </div>
            `;
            return;
        }
        
        // 找出 GeoJSON 中使用的行政區名稱屬性和縣市屬性
        // 政府開放資料（TOWN_MOI）通常使用：TOWNNAME（鄉鎮名）、COUNTYNAME（縣市名）
        const firstFeature = geoJson.features[0];
        const firstProps = firstFeature.properties;
        let districtKey = null;
        let countyKey = null;
        
        // 政府開放資料的屬性名稱（優先）
        const possibleDistrictKeys = [
            'TOWNNAME',      // 政府開放資料標準格式
            'TOWN', 
            'name', 
            '鄉鎮', 
            '行政區', 
            'NAME_2014', 
            'TOWNNAME_2014',
            'TOWNNAME_109'   // 109年版本
        ];
        for (const key of possibleDistrictKeys) {
            if (firstProps[key]) {
                districtKey = key;
                break;
            }
        }
        
        // 政府開放資料的縣市屬性名稱（優先）
        const possibleCountyKeys = [
            'COUNTYNAME',    // 政府開放資料標準格式
            'COUNTY', 
            '縣市', 
            'COUNTY_2014',
            'COUNTYNAME_109' // 109年版本
        ];
        for (const key of possibleCountyKeys) {
            if (firstProps[key]) {
                countyKey = key;
                break;
            }
        }
        
        console.log('找到的屬性鍵:', { districtKey, countyKey });
        console.log('第一個 feature 的屬性:', firstProps);
        
        if (!districtKey) {
            console.error('找不到行政區名稱屬性');
            return;
        }
        
        // 準備 Plotly 資料
        const locations = [];
        const z = [];
        const text = [];
        const locationNames = [];  // 用於匹配的行政區名稱
        
        // 目標縣市名稱（用於過濾）
        // 政府開放資料中，縣市名稱可能是「高雄市」或「高雄」，且可能使用「臺」而非「台」
        const targetCounty = COUNTY_NAME.replace('市', '').replace('縣', '');
        const targetCountyFull = COUNTY_NAME;
        
        // 處理「台」vs「臺」的差異
        const targetCountyWithTai = COUNTY_NAME.replace('台', '臺');
        const targetCountyWithTaiClean = targetCountyWithTai.replace('市', '').replace('縣', '');
        
        const targetCountyVariants = [
            COUNTY_NAME,                    // 完整名稱：高雄市、台南市
            targetCounty,                   // 簡稱：高雄、台南
            targetCountyWithTai,            // 變體：高雄市、臺南市（使用「臺」）
            targetCountyWithTaiClean,       // 變體：高雄、臺南（使用「臺」）
            COUNTY_NAME.replace('市', '縣'), // 變體：高雄縣、台南縣（雖然已改制）
            targetCountyWithTai.replace('市', '縣'), // 變體：高雄縣、臺南縣
        ];
        
        console.log('目標縣市變體:', targetCountyVariants);
        
        geoJson.features.forEach(feature => {
            const props = feature.properties;
            
            // 檢查是否屬於該縣市
            if (countyKey) {
                const featureCounty = props[countyKey];
                if (featureCounty) {
                    const featureCountyClean = featureCounty.replace('市', '').replace('縣', '');
                    // 檢查是否匹配任何目標縣市變體
                    const isMatch = targetCountyVariants.some(variant => {
                        const variantClean = variant.replace('市', '').replace('縣', '');
                        return featureCounty === variant || 
                               featureCounty.includes(variant) || 
                               variant.includes(featureCounty) ||
                               featureCountyClean === variantClean ||
                               featureCountyClean.includes(variantClean) ||
                               variantClean.includes(featureCountyClean);
                    });
                    
                    if (!isMatch) {
                        return; // 跳過不屬於該縣市的行政區
                    }
                }
            }
            
            const districtName = props[districtKey];
            if (!districtName) return;
            
            // 移除可能的後綴（如「區」、「鄉」、「鎮」、「市」）
            const cleanDistrictName = districtName.replace(/[區鄉鎮市]$/, '');
            
            let matchedName = districtName;
            let cases = casesMap[districtName];
            
            // 嘗試直接匹配
            if (cases === undefined) {
                cases = casesMap[cleanDistrictName];
                if (cases !== undefined) {
                    matchedName = cleanDistrictName;
                }
            }
            
            // 嘗試模糊匹配
            if (cases === undefined) {
                for (const [key, value] of Object.entries(casesMap)) {
                    const cleanKey = key.replace(/[區鄉鎮市]$/, '');
                    if (districtName === key || 
                        districtName.includes(key) || 
                        key.includes(districtName) ||
                        cleanDistrictName === cleanKey ||
                        cleanDistrictName.includes(cleanKey) ||
                        cleanKey.includes(cleanDistrictName)) {
                        matchedName = key;
                        cases = value;
                        break;
                    }
                }
            }
            
            if (cases === undefined) cases = 0;
            
            locations.push(feature);
            locationNames.push(districtName);  // 使用原始行政區名稱
            z.push(cases);
            text.push(`${matchedName || districtName}<br>病例數: ${cases.toLocaleString()}`);
        });
        
        console.log('過濾後的行政區數量:', locations.length);
        console.log('病例數範圍:', Math.min(...z, 0), '到', Math.max(...z, 0));
        
        if (locations.length === 0) {
            console.error('過濾後沒有找到任何行政區！');
            mapElement.innerHTML = `
                <div style="display: flex; align-items: center; justify-content: center; height: 100%; background: #f0f0f0; border-radius: 4px;">
                    <div style="text-align: center; padding: 20px;">
                        <p style="font-size: 16px; color: #666;">找不到 ${COUNTY_NAME} 的行政區資料</p>
                        <p style="font-size: 14px; color: #999; margin-top: 10px;">請檢查 GeoJSON 檔案中的縣市名稱是否正確</p>
                        <p style="font-size: 12px; color: #999; margin-top: 5px;">找到的屬性鍵: ${districtKey}, ${countyKey}</p>
                    </div>
                </div>
            `;
            return;
        }
        
        // === 使用實際座標計算邊界與容器高度 ===
        const mapContainer = mapElement;
        const containerWidth = mapContainer ? mapContainer.offsetWidth : 1095;
        
        let minLat = Infinity, maxLat = -Infinity;
        let minLon = Infinity, maxLon = -Infinity;
        let coordinateCount = 0;
        const LAT_MIN_LIMIT = 20;
        const LAT_MAX_LIMIT = 25;
        const LON_MIN_LIMIT = 118;
        const LON_MAX_LIMIT = 123;
        
        function extractCoordinates(coords) {
            if (!Array.isArray(coords)) return;
            if (coords.length === 2 && typeof coords[0] === 'number' && typeof coords[1] === 'number') {
                const [lon, lat] = coords;
                if (
                    Number.isFinite(lon) && Number.isFinite(lat) &&
                    lat >= LAT_MIN_LIMIT && lat <= LAT_MAX_LIMIT &&
                    lon >= LON_MIN_LIMIT && lon <= LON_MAX_LIMIT
                ) {
                    minLon = Math.min(minLon, lon);
                    maxLon = Math.max(maxLon, lon);
                    minLat = Math.min(minLat, lat);
                    maxLat = Math.max(maxLat, lat);
                    coordinateCount += 1;
                }
                return;
            }
            coords.forEach(item => {
                if (Array.isArray(item)) extractCoordinates(item);
            });
        }
        
        locations.forEach(feature => {
            const geometry = feature.geometry;
            if (geometry && geometry.coordinates) {
                extractCoordinates(geometry.coordinates);
            }
        });
        
        console.log('邊界計算結果（排除離島）:', {
            coordinateCount,
            minLon: Number.isFinite(minLon) ? minLon.toFixed(6) : 'N/A',
            maxLon: Number.isFinite(maxLon) ? maxLon.toFixed(6) : 'N/A',
            minLat: Number.isFinite(minLat) ? minLat.toFixed(6) : 'N/A',
            maxLat: Number.isFinite(maxLat) ? maxLat.toFixed(6) : 'N/A'
        });
        
        if (!Number.isFinite(minLat) || !Number.isFinite(maxLat) ||
            !Number.isFinite(minLon) || !Number.isFinite(maxLon)
        ) {
            console.warn('無法從 GeoJSON 中計算邊界，使用預設值');
            if (COUNTY_NAME === '台南市' || COUNTY_NAME === '臺南市') {
                minLat = 22.7;
                maxLat = 23.3;
                minLon = 119.9;
                maxLon = 120.5;
            } else {
                minLat = 22.3;
                maxLat = 22.9;
                minLon = 120.0;
                maxLon = 120.6;
            }
        }
        
        // 根據南北距離設定容器高度（1 度 ≈ 1000px）
        let latSpan = Math.max(maxLat - minLat, 0.1);
        const pixelsPerDegree = 800;
        let targetHeight = Math.min(Math.max(latSpan * pixelsPerDegree, 360), 800);
        if (mapContainer) {
            mapContainer.style.height = `${targetHeight}px`;
        }
        const containerHeight = targetHeight;
        const containerDiagonal = Math.sqrt(containerWidth * containerWidth + containerHeight * containerHeight);
        const containerAspectRatio = containerWidth / containerHeight;
        
        // 依據容器比例計算經度範圍
        const targetLonSpan = latSpan * containerAspectRatio;
        let centerLon = (minLon + maxLon) / 2;
        let centerLat = (minLat + maxLat) / 2;
        minLon = centerLon - targetLonSpan / 2;
        maxLon = centerLon + targetLonSpan / 2;
        
        // 台南市微調（視覺置中）
        if (COUNTY_NAME === '台南市' || COUNTY_NAME === '臺南市') {
            centerLon -= 0.03;
            centerLat -= 0.02;
            minLon = centerLon - targetLonSpan / 2;
            maxLon = centerLon + targetLonSpan / 2;
        }
        
        // 添加少量邊距（3%）
        const lonSpan = maxLon - minLon;
        const padding = 0.03;
        const lonRange = [
            minLon - lonSpan * padding,
            maxLon + lonSpan * padding
        ];
        const latRange = [
            minLat - latSpan * padding,
            maxLat + latSpan * padding
        ];
        
        console.log('計算的地圖邊界（基於容器比例）:', {
            container: { 
                width: containerWidth, 
                height: containerHeight, 
                aspectRatio: containerAspectRatio.toFixed(3)
            },
            countyRange: { 
                minLat: minLat.toFixed(6), 
                maxLat: maxLat.toFixed(6), 
                latSpan: latSpan.toFixed(6),
                centerLon: centerLon.toFixed(6),
                targetLonSpan: targetLonSpan.toFixed(6)
            },
            finalRange: { 
                lonRange: lonRange.map(v => v.toFixed(6)), 
                latRange: latRange.map(v => v.toFixed(6))
            },
            center: { 
                lon: centerLon.toFixed(6), 
                lat: centerLat.toFixed(6) 
            }
        });
        
        // 過濾 GeoJSON，只保留該縣市的行政區
        const filteredGeoJson = {
            type: 'FeatureCollection',
            features: locations
        };
        
        console.log('Plotly 資料準備:', {
            featuresCount: filteredGeoJson.features.length,
            locationsCount: locationNames.length,
            zValuesCount: z.length,
            districtKey: districtKey,
            sampleFeature: filteredGeoJson.features[0]?.properties,
            sampleLocationName: locationNames[0],
            centerLat: centerLat,
            centerLon: centerLon,
            lonRange: lonRange,
            latRange: latRange
        });
        
        const data = [{
            type: 'choropleth',
            geojson: filteredGeoJson,
            locations: locationNames,  // 使用行政區名稱，而不是索引
            z: z,
            text: text,
            featureidkey: `properties.${districtKey}`,  // 指定匹配的屬性鍵
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
                // 使用計算出的範圍，確保地圖放大到最大可視範圍
                center: {
                    lon: centerLon,
                    lat: centerLat
                },
                lonaxis: {
                    range: lonRange
                },
                lataxis: {
                    range: latRange
                }
            },
            margin: { t: 0, b: 0, l: 0, r: 100 },
            height: 600,
            autosize: true,
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)'
        };
        
        const config = {
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
        };
        
        console.log('準備繪製地圖，資料點數量:', locations.length);
        console.log('地圖配置:', { centerLat, centerLon, maxCases });
        
        try {
            // 確保地圖容器存在且可見
            const mapContainer = document.getElementById('countyMap');
            if (mapContainer) {
                mapContainer.style.display = 'block';
                mapContainer.style.visibility = 'visible';
                mapContainer.style.width = '100%';
                mapContainer.style.height = '600px';
                console.log('地圖容器狀態:', {
                    display: mapContainer.style.display,
                    visibility: mapContainer.style.visibility,
                    width: mapContainer.offsetWidth,
                    height: mapContainer.offsetHeight
                });
            }
            
            Plotly.newPlot('countyMap', data, layout, config).then(() => {
                console.log('✅ 縣市地圖繪製完成');
                // 再次確保地圖容器可見
                if (mapContainer) {
                    mapContainer.style.display = 'block';
                    mapContainer.style.visibility = 'visible';
                    // 強制重新渲染
                    Plotly.Plots.resize('countyMap');
                }
            }).catch(err => {
                console.error('Plotly 繪圖 Promise 錯誤:', err);
            });
            
            window.addEventListener('resize', function() {
                Plotly.Plots.resize('countyMap');
            });
        } catch (error) {
            console.error('❌ Plotly 繪圖錯誤:', error);
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
    });
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
    
    // 反轉資料順序以實現逆時針方向繪製
    const reversedData = [...sortedGenderData].reverse();
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: reversedData.map(d => d.label),
            datasets: [{
                data: reversedData.map(d => d.病例數),
                backgroundColor: reversedData.map(d => d.color)
            }]
        },
        options: {
            rotation: 0, // 從上方開始（-90度 = 12點鐘方向）
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: `${COUNTY_NAME}性別分布`,
                    font: { size: 16, weight: 'bold' }
                },
                legend: {
                    position: 'bottom',
                    labels: {
                        // 反轉圖例順序，恢復到原始順序（男性、女性、未知）
                        generateLabels: function(chart) {
                            const data = chart.data;
                            if (data.labels.length && data.datasets.length) {
                                // 先按照資料順序生成圖例
                                const labels = data.labels.map((label, i) => {
                                    const dataset = data.datasets[0];
                                    return {
                                        text: label,
                                        fillStyle: dataset.backgroundColor[i],
                                        hidden: false,
                                        index: i
                                    };
                                });
                                // 反轉圖例順序，恢復到原始順序
                                return labels.reverse();
                            }
                            return [];
                        },
                        // 確保圖例按照反轉後的順序排序
                        sort: function(a, b) {
                            return b.index - a.index; // 反轉排序
                        }
                    }
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
    
    // 固定年齡層排序（與後端保持一致，使用 '70+' 表示所有70歲以上）
    const ageOrder = ['0-4', '5-9', '10-14', '15-19', '20-24', '25-29', '30-34', 
                      '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', 
                      '65-69', '70+', '未知'];
    
    const sortedAgeData = ageOrder.map(age => {
        const item = ageData.find(d => d.年齡層 === age);
        return item || { 年齡層: age, 病例數: 0 };
    }).filter(d => d.病例數 > 0 || d.年齡層 === '未知'); // 只顯示有資料的年齡層
    
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

