from tkinter import *

bound_x = 15
bound_y = 15
width = 50
org = 30


def draw_roads(w):
    line_num = 11
    line_len = width*(line_num-1)

    for i in range(line_num):
        x1 = bound_x + i*width
        x2 = bound_x + i*width
        y1 = bound_y
        y2 = bound_y + line_len
        w.create_line(org + x1, org + y1, org + x2, org + y2)
    for i in range(line_num):
        x1 = bound_x
        x2 = bound_x + line_len
        y1 = bound_y + i*width
        y2 = bound_y + i*width
        w.create_line(org + x1, org + y1, org + x2, org + y2)


def draw_bs(w, bs_list):
    radius = 3
    for bs in bs_list:
        x_in_canvas = bs.x/(2500/width) + bound_x
        y_in_canvas = bs.y/(2500/width) + bound_y
        w.create_oval(org + x_in_canvas - radius, org + y_in_canvas - radius, org +
                      x_in_canvas + radius, org + y_in_canvas + radius, fill="red")


def draw_single_car(w, x, y):
    radius = 3
    x_in_canvas = x/(2500/width) + bound_x
    y_in_canvas = y/(2500/width) + bound_y
    dot = w.create_oval(org + x_in_canvas - radius, org + y_in_canvas - radius, org +
                        x_in_canvas + radius, org + y_in_canvas + radius, fill="blue")
    w.update_idletasks()
    w.pack()
    return dot


def draw_connected_BS(w, cx, cy, bx, by):
    cx_in_canvas = cx/(2500/width) + bound_x
    cy_in_canvas = cy/(2500/width) + bound_y
    bx_in_canvas = bx/(2500/width) + bound_x
    by_in_canvas = by/(2500/width) + bound_y
    w.create_line(org + cx_in_canvas, org + cy_in_canvas,
                  org + bx_in_canvas, org + by_in_canvas)
