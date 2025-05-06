<template>
    <div class="transportation-panel">
        <div class="panel-header">
            <h2>Region</h2>
            <h3>King'sCross to Farringdon(25km²)</h3>
            <button class="close-btn" @click="$emit('close')">×</button>
        </div>
        
        <div class="panel-content">
            <div class="file-preview">
                <h4>File Preview</h4>
                <button @click="triggerFileUpload" class="upload-btn">
                    upload
                </button>
                <input
                    type="file"
                    ref="fileInput"
                    @change="handleFileUpload"
                    style="display: none"
                    accept=".geojson"
                />
                
                <div class="checkbox-group">
                    <div class="checkbox-with-info">
                        <el-checkbox v-model="roadNetworks" disabled>
                            Road Networks
                        </el-checkbox>
                        <el-tooltip content="Please import geojson file of road networks" placement="right">
                            <el-icon class="info-icon"><InfoFilled /></el-icon>
                        </el-tooltip>
                    </div>
                    
                    <div class="checkbox-with-info">
                        <el-checkbox v-model="inundationMap" disabled>
                            Inundation Map
                        </el-checkbox>
                        <el-tooltip content="Please import asc files as zip file" placement="right">
                            <el-icon class="info-icon"><InfoFilled /></el-icon>
                        </el-tooltip>
                    </div>
                    
                    <div class="checkbox-with-info">
                        <el-checkbox v-model="buildings" disabled>
                            Buildings
                        </el-checkbox>
                        <el-tooltip content="Please import geojson file of buildings in chosen area" placement="right">
                            <el-icon class="info-icon"><InfoFilled /></el-icon>
                        </el-tooltip>
                    </div>
                </div>

                <div class="optional-section">
                    <p class="optional-text">optional</p>
                    <div class="checkbox-group">
                        <div class="checkbox-with-info">
                            <el-checkbox v-model="landUse">
                                Land Use
                            </el-checkbox>
                            <el-tooltip content="Please import the landuse info of chosen area. Otherwise it would apply default config" placement="right">
                                <el-icon class="info-icon"><InfoFilled /></el-icon>
                            </el-tooltip>
                        </div>
                        
                        <div class="checkbox-with-info">
                            <el-checkbox v-model="vehicleType">
                                Vehicle Type
                            </el-checkbox>
                            <el-tooltip content="Please import the verhicle type info of chosen area. Otherwise it would apply default config" placement="right">
                                <el-icon class="info-icon"><InfoFilled /></el-icon>
                            </el-tooltip>
                        </div>
                        
                        <div class="checkbox-with-info">
                            <el-checkbox v-model="ageStructure">
                                Age Structure
                            </el-checkbox>
                            <el-tooltip content="Please import the age info of chosen area. Otherwise it would apply default config" placement="right">
                                <el-icon class="info-icon"><InfoFilled /></el-icon>
                            </el-tooltip>
                        </div>
                    </div>
                </div>
            </div>

            <div class="simulation-section">
                <h4>Transportation Simulation</h4>
                <img src="@/assets/transportation_1.jpg" alt="Simulation Diagram" class="diagram-img"/>
                
                <div class="matsim-config">
                    <h5>• Matsim config</h5>
                    <div class="slider-container">
                        <div class="slider-label">
                            <span>Agent Count</span>
                            <span class="slider-value">{{ agentCount }}</span>
                        </div>
                        <el-slider 
                            v-model="agentCount" 
                            :min="100" 
                            :max="10000" 
                            :step="100"
                        />
                        
                        <div class="slider-label">
                            <span>Iteration</span>
                            <span class="slider-value">{{ iteration }}</span>
                        </div>
                        <el-slider 
                            v-model="iteration" 
                            :min="1" 
                            :max="10" 
                            :step="1"
                        />
                    </div>
                    
                    <el-checkbox v-model="multiModal">Multi Modal</el-checkbox>
                </div>

                <el-button 
                    class="calculation-btn" 
                    type="primary"
                    @click="handleCalculation"
                >
                    Calculation
                </el-button>
            </div>

            <div>
                <el-button 
                    class="view-result-btn" 
                    @click="handleViewResults"
                >
                    View Results
                </el-button>
            </div>

            <!-- <div>
                <el-button 
                    class="view-result-btn" 
                    :disabled="!hasCalculationResults"
                    @click="handleViewResults"
                >
                    View Results
                </el-button>
            </div> -->
        </div>

        <CalculationProgress
            v-model:visible="showProgress"
            :project-id="projectId"
            mode="transportation"
            title="Transportation Calculation Progress"
            @calculation-complete="handleCalculationComplete"
        />
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElCheckbox, ElSlider, ElButton, ElTooltip, ElMessage } from 'element-plus'
import { InfoFilled } from '@element-plus/icons-vue'
import 'element-plus/es/components/checkbox/style/css'
import 'element-plus/es/components/slider/style/css'
import 'element-plus/es/components/button/style/css'
import axios from '@/utils/axios'
import CalculationProgress from './CalculationProgress.vue'

