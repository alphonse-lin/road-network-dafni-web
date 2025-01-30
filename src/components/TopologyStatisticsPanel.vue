<template>
    <div class="statistics-panel">
        <div class="panel-header">
            <h2>Topology Calculation Report</h2>
            <button class="close-btn" @click="$emit('close')">×</button>
        </div>
        
        <div class="panel-content">
            <!-- 基础信息部分 -->
            <div class="basic-info">
                <h3>Basic Information</h3>
                <div class="parameters">
                    <h4>Parameters:</h4>
                    <p>Network interpolation directed</p>
                </div>

                <div class="results">
                    <h4>Results:</h4>
                    <p>Network Statistics:</p>
                    <p>Total Roads: {{ basicStats.totalRoads }}</p>
                    <p>Network Area: {{ basicStats.networkArea.toFixed(2) }} km²</p>
                    <p>Network Density: {{ basicStats.networkDensity.toFixed(2) }} km/km²</p>
                    <!-- <p>Diameter: {{ basicStats.diameter }}</p>
                    <p>Radius: {{ basicStats.radius }}</p>
                    <p>Average Path length: {{ basicStats.avgPathLength }}</p> -->
                </div>
            </div>

            <!-- 特定统计信息部分 -->
            <div class="specific-stats">
                <div class="stats-header">
                    <h3>Detailed Statistics</h3>
                </div>

                <div class="charts">
                    <div class="chart-container">
                        <h4>Betweenness Value Distribution</h4>
                        <div ref="mcScatterChart" style="height: 200px;"></div>
                    </div>
                    <div class="chart-container">
                        <h4>Betweenness Histogram</h4>
                        <div ref="histogramChart" style="height: 200px;"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const props = defineProps({
    type: {
        type: String,
        required: true
    },
    hasDynamicData: {
        type: Boolean,
        default: false
    },
    projectId: {
        type: String,
        required: true
    }
})

const emit = defineEmits(['close', 'geojsonUpdated', 'topology-result'])

const mcScatterChart = ref(null)
const histogramChart = ref(null)

const basicStats = ref({
    diameter: (Math.random() * 10).toFixed(2),
    radius: (Math.random() * 5).toFixed(2),
    avgPathLength: (Math.random() * 15).toFixed(2),
    totalRoads: 0,
    networkArea: 0,
    networkDensity: 0
})

const calculateNetworkStats = (geojsonData) => {
    // 计算道路总数
    const totalRoads = geojsonData.features.length

    // 计算边界框
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity
    let totalLength = 0

    geojsonData.features.forEach(feature => {
        const coords = feature.geometry.coordinates
        coords.forEach(coord => {
            minX = Math.min(minX, coord[0])
            maxX = Math.max(maxX, coord[0])
            minY = Math.min(minY, coord[1])
            maxY = Math.max(maxY, coord[1])
            
            // 如果有下一个坐标点，计算线段长度
            if (coords[coords.indexOf(coord) + 1]) {
                const nextCoord = coords[coords.indexOf(coord) + 1]
                const dx = nextCoord[0] - coord[0]
                const dy = nextCoord[1] - coord[1]
                totalLength += Math.sqrt(dx * dx + dy * dy)
            }
        })
    })

    // 计算面积（平方米转换为平方公里）
    const area = ((maxX - minX) * (maxY - minY)) / 1000000
    
    // 计算密度（公里/平方公里）
    const density = (totalLength / 1000) / area

    basicStats.value = {
        ...basicStats.value,
        totalRoads,
        networkArea: area,
        networkDensity: density
    }
}

const updateMCScatterChart = (geojsonData) => {
    if (!mcScatterChart.value) return
    
    const mcValues = geojsonData.features.map(feature => ({
        value: [feature.properties.CurveId, feature.properties.MC_100]
    }))

    const chart = echarts.init(mcScatterChart.value)
    chart.setOption({
        grid: {
            top: 30,
            right: 20,
            bottom: 30,
            left: 50
        },
        tooltip: {
            trigger: 'item',
            formatter: function(params) {
                return `Road ID: ${params.value[0]}<br/>Betweenness: ${params.value[1]}`
            }
        },
        xAxis: {
            type: 'value',
            name: 'Road ID'
        },
        yAxis: {
            type: 'value',
            name: 'Betweenness'
        },
        series: [{
            data: mcValues,
            type: 'scatter',
            symbolSize: 5,
            itemStyle: {
                color: '#5470C6'
            }
        }]
    })
}

