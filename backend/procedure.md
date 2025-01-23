# Running Procedures

## Run Topology Calculation
- [create seq inundated map](./prepare/createSeqInundateMap.py)
- [create time-variant sequence road network geojson](./prepare/createSeqGeoJSON.py)
- [run space syntax calculation](./prepare/csharpCalculation.py)

## Run Matsim
- [generate daily activity chain](./prepare/generateDailyActivityChain.py)
- [run matsim](./prepare/runMatsim.py)
- [!!!!!!!!convert data to frontend](./prepare/convertData.py)

## Run risk calculation
- [merge data from matsim and space syntax](./prepare/mergeData.py)
- [run dtw matching](./prepare/dtwmatching.py)
- [TODO: run vulnerability&risk calculation](./prepare/IndexCalculation.py)