// 文件预览复选框状态
const roadNetworks = ref(false)
const inundationMap = ref(false)
const buildings = ref(false)
const landUse = ref(false)
const vehicleType = ref(false)
const ageStructure = ref(false)

// Matsim配置
const agentCount = ref(1000)
const iteration = ref(5)
const multiModal = ref(false)

// 文件上传相关
const fileInput = ref(null)
const triggerFileUpload = () => {
    fileInput.value.click()
}

const props = defineProps({
    projectId: {
        type: String,
        required: true
    }
})

const emit = defineEmits(['close', 'calculate', 'updateBuildings'])

// 添加计算结果状态
const hasCalculationResults = ref(false)

// 处理文件上传
const handleFileUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    try {
        const formData = new FormData()
        formData.append('building', file)
        formData.append('projectId', props.projectId)

        // 读取文件内容
        const reader = new FileReader()
        reader.onload = async (e) => {
            try {
                const geojsonData = JSON.parse(e.target.result)
                emit('updateBuildings', geojsonData) // 发送解析后的 GeoJSON 数据
            } catch (error) {
                console.error('Error parsing GeoJSON:', error)
                ElMessage.error('Invalid GeoJSON file')
            }
        }
        reader.readAsText(file)

        const response = await axios.post('http://localhost:5000/api/upload-building', formData)
        
        if (response.data.success) {
            buildings.value = true
            ElMessage.success('Buildings file uploaded successfully')
        }
    } catch (error) {
        console.error('Error uploading buildings file:', error)
        ElMessage.error('Failed to upload buildings file')
    }
}

// 在组件挂载时检查已有文件状态
onMounted(async () => {
    try {
        const response = await axios.get(`/api/check-files/${props.projectId}`)
        roadNetworks.value = response.data.hasRoadNetworks
        inundationMap.value = response.data.hasInundationMap
        buildings.value = response.data.hasBuildings
    } catch (error) {
        console.error('Error checking file status:', error)
    }
})

const showProgress = ref(false)

const handleCalculation = () => {
    showProgress.value = true
}

const handleCalculationComplete = () => {
    hasCalculationResults.value = true
    // 自动显示统计面板
    emit('calculate')
}

// 添加查看结果的处理函数
const handleViewResults = () => {
    emit('calculate')
}
</script>

<style scoped>
.transportation-panel {
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

.file-preview, .simulation-section {
    margin-bottom: 20px;
}

h4 {
    margin: 15px 0;
    color: #333;
}

h5 {
    margin: 10px 0;
    color: #666;
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
    text-transform: lowercase;
}

.upload-btn:hover {
    background-color: #45a049;
}

.checkbox-group {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin: 10px 0;
}

.settings-icon {
    margin-left: 8px;
    cursor: pointer;
}

.optional-text {
    color: #666;
    font-style: italic;
    margin: 15px 0 5px;
}

.diagram-img {
    width: 100%;
    height: auto;
    margin: 10px 0;
    border-radius: 8px;
}

.slider-container {
    margin: 15px 0;
}

.slider-label {
    display: flex;
    justify-content: space-between;
    margin-bottom: 5px;
    color: #666;
}

.calculation-btn
{
    width: 100%;
    margin: 20px 0 10px;
}

.view-result-btn {
    width: 100%;
    margin: 10px 0;
}

:deep(.el-checkbox) {
    display: flex;
    align-items: center;
    margin-bottom: 8px;
}

:deep(.el-slider) {
    margin-bottom: 20px;
}

.checkbox-with-info {
    display: flex;
    align-items: center;
    gap: 8px;
}

.info-icon {
    color: #909399;
    cursor: help;
}
</style> 