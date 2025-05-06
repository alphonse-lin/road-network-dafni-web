<template>
    <div class="topology-panel">
        <div class="panel-header">
            <h2>Region</h2>
            <h3>King'sCross to Farringdon(25km²)</h3>
            <button class="close-btn" @click="$emit('close')">×</button>
        </div>
        
        <div class="panel-content">
            <div class="file-preview">
                <h4>File Preview</h4>
                <input
                    type="file"
                    ref="geojsonInput"
                    @change="handleGeojsonUpload"
                    style="display: none"
                    accept=".geojson"
                />
                <input
                    type="file"
                    ref="zipInput"
                    @change="handleZipUpload"
                    style="display: none"
                    accept=".zip"
                />
                <button @click="triggerFileUpload" class="upload-btn">
                    Upload Files
                </button>
                
                <div class="checkbox-group">
                    <div class="checkbox-with-info">
                        <el-checkbox v-model="hasRoadNetworks" disabled>
                            Road Networks
                        </el-checkbox>
                        <el-tooltip
                            content="Please import geojson file of road networks"
                            placement="right"
                        >
                            <el-icon class="info-icon"><InfoFilled /></el-icon>
                        </el-tooltip>
                    </div>
                    
                    <div class="checkbox-with-info">
                        <el-checkbox v-model="hasInundationMap" disabled>
                            Inundation Map
                        </el-checkbox>
                        <el-tooltip
                            content="Please import asc files as zip file"
                            placement="right"
                        >
                            <el-icon class="info-icon"><InfoFilled /></el-icon>
                        </el-tooltip>
                    </div>
                </div>
            </div>

            <div class="topology-calculation">
                <h4>Topology Calculation</h4>
                
                <div class="static-section">
                    <h5>• Static</h5>
                    <div class="topology-images">
                    <img src="@/assets/topology_1.jpg" alt="Topology 1" />
                </div>
                    <el-checkbox 
                        v-model="addMergedSegments"
                        :disabled="!hasRoadNetworks"
                    >
                        Add Merged Segments
                    </el-checkbox>
                    <el-checkbox 
                        v-model="includeRoadNetworks"
                        :disabled="!hasRoadNetworks"
                        checked
                    >
                        Road Networks
                    </el-checkbox>
                    <el-button 
                        type="primary" 
                        @click="handleStaticCalculation"
                        :disabled="!canCalculateStatic"
                        class="calculation-btn"
                    >
                        Calculation
                    </el-button>
                </div>

                <div class="dynamic-section">
                    <h5>• Dynamic</h5>
                    <div class="dynamic-images">
                        <img src="@/assets/topology_2.jpg" alt="Topology 2" />
                    </div>
                    <el-checkbox v-model="loadingInundationMap">Loading Inudation Map</el-checkbox>
                    <el-button 
                        type="primary" 
                        @click="handleDynamicCalculation"
                        :disabled="!canCalculateDynamic"
                        class="calculation-btn"
                    >
                        Calculation
                    </el-button>
                </div>
                <!-- <div>
                    <el-button class="simulation-btn" type="info">Simulation</el-button>
                </div> -->
                <div class="calculation-buttons">
                    <el-dropdown 
                        v-if="hasStaticResults || hasDynamicResults"
                        @command="handleViewResults"
                        trigger="click"
                    >
                        <el-button type="default" class="view-result-btn">
                            View Results
                            <el-icon class="el-icon--right"><arrow-down /></el-icon>
                        </el-button>
                        <template #dropdown>
                            <el-dropdown-menu>
                                <el-dropdown-item 
                                    command="static"
                                    :disabled="!hasStaticResults"
                                >
                                    Static Results
                                </el-dropdown-item>
                                <el-dropdown-item 
                                    command="dynamic"
                                    :disabled="!hasDynamicResults"
                                >
                                    Dynamic Results
                                </el-dropdown-item>
                            </el-dropdown-menu>
                        </template>
                    </el-dropdown>
                </div>
            </div>

            <!-- 添加进度弹窗组件 -->
            <CalculationProgress
                v-model:visible="showCalculationProgress"
                :project-id="projectId"
                :mode="calculationType"
                :title="calculationType === 'single' ? 'Static Calculation' : 'Dynamic Calculation'"
                @calculation-complete="handleCalculationComplete"
            />
        </div>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElButton, ElCheckbox, ElTooltip, ElMessage, ElDropdown, ElDropdownMenu, ElDropdownItem } from 'element-plus'
