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
/>
<TransportationPanel
    v-if="activePanel === 'transportation'"
    @close="closeTransportationPanel"
    @calculate="handleTransportationCalculation"
/>
<IndexPanel
    v-if="activePanel === 'index'"
    @close="closeIndexPanel"
    @vulnerabilityCalculation="handleVulnerabilityCalculation"
    @riskCalculation="handleRiskCalculation"
/>
<TransportationStatisticsPanel
    v-if="showTransportationStatsPanel"
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
    @close="closeStatisticsPanel"
/>
<IndexStatisticsPanel
    v-if="showIndexStatsPanel"
    :analysis-type="indexAnalysisType"
    @close="closeIndexStatsPanel"
/>
</template>

<script>
import * as Cesium from 'cesium'
import 'cesium/Build/CesiumUnminified/Widgets/widgets.css'
import TopNavigation from './TopNavigation.vue'
import InfoPanel from './InfoPanel.vue'
import markerIcon from '@/assets/marker-icon.png'
import ControlButtons from './ControlButtons.vue'
import TopologyPanel from './TopologyPanel.vue'
import TopologyStatisticsPanel from './TopologyStatisticsPanel.vue'
import TransportationPanel from './TransportationPanel.vue'
import TransportationStatisticsPanel from './TransportationStatisticsPanel.vue'
import IndexPanel from './IndexPanel.vue'
import IndexStatisticsPanel from './IndexStatisticsPanel.vue'
import { ElMessage } from 'element-plus'

export default {
    name: 'MapViewer',
    components: {
        TopNavigation,
        InfoPanel,
        ControlButtons,
        TopologyPanel,
        StatisticsPanel: TopologyStatisticsPanel,
        TransportationPanel,
        TransportationStatisticsPanel,
        IndexPanel,
        IndexStatisticsPanel
    },
    data() {
        return {
            viewer: null,
            selectedEntity: null,
            isComputed: false,
            showStatisticsPanel: false,
            statisticsType: 'static',
            hasDynamicData: false,
            showTransportationStatsPanel: false,
            activePanel: null,
            londonEntity: null,
            showIndexStatsPanel: false,
            indexAnalysisType: 'vulnerability'  // or 'risk'
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
            this.statisticsType = type;
            if (type === 'dynamic') {
                this.hasDynamicData = true;
                if (this.$refs.statisticsPanel) {
                    this.$refs.statisticsPanel.selectedStatsType = 'dynamic';
                }
            }
            this.showStatisticsPanel = true;
            this.showTransportationStatsPanel = false;
        },
        closeStatisticsPanel() {
            console.log('closeStatisticsPanel')
            this.showStatisticsPanel = false
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
            this.showTransportationStatsPanel = true;
            this.showStatisticsPanel = false;
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
                        entities.forEach(entity => {
                            if (entity && entity.polyline) {
                                entity.polyline.width = 2;
                                entity.polyline.material = new Cesium.ColorMaterialProperty(
                                    new Cesium.Color(0, 0, 1, 1)
                                );
                            }
                        });

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
        }
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
</style>
