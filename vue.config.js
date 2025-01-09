const { defineConfig } = require('@vue/cli-service')
const path = require('path')
const webpack = require('webpack')
const CopyWebpackPlugin = require('copy-webpack-plugin')

module.exports = defineConfig({
    transpileDependencies: true,
    configureWebpack: {
        resolve: {
            fallback: {
                "https": false,
                "zlib": false,
                "http": false,
                "url": false
            }
        },
        plugins: [
            // Copy Cesium Assets, Widgets, and Workers to a static directory
            new CopyWebpackPlugin({
                patterns: [{
                        from: 'node_modules/cesium/Build/CesiumUnminified/Workers',
                        to: 'Workers'
                    },
                    {
                        from: 'node_modules/cesium/Build/CesiumUnminified/ThirdParty',
                        to: 'ThirdParty'
                    },
                    {
                        from: 'node_modules/cesium/Build/CesiumUnminified/Assets',
                        to: 'Assets'
                    },
                    {
                        from: 'node_modules/cesium/Build/CesiumUnminified/Widgets',
                        to: 'Widgets'
                    }
                ]
            }),
            new webpack.DefinePlugin({
                CESIUM_BASE_URL: JSON.stringify('/')
            })
        ],
        module: {
            rules: [{
                test: /\.mjs$/,
                include: /node_modules/,
                type: 'javascript/auto'
            }]
        }
    }
})