import { InfoFilled, ArrowDown } from '@element-plus/icons-vue'
import 'element-plus/es/components/button/style/css'
import 'element-plus/es/components/checkbox/style/css'
import 'element-plus/es/components/tooltip/style/css'
import 'element-plus/es/components/message/style/css'
// 引入 proj4 进行坐标转换
import proj4 from 'proj4'
import { v4 as uuidv4 } from 'uuid'
import axios from '@/utils/axios'
import CalculationProgress from './CalculationProgress.vue'

// 添加 projectId ref
const projectId = ref(null)

// 文件上传状态
const hasRoadNetworks = ref(false)  // 是否已上传道路网络文件
const hasInundationMap = ref(false)  // 是否已上传淹没图文件

// 计算选项
const addMergedSegments = ref(false)
const includeRoadNetworks = ref(true)  // 重命名为 includeRoadNetworks 以区分
const loadingInundationMap = ref(false)

// 文件上传相关
const geojsonInput = ref(null)
const zipInput = ref(null)
const geojsonFile = ref(null)
const zipFile = ref(null)

const emit = defineEmits(['close', 'showStatistics', 'updateGeojson', 'projectIdGenerated'])

// 添加状态
const showCalculationProgress = ref(false)
const calculationType = ref('single') // or 'sequence'

// 分别追踪静态和动态计算结果
const hasStaticResults = ref(false)
const hasDynamicResults = ref(false)

// 计算属性来控制按钮的启用状态
const canCalculateStatic = computed(() => {
    return hasRoadNetworks.value && addMergedSegments.value && includeRoadNetworks.value
})

const canCalculateDynamic = computed(() => {
    return loadingInundationMap.value
})

// 定义英国国家网格坐标系统
proj4.defs("EPSG:27700", "+proj=tmerc +lat_0=49 +lon_0=-2 +k=0.9996012717 +x_0=400000 +y_0=-100000 +ellps=airy +towgs84=446.448,-125.157,542.06,0.15,0.247,0.842,-20.489 +units=m +no_defs");

// 转换坐标的函数
const convertCoordinates = (coordinates) => {
    // 如果是多维数组（MultiLineString 或 Polygon），递归处理
    if (Array.isArray(coordinates[0])) {
        return coordinates.map(coord => convertCoordinates(coord));
    }
    // 转换单个坐标点
    const [x, y] = coordinates;
    const [lon, lat] = proj4('EPSG:27700', 'EPSG:4326', [x, y]);
    return [lon, lat];
};

const convertGeoJSON = (geojson) => {
    const converted = JSON.parse(JSON.stringify(geojson)); // 深拷贝

    const convertFeature = (feature) => {
        if (feature.geometry) {
            const coordinates = feature.geometry.coordinates;
            feature.geometry.coordinates = convertCoordinates(coordinates);
        }
        return feature;
    };

    if (converted.type === 'FeatureCollection') {
        converted.features = converted.features.map(convertFeature);
    } else if (converted.type === 'Feature') {
        convertFeature(converted);
    }

    return converted;
};

// 修改计算按钮的处理函数
const handleStaticCalculation = () => {
    calculationType.value = 'single'
    showCalculationProgress.value = true
}

const handleDynamicCalculation = () => {
    calculationType.value = 'sequence'
    showCalculationProgress.value = true
}

// // 修改 props 定义
// const props = defineProps({
//     projectId: {
//         type: String,
//         required: true
//     }
// })

