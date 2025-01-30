<template>
    <div id="cesiumContainer"></div>
    <TopNavigation />
    <InfoPanel 
        v-if="activePanel === 'info'"
        :entity="selectedEntity"
        @close="closeInfoPanel"
    />
    <TopologyPanel
        v-if="activePanel === 'topology'"
        @close="closeTopologyPanel"
        @showStatistics="handleShowStatistics"
        @updateGeojson="handleGeojsonUpdate"
        @projectIdGenerated="handleProjectIdGenerated"
    />
    <TransportationPanel
        v-if="activePanel === 'transportation'"
        :projectId="projectId"
        @close="closeTransportationPanel"
        @calculate="handleTransportationCalculation"
        @updateBuildings="handleBuildingsUpdate"
    />
    <IndexPanel
        v-if="activePanel === 'index'"
        :project-id="projectId"
        @close="closeIndexPanel"
        @vulnerabilityCalculation="handleVulnerabilityCalculation"
        @riskCalculation="handleRiskCalculation"
    />
    <TransportationStatisticsPanel
        v-if="showTransportationStatsPanel"
        :projectId="projectId"
        @close="closeTransportationStatsPanel"
    />
    <ControlButtons 
        :isMarkerClicked="!!selectedEntity"
        :isComputed="isComputed"
        @compute="handleCompute"
        @topology="handleTopology"
        @transportation="handleTransportation"
        @index="handleIndex"
    />
    <StatisticsPanel
        v-if="showStatisticsPanel"
        ref="statisticsPanel"
        :type="statisticsType"
        :hasDynamicData="hasDynamicData"
        :projectId="projectId"
        :radius="currentRadii"
        @close="closeStatisticsPanel"
        @topology-result="handleTopologyResult"
        @time-point-changed="handleTimePointChange"
    />
    <IndexStatisticsPanel
        v-if="showIndexStatsPanel"
        :analysis-type="indexAnalysisType"
        @close="closeIndexStatsPanel"
    />
    <CalculationProgress
        v-if="showCalculationProgress"
        v-model:visible="showCalculationProgress"
        :mode="calculationType"
        :projectId="projectId"
        @calculation-complete="handleCalculationComplete"
    />
    <div v-if="showLegend" class="legend-container">
        <div class="legend-title">Betweenness Centrality</div>
        <div class="legend-gradient"></div>
        <div class="legend-labels">
            <span>{{ minMC.toFixed(2) }}</span>
            <span>{{ maxMC.toFixed(2) }}</span>
        </div>
    </div>
    <div v-if="mapStore.showLegend" class="traffic-flow-legend">
        <h4>Traffic Flow</h4>
        <div class="flow-gradient"></div>
        <div class="flow-labels">
            <span>0</span>
            <span>60</span>
            <span>120</span>
        </div>
    </div>
    </template>
    
    <script>
    import * as Cesium from 'cesium'
    import 'cesium/Build/CesiumUnminified/Widgets/widgets.css'
    import TopNavigation from './TopNavigation.vue'
    import InfoPanel from './InfoPanel.vue'
    import markerIcon from '@/assets/marker-icon.png'
    import ControlButtons from './ControlButtons.vue'
    import TopologyPanel from './TopologyPanel.vue'
    // import TopologyStatisticsPanel from './TopologyStatisticsPanel.vue'
    import TransportationPanel from './TransportationPanel.vue'
    import TransportationStatisticsPanel from './TransportationStatisticsPanel.vue'
    import IndexPanel from './IndexPanel.vue'
    import IndexStatisticsPanel from './IndexStatisticsPanel.vue'
    import CalculationProgress from './CalculationProgress.vue'
    import { ElMessage } from 'element-plus'
    import proj4 from 'proj4'
    import { ref, inject, nextTick } from 'vue'
    import { useTopologyStore } from '@/stores/topology'
    import axios from '@/utils/axios'
    import { defineAsyncComponent } from 'vue'
    import { useMapStore } from '@/stores/map'
    
    // 定义英国国家网格坐标系统 (EPSG:27700)
    proj4.defs("EPSG:27700", "+proj=tmerc +lat_0=49 +lon_0=-2 +k=0.9996012717 +x_0=400000 +y_0=-100000 +ellps=airy +towgs84=446.448,-125.157,542.06,0.15,0.247,0.842,-20.489 +units=m +no_defs");
    
    export default {
        name: 'MapViewer',
        components: {
            TopNavigation,
            InfoPanel,
            ControlButtons,
            TopologyPanel,
            StatisticsPanel: defineAsyncComponent(() => import('./TopologyStatisticsPanel.vue')),
            TransportationPanel,
            TransportationStatisticsPanel,
            IndexPanel,
            IndexStatisticsPanel,
            CalculationProgress
        },
        data() {
            return {
                viewer: null,
                selectedEntity: null,
                isComputed: false,
                showStatisticsPanel: false,
                statisticsType: '',
                hasDynamicData: false,
                showTransportationStatsPanel: false,
                activePanel: null,
                londonEntity: null,
                showIndexStatsPanel: false,
                indexAnalysisType: 'vulnerability',
                projectId: null,
                currentBuildingsDataSource: null,
                showLegend: false,
                minMC: 0,
                maxMC: 1,
                currentRadii: '100',
                showCalculationProgress: false,
                calculationType: 'static',
                pendingRadius: null,
                availableCalculationTypes: new Set(), // 追踪可用的计算类型
                calculationResults: {
                    static: false,
                    dynamic: false
                },
                trafficDataSource: null, // 新增：专门用于显示交通流量的数据源
                trafficDataCache: null, // 新增：用于缓存交通数据
            }
        },
        setup() {
            const calculationRadius = inject('calculationRadius', ref('100'))
            const topologyStore = useTopologyStore()
            const mapStore = useMapStore()
            
            return {
                calculationRadius,
                topologyStore,
                mapStore
            }
        },
        mounted() {
            Cesium.Ion.defaultAccessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJlNTcwOGMwZC1hZTI2LTQ3MTktYTA5YS1kMWZkOGMzMTFkMTMiLCJpZCI6MjkwOTksInNjb3BlcyI6WyJhc3IiLCJnYyJdLCJpYXQiOjE1OTE3NzUxNTh9.hzycCEi-nNawNPMnBkCYVMlkbC1QP60ULGMcUYIGxdw'
    
            this.viewer = new Cesium.Viewer('cesiumContainer', {
                imageryProvider: new Cesium.BingMapsImageryProvider({
                    url: 'https://dev.virtualearth.net',
                    key: 'AicWh_KjXV9j-4PekYNc8V3-cWtF-YtlYld133rs8WMp3SwYhY-_iZY_UqzJYmpw',
                    mapStyle: Cesium.BingMapsStyle.AERIAL_WITH_LABELS_ON_DEMAND
                }),
                baseLayerPicker: true,
                geocoder: false,
                homeButton: false,
                sceneModePicker: false,
                navigationHelpButton: false,
                animation: false,
                timeline: false,
                fullscreenButton: false
            })
    
            this.viewer.scene.mode = Cesium.SceneMode.SCENE3D;
            this.viewer.scene.screenSpaceCameraController.enableTilt = false;
    
            this.viewer.camera.setView({
                destination: Cesium.Rectangle.fromDegrees(
                    -0.3,
                    51.4,
                    0.1,
                    51.6
                )
            });
    
            const centerLon = -0.08845;
            const centerLat = 51.51839;
            const offset = 0.02; // 从中心点向四周偏移的距离（以度为单位）
            
    
            this.londonEntity = this.viewer.entities.add({
                name: 'London City',
                position: Cesium.Cartesian3.fromDegrees(centerLon, centerLat),
                billboard: {
                    image: markerIcon,
                    verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
                    scale: 0.2,
                    scaleByDistance: new Cesium.NearFarScalar(1.5e2, 0.25, 1.5e7, 0.15),
                    translucencyByDistance: new Cesium.NearFarScalar(1.5e2, 1.0, 1.5e7, 0.9)
                },
                polygon: {
                    hierarchy: new Cesium.PolygonHierarchy(
                        Cesium.Cartesian3.fromDegreesArray([
                            centerLon - offset, centerLat + 0.8*offset, // 左上
                            centerLon + offset, centerLat + 0.8*offset, // 右上
                            centerLon + offset, centerLat - 0.8*offset, // 右下
                            centerLon - offset, centerLat - 0.8*offset, // 左下
                        ])
                    ),
                    material: new Cesium.ColorMaterialProperty(
                        Cesium.Color.RED.withAlpha(0.1)
                    ),
                    outline: true,
                    outlineColor: Cesium.Color.RED,
                    outlineWidth: 10,
                    height: 0,
                    extrudedHeight: 0,
                    perPositionHeight: false,
                    show: false
                }
            });
    
            this.viewer.screenSpaceEventHandler.setInputAction((click) => {
                const pickedObject = this.viewer.scene.pick(click.position);
                
                if (Cesium.defined(pickedObject) && pickedObject.id && pickedObject.id.id === this.londonEntity.id) {
                    console.log('London entity clicked!');
                    
                    // 显示多边形
                    this.londonEntity.polygon.show = true;
                    
                    // 放大到更详细的视图
                    this.viewer.camera.flyTo({
                        destination: Cesium.Rectangle.fromDegrees(
                            centerLon - offset * 1,
                            centerLat - offset * 1,
                            centerLon + offset * 1,
                            centerLat + offset * 1
                        ),
                        duration: 2
                    });
    
                    // 显示信息面板
                    this.selectedEntity = this.londonEntity;
                    this.activePanel = 'info';
                }
            }, Cesium.ScreenSpaceEventType.LEFT_CLICK);
    
            // hover 效果
            this.viewer.screenSpaceEventHandler.setInputAction((movement) => {
                const pickedObject = this.viewer.scene.pick(movement.endPosition);
                if (Cesium.defined(pickedObject) && 
                    pickedObject.id && 
                    this.londonEntity &&
                    pickedObject.id.id === this.londonEntity.id) {
                    if (this.londonEntity.billboard) {
                        this.londonEntity.billboard.scale = 0.9;  // 放大图标
                    }
                } else if (this.londonEntity && this.londonEntity.billboard) {
                    this.londonEntity.billboard.scale = 0.7;   // 恢复原始大小
                }
            }, Cesium.ScreenSpaceEventType.MOUSE_MOVE);

            // 将 viewer 实例保存到 mapStore
            this.mapStore.setMapInstance({
                loadTrafficNetwork: this.loadTrafficNetwork.bind(this),
                updateTrafficVisualization: this.updateTrafficVisualization.bind(this),
                clearTrafficVisualization: this.clearTrafficVisualization.bind(this),
                clearAllDataSources: this.clearAllDataSources.bind(this)
            });
        },
        beforeUnmount() {
            if (this.viewer) {
                this.viewer.destroy()
            }
        },
        methods: {
            closeInfoPanel() {
                this.activePanel = null;
                if (this.viewer.entities.values.length > 0) {
                    this.viewer.entities.values[0].polygon.show = false;
                }
            },
            handleEntityClick() {
                this.selectedEntity = this.londonEntity;
                this.activePanel = 'info';
            },
            closeAllRightPanels() {
                this.showStatisticsPanel = false;
                this.showTransportationStatsPanel = false;
                this.showIndexStatsPanel = false;
            },
            handleCompute() {
                if (this.activePanel !== 'topology') {
                    this.closeAllRightPanels();
                }
                this.isComputed = true;
                this.activePanel = 'topology';
            },
            handleTopology() {
                if (this.activePanel !== 'topology') {
                    this.closeAllRightPanels();
                }
                this.activePanel = 'topology';
            },
            closeTopologyPanel() {
                this.activePanel = null;
                this.closeAllRightPanels();
            },
            handleShowStatistics(type) {
                console.log('handleShowStatistics called with type:', type)
                if (this.pendingRadius) {
                    this.currentRadii = this.pendingRadius
                }
                console.log('Using radius:', this.currentRadii)
                
                this.statisticsType = type
                this.showStatisticsPanel = true
            },
            closeStatisticsPanel() {
                this.showStatisticsPanel = false
                this.pendingRadius = null
            },
            handleTransportation() {
                if (this.activePanel !== 'transportation') {
                    this.closeAllRightPanels();
                }
                this.activePanel = 'transportation';
            },
            closeTransportationPanel() {
                this.activePanel = null;
                this.closeAllRightPanels();
            },
            handleTransportationCalculation() {
                this.showTransportationStatsPanel = true
            },
            closeTransportationStatsPanel() {
                this.showTransportationStatsPanel = false
            },
            handleIndex() {
                if (this.activePanel !== 'index') {
                    this.closeAllRightPanels();
                }
                this.activePanel = 'index';
            },
            closeIndexPanel() {
                this.activePanel = null;
                this.closeAllRightPanels();
            },
            handleVulnerabilityCalculation() {
                console.log('Handling vulnerability calculation')
                this.indexAnalysisType = 'vulnerability'
                this.showIndexStatsPanel = true
            },
            
            handleRiskCalculation() {
                console.log('Handling risk calculation')
                this.indexAnalysisType = 'risk'
                this.showIndexStatsPanel = true
            },
            
            closeIndexStatsPanel() {
                this.showIndexStatsPanel = false
            },
            async handleGeojsonUpdate(geojsonData) {
                try {
                    console.log('Starting handleGeojsonUpdate');
                    
                    // 首先移除鼠标移动事件处理器
                    if (this.viewer && this.viewer.screenSpaceEventHandler) {
                        this.viewer.screenSpaceEventHandler.removeInputAction(Cesium.ScreenSpaceEventType.MOUSE_MOVE);
                    }
    
                    // 确保 viewer 存在且未被销毁
                    if (!this.viewer || this.viewer.isDestroyed()) {
                        console.error('Viewer is not available or has been destroyed');
                        return;
                    }
    
                    // 安全地移除现有数据源
                    if (this.currentGeoJsonDataSource) {
                        try {
                            if (!this.currentGeoJsonDataSource.isDestroyed()) {
                                await this.viewer.dataSources.remove(this.currentGeoJsonDataSource);
                            }
                        } catch (e) {
                            console.warn('Error removing existing data source:', e);
                        }
                        this.currentGeoJsonDataSource = null;
                    }
    
                    // 安全地移除 London entity
                    if (this.londonEntity) {
                        try {
                            if (this.viewer.entities.contains(this.londonEntity)) {
                                this.viewer.entities.remove(this.londonEntity);
                            }
                        } catch (e) {
                            console.warn('Error removing London entity:', e);
                        }
                        this.londonEntity = null;
                    }
    
                    // 验证 GeoJSON 数据
                    if (!geojsonData || !geojsonData.features) {
                        console.error('Invalid GeoJSON data');
                        return;
                    }
    
                    // 创建新的数据源
                    const dataSource = new Cesium.GeoJsonDataSource('roadNetwork');
                    
                    try {
                        await dataSource.load(geojsonData, {
                            stroke: new Cesium.Color(0, 0, 1, 1),
                            strokeWidth: 3,
                            fill: new Cesium.Color(0, 0, 1, 0.1),
                            clampToGround: false
                        });
    
                        // 添加到查看器
                        await this.viewer.dataSources.add(dataSource);
                        this.currentGeoJsonDataSource = dataSource;
    
                        // 获取实体并设置样式
                        const entities = dataSource.entities.values;
                        if (entities && entities.length > 0) {
                            // 检查是否有 MC_100 值
                            const hasMCValues = geojsonData.features.some(f => 'MC_100' in f.properties);
                            console.log(hasMCValues)
                            if (hasMCValues) {
                                // 计算 MC 值的范围
                                const mcValues = geojsonData.features.map(f => f.properties.MC_100);
                                const minMC = Math.min(...mcValues);
                                const maxMC = Math.max(...mcValues);
                                
                                // 显示图例
                                this.showLegend = true;
                                this.minMC = minMC;
                                this.maxMC = maxMC;

                                // 为每条道路设置颜色
                                entities.forEach((entity, index) => {
                                    if (entity && entity.polyline) {
                                        const mcValue = geojsonData.features[index].properties.MC_100;
                                        const normalizedValue = (mcValue - minMC) / (maxMC - minMC);
                                        
                                        const color = Cesium.Color.fromHsl(
                                            (1 - normalizedValue) * 0.6, // hue: 0.6(蓝) -> 0(红)
                                            1.0,  // saturation
                                            0.5,  // lightness
                                            1.0   // alpha
                                        );
                                        
                                        entity.polyline.width = 2;
                                        entity.polyline.material = new Cesium.ColorMaterialProperty(color);
                                    }
                                });
                            } else {
                                // 使用默认颜色（原始的青色）
                                entities.forEach(entity => {
                                    if (entity && entity.polyline) {
                                        entity.polyline.width = 2;
                                        entity.polyline.material = new Cesium.ColorMaterialProperty(
                                            new Cesium.Color(0, 1, 1, 1)
                                        );
                                    }
                                });
                                // 隐藏图例
                                this.showLegend = false;
                            }
    
                            // 计算边界框
                            let west = Infinity;
                            let south = Infinity;
                            let east = -Infinity;
                            let north = -Infinity;
    
                            // 遍历所有特征以找到边界
                            geojsonData.features.forEach(feature => {
                                if (feature.geometry && feature.geometry.coordinates) {
                                    const coordinates = feature.geometry.coordinates;
                                    if (feature.geometry.type === 'LineString') {
                                        coordinates.forEach(coord => {
                                            west = Math.min(west, coord[0]);
                                            south = Math.min(south, coord[1]);
                                            east = Math.max(east, coord[0]);
                                            north = Math.max(north, coord[1]);
                                        });
                                    } else if (feature.geometry.type === 'MultiLineString') {
                                        coordinates.forEach(line => {
                                            line.forEach(coord => {
                                                west = Math.min(west, coord[0]);
                                                south = Math.min(south, coord[1]);
                                                east = Math.max(east, coord[0]);
                                                north = Math.max(north, coord[1]);
                                            });
                                        });
                                    }
                                }
                            });
    
                            // 添加一些边距
                            const padding = 0.001; // 根据需要调整边距大小
                            west -= padding;
                            south -= padding;
                            east += padding;
                            north += padding;
    
                            // 设置为 2D 模式并禁用倾斜
                            if (!this.viewer.isDestroyed()) {
                                this.viewer.scene.mode = Cesium.SceneMode.SCENE2D;
                                this.viewer.scene.screenSpaceCameraController.enableTilt = false;
                                this.viewer.scene.screenSpaceCameraController.enableRotate = false;
                                
                                // 移除 cesium 的 credit 信息
                                this.viewer.cesiumWidget.creditContainer.style.display = "none";
    
                                // 将视图设置到边界框
                                this.viewer.camera.setView({
                                    destination: Cesium.Rectangle.fromDegrees(west, south, east, north)
                                });
                            }
                        }
    
                    } catch (error) {
                        console.error('Error processing GeoJSON:', error);
                        ElMessage.error('Error loading GeoJSON data');
                    }
    
                } catch (error) {
                    console.error('Error in handleGeojsonUpdate:', error);
                    ElMessage.error('An error occurred while updating the map');
                }
            },
            handleProjectIdGenerated(id) {
                this.projectId = id;
                console.log('Project ID set in MapViewer:', id);
            },
            async handleTopologyResult(geojsonData) {
                try {
                    if (!this.currentGeoJsonDataSource) {
                        console.error('No existing data source to update')
                        return
                    }

                    const mcField = `MC_${this.topologyStore.currentRadius}`
                    console.log('MapViewer: Using MC field:', mcField)
                    
                    // 获取所有 MC 值
                    const mcValues = geojsonData.features.map(f => f.properties[mcField])
                    
                    // 对非零值进行对数变换
                    const logMcValues = mcValues.map(value => {
                        if (value > 0) {
                            return Math.log10(value)
                        }
                        return value  // 保持零值不变
                    })

                    const minLogMC = Math.min(...logMcValues.filter(v => v > 0))  // 只用非零值计算最小值
                    const maxLogMC = Math.max(...logMcValues)
                    
                    console.log('MC Values Summary:', {
                        total: mcValues.length,
                        zeros: mcValues.filter(v => v === 0).length,
                        nonZeros: mcValues.filter(v => v > 0).length
                    })
                    
                    console.log('Original MC value range:', {
                        min: Math.pow(10, minLogMC),
                        max: Math.pow(10, maxLogMC)
                    })
                    console.log('Log10 MC value range:', { minLogMC, maxLogMC })
                    
                    // 显示图例
                    this.showLegend = true
                    this.minMC = Math.pow(10, minLogMC)
                    this.maxMC = Math.pow(10, maxLogMC)

                    // 更新现有实体的颜色
                    const entities = this.currentGeoJsonDataSource.entities.values
                    entities.forEach((entity, index) => {
                        if (entity && entity.polyline) {
                            const mcValue = geojsonData.features[index].properties[mcField]
                            
                            if (mcValue === 0) {
                                // 零值使用特定颜色（比如深蓝色）
                                entity.polyline.material = new Cesium.ColorMaterialProperty(
                                    Cesium.Color.DARKBLUE
                                )
                            } else {
                                // 非零值使用对数渐变色
                                const logValue = Math.log10(mcValue)
                                const normalizedValue = (logValue - minLogMC) / (maxLogMC - minLogMC)
                                
                                const color = Cesium.Color.fromHsl(
                                    (1 - normalizedValue) * 0.6, // hue: 0.6(蓝) -> 0(红)
                                    1.0,  // saturation
                                    0.5,  // lightness
                                    1.0   // alpha
                                )
                                
                                entity.polyline.material = new Cesium.ColorMaterialProperty(color)
                            }
                        }
                    })

                } catch (error) {
                    console.error('Error in handleTopologyResult:', error)
                }
            },
            handleCalculationComplete() {
                const type = this.calculationType === 'single' ? 'static' : 'dynamic'
                this.calculationResults[type] = true
            },
            handleViewResults(type) {
                if (this.calculationResults[type]) {
                    this.statisticsType = type
                    this.showStatisticsPanel = true
                    // 确保 StatisticsPanel 组件知道要显示哪种类型
                    if (this.$refs.statisticsPanel) {
                        this.$refs.statisticsPanel.enableCalculationType(type)
                    }
                }
            },
            async handleTimePointChange(data) {
                try {
                    await this.handleDynamicNetworkUpdate(data.geojsonData);
                } catch (error) {
                    console.error('Error updating network display:', error);
                    ElMessage.error('Failed to update network display');
                }
            },
            async handleDynamicNetworkUpdate(geojsonData) {
                try {
                    // 创建新的数据源
                    const dataSource = new Cesium.GeoJsonDataSource('dynamicNetwork');
                    
                    await dataSource.load(geojsonData, {
                        stroke: new Cesium.Color(0, 0, 1, 1),
                        strokeWidth: 3,
                        fill: new Cesium.Color(0, 0, 1, 0.1),
                        clampToGround: false
                    });

                    // 移除之前的动态网络数据源（如果存在）
                    if (this.dynamicNetworkDataSource) {
                        await this.viewer.dataSources.remove(this.dynamicNetworkDataSource);
                    }

                    // 添加新的数据源
                    await this.viewer.dataSources.add(dataSource);
                    this.dynamicNetworkDataSource = dataSource;

                    // 更新样式
                    const mcField = `MC_${this.topologyStore.currentRadius}`;
                    const entities = dataSource.entities.values;
                    
                    if (entities && entities.length > 0) {
                        const mcValues = geojsonData.features.map(f => f.properties[mcField]);
                        const minMC = Math.min(...mcValues);
                        const maxMC = Math.max(...mcValues);

                        entities.forEach((entity, index) => {
                            if (entity && entity.polyline) {
                                const mcValue = geojsonData.features[index].properties[mcField];
                                const normalizedValue = (mcValue - minMC) / (maxMC - minMC);
                                
                                const color = Cesium.Color.fromHsl(
                                    (1 - normalizedValue) * 0.6,
                                    1.0,
                                    0.5,
                                    1.0
                                );
                                
                                entity.polyline.width = 2;
                                entity.polyline.material = new Cesium.ColorMaterialProperty(color);
                            }
                        });
                    }
                } catch (error) {
                    console.error('Error in handleDynamicNetworkUpdate:', error);
                    ElMessage.error('Failed to update dynamic network');
                }
            },
            // 处理静态计算按钮点击
            async handleStaticCalculation() {
                this.statisticsType = 'static'
                this.showStatisticsPanel = true
                if (this.$refs.statisticsPanel) {
                    this.$refs.statisticsPanel.enableCalculationType('static')
                }
            },

            // 处理动态计算按钮点击
            async handleDynamicCalculation() {
                this.statisticsType = 'dynamic'
                this.showStatisticsPanel = true
                if (this.$refs.statisticsPanel) {
                    this.$refs.statisticsPanel.enableCalculationType('dynamic')
                }
            },

            // 添加 loadTimePoints 方法
            async loadTimePoints() {
                if (!this.projectId) {
                    console.warn('No project ID available');
                    return;
                }

                try {
                    const response = await axios.get('/api/topology/dynamic_networks', {
                        params: { project_id: this.projectId }
                    });
                    
                    if (response.data.status === 'success' && this.$refs.statisticsPanel) {
                        // 确保组件已挂载并且方法存在
                        const panel = this.$refs.statisticsPanel;
                        if (typeof panel.updateTimePoints === 'function') {
                            panel.updateTimePoints(response.data.timePoints);
                        } else {
                            console.warn('updateTimePoints method not found on statisticsPanel');
                        }
                    } else {
                        console.warn('Statistics panel not ready or invalid response');
                    }
                } catch (error) {
                    console.error('Error loading time points:', error);
                    ElMessage.error('Failed to load time points');
                }
            },

            // 新增：加载交通流量网络
            async loadTrafficNetwork(geojsonData) {
                try {
                    console.log('Loading traffic network...');
                    
                    await this.clearAllDataSources();
                    
                    const dataSource = new Cesium.GeoJsonDataSource('trafficNetwork');
                    
                    await dataSource.load(geojsonData, {
                        stroke: new Cesium.Color(0.8, 0.8, 0.8, 1.0),
                        strokeWidth: 2,
                        clampToGround: true
                    });

                    const entities = dataSource.entities.values;
                    console.log(`Processing ${entities.length} entities...`);
                    
                    entities.forEach((entity, index) => {
                        if (entity && entity.polyline) {
                            // 确保每个实体都有正确的ID
                            const roadId = geojsonData.features[index].properties.id;
                            entity.properties = entity.properties || {};
                            entity.properties.id = new Cesium.ConstantProperty(roadId);
                            
                            // 设置初始样式
                            entity.polyline.width = new Cesium.ConstantProperty(2);
                            entity.polyline.material = new Cesium.ColorMaterialProperty(
                                new Cesium.Color(0.8, 0.8, 0.8, 1.0)
                            );
                            entity.polyline.show = new Cesium.ConstantProperty(true);
                            
                            // 确保线条贴地
                            entity.polyline.clampToGround = true;
                        }
                    });

                    this.trafficDataSource = dataSource;
                    await this.viewer.dataSources.add(dataSource);
                    
                    console.log('Traffic network loaded successfully');
                    
                    // 验证数据
                    const sampleEntity = entities[0];
                    if (sampleEntity) {
                        console.log('Sample entity:', {
                            id: sampleEntity.properties?.id?.getValue(),
                            hasPolyline: !!sampleEntity.polyline,
                            material: sampleEntity.polyline?.material
                        });
                    }
                    
                } catch (error) {
                    console.error('Error loading traffic network:', error);
                    ElMessage.error('Failed to load traffic network');
                }
            },

            // 更新交通流量可视化
            async updateTrafficVisualization() {
                if (!this.trafficDataSource) {
                    console.warn('No traffic data source available');
                    return;
                }

                try {
                    const entities = this.trafficDataSource.entities.values;
                    const currentTimePoint = this.mapStore.currentTimePoint;
                    console.log(`Updating traffic for time ${currentTimePoint}, total entities: ${entities.length}`);
                    
                    let updatedCount = 0;
                    // 遍历所有实体并更新
                    for (const entity of entities) {
                        if (entity && entity.polyline) {
                            const roadId = entity.properties?.id?.getValue();
                            if (!roadId) continue;

                            // 获取当前时间点的交通流量
                            const trafficValue = this.mapStore.trafficData?.[roadId]?.[currentTimePoint];
                            if (typeof trafficValue !== 'number') {
                                // console.warn(`No traffic data for road ${roadId} at time ${currentTimePoint}`);
                                continue;
                            }

                            // 计算颜色和宽度
                            const color = this.mapStore.getTrafficColor(trafficValue);
                            const width = this.mapStore.getTrafficWidth(trafficValue);

                            // 创建新的颜色实例
                            let cesiumColor;
                            if (color.startsWith('hsl')) {
                                const hslMatch = color.match(/hsl\((\d+),\s*(\d+)%,\s*(\d+)%\)/);
                                if (hslMatch) {
                                    const [, h, s, l] = hslMatch;
                                    const rgb = this.hslToRgb(h/360, s/100, l/100);
                                    cesiumColor = new Cesium.Color(rgb.r, rgb.g, rgb.b, 1.0);
                                }
                            } else if (color.startsWith('#')) {
                                cesiumColor = Cesium.Color.fromCssColorString(color);
                            }

                            if (cesiumColor) {
                                // 更新实体的颜色和宽度
                                entity.polyline.material = new Cesium.ColorMaterialProperty(cesiumColor);
                                entity.polyline.width = new Cesium.ConstantProperty(width);
                                updatedCount++;
                            }
                        }
                    }

                    console.log(`Updated ${updatedCount} entities for time ${currentTimePoint}`);
                    
                    // 强制场景刷新
                    this.viewer.scene.requestRender();
                    
                } catch (error) {
                    console.error('Error updating traffic visualization:', error);
                }
            },

            // 添加 HSL 到 RGB 的转换函数
            hslToRgb(h, s, l) {
                let r, g, b;

                if (s === 0) {
                    r = g = b = l; // achromatic
                } else {
                    const hue2rgb = (p, q, t) => {
                        if (t < 0) t += 1;
                        if (t > 1) t -= 1;
                        if (t < 1/6) return p + (q - p) * 6 * t;
                        if (t < 1/2) return q;
                        if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
                        return p;
                    };

                    const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
                    const p = 2 * l - q;
                    r = hue2rgb(p, q, h + 1/3);
                    g = hue2rgb(p, q, h);
                    b = hue2rgb(p, q, h - 1/3);
                }

                return { r, g, b };
            },

            // 新增：清除交通流量显示
            clearTrafficVisualization() {
                if (this.trafficDataSource) {
                    this.viewer.dataSources.remove(this.trafficDataSource);
                    this.trafficDataSource = null;
                }
            },

            // 将清除方法暴露给外部
            async clearAllDataSources() {
                try {
                    console.log('Clearing all data sources...');
                    
                    // 清除拓扑分析数据
                    if (this.currentGeoJsonDataSource) {
                        await this.viewer.dataSources.remove(this.currentGeoJsonDataSource);
                        this.currentGeoJsonDataSource = null;
                    }
                    
                    // 清除动态网络数据
                    if (this.dynamicNetworkDataSource) {
                        await this.viewer.dataSources.remove(this.dynamicNetworkDataSource);
                        this.dynamicNetworkDataSource = null;
                    }
                    
                    // 清除交通数据
                    if (this.trafficDataSource) {
                        await this.viewer.dataSources.remove(this.trafficDataSource);
                        this.trafficDataSource = null;
                    }
                    
                    // 隐藏图例
                    this.showLegend = false;
                    
                    console.log('All data sources cleared');
                } catch (error) {
                    console.error('Error clearing data sources:', error);
                }
            },

            // 添加缓存初始化方法
            async initTrafficDataCache() {
                if (!this.trafficDataSource || !this.mapStore.trafficData || !this.mapStore.currentTimePoint) {
                    return;
                }

                try {
                    console.log('Initializing traffic data cache...');
                    const entities = this.trafficDataSource.entities.values;
                    const timePoints = Object.keys(Object.values(this.mapStore.trafficData)[0] || {})
                        .filter(key => key.startsWith('traffic_'));

                    // 为每个实体和时间点创建缓存
                    this.trafficDataCache = new Map();

                    entities.forEach(entity => {
                        if (entity && entity.polyline) {
                            const roadId = entity.properties?.id?.getValue();
                            if (!roadId) return;

                            const roadCache = new Map();
                            timePoints.forEach(timePoint => {
                                const trafficValue = this.mapStore.trafficData[roadId][timePoint];
                                const traffic = typeof trafficValue === 'number' ? trafficValue : 0;
                                const color = this.mapStore.getTrafficColor(traffic);
                                const width = this.mapStore.getTrafficWidth(traffic);

                                let cesiumColor;
                                if (color.startsWith('hsl')) {
                                    const hslMatch = color.match(/hsl\((\d+),\s*(\d+)%,\s*(\d+)%\)/);
                                    if (hslMatch) {
                                        const [, h, s, l] = hslMatch;
                                        const rgb = this.hslToRgb(h/360, s/100, l/100);
                                        cesiumColor = new Cesium.Color(rgb.r, rgb.g, rgb.b, 1.0);
                                    }
                                } else if (color.startsWith('#')) {
                                    cesiumColor = Cesium.Color.fromCssColorString(color);
                                }

                                roadCache.set(timePoint, {
                                    cesiumColor,
                                    width: new Cesium.ConstantProperty(width)
                                });
                            });

                            this.trafficDataCache.set(roadId, roadCache);
                        }
                    });

                    console.log('Traffic data cache initialized');
                    
                } catch (error) {
                    console.error('Error initializing traffic data cache:', error);
                }
            },
        },
        computed: {
            showTopologyPanel() {
                return this.activePanel === 'topology'
            },
            showTransportationPanel() {
                return this.activePanel === 'transportation'
            },
            showIndexPanel() {
                return this.activePanel === 'index'
            },
            isDynamicMode() {
                return this.statisticsType === 'dynamic'
            }
        },
        watch: {
            currentRadii: {
                immediate: true,
                handler(newVal, oldVal) {
                    console.log('currentRadii changed from', oldVal, 'to', newVal)
                }
            },
            showStatisticsPanel: {
                immediate: true,
                handler(newVal) {
                    if (newVal) {
                        const radius = this.pendingRadius || this.currentRadii
                        console.log('Opening statistics panel with radius:', radius)
                    }
                }
            },
            pendingRadius(newVal) {
                console.log('pendingRadius updated to:', newVal)
            },
            isDynamicMode: {
                immediate: true,
                async handler(newVal) {
                    if (newVal && this.projectId) {
                        // 添加延迟确保组件已挂载
                        await nextTick();
                        if (this.$refs.statisticsPanel) {
                            await this.loadTimePoints();
                        } else {
                            console.warn('Statistics panel not mounted yet');
                        }
                    }
                }
            },
            activePanel: {
                immediate: true,
                async handler(newPanel, oldPanel) {
                    if (newPanel !== oldPanel) {
                        // 当面板切换时，清除所有数据
                        // await this.clearAllDataSources();
                        
                        // 如果切换到交通模拟面板，初始化交通数据
                        if (newPanel === 'transportation' && this.projectId) {
                            // 可以在这里添加初始化交通模拟的逻辑
                        }
                    }
                }
            }
        }
    }
    </script>
    
    <style>
    html,
    body,
    #app {
        height: 100%;
        margin: 0;
        padding: 0;
        overflow: hidden;
    }
    
    #cesiumContainer {
        width: 100%;
        height: 100%;
        position: absolute;
        top: 0;
        left: 0;
    }
    
    .cesium-viewer-toolbar {
        top: 20px !important;
        right: 20px !important;
    }
    
    .cesium-viewer-geocoderContainer {
        top: 20px !important;
        right: 20px !important;
    }
    
    /* 修改图例容器的样式 */
    .legend-container {
        position: fixed;
        left: 480px; /* TopologyPanel 的宽度(400px) + 左边距(20px) + 间距(20px) */
        top: 780px; /* 与 TopologyPanel 对齐 */
        background: rgba(255, 255, 255, 0.95);
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        z-index: 1000;
        width: 200px; /* 固定宽度 */
    }
    
    .legend-title {
        font-size: 14px;
        margin-bottom: 8px;
        color: #333;
        font-weight: 500;
    }
    
    .legend-gradient {
        width: 100%;
        height: 20px;
        background: linear-gradient(to right, 
            hsl(216, 100%, 50%),  /* 蓝色 */
            hsl(180, 100%, 50%),  /* 青色 */
            hsl(120, 100%, 50%),  /* 绿色 */
            hsl(60, 100%, 50%),   /* 黄色 */
            hsl(0, 100%, 50%)     /* 红色 */
        );
        border-radius: 4px;
        margin: 5px 0;
    }
    
    .legend-labels {
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        color: #666;
        margin-top: 4px;
    }

    .traffic-legend {
        position: absolute;
        top: 760px;
        left: 480px;
        background: white;
        padding: 10px;
        border-radius: 4px;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
        z-index: 1;
    }

    .legend-item {
        display: flex;
        align-items: center;
        margin: 5px 0;
    }

    .legend-color {
        width: 20px;
        height: 4px;
        margin-right: 8px;
        border-radius: 2px;
    }

    h4 {
        margin: 0 0 8px 0;
        font-size: 14px;
        color: #333;
    }

    .traffic-flow-legend {
        position: fixed;
        left: 480px;
        top: 780px;
        background: rgba(255, 255, 255, 0.95);
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        z-index: 1000;
        width: 200px;
    }

    .flow-gradient {
        width: 100%;
        height: 20px;
        background: linear-gradient(to right,
            #ccc,  /* 0 traffic */
            hsl(240, 100%, 50%),  /* 深蓝色 */
            hsl(180, 100%, 50%),  /* 青色 */
            hsl(120, 100%, 50%),  /* 绿色 */
            hsl(60, 100%, 50%),   /* 黄色 */
            hsl(0, 100%, 50%)     /* 红色 */
        );
        border-radius: 4px;
        margin: 5px 0;
    }

    .flow-labels {
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        color: #666;
        margin-top: 4px;
    }
    </style>