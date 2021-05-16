import numpy as np

def get_turn_route(start, dir, dim):
  route_name = lambda x, y, d: "road_%d_%d_%d" % (x, y, d)

  rows, cols = dim
  grid = [False] * (cols + 2) * (rows + 2)
  x, y = start
  newX = x + dir[0]
  newY = y + dir[1]
  grid[y * cols + x] = True
  grid[newY * cols + newX] = True

  def find_routes(s, grid):
    x, y = s
    route = []

    for i in range(0, 4):
      newX, newY, dir = get_successor(s, i)
      direction = get_dir(dir)
      new_route = route_name(x, y, direction)
      if grid[newY * cols + newX]:
        continue
      if newY < 0 or newX < 0 or newY > rows + 1 or newX > cols + 1:
        continue
      if newY <= 0 or newX <= 0 or newY >= rows + 1 or newX >= cols + 1:
        route.append(new_route)
        continue
      route.append(new_route)
      grid[newY * cols + newX] = True
      route.append(find_routes((newX, newY), grid.copy()))
    
    return route 

  def build_routes(existing, start, routes):
    if len(routes) <= 0:
      return

    if isinstance(routes, str):
      return existing.append(start + [routes])

    for i in range(0, len(routes)):
      if (i < len(routes) - 1 and isinstance(routes[i], str) and not isinstance(routes[i + 1], list)) or (i >= len(routes) - 1 and isinstance(routes[i], str)):
        existing.append(start + [routes[i]])
        continue
      if isinstance(routes[i], list):
        build_routes(existing, start + [routes[i - 1]], routes[i])
        continue

  routes = find_routes((newX, newY), grid.copy())
  existing = []
  build_routes(existing, [route_name(x, y, get_dir(dir))], routes)

  return existing

def get_successor(pos, index):
  x, y = pos

  dir = ((np.sign(2 - index) * ((2 - index) % 2)), (np.sign(index - 1) * ((index - 1) % 2)))

  newX = x + dir[0]
  newY = y + dir[1]

  return newX, newY, dir

def get_dir(dir):
  x, y = dir
  if x == 1 and y == 0:
    return 0
  if x == 0 and y == 1:
    return 1
  if x == -1 and y == 0:
    return 2
  return 3