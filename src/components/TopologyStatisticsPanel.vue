<template>
    <div class="statistics-panel">
        <div class="panel-header">
            <h2>Topology Calculation Report</h2>
            <button class="close-btn" @click="$emit('close')">×</button>
        </div>
        
        <div class="panel-content">
            <!-- 添加计算类型选择器 -->
            <div class="calculation-type-selector">
                <h3>Calculation Type</h3>
                <el-select v-model="calculationType" @change="handleCalculationTypeChange">
                    <el-option
                        v-for="type in calculationTypes"
                        :key="type.value"
                        :label="type.label"
                        :value="type.value"
                    />
                </el-select>
            </div>

            <!-- 时间选择器（仅在 dynamic 模式下显示） -->
            <div v-if="calculationType === 'dynamic'" class="time-selector">
                <h3>Time Point Selection</h3>
                <el-select v-model="selectedTimePoint" @change="handleTimePointChange">
                    <el-option
                        v-for="time in timePoints"
                        :key="time"
                        :label="`Time: ${time}`"
                        :value="time"
                    />
                </el-select>
            </div>

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
                    <!-- <p>Network Area: {{ basicStats.networkArea.toFixed(2) }} km²</p>
                    <p>Network Density: {{ basicStats.networkDensity.toFixed(2) }} m/km²</p> -->
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
import { ref, onMounted, computed, watch, nextTick, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import axios from '@/utils/axios'
import { ElMessage } from 'element-plus'
import { useTopologyStore } from '@/stores/topology'
import { storeToRefs } from 'pinia'

const props = defineProps({
    type: {
        type: String,
        required: true
    },
    projectId: {
        type: String,
        required: true
    },
    radius: {
        type: Number,
        required: true
    }
})

const emit = defineEmits(['close', 'topology-result', 'time-point-changed'])

const topologyStore = useTopologyStore()
const { currentRadius } = storeToRefs(topologyStore)

const mcScatterChart = ref(null)
const histogramChart = ref(null)
let mcChartInstance = null  // 添加图表实例引用
let histogramChartInstance = null  // 添加图表实例引用
const isComponentMounted = ref(false)  // 添加组件挂载状态标志

const selectedTimePoint = ref(null)
const timePoints = ref([])

// 添加计算类型相关的响应式变量
const calculationType = ref(props.type)
const availableTypes = ref(new Set([props.type]))

// 添加一个 watch 来调试
watch(() => props.radius, (newRadius) => {
    console.log('Radius changed:', newRadius)
})

// 计算 MC 字段名
const mcField = computed(() => {
    console.log('TopologyStatisticsPanel: Using radius:', currentRadius.value)
    return `MC_${currentRadius.value}`
})

const calculationTypes = computed(() => {
    const types = []
    if (availableTypes.value.has('static')) {
        types.push({ label: 'Static Analysis', value: 'static' })
    }
    if (availableTypes.value.has('dynamic')) {
        types.push({ label: 'Dynamic Analysis', value: 'dynamic' })
    }
    return types
})

const basicStats = ref({
    diameter: (Math.random() * 10).toFixed(2),
    radius: (Math.random() * 5).toFixed(2),
    avgPathLength: (Math.random() * 15).toFixed(2),
    totalRoads: 0,
    networkArea: 0,
    networkDensity: 0
})

const calculateNetworkStats = (geojsonData) => {
    console.log('Calculating network stats...');
    // 计算道路总数
    const totalRoads = geojsonData.features.length
    console.log('Total roads:', totalRoads);

    // 计算边界框
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity
    let totalLength = 0

    geojsonData.features.forEach(feature => {
        if (!feature.geometry || !feature.geometry.coordinates) {
            console.warn('Invalid feature:', feature);
            return;
        }
        
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
    console.log('Calculating area...');
    console.log('maxX:', maxX, 'minX:', minX, 'maxY:', maxY, 'minY:', minY);
    const area = ((maxX - minX) * (maxY - minY)) / 1000000
    
    
    // 计算密度（公里/平方公里）
    const density = (totalLength / 1000) / area

    console.log('New stats:', {
        totalRoads,
        networkArea: area,
        networkDensity: density
    });

    // 使用 Vue 的响应式更新
    basicStats.value = {
        ...basicStats.value,
        totalRoads,
        networkArea: area,
        networkDensity: density
    }
}

const updateMCScatterChart = (geojsonData) => {
    if (!isComponentMounted.value || !mcScatterChart.value || !geojsonData?.features) {
        console.log('Skipping MC chart update - component not ready');
        return;
    }
    
    try {
        // 销毁旧实例
        if (mcChartInstance) {
            mcChartInstance.dispose()
        }
        
        // 创建新实例
        mcChartInstance = echarts.init(mcScatterChart.value)
        const mcValues = geojsonData.features.map(feature => ({
            value: [feature.properties.CurveId, feature.properties[mcField.value]]
        }))

        mcChartInstance.setOption({
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
    } catch (error) {
        console.error('Error updating MC scatter chart:', error)
    }
}

const updateHistogram = (geojsonData) => {
    if (!isComponentMounted.value || !histogramChart.value || !geojsonData?.features) {
        console.log('Skipping histogram update - component not ready');
        return;
    }
    
    try {
        // 销毁旧实例
        if (histogramChartInstance) {
            histogramChartInstance.dispose()
        }
        
        // 创建新实例
        histogramChartInstance = echarts.init(histogramChart.value)
        
        // 获取所有MC值，使用动态字段名
        const mcValues = geojsonData.features.map(feature => feature.properties[mcField.value])
        
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

        histogramChartInstance.setOption({
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
    } catch (error) {
        console.error('Error updating histogram:', error)
    }
}

const loadTimePoints = async () => {
    try {
        console.log('Loading time points for project:', props.projectId)
        const response = await axios.get('/api/topology/dynamic_networks', {
            params: { project_id: props.projectId }
        })
        if (response.data.status === 'success') {
            timePoints.value = response.data.timePoints
            console.log('Loaded time points:', timePoints.value)
            if (timePoints.value.length > 0) {
                selectedTimePoint.value = timePoints.value[0]
                await loadGeojsonData()
            }
        }
    } catch (error) {
        console.error('Error loading time points:', error)
        ElMessage.error('Failed to load time points')
    }
}


const loadGeojsonData = async () => {
    try {
        const url = calculationType.value === 'dynamic' 
            ? '/api/topology/network_at_time'
            : '/api/topology/network'
            
        const params = {
            project_id: props.projectId,
            ...(calculationType.value === 'dynamic' && { time: selectedTimePoint.value })
        }
        
        const response = await axios.get(url, { params })
        if (response.data) {
            const geojsonData = response.data
            calculateNetworkStats(geojsonData)
            updateMCScatterChart(geojsonData)
            updateHistogram(geojsonData)
            emit('topology-result', geojsonData)
        }
    } catch (error) {
        console.error('Error loading data:', error)
        ElMessage.error('Failed to load network data')
    }
}

// 处理时间点变化
const handleTimePointChange = async () => {
    await loadGeojsonData()
}

// 修改 updateData 方法
const updateData = async (geojsonData) => {
    if (!isComponentMounted.value) {
        console.log('Component not mounted, skipping update');
        return;
    }

    if (!geojsonData?.features) {
        console.warn('Invalid geojson data received');
        return;
    }
    
    console.log('TopologyStatisticsPanel updating with new data, features count:', geojsonData.features.length);
    
    // 更新统计信息
    calculateNetworkStats(geojsonData);
    
    // 使用 nextTick 确保 DOM 更新完成
    await nextTick()
    try {
        updateMCScatterChart(geojsonData);
        updateHistogram(geojsonData);
    } catch (error) {
        console.error('Error updating charts:', error)
    }
}

// 修改 enableCalculationType 函数
const enableCalculationType = async (type) => {
    availableTypes.value.add(type)
    calculationType.value = type
    
    // 如果是动态模式，立即加载时间点
    if (type === 'dynamic') {
        await loadTimePoints()
    }
}

// 修改 handleCalculationTypeChange
const handleCalculationTypeChange = async (newType) => {
    console.log('Calculation type changed to:', newType)
    calculationType.value = newType
    
    if (newType === 'dynamic') {
        if (!timePoints.value.length) {
            await loadTimePoints()
        }
    } else {
        await loadGeojsonData()
    }
}

// 监听初始类型
watch(() => props.type, (newType) => {
    if (newType) {
        enableCalculationType(newType)
    }
}, { immediate: true });

// 修改 onMounted 钩子
onMounted(async () => {
    console.log('Component mounted');
    isComponentMounted.value = true
    await nextTick()
    
    try {
        if (props.type === 'dynamic') {
            await loadTimePoints()
        } else {
            await loadGeojsonData()
        }
    } catch (error) {
        console.error('Error in onMounted:', error)
    }
})

// 添加 onUnmounted 钩子
onUnmounted(() => {
    console.log('Component unmounting');
    isComponentMounted.value = false
    
    // 清理图表实例
    if (mcChartInstance) {
        mcChartInstance.dispose()
        mcChartInstance = null
    }
    if (histogramChartInstance) {
        histogramChartInstance.dispose()
        histogramChartInstance = null
    }
})

// 添加 updateTimePoints 方法
const updateTimePoints = (points) => {
    if (!points || !Array.isArray(points)) {
        console.warn('Invalid time points data received');
        return;
    }
    
    console.log('Updating time points:', points);
    timePoints.value = points;
    
    if (points.length > 0) {
        selectedTimePoint.value = points[0];
        // 加载第一个时间点的数据
        loadGeojsonData();
    }
};

// 确保所有方法都被正确暴露
defineExpose({
    updateData,
    enableCalculationType,
    updateTimePoints
});
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

.time-selector {
    margin-bottom: 20px;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;
}

.time-selector h3 {
    margin-bottom: 10px;
}

.calculation-type-selector {
    margin-bottom: 20px;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;
}

.calculation-type-selector h3 {
    margin-bottom: 10px;
}
</style> 