const uploadFiles = async () => {
    try {
        projectId.value = uuidv4()
        
        // 通知父组件新生成的 projectId
        emit('projectIdGenerated', projectId.value)
        
        const formData = new FormData()
        formData.append('projectId', projectId.value)
        
        if (geojsonFile.value) {
            formData.append('geojson', geojsonFile.value)
        }
        if (zipFile.value) {
            formData.append('inundation', zipFile.value)
        }

        const response = await axios.post('/api/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        })

        if (response.data.success) {
            ElMessage.success('Files uploaded successfully')
            hasRoadNetworks.value = !!geojsonFile.value
            hasInundationMap.value = !!zipFile.value
        }
    } catch (error) {
        console.error('Upload error:', error)
        ElMessage.error('Failed to upload files')
    }
}

const handleGeojsonFile = (file) => {
    console.log('Processing GeoJSON file:', file.name)
    geojsonFile.value = file
    
    const reader = new FileReader()
    reader.onload = (e) => {
        try {
            const geojsonData = JSON.parse(e.target.result)
            emit('updateGeojson', convertGeoJSON(geojsonData))
        } catch (error) {
            ElMessage.error('Error processing GeoJSON file')
            console.error('Error processing GeoJSON:', error)
        }
    }
    reader.readAsText(file)
}

const handleZipFile = (file) => {
    console.log('Processing ZIP file:', file.name)
    zipFile.value = file
}

const triggerFileUpload = () => {
    const input = document.createElement('input')
    input.type = 'file'
    input.multiple = true
    input.accept = '.geojson,.zip'
    
    input.onchange = (event) => {
        const files = Array.from(event.target.files)
        files.forEach(file => {
            if (file.name.endsWith('.geojson')) {
                handleGeojsonFile(file)
            } else if (file.name.endsWith('.zip')) {
                handleZipFile(file)
            }
        })
        // 当两个文件都准备好后，自动上传
        if (geojsonFile.value && zipFile.value) {
            uploadFiles()
        }
    }
    
    input.click()
}

// 修改计算完成的处理函数
const handleCalculationComplete = () => {
    if (calculationType.value === 'single') {
        hasStaticResults.value = true
    } else {
        hasDynamicResults.value = true
    }
    // 自动显示统计面板
    emit('showStatistics', calculationType.value === 'single' ? 'static' : 'dynamic')
}

// 保留查看结果的处理函数
const handleViewResults = (type) => {
    emit('showStatistics', type)
}
</script>

<style scoped>
.topology-panel {
    position: fixed;
    left: 20px;
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
    font-size: 24px;
    color: #333;
    text-align: left;
}

.panel-header h3 {
    margin: 5px 0 0;
    font-size: 16px;
    color: #666;
    font-weight: normal;
    text-align: left;
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

.file-preview {
    margin-bottom: 20px;
}

.upload-btn {
    width: 100%;
    background-color: #4CAF50;
    color: white;
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    margin: 10px 0;
}

.upload-btn:hover {
    background-color: #45a049;
}

.checkbox-group {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.settings-icon {
    margin-left: 8px;
    cursor: pointer;
}

.topology-calculation h4,
.file-preview h4 {
    margin: 15px 0;
    color: #333;
}

h5 {
    margin: 10px 0;
    color: #666;
    font-style: italic;
}

.calculation-btn,
.simulation-btn,
.view-result-btn{
    width: 100%;
    margin: 10px 0;
}


.topology-images img,
.dynamic-images img {
    width: 100%;
    height: auto;
    border-radius: 8px;
    object-fit: cover;
}

.topology-images,
.dynamic-images {
    width: 100%;
    margin: 10px 0;
    border-radius: 8px;
    overflow: hidden;
}

.static-section,
.dynamic-section {
    margin: 15px 0;
}

:deep(.el-checkbox) {
    display: flex;
    align-items: center;
    margin-bottom: 8px;
}

.checkbox-with-info {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
}

.info-icon {
    color: #909399;
    font-size: 16px;
    cursor: help;
}

.calculation-buttons {
    display: flex;
    gap: 10px;
    margin-top: 10px;
}

.view-result-btn {
    width: 100%;
}

:deep(.el-dropdown) {
    width: 100%;
    display: block;
}
</style> 