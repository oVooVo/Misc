#!/usr/bin/python3

import math
import cmath
import cairo
import sys
import os
import getopt
import random

# for the penrose-generator, I modified the script explained there:
#   http://preshing.com/20110831/penrose-tiling-explained/

# Validate input
try:
    int(sys.argv[1])
except ValueError:
    print("Expected positive integer (#subdivisions) as first argument")
    sys.exit()

try:
    name = sys.argv[2]
    try:
        os.mkdir(name)
    except FileExistsError:
        pass

    for filename in os.listdir(name):
        os.remove(os.path.join(name, filename))
except:
    print("Invalid output directory name: " + sys.argv[2])
    sys.exit()

#------ Configuration --------
IMAGE_SIZE = (1000, 1000)
NUM_SUBDIVISIONS = int(sys.argv[1])
OUTPUT_DIRECTORY = sys.argv[2]
SEED = 100
#-----------------------------




goldenRatio = (1 + math.sqrt(5)) / 2

def subdivide(triangles):
    result = []
    for (color, [A, B, C]) in triangles:
        if color == 0:
            # Subdivide red triangle
            P = A + (B - A) / goldenRatio
            result += [(0, [C, P, B]), (1, [P, C, A])]
        else:
            # Subdivide blue triangle
            Q = B + (A - B) / goldenRatio
            R = B + (C - B) / goldenRatio
            result += [(1, [R, C, A]), (1, [Q, R, B]), (0, [R, Q, A])]
    return result


print("Create wheel of red triangles around the origin...")
triangles = []
for i in range(10):
    B = cmath.rect(1, (2*i - 1) * math.pi / 10)
    C = cmath.rect(1, (2*i + 1) * math.pi / 10)
    if i % 2 == 0:
        B, C = C, B  # Make sure to mirror every second triangle
    triangles.append((0, [0j, B, C]))

print("Perform subdivisions...")
for i in range(NUM_SUBDIVISIONS):
    triangles = subdivide(triangles)

(_, [A, B, C]) = triangles[0]
baseSize = abs(B - A) / 10.0

def eq(a, b):
    return abs(a-b) < 0.00001

print("Convert the triangles to quads...")
quads = []
allQuads = []
for color_index, color in [(0, [0.2, 0.2, 1]), (1, [1, 0.2, 0.2])]:
    cQuads = []
    for i in range(len(triangles)):
        (color1, [a1, b1, c1]) = triangles[i]
        if color1 == color_index:
            for j in range(i+1, len(triangles)):
                (color2, [a2, b2, c2]) = triangles[j]
                if color2 == color_index:
                    if (eq(b1, b2) and eq(c1, c2)) or (eq(b1, c2) and eq(c1, b2)):
                        cQuads.append([a1, b1, a2, c1])
                        allQuads.append([a1, b1, a2, c1])
    quads.append((color, cQuads))

def areNeighbors(qs, ps):
    n = 0
    for q in qs:
        for p in ps:
            if eq(p, q):
                n += 1
    return n == 2

print("Find neighbors...")
neighbors = []
# neighbors is symmetric, i.e. (i,j)\in neigbors => (j,i)\in neighbors
for i in range(len(allQuads)):
    for j in range(len(allQuads)):
        if i != j:
            if (areNeighbors(allQuads[i], allQuads[j])):
                neighbors.append((i, j))

print("Initialize #sandpiles per quad...")
allQuads = [ (0, vertices) for vertices in allQuads ]

def set(i, val):
    allQuads[i] = (val, allQuads[i][1])

def topple():
    todo = []
    for i in range(len(allQuads)):
        n, _ = allQuads[i]
        if n >= 4:
            todo.append(i)
            set(i, allQuads[i][0] - 4)

    for i in todo:
        # thanks to symmetry of neighbors, the following is simple.
        for j in [ j for (k, j) in neighbors if k == i]:
            set(j, allQuads[j][0] + 1)

    return len(todo)

print("Seed sandpiles...")
# random seed
for i in range(len(allQuads)):
    set(i, random.choice(range(17)))

"""
for i in range(len(allQuads)):
    for vertex in allQuads[i][1]:
        if eq(vertex, 0):
            set(i, SEED)
"""

def draw(filename):
    # Prepare cairo surface
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, IMAGE_SIZE[0], IMAGE_SIZE[1])
    cr = cairo.Context(surface)
    cr.translate(IMAGE_SIZE[0] / 2.0, IMAGE_SIZE[1] / 2.0)
    wheelRadius = 1.2 * math.sqrt((IMAGE_SIZE[0] / 2.0) ** 2 + (IMAGE_SIZE[1] / 2.0) ** 2)
    cr.scale(wheelRadius, wheelRadius)

    # fill the tiles
    for n, vertices in allQuads:
        cr.move_to(vertices[0].real, vertices[0].imag)
        for vertex in vertices[1:]:
            cr.line_to(vertex.real, vertex.imag)
        cr.close_path()

        if n == 0:
            color = [.2,.2,.2]
        else:
            color = [ [1,.2,.2], [.2,1,.2], [.2,.2,1], [1,1,.2] ][n % 4]

        cr.set_source_rgb(*color)
        cr.fill()

    # draw the stroke
    cr.set_line_width(baseSize/2)
    cr.set_line_join(cairo.LINE_JOIN_ROUND)
    cr.set_source_rgb(0, 0, 0)
    for _, vertices in allQuads:        
        cr.move_to(vertices[0].real, vertices[0].imag)
        for vertex in vertices[1:]:
            cr.line_to(vertex.real, vertex.imag)
        cr.close_path()
        cr.stroke()

    #write the counts
    cr.set_source_rgb(0,0,0)
    cr.set_font_size(2*baseSize)
    for n, vertices in allQuads:
        center = sum(vertices)/4.0
        _, _, width, height, _, _ = cr.text_extents(str(n))
        cr.move_to(center.real - width/2, center.imag + height/2)
        cr.show_text(str(n))

    surface.write_to_png(filename)

print("Compute images...")
i = 0
while True:
    filename = os.path.join(OUTPUT_DIRECTORY, 'penrose_{num:04d}.png'.format(num=i))
    draw(filename)
    i += 1
    n = topple()
    if i%10 == 0 or n == 0:
        print("%d images done (toppled %d quads last iteration)" % (i, n))

    if n == 0:
        break

