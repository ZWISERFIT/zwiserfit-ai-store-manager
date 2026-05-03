#!/usr/bin/env python3
"""Generate Stella avatar - optimized."""
import struct, zlib, math

def create_png(width, height, pixels):
    def chunk(ctype, data):
        c = ctype + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    raw = b''
    for row in pixels:
        raw += b'\x00' + bytes(row)
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b'')

W = H = 256
px = [[[0,0,0,0] for _ in range(W)] for _ in range(H)]

def setp(x, y, r, g, b, a=255):
    if 0 <= x < W and 0 <= y < H:
        px[y][x][:] = r, g, b, a

def fill_circle(cx, cy, radius, r, g, b, a=255):
    rr = radius*radius
    for dy in range(-radius, radius+1):
        y = cy+dy
        if y < 0 or y >= H: continue
        for dx in range(-radius, radius+1):
            if dx*dx+dy*dy <= rr:
                x = cx+dx
                if 0 <= x < W:
                    px[y][x][:] = r, g, b, a

def fill_ring(cx, cy, o, i, r, g, b, a=255):
    o2, i2 = o*o, i*i
    for dy in range(-o, o+1):
        y = cy+dy
        if y < 0 or y >= H: continue
        for dx in range(-o, o+1):
            d2 = dx*dx+dy*dy
            if o2 >= d2 > i2:
                x = cx+dx
                if 0 <= x < W:
                    px[y][x][:] = r, g, b, a

def fill_rect(x0, y0, x1, y1, r, g, b, a=255):
    for y in range(max(0,y0), min(H,y1)):
        row = px[y]
        for x in range(max(0,x0), min(W,x1)):
            row[x][:] = r, g, b, a

def sign(a,b,c): return (a[0]-c[0])*(b[1]-c[1]) - (b[0]-c[0])*(a[1]-c[1])

def fill_tri(p1, p2, p3, r, g, b, a=255):
    xs = [p1[0],p2[0],p3[0]]
    ys = [p1[1],p2[1],p3[1]]
    xmin = max(0, min(xs))
    xmax = min(W-1, max(xs))
    ymin = max(0, min(ys))
    ymax = min(H-1, max(ys))
    for y in range(ymin, ymax+1):
        row = px[y]
        for x in range(xmin, xmax+1):
            w0 = sign((x,y), p2, p3)
            w1 = sign((x,y), p3, p1)
            w2 = sign((x,y), p1, p2)
            if (w0>=0 and w1>=0 and w2>=0) or (w0<=0 and w1<=0 and w2<=0):
                row[x][:] = r, g, b, a

def hex_verts(cx, cy, r, rot=0):
    return [(int(cx+r*math.cos(rot+i*math.pi/3)), int(cy+r*math.sin(rot+i*math.pi/3))) for i in range(6)]

def fill_poly(verts, r, g, b, a):
    xs = [v[0] for v in verts]
    ys = [v[1] for v in verts]
    ymin, ymax = max(0, min(ys)), min(H-1, max(ys))
    for y in range(ymin, ymax+1):
        ix = []
        for i in range(len(verts)):
            x1,y1 = verts[i]
            x2,y2 = verts[(i+1)%len(verts)]
            if (y1 <= y < y2) or (y2 <= y < y1):
                if y1 != y2:
                    ix.append(x1 + (y-y1)*(x2-x1)/(y2-y1))
        ix.sort()
        for k in range(0, len(ix)-1, 2):
            x0, x1 = int(ix[k]), int(ix[k+1])
            for x in range(max(0,x0), min(W,x1+1)):
                px[y][x][:] = r, g, b, a

# === RENDER ===
cx = cy = W//2

# Background
for y in range(H):
    t = y/H
    r0, g0, b0 = int(10+15*t), int(12+18*t), int(30+25*t)
    row = px[y]
    for x in range(W):
        row[x][:] = r0, g0, b0, 255

sr = 110

# Outer glow
fill_ring(cx, cy, sr+8, sr, 0, 160, 255, 35)
# Shield bg
fill_circle(cx, cy, sr, 8, 28, 55, 255)
# Hexagon
verts = hex_verts(cx, cy, sr-10, -math.pi/6)
fill_poly(verts, 12, 55, 110, 190)

# Hex border glow
for i in range(6):
    x1,y1 = verts[i]
    x2,y2 = verts[(i+1)%6]
    for t in range(60):
        f = t/60
        x, y = int(x1+(x2-x1)*f), int(y1+(y2-y1)*f)
        for dx,dy in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
            setp(x+dx,y+dy, 0, 210, 255, 120)
        setp(x,y, 0, 240, 255, 255)

# Chevron
fill_tri((cx-65,cy+30), (cx,cy-35), (cx+65,cy+30), 0, 200, 255, 230)
fill_tri((cx-45,cy+18), (cx,cy-18), (cx+45,cy+18), 8, 28, 55, 255)

# S dots
for dx,dy in [(-5,-10),(-5,0),(-5,10),(5,10),(5,0),(5,-10)]:
    fill_circle(cx+dx, cy-35+dy, 2, 0, 240, 255, 255)

# Spots
for ax,ay,ar in [(cx-88,cy-75,2),(cx+88,cy-75,2),(cx-98,cy,2),(cx+98,cy,2),
              (cx-82,cy+78,2),(cx+82,cy+78,2),(cx-52,cy-95,2),(cx+52,cy-95,2),(cx,cy+100,2)]:
    fill_circle(ax, ay, ar, 0, 200, 255, 160)

# Scanlines
for sy in [cy-50, cy-20, cy+5, cy+40]:
    for x in range(cx-75, cx+75):
        alpha = max(0, 150 - abs(x-cx))
        if alpha > 0:
            setp(x, sy, 0, 220, 190, alpha//4)

# Bottom bars
by = cy + 85
bw, bg = 18, 3
bhs = [5, 12, 16, 10, 4]
bx0 = cx - (5*bw+4*bg)//2
for i,bh in enumerate(bhs):
    bx = bx0 + i*(bw+bg)
    fill_rect(bx, by-bh, bx+bw, by, 0, 180+bh*4, 255, 200)

# Checkmark
fill_tri((cx,by+6), (cx-10,by-2), (cx+10,by-2), 0, 200, 255, 80)

# Outer rings
for i in range(2):
    r = sr + 18 + i*8
    fill_ring(cx, cy, r, r-2, 0, 200, 255, max(0, 30-i*10))

# Canvas scanlines
for y in range(0, H, 3):
    row = px[y]
    for x in range(W):
        r,g,b,a = row[x]
        row[x][:] = max(0,r-5), max(0,g-6), max(0,b-8), a

# Flatten
flat = [px[y][x] for y in range(H) for x in range(W)]
png_data = create_png(W, H, flat)
out = '/home/agentuser/.openclaw/workspace/security_lead/stella_avatar.png'
with open(out, 'wb') as f:
    f.write(png_data)
print(f"Done: {len(png_data)} bytes -> {out}")
