import { defineStore } from 'pinia'

export const useMapStore = defineStore('map', {
    state: () => ({
        roadNetwork: null,
        trafficData: null,
        mapInstance: null,
        showLegend: false,
        currentTimePoint: null,
        currentVulnerabilityTimePoint: null,
        showVulnerabilityLegend: false,
        vulnerabilityData: null,
        vulnerabilityColorCache: new Map(),
        lastUpdateTimestamp: 0,
        showRiskLegend: false,
        riskLevels: {
            'lowest': { color: '#00FF00', label: 'Lowest' },
            'low_risk': { color: '#90EE90', label: 'Low' },
            'high_risk': { color: '#FFA500', label: 'High' },
            'highest_risk': { color: '#FF0000', label: 'Highest' },
            'flooded': { color: '#000000', label: 'Flooded' }
        }
    }),
    
    actions: {
        setMapInstance(instance) {
            console.log('Setting map instance with methods:', Object.keys(instance));
            this.mapInstance = instance;
        },

        setRoadNetwork(network) {
            this.roadNetwork = network;
            console.log('Road network set:', network);
        },
        
        setTrafficData(data) {
            this.trafficData = data;
            console.log('Traffic data set:', Object.keys(data).length, 'roads');
        },
        
        setCurrentTimePoint(timePoint) {
            this.currentTimePoint = timePoint;
            // console.log('Current time point set to:', timePoint);
        },
        
        async initializeTrafficVisualization() {
            if (this.mapInstance?.loadTrafficNetwork && this.roadNetwork) {
                try {
                    await this.mapInstance.loadTrafficNetwork(this.roadNetwork);
                    console.log('Traffic network initialized successfully');
                } catch (error) {
                    console.error('Error initializing traffic network:', error);
                }
            }
        },
        
        updateTrafficVisualization(timePoint) {
            if (!this.roadNetwork || !this.trafficData || !timePoint) {
                return;
            }
            
            this.currentTimePoint = timePoint;
            
            try {
                if (this.mapInstance?.updateLayer) {
                    this.mapInstance.updateLayer();
                }
            } catch (error) {
                console.error('Error updating traffic visualization:', error);
            }
        },
        
        showTrafficLegend(show) {
            this.showLegend = show;
        },

        getTrafficColor(traffic) {
            if (typeof traffic !== 'number' || isNaN(traffic)) {
                return '#cccccc';
            }

            if (traffic <= 0) {
                return '#cccccc';
            }

            try {
                const maxTraffic = 60;
                const normalizedValue = Math.max(0, Math.min(traffic, maxTraffic)) / maxTraffic;
                const hue = Math.floor((1 - normalizedValue) * 240);
                return `hsl(${hue}, 100%, 50%)`;
            } catch (error) {
                console.error('Error calculating traffic color:', error);
                return '#cccccc';
            }
        },
        
        getTrafficWidth(traffic) {
            if (typeof traffic !== 'number' || isNaN(traffic)) {
                return 2;
            }
            const safeTraffic = Math.max(0, traffic);
            return Math.min(2 + (safeTraffic / 15), 10);
        },

        setVulnerabilityData(data) {
            this.vulnerabilityData = data;
            // 初始化颜色缓存
            this.initVulnerabilityColorCache();
            console.log('Vulnerability data set:', data);
        },

        async setCurrentVulnerabilityTimePoint(timePoint) {
            this.currentVulnerabilityTimePoint = timePoint;
            this.showVulnerabilityLegend = true;
            
            if (this.mapInstance?.updateRoadColors) {
                await this.mapInstance.updateRoadColors(timePoint);
            }
        },

        setShowVulnerabilityLegend(show) {
            this.showVulnerabilityLegend = show;
        },

        // 初始化颜色缓存
        initVulnerabilityColorCache() {
            this.vulnerabilityColorCache.clear();
            // 预计算1000个颜色值
            for (let i = 0; i <= 1000; i++) {
                const value = i * 10; // 0 到 10000 的范围
                const maxVulnerability = 10000;
                const normalizedValue = value / maxVulnerability;
                const hue = Math.max(0, 120 - (normalizedValue * 120));
                const color = `hsl(${hue}, 100%, 50%)`;
                this.vulnerabilityColorCache.set(value, color);
            }
        },

        // 优化后的颜色获取方法
        getVulnerabilityColor(value) {
            // 根据脆弱性值返回颜色
            // 例如：从绿色(低脆弱性)到红色(高脆弱性)的渐变
            // const normalizedValue = Math.min(Math.max(value, 0), 1);
            const normalizedValue = Math.min(value/12000, 1);
            return `hsl(${120 - (normalizedValue * 120)}, 100%, 50%)`;
        },

        getVulnerabilityColorRange() {
            return {
                low: 'hsl(120, 100%, 50%)',
                mediumLow: 'hsl(90, 100%, 50%)',
                medium: 'hsl(60, 100%, 50%)',
                mediumHigh: 'hsl(30, 100%, 50%)',
                high: 'hsl(0, 100%, 50%)'
            };
        },

        getVulnerabilityWidth(vulnerability) {
            if (typeof vulnerability !== 'number' || isNaN(vulnerability)) {
                return 2;
            }
            return 2 + (vulnerability * 4);
        },

        resetVulnerabilityState() {
            this.showVulnerabilityLegend = false;
            this.currentVulnerabilityTimePoint = null;
        },

        async forceMapUpdate() {
            if (this.mapInstance?.updateVulnerabilityVisualization) {
                return new Promise((resolve) => {
                    requestAnimationFrame(async () => {
                        try {
                            await this.mapInstance.updateVulnerabilityVisualization();
                            requestAnimationFrame(() => {
                                requestAnimationFrame(() => {
                                    resolve();
                                });
                            });
                        } catch (error) {
                            console.error('Error in force map update:', error);
                            resolve();
                        }
                    });
                });
            }
        },

        // 新增方法处理时间区间
        getTimeRangeLabel(timeStep) {
            const start = timeStep;
            const end = timeStep + 450; // 450秒间隔
            return `${start}-${end}s`;
        },

        getRiskLevelColor(level) {
            // console.log('Getting color for risk level:', level);
            const colorMap = {
                'lowest': '#008100',     // 深绿色
                'low_risk': '#BDE101',   // 浅绿色
                'high_risk': '#FFBE00',  // 橙色
                'highest_risk': '#F80203' // 红色
            };
            const color = colorMap[level] || '#CCCCCC';
            // console.log('Mapped color:', color);
            return color;
        },

        // 添加获取风险等级配置的方法
        getRiskLevelConfig() {
            return this.riskLevels;
        },
        
        setShowRiskLegend(show) {
            this.showRiskLegend = show;
        },
    }
})