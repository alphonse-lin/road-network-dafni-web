import { defineStore } from 'pinia'

export const useTopologyStore = defineStore('topology', {
    state: () => ({
        currentRadius: '100'
    }),
    actions: {
        setRadius(radius) {
            console.log('Store: Setting radius to:', radius)
            this.currentRadius = radius
        }
    }
}) 