<template>
    <div class="topology-panel">
        <div class="panel-header">
            <h2>Region</h2>
            <h3>King’sCross to Farringdon(25km²)</h3>
            <button class="close-btn" @click="$emit('close')">×</button>
        </div>
        
        <div class="panel-content">
            <div class="file-preview">
                <h4>File Preview</h4>
                <input
                    type="file"
                    ref="fileInput"
                    @change="handleFileUpload"
                    style="display: none"
                    accept=".csv, .json"
                />
                <button @click="triggerFileUpload" class="upload-btn">
                    Upload File
                </button>
                
                <div class="checkbox-group">
                    <el-checkbox v-model="roadNetworks">
                        Road Networks
                        <el-icon class="settings-icon"><Setting /></el-icon>
                    </el-checkbox>
                    
                    <el-checkbox v-model="inundationMap">
                        Inundation Map
                        <el-icon class="settings-icon"><Setting /></el-icon>
                    </el-checkbox>
                </div>
            </div>

            <div class="topology-calculation">
                <h4>Topology Calculation</h4>
                <div class="topology-images">
                    <img src="@/assets/topology_1.jpg" alt="Topology 1" />
                </div>
                
                <div class="static-section">
                    <h5>• Static</h5>
                    <el-checkbox v-model="addMergedSegments">Add Merged Segments</el-checkbox>
                    <el-checkbox v-model="roadNetworksStatic">Road Networks</el-checkbox>
                    <el-button 
                        class="calculation-btn" 
                        type="primary"
                        @click="handleStaticCalculation"
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
                        class="calculation-btn" 
                        type="primary"
                        @click="handleDynamicCalculation"
                    >
                        Calculation
                    </el-button>
                </div>
                <div>
                    <el-button class="simulation-btn" type="info">Simulation</el-button>
                </div>
                <div>
                    <el-button class="view-result-btn" disabled>View Result</el-button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElButton, ElCheckbox } from 'element-plus'
import { Setting } from '@element-plus/icons-vue'
import 'element-plus/es/components/button/style/css'
import 'element-plus/es/components/checkbox/style/css'

// 复选框状态
const roadNetworks = ref(false)
const inundationMap = ref(false)
const addMergedSegments = ref(false)
const roadNetworksStatic = ref(false)
const loadingInundationMap = ref(false)
// const statisticsType = ref('static')

const emit = defineEmits(['close', 'showStatistics'])

const handleStaticCalculation = () => {
    emit('showStatistics', 'static')
}

const handleDynamicCalculation = () => {
    emit('showStatistics', 'dynamic')
}

const fileInput = ref(null)

const triggerFileUpload = () => {
    fileInput.value.click()
}

const handleFileUpload = (event) => {
    const file = event.target.files[0]
    if (file) {
        console.log('File selected:', file.name)
        // TODO: 处理文件上传逻辑
        // 可以使用 FormData 或其他方式将文件发送到服务器
    }
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
</style> 