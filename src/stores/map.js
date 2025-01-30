import { defineStore } from 'pinia'

export const useMapStore = defineStore('map', {
    state: () => ({
        roadNetwork: null,
        trafficData: null,
        mapInstance: null,
        showLegend: false,
        currentTimePoint: null
    }),
    
    actions: {
        setMapInstance(instance) {
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
            console.log('Current time point set to:', timePoint);
        },
        
        async initializeTrafficVisualization() {
            console.log('Initializing traffic visualization...');
            console.log('Road network:', !!this.roadNetwork);
            console.log('Traffic data:', !!this.trafficData);
            console.log('Map instance:', !!this.mapInstance);
            
            if (this.mapInstance?.loadTrafficNetwork && this.roadNetwork) {
                try {
                    await this.mapInstance.loadTrafficNetwork(this.roadNetwork);
                    console.log('Traffic network initialized successfully');
                } catch (error) {
                    console.error('Error initializing traffic network:', error);
                }
            } else {
                console.warn('Unable to initialize traffic visualization - missing dependencies');
            }
        },
        
        updateTrafficVisualization(timePoint) {
            if (!this.roadNetwork || !this.trafficData || !timePoint) {
                console.warn('Missing required data for visualization');
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
                console.warn('Invalid traffic value:', traffic);
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
        }
    }
}) 