const updateHistogram = (geojsonData) => {
    if (!histogramChart.value) return

    // 获取所有MC值
    const mcValues = geojsonData.features.map(feature => feature.properties.MC_100)
    
    // 计算直方图数据
    const binCount = 20  // 直方图柱子数量
    const minValue = Math.min(...mcValues)
    const maxValue = Math.max(...mcValues)
    const binWidth = (maxValue - minValue) / binCount
    
    // 初始化bins
    const bins = new Array(binCount).fill(0)
    
    // 统计每个bin的数量
    mcValues.forEach(value => {
        const binIndex = Math.min(
            Math.floor((value - minValue) / binWidth),
            binCount - 1
        )
        bins[binIndex]++
    })
    
    // 生成x轴标签
    const xAxisData = bins.map((_, index) => {
        const binStart = (minValue + index * binWidth).toFixed(2)
        return binStart
    })

    const chart = echarts.init(histogramChart.value)
    chart.setOption({
        grid: {
            top: 30,
            right: 20,
            bottom: 30,
            left: 50
        },
        tooltip: {
            trigger: 'item',
            formatter: function(params) {
                const binStart = parseFloat(params.name)
                const binEnd = (binStart + binWidth).toFixed(2)
                return `Range: ${params.name} - ${binEnd}<br/>Count: ${params.value}`
            }
        },
        xAxis: {
            type: 'category',
            name: 'Betweenness',
            data: xAxisData,
            axisLabel: {
                rotate: 45,
                interval: Math.floor(binCount / 5)
            }
        },
        yAxis: {
            type: 'value',
            name: 'Frequency'
        },
        series: [{
            data: bins,
            type: 'bar',
            barWidth: '99%',
            itemStyle: {
                color: '#91cc75'
            }
        }]
    })
}

const loadGeojsonData = async () => {
    try {
        const projectId = props.projectId
        const url = `/api/topology/network?project_id=${projectId}`
        const response = await axios.get(url)
        
        if (response.data.status === 'error') {
            console.error('Server error:', response.data.message)
            ElMessage.error(response.data.message)
            emit('close')
            return
        }
        
        const geojsonData = response.data
        
        if (!geojsonData.features.some(f => 'MC_100' in f.properties)) {
            console.error('No MC_100 values found in the data')
            ElMessage.error('Topology calculation results not available')
            emit('close')
            return
        }

        calculateNetworkStats(geojsonData)
        updateMCScatterChart(geojsonData)
        updateHistogram(geojsonData)
        
        emit('topology-result', geojsonData)
        
    } catch (error) {
        console.error('Error loading data:', error)
        ElMessage.error(error.response?.data?.message || 'Failed to load data')
        emit('close')
    }
}

onMounted(() => {
    loadGeojsonData()
})
</script>

<style scoped>
.statistics-panel {
    position: fixed;
    right: 20px;
    top: 80px;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    padding: 20px;
    width: 400px;
    max-height: 80vh;
    overflow-y: auto;
    z-index: 1000;
}

.panel-header {
    position: relative;
    margin-bottom: 20px;
}

.panel-header h2 {
    margin: 0;
    font-size: 20px;
    color: #333;
}

.close-btn {
    position: absolute;
    top: 0;
    right: 0;
    background: none;
    border: none;
    font-size: 24px;
    color: #666;
    cursor: pointer;
    padding: 5px;
}

.basic-info, .specific-stats {
    margin-bottom: 30px;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;
}

.stats-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

h3 {
    margin: 0 0 15px;
    font-size: 18px;
    color: #333;
}

h4 {
    margin: 10px 0;
    font-size: 16px;
    color: #444;
}

p {
    margin: 5px 0;
    color: #666;
}

.chart-container {
    margin-bottom: 20px;
    padding: 10px;
    background: white;
    border-radius: 6px;
}
</style> 