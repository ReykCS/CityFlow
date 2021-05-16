import argparse
import json
import os
from generate_json_from_grid import gridToRoadnet

from get_turn_route import get_turn_route

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("rowNum", type=int)
    parser.add_argument("colNum", type=int)
    parser.add_argument("--rowDistance", type=int, default=300)
    parser.add_argument("--columnDistance", type=int, default=300)
    parser.add_argument("--intersectionWidth", type=int, default=30)
    parser.add_argument("--numLeftLanes", type=int, default=1)
    parser.add_argument("--numStraightLanes", type=int, default=1)
    parser.add_argument("--numRightLanes", type=int, default=1)
    parser.add_argument("--laneMaxSpeed", type=float, default=16.67)
    parser.add_argument("--vehLen", type=float, default=5.0)
    parser.add_argument("--vehWidth", type=float, default=2.0)
    parser.add_argument("--vehMaxPosAcc", type=float, default=2.0)
    parser.add_argument("--vehMaxNegAcc", type=float, default=4.5)
    parser.add_argument("--vehUsualPosAcc", type=float, default=2.0)
    parser.add_argument("--vehUsualNegAcc", type=float, default=4.5)
    parser.add_argument("--vehMinGap", type=float, default=2.5)
    parser.add_argument("--vehMaxSpeed", type=float, default=16.67)
    parser.add_argument("--vehHeadwayTime", type=float, default=1.5)
    parser.add_argument("--dir", type=str, default="./")
    parser.add_argument("--roadnetFile", type=str)
    parser.add_argument("--turn", action="store_true")
    parser.add_argument("--tlPlan", action="store_true")
    parser.add_argument("--interval", type=float, default=2.0)
    parser.add_argument("--flowFile", type=str)
    return parser.parse_args()

def get_straight_routes(rowNum, colNum):
    routes = []
    move = [(1, 0), (0, 1), (-1, 0), (0, -1)]

    def generate_straight_route(start, direction, step):
        x, y = start
        route = []
        for _ in range(step):
            route.append("road_%d_%d_%d" % (x, y, direction))
            x += move[direction][0]
            y += move[direction][1]
        return route

    for i in range(1, rowNum+1):
        routes.append(generate_straight_route((0, i), 0, colNum+1))
        routes.append(generate_straight_route((colNum+1, i), 2, colNum+1))
    for i in range(1, colNum+1):
        routes.append(generate_straight_route((i, 0), 1, rowNum+1))
        routes.append(generate_straight_route((i, rowNum+1), 3, rowNum+1))

    return routes

def get_turn_routes(rowNum, colNum):
    routes = []

    dims = (rowNum, colNum)

    # bottom & top
    for i in range(0, rowNum):
        routes.append(get_turn_route((i + 1, 0), (0, 1), dims))
        routes.append(get_turn_route((i + 1, colNum + 1), (0, -1), dims))

    # left & right
    for i in range(0, colNum):
        routes.append(get_turn_route((0, i + 1), (1, 0), dims))
        routes.append(get_turn_route((rowNum + 1, i + 1), (-1, 0), dims))

    return routes

if __name__ == '__main__':
    args = parse_args()
    if args.roadnetFile is None:
        args.roadnetFile = "roadnet_%d_%d%s.json" % (args.rowNum, args.colNum, "_turn" if args.turn else "")
    if args.flowFile is None:
        args.flowFile = "flow_%d_%d%s.json" % (args.rowNum, args.colNum, "_turn" if args.turn else "")

    grid = {
        "rowNumber": args.rowNum,
        "columnNumber": args.colNum,
        "rowDistances": [args.rowDistance] * (args.colNum-1),
        "columnDistances": [args.columnDistance] * (args.rowNum-1),
        "outRowDistance": args.rowDistance,
        "outColumnDistance": args.columnDistance,
        "intersectionWidths": [[args.intersectionWidth] * args.colNum] * args.rowNum,
        "numLeftLanes": args.numLeftLanes,
        "numStraightLanes": args.numStraightLanes,
        "numRightLanes": args.numRightLanes,
        "laneMaxSpeed": args.laneMaxSpeed,
        "tlPlan": args.tlPlan
    }

    json.dump(gridToRoadnet(**grid), open(os.path.join(args.dir, args.roadnetFile), "w"), indent=2)
    
    vehicle_template = {
        "length": args.vehLen,
        "width": args.vehWidth,
        "maxPosAcc": args.vehMaxPosAcc,
        "maxNegAcc": args.vehMaxNegAcc,
        "usualPosAcc": args.vehUsualPosAcc,
        "usualNegAcc": args.vehUsualNegAcc,
        "minGap": args.vehMinGap,
        "maxSpeed": args.vehMaxSpeed,
        "headwayTime": args.vehHeadwayTime
    }
    routes = get_turn_routes(args.rowNum, args.colNum) if args.turn else get_straight_routes(args.rowNum, args.colNum)

    flow = []
    if args.turn:
        for route in routes:
            for index, r in enumerate(route):
                flow.append({
                    "vehicle": vehicle_template,
                    "route": r,
                    "interval": len(route),
                    "startTime": index,
                    "endTime": -1
                })
    else:
        for route in routes:
            flow.append({
                "vehicle": vehicle_template,
                "route": route,
                "interval": args.interval,
                "startTime": 0,
                "endTime": -1
            })

    json.dump(flow, open(os.path.join(args.dir, args.flowFile), "w"), indent=2)

