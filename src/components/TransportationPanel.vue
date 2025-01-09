<template>
    <div class="transportation-panel">
        <div class="panel-header">
            <h2>Region</h2>
            <h3>King’sCross to Farringdon(25km²)</h3>
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
                    accept=".csv, .json"
                />
                
                <div class="checkbox-group">
                    <el-checkbox v-model="roadNetworks">
                        Road Networks
                        <el-icon class="settings-icon"><Setting /></el-icon>
                    </el-checkbox>
                    
                    <el-checkbox v-model="inundationMap">
                        Inundation Map
                        <el-icon class="settings-icon"><Setting /></el-icon>
                    </el-checkbox>
                    
                    <el-checkbox v-model="buildings">
                        Buildings
                        <el-icon class="settings-icon"><Setting /></el-icon>
                    </el-checkbox>
                </div>

                <div class="optional-section">
                    <p class="optional-text">optional</p>
                    <div class="checkbox-group">
                        <el-checkbox v-model="landUse">
                            Land Use
                            <el-icon class="settings-icon"><Setting /></el-icon>
                        </el-checkbox>
                        
                        <el-checkbox v-model="vehicleType">
                            Vehicle Type
                            <el-icon class="settings-icon"><Setting /></el-icon>
                        </el-checkbox>
                        
                        <el-checkbox v-model="ageStructure">
                            Age Structure
                            <el-icon class="settings-icon"><Setting /></el-icon>
                        </el-checkbox>
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
                            <span class="slider-value">100 - 10000</span>
                        </div>
                        <el-slider v-model="agentCount" :min="100" :max="10000" range />
                        
                        <div class="slider-label">
                            <span>Iteration</span>
                            <span class="slider-value">20 - 100</span>
                        </div>
                        <el-slider v-model="iteration" :min="20" :max="100" range />
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
                <el-button class="view-result-btn" disabled>View Result</el-button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElCheckbox, ElSlider, ElButton } from 'element-plus'
import { Setting } from '@element-plus/icons-vue'
import 'element-plus/es/components/checkbox/style/css'
import 'element-plus/es/components/slider/style/css'
import 'element-plus/es/components/button/style/css'

// 文件预览复选框状态
const roadNetworks = ref(false)
const inundationMap = ref(false)
const buildings = ref(false)
const landUse = ref(false)
const vehicleType = ref(false)
const ageStructure = ref(false)

// Matsim配置
const agentCount = ref([100, 10000])
const iteration = ref([20, 100])
const multiModal = ref(false)

// 文件上传相关
const fileInput = ref(null)
const triggerFileUpload = () => {
    fileInput.value.click()
}

const handleFileUpload = (event) => {
    const file = event.target.files[0]
    if (file) {
        console.log('File selected:', file.name)
    }
}

const emit = defineEmits(['close', 'calculate'])

const handleCalculation = () => {
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
    text-align: center;
}

.panel-header h3 {
    margin: 5px 0 0;
    font-size: 16px;
    color: #666;
    font-weight: normal;
    text-align: center;
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
</style> 