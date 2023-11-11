import PySimpleGUI as sg
from PIL import Image, ImageDraw
from DS_Street import list_pho
from DS_Street import Destinations
from Xu_Ly_Danh_Sach_Dinh_Ke import matran_dinhke
from DS_Node import danh_sach_node
from DS_Node import Node
from Astar import Astar
import copy
import time
import math


# Set up: line 16
# Functions: line 104
# Event handler: line 625


##################         Set up           ###################
# variables
sg.set_options(font=("Arial Bold", 10))
mapsize = 750
markersize = 40
rate = mapsize / float(2928)
# initial values
buttonChooseDi = buttonChooseDen = 0
nearest = nearDi = nearDen = Destinations("Rỗng", 0, 0, "", [], 0)
chDi = chDen = (0, 0)
# direction box
# global directionLines, directionList
directionList = []
directionLines = ""

# resize map (not recommended)
img = Image.open("BTL AI\\Pics\\HANGMA_GUIcopy.png")
imm = img.resize((mapsize, mapsize))
imm.save("BTL AI\\Pics\\resized.png")


# combobox values
itemsPho = []  # list pho
for pho in list_pho:
    itemsPho.append(pho.ten_pho)
    
itemsDiaDiemFull = []  # list ALL destinations
dicStreet = {}  # map: pho - id pho
dicDes = {}  # map: ten+diachi - destination

# mapping
for pho in list_pho:
    dicStreet[pho.ten_pho] = pho.id
    for d in pho.danh_sach_dia_diem:
        if "Unknown" not in d.ten_dia_diem:
            line = d.ten_dia_diem + ", " + d.address
        else:
            line = d.address
        itemsDiaDiemFull.append(line)
        dicDes[line] = d
        p = (d.vi_tri_x, d.vi_tri_y)


# elements & layout
col_1 = [
        [sg.Graph(canvas_size=(mapsize, mapsize), graph_bottom_left=(0, 0),
                  graph_top_right=(mapsize, mapsize),
                  enable_events=True,  # mouse click events
                  key="-GRAPH-", pad=15)]
]

col_2 = [
        [sg.Text(text='Xuất phát', size=(8, 0)),
         sg.Combo(values=itemsPho, size=(20, 5),
                  key="-ComboPhoDi-", enable_events=True),
         sg.Combo(values=itemsDiaDiemFull, size=(40, 5), key="-ComboDiaDiemDi-", enable_events=True)],

        [sg.Text("", size=(8, 2)), sg.Button("Chọn trên bản đồ",
                                             key="-ChooseDi-", button_color=('white', 'DarkMagenta'))],

        [sg.Text(text='Điểm đến', size=(8, 0)),
         sg.Combo(values=itemsPho, size=(20, 5),
                  key="-ComboPhoDen-", enable_events=True),
         sg.Combo(values=itemsDiaDiemFull, size=(40, 5), key="-ComboDiaDiemDen-", enable_events=True)],

        [sg.Text("", size=(8, 2)), sg.Button("Chọn trên bản đồ",
                                             key="-ChooseDen-", button_color=('white', 'DarkMagenta'))],

        [sg.Button("Reset", size=(7, 0)),
         sg.Button("Tìm đường", size=(19, 0))],

        [sg.Text("Chỉ dẫn:", size=(8, 2)), sg.Multiline(
            "", size=(64, 10), key='-Direction-')]
]

layout = [
    [sg.Column(col_1), sg.Column(
        col_2, vertical_alignment="top", pad=15, justification="left")]
]

window = sg.Window('Tìm đường Hàng Mã', layout, finalize=True, margins=(0, 0))


# import map on graph
graph = window["-GRAPH-"]
image = graph.draw_image(filename="BTL AI\\Pics\\resized.png", location=(0, mapsize))


##################         Functions          ###################

# change coordinate
def changeCoor(x1, x2):
    x = round(x1*rate)
    y = mapsize - round(x2*rate)
    return x, y


# borderlines:
def d1(p):  # inside < 0
    x, y = p
    return y+0.04*x-656
def d2(p):  # inside < 0
    x, y = p
    return y+1.55*x-1297
def d3(p):      # inside > 0
    x, y = p
    return y-0.12*x-148
def d4(p):      # inside > 0
    x, y = p
    return y-5.39*x+1785
def d5(p):      # inside > 0
    x, y = p
    return y+0.02*x-28
def d6(p):  # inside < 0
    x, y = p
    return y-7.32*x+369
def d7(p):  # inside < 0
    x, y = p
    return y+0.03*x-586
def d8(p):  # inside < 0
    x, y = p
    return y-2.52*x-42


# reset everything
def reset():
    # reset variables
    global buttonChooseDi, buttonChooseDen, nearest, nearDi, nearDen, directionList, directionLines
    buttonChooseDi = buttonChooseDen = 0
    nearest = nearDi = nearDen = Destinations("init val", 0, 0, "", [], 0)
    directionLines = ""
    directionList = []

    # reset GUI
    window["-ComboPhoDi-"].update('')
    window["-ComboDiaDiemDi-"].update(values=itemsDiaDiemFull)
    window["-ComboPhoDen-"].update('')
    window["-ComboDiaDiemDen-"].update(values=itemsDiaDiemFull)
    
    window['-GRAPH-'].erase()
    image = graph.draw_image(
        filename="BTL AI\\Pics\\resized.png", location=(0, mapsize))

    window["-ChooseDi-"].update(button_color=('white', 'DarkMagenta'))
    window["-ChooseDen-"].update(button_color=('white', 'DarkMagenta'))
    
    window["-Direction-"].update("")


# chosen point is outside the map
def choose_again():
    sg.popup_ok("Địa điểm này nằm ngoài Hàng Mã\nHãy chọn lại",
                title="Sai địa điểm!", font=("Arial", 12))
    reset()


# check if chosen point is inside the map
def in_hang_ma(x1, x2):
    p = (x1, x2)
    if (d1(p) > 0 or d2(p) > 0 or (d3(p) < 0 and d4(p) < 0) or d5(p) < 0 or d6(p) > 0 or (d7(p) > 0 and d8(p) > 0)):
        return 0
    return 1

        
# 1 left - 2 right - 0 straight
def orientation(A, B, C):
    v1 = [B[0] - A[0], B[1] - A[1]]
    v2 = [C[0] - B[0], C[1] - B[1]]

    length1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
    length2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2)

    dot_product = v1[0] * v2[0] + v1[1] * v2[1]
    cos_angle = dot_product / (length1 * length2)
    angle = math.acos(cos_angle)*180/(math.pi)
    if 25 < angle < 155:
        cross_product = v1[0] * v2[1] - v1[1] * v2[0]
        if cross_product > 0:
            return 1
        elif cross_product < 0:
            return 2
    else:
        return 0
        
        
# find ten_pho of the two nodes      
def findPho(node1, node2):
    for pho in node1.danh_sach_duong:
        for ppho in node2.danh_sach_duong:  
            if ppho == pho:
                return ppho.ten_pho


def lay_duong( vv):
    ppp = vv.danh_sach_duong
    l = ""
    for i in range(len(ppp)):
       l += ppp[i].ten_pho +" "
    return l



def ve(path, dsn, mtdk,directionLines):
    i=0
    # 0 - 2
    if path[i] == 0 and path[i+1] == 2:
       directionLines= draw_0_2(directionLines)
    # 5 - 9
    elif mtdk[path[i]][path[i+1]] == 6:
        if dsn[path[i]].vi_tri_y > dsn[path[i+1]].vi_tri_y:
            draw_5_9(dsn[path[i]], dsn[path[i+1]])
        else:
            draw_5_9(dsn[path[i+1]], dsn[path[i]])
        des1 = (dsn[path[i]].vi_tri_x, dsn[path[i]].vi_tri_y)
        des2 = (dsn[path[i+1]].vi_tri_x, dsn[path[i+1]].vi_tri_y)
        graph.draw_circle(des1, 3, fill_color='blue',
                            line_color='blue', line_width=3)
        graph.draw_circle(des2, 3, fill_color='blue',
                            line_color='blue', line_width=3)
    # ngo 8 LND
    elif mtdk[path[i]][path[i+1]] == 15 and ((dsn[path[i]].ten_dinh_nut == 4 and dsn[path[i+1]].vi_tri_x == round(755*rate)) or (dsn[path[i+1]].ten_dinh_nut == 4 and dsn[path[i]].vi_tri_x == round(755*rate))):
        drawNgo8(dsn[path[i]], dsn[path[i+1]])
        des1 = (dsn[path[i]].vi_tri_x, dsn[path[i]].vi_tri_y)
        des2 = (dsn[path[i+1]].vi_tri_x, dsn[path[i+1]].vi_tri_y)
        graph.draw_circle(des1, 3, fill_color='blue',
                            line_color='blue', line_width=3)
        graph.draw_circle(des2, 3, fill_color='blue',
                            line_color='blue', line_width=3)
        
    # normal edges
    else:
        des1 = (dsn[path[i]].vi_tri_x, dsn[path[i]].vi_tri_y)
        des2 = (dsn[path[i+1]].vi_tri_x, dsn[path[i+1]].vi_tri_y)
        graph.draw_circle(des1, 3, fill_color='blue',
                            line_color='blue', line_width=3)
        graph.draw_line(des1, des2, color="blue", width=4)
        graph.draw_circle(des2, 3, fill_color='blue',
                            line_color='blue', line_width=3)

    return directionLines
# draw way
def draw_way(xuatPhat, dichDen):
    x1 = xuatPhat.vi_tri_x
    x2 = xuatPhat.vi_tri_y
    p1 = (x1, x2)

    x3 = dichDen.vi_tri_x
    x4 = dichDen.vi_tri_y
    p2 = (x3, x4)
    global directionLines,directionList
    directionLines = ""
    # draw start point
    # comboDi, comboDen
    if buttonChooseDi == 0 and buttonChooseDen == 0:
        graph.draw_circle(p1, 2, fill_color=None,
                          line_color="Blue", line_width=3)
        graph.draw_circle(p1, 8, fill_color=None,
                          line_color="Blue", line_width=3)
        window.refresh()
        time.sleep(1)
    # comboDi, chooseDen
    if buttonChooseDi == 0 and buttonChooseDen == 1:
        graph.draw_circle(p1, 2, fill_color=None,
                          line_color="Blue", line_width=3)
        graph.draw_circle(p1, 8, fill_color=None,
                          line_color="Blue", line_width=3)
        window.refresh()
        time.sleep(1)
    # chooseDi, comboDen
    if buttonChooseDi == 1 and buttonChooseDen == 0:
        draw_dotted_line(chDi, q1, 5, 5, 'blue')
        graph.draw_circle(q1, 3, fill_color='blue',
                            line_color='blue', line_width=3)
        linee = "- Đi bộ ra " + Xuatphat.address
        directionList.append(linee)
        directionLines += linee + "\n"
        window["-Direction-"].update(directionLines)
        window.refresh()
        time.sleep(1)
    # chooseDi, chooseDen
    if buttonChooseDi == 1 and buttonChooseDen == 1:
        draw_dotted_line(chDi, q1, 5, 5, 'blue')
        graph.draw_circle(q1, 3, fill_color='blue',
                            line_color='blue', line_width=3)
        linee = "- Đi ra " +xuatPhat.address
        directionList.append(linee)
        directionLines += linee + "\n"
        window["-Direction-"].update(directionLines)
        window.refresh()
        time.sleep(1)

    # Add new nodes to matran_dinhke
    mtdk = copy.deepcopy(matran_dinhke)
    dsn = copy.deepcopy(danh_sach_node)

    desDi = Node(len(dsn), xuatPhat.vi_tri_x, xuatPhat.vi_tri_y, [])
    #densDi.danh_sach_duong.append(xuatPhat.address)
    desDen = Node(len(dsn)+1, dichDen.vi_tri_x, dichDen.vi_tri_y, [])
    #densDen.danh_sach_duong.append(dichDen.address)

    dsn.append(desDi)
    dsn.append(desDen)

    a = dsn.index(desDi)
    b = dsn.index(desDen)
    x = xuatPhat.danh_sach_dinh_ke[0]
    y = xuatPhat.danh_sach_dinh_ke[1]
    z = dichDen.danh_sach_dinh_ke[0]
    t = dichDen.danh_sach_dinh_ke[1]

    if y == -1:
        mtdk[x][a] = mtdk[a][x] = xuatPhat.thuoc_pho
    else:
        if mtdk[y][x] != -2:
            mtdk[x][a] = mtdk[a][x] = mtdk[y][a] = mtdk[a][y] = mtdk[y][x]
        else:
            mtdk[x][a] = mtdk[a][y] = mtdk[x][y]

    if t == -1:
        mtdk[z][b] = mtdk[b][z] = dichDen.thuoc_pho
    else:
        if mtdk[t][z] != -2:
            mtdk[z][b] = mtdk[b][z] = mtdk[t][b] = mtdk[b][t] = mtdk[t][z]
        else:
            mtdk[z][b] = mtdk[b][t] = mtdk[z][t]

    if x == z and y == t:
        if y == -1:
            if dist(desDi.vi_tri_x, desDi.vi_tri_y, dsn[x].vi_tri_x, dsn[x].vi_tri_y) < dist(desDen.vi_tri_x, desDen.vi_tri_y, dsn[x].vi_tri_x, dsn[x].vi_tri_y):
                mtdk[x][b] = mtdk[b][x] = -2
                mtdk[a][b] = mtdk[b][a] = dichDen.thuoc_pho
            else:
                mtdk[x][a] = mtdk[a][x] = -2
                mtdk[a][b] = mtdk[b][a] = dichDen.thuoc_pho
        else:
            if mtdk[y][x] != -2:
                mtdk[a][b] = mtdk[b][a] = mtdk[x][y]
            else:
                if dist(desDi.vi_tri_x, desDi.vi_tri_y, dsn[x].vi_tri_x, dsn[x].vi_tri_y) < dist(desDen.vi_tri_x, desDen.vi_tri_y, dsn[x].vi_tri_x, dsn[x].vi_tri_y):
                    mtdk[x][b] = mtdk[a][y] = -2
                    mtdk[x][a] = mtdk[a][b] = mtdk[b][y] = mtdk[x][y]
                else:
                    mtdk[x][a] = mtdk[b][y] = -2
                    mtdk[x][b] = mtdk[b][a] = mtdk[a][y] = mtdk[x][y]

    # apply A*
    path = Astar(mtdk, dsn, 22, 23)
    # 0 2: duong ngang pho Quan Thanh
    p= []
    chihuong = []
    for i in range(len(path)-2):
        pre = (dsn[path[i]].vi_tri_x, dsn[path[i]].vi_tri_y) # previous node 
        cur = (dsn[path[i+1]].vi_tri_x, dsn[path[i+1]].vi_tri_y) # current node
        nex = (dsn[path[i+2]].vi_tri_x, dsn[path[i+2]].vi_tri_y) # next node
        ori = orientation(pre, cur, nex)
        print(ori)
        if(path[i+1]==0 and path[i+2]==2): ori = 3
        if(path[i]==0 and path[i+1]==2): ori = 4
        p.append((path[i],path[i+1],ori))
    p.append((path[len(path)-2],path[-1],-1))

        
        
            
    
    # draw path
    i = 0
    li=directionLines
    while i<len(p)-1:
        if(p[i][0]!=0 or p[i][1]!=2):
            
            li += "Đi thẳng "+ list_pho[mtdk[p[i][0]][p[i][1]]].ten_pho +" đến "
            while(p[i][2]==0):
                ve((p[i][0],p[i][1]),dsn,mtdk,li)
                i +=1
            if i<len(p)-1:
                if(p[i][2]==3):
                    ve((p[i][0],p[i][1]),dsn,mtdk,li)
                    li += "ngã rẽ "+ lay_duong(dsn[0])+"phố Hàng Đậu \n"
                    if mtdk[p[i][0]][p[i][1]]==5:
                    
                        li += "Rẽ phải vào phố Hàng Đậu\n"
                        window["-Direction-"].update(li)
                        window.refresh()
                        time.sleep(1)
                        li += "Đi thẳng phố Hàng Đậu đến ngã rẽ phố Hàng Than phố Hàng Đậu\n"
                        li = ve((p[i+1][0],p[i+1][1]),dsn,mtdk,li)
                        if(mtdk[p[i+2][0]][p[i+2][1]]==1):
                            li += "Đi thẳng phố Phan Đình Phùng đến ngã rẽ phố Lý Nam Đế phố Phan Đình Phùng\n" 
                            li += "Rẽ phải vào phố Lý Nam Đế \n"
                            window["-Direction-"].update(li)
                            window.refresh()
                            time.sleep(1)
                    else:
                        window.refresh()
                        time.sleep(1)
                        li +="Đi thẳng vào phố Hằng Đậu đến ngã rẽ phố Hàng Than phố Hàng Đậu\n"
                        window["-Direction-"].update(li)
                        li = ve((p[i+1][0],p[i+1][1]),dsn,mtdk,li)
                        if(mtdk[p[i+2][0]][p[i+2][1]]==1): 
                            li += "Đi thẳng phố Phan Đình Phùng đến ngã rẽ phố Lý Nam Đế phố Phan Đình Phùng\n" 
                            li += "Rẽ phải vào phố Lý Nam Đế \n"
                            window["-Direction-"].update(li)
                            window.refresh()
                            time.sleep(1)
                else:
                    ve((p[i][0],p[i][1]),dsn,mtdk,li)
                    li += "ngã rẽ "+ lay_duong(dsn[p[i][1]])+"\n"
                    if(p[i][2]==1):
                        li += "Rẽ trái vào " +list_pho[mtdk[p[i+1][0]][p[i+1][1]]].ten_pho +  "\n"
                    else: 
                        li += "Rẽ phải vào " +list_pho[mtdk[p[i+1][0]][p[i+1][1]]].ten_pho +  "\n"
                    window["-Direction-"].update(li)
                    window.refresh()
                    time.sleep(1)
        i +=1
    
    i= len(p)-1
    ve((p[i][0],p[i][1]),dsn,mtdk,directionLines)
    if(p[i-1][2]!=0): li += "Đi thẳng " + list_pho[mtdk[p[i][0]][p[i][1]]].ten_pho +" đến "
    li +=  dichDen.address
    window["-Direction-"].update(li)
    window.refresh()
    time.sleep(1)
    directionLines = li+"\n"




        


    # for i in range(len(path)-1):
        

    #     # left-right orientation
    #     ngaRe = ""
    #     # node 22 - first node in path list
    #     if i == 0:
    #         for j in range(len(path)-2):
    #             if path[j-1] == 0 and path[j] == 2:
    #                 ngaRe = "Phố Phan Đình Phùng, Phố Hàng Cót"
    #                 break
    #             else:
    #                 cur = (dsn[path[j]].vi_tri_x, dsn[path[j]].vi_tri_y) # current node
    #                 nex = (dsn[path[j+1]].vi_tri_x, dsn[path[j+1]].vi_tri_y) # next node
    #                 nexx = (dsn[path[j+2]].vi_tri_x, dsn[path[j+2]].vi_tri_y) # next next node
    #                 ori = orientation(cur, nex, nexx)
    #                 if ori == 1 or ori == 2:
    #                     break 
    #         if j != len(path)-2:   
    #             for pho in dsn[path[j+1]].danh_sach_duong:
    #                 ngaRe += pho.ten_pho + ", "
    #             linee = "- Đi thẳng đến ngã rẽ " + ngaRe.rstrip(", ")
    #             directionList.append(linee)
    #             directionLines += linee + "\n"
    #             window["-Direction-"].update(directionLines)
    #         # node 23 doesnt have danh_sach_duong
    #         else:
    #             linee = "- Đi thẳng theo " + \
    #                 findPho(dsn[path[j]], dsn[path[j+1]])
    #             directionList.append(linee)
    #             directionLines += linee + "\n"
    #             window["-Direction-"].update(directionLines)
                
    #     # node before 23 in path list
    #     if i == len(path)-2:
    #         pre = (dsn[path[i-1]].vi_tri_x, dsn[path[i-1]].vi_tri_y) # previous node 
    #         cur = (dsn[path[i]].vi_tri_x, dsn[path[i]].vi_tri_y) # current node
    #         nex = (dsn[path[i+1]].vi_tri_x, dsn[path[i+1]].vi_tri_y) # next node
            
    #         # orientation: 1 left - 2 right - 0 straight
    #         ori = orientation(pre, cur, nex)
    #         if ori == 1:
    #             linee = "- Rẽ trái vào " + list_pho[dichDen.thuoc_pho].ten_pho
    #             directionList.append(linee)
    #             directionLines += linee + "\n"
    #             window["-Direction-"].update(directionLines)
    #         elif ori == 2:
    #             linee = "- Rẽ phải vào " + list_pho[dichDen.thuoc_pho].ten_pho
    #             directionList.append(linee)
    #             directionLines += linee + "\n"
    #             window["-Direction-"].update(directionLines)
    #         else:
    #             linee = "- Đi thẳng theo " + \
    #                 list_pho[dichDen.thuoc_pho].ten_pho
    #             directionList.append(linee)
    #             directionLines += linee + "\n"
    #             window["-Direction-"].update(directionLines)
            
    #     # nodes between 22 and 23
    #     if 0 < i < len(path)-2:
    #         if path[i] == 0 and path[i+1] == 2:
    #             linee = "- Đi thẳng Phố Hàng Đậu, vòng qua Phố Thánh Quán, quay về Phố Phan Đình Phùng"
    #             directionList.append(linee)
    #             directionLines += linee + "\n"
    #             window["-Direction-"].update(directionLines)
    #         else:    
    #             pre = (dsn[path[i-1]].vi_tri_x, dsn[path[i-1]].vi_tri_y) # previous node 
    #             cur = (dsn[path[i]].vi_tri_x, dsn[path[i]].vi_tri_y) # current node
    #             nex = (dsn[path[i+1]].vi_tri_x, dsn[path[i+1]].vi_tri_y) # next node
                
    #             #orientation: 1 left - 2 right - 0 straight
    #             ori = orientation(pre, cur, nex)
    #             if ori == 1:
    #                 linee = "- Rẽ trái vào " + \
    #                     findPho(dsn[path[i]], dsn[path[i+1]])
    #                 directionList.append(linee)
    #                 directionLines += linee + "\n"
    #                 window["-Direction-"].update(directionLines)
                    
    #             elif ori == 2:
    #                 linee = "- Rẽ phải vào " + findPho(dsn[path[i]], dsn[path[i+1]])
    #                 directionList.append(linee)
    #                 directionLines += linee + "\n"
    #                 window["-Direction-"].update(directionLines)
                    
    #             else:
    #                 if "Đi thẳng đến ngã rẽ" not in directionList[len(directionList)-1]:
    #                     for j in range(i, len(path)-2):
    #                         if path[j] == 0 and path[j+1] == 2:
    #                             ngaRe = "Phố Phan Đình Phùng, Phố Hàng Cót"
    #                         else:
    #                             cur = (dsn[path[j]].vi_tri_x, dsn[path[j]].vi_tri_y)
    #                             nex = (dsn[path[j+1]].vi_tri_x, dsn[path[j+1]].vi_tri_y)
    #                             nexx = (dsn[path[j+2]].vi_tri_x, dsn[path[j+2]].vi_tri_y)
    #                             ori = orientation(cur, nex, nexx)
    #                             if ori == 1 or ori == 2:
    #                                 break
                            
    #                     if j != len(path)-2:     
    #                         for pho in dsn[path[j+1]].danh_sach_duong:
    #                             ngaRe += pho.ten_pho + ", "   
    #                         linee = "- Đi thẳng đến ngã rẽ " + ngaRe.rstrip(", ")
    #                         directionList.append(linee)
    #                         directionLines += linee + "\n"
    #                         window["-Direction-"].update(directionLines)
    #                     # node 23 doesnt have danh_sach_duong
    #                     else:
    #                         linee = "- Đi thẳng theo " + \
    #                         findPho(dsn[path[j]], dsn[path[j+1]])
    #                         directionList.append(linee)
    #                         directionLines += linee + "\n"
    #                         window["-Direction-"].update(directionLines)
                

    
    #     # delay 1s
    #     if(i<len(path)-3):

    #         pre = (dsn[path[i]].vi_tri_x, dsn[path[i-1]].vi_tri_y) # previous node 
    #         cur = (dsn[path[i+1]].vi_tri_x, dsn[path[i]].vi_tri_y) # current node
    #         nex = (dsn[path[i+2]].vi_tri_x, dsn[path[i+1]].vi_tri_y) # next node
    #         pre1 = (dsn[path[i+1]].vi_tri_x, dsn[path[i-1]].vi_tri_y) # previous node 
    #         cur1 = (dsn[path[i+2]].vi_tri_x, dsn[path[i]].vi_tri_y) # current node
    #         nex1 = (dsn[path[i+3]].vi_tri_x, dsn[path[i+1]].vi_tri_y) # next node
    #         ori = orientation(pre, cur, nex)
    #         ori1 = orientation(pre1, cur1, nex1)
    #         if(ori !=0 or ori1 !=0):
    #             window.refresh()
    #             time.sleep(1)
        
        
    # draw end point
    # comboDi, comboDen
    if buttonChooseDi == 0 and buttonChooseDen == 0:
        graph.draw_image(filename="BTL AI\\Pics\\resized_marker.png",
                         location=(p2[0]-19, p2[1]+37))
        linee = "- ĐÃ ĐẾN!!!"
        directionList.append(linee)
        directionLines += linee + "\n"
        window["-Direction-"].update(directionLines)
    # comboDi, chooseDen
    if buttonChooseDi == 0 and buttonChooseDen == 1:
        draw_dotted_line(chDen, q2, 5, 5, 'blue')
        graph.draw_circle(q2, 3, fill_color='blue',
                            line_color='blue', line_width=3)
        graph.draw_image(filename="BTL AI\\Pics\\resized_marker.png",
                            location=(chDen[0]-19, chDen[1]+37))
        linee = "- Đi vào là đến!!!"
        directionList.append(linee)
        directionLines += linee + "\n"
        window["-Direction-"].update(directionLines)    
    # chooseDi, comboDen
    if buttonChooseDi == 1 and buttonChooseDen == 0:
        graph.draw_image(filename="BTL AI\\Pics\\resized_marker.png",
                         location=(p2[0]-19, p2[1]+37))
        linee = "- ĐÃ ĐẾN!!!"
        directionList.append(linee)
        directionLines += linee + "\n"
        window["-Direction-"].update(directionLines)
    # chooseDi, chooseDen
    if buttonChooseDi == buttonChooseDen == 1:
        draw_dotted_line(chDen, q2, 5, 5, 'blue')
        graph.draw_image(filename="BTL AI\\Pics\\resized_marker.png",
                            location=(chDen[0]-19, chDen[1]+37))
        linee = "- Đi vào là đến!!!"
        directionList.append(linee)
        directionLines += linee + "\n"
        window["-Direction-"].update(directionLines)
        
        
def draw_0_2(directionLines):
    graph.draw_line((1670*rate, mapsize - 425*rate),
                    (1930*rate, mapsize - 355*rate), color="blue", width=4)
    directionLines +="Rẽ trái vào phố Hàng Than\n"
    window["-Direction-"].update(directionLines)
    window.refresh()
    time.sleep(1)
    
    graph.draw_line((1930*rate, mapsize - 355*rate),
                    (1880*rate, mapsize - 210*rate), color="blue", width=4)
    directionLines += "Đi thẳng phố Hàng Than đến ngã rẽ phố Quán Thánh phố Hàng Than\n" +"Rẽ trái vào phố Quán Thánh\n"
    window["-Direction-"].update(directionLines)
    window.refresh()
    time.sleep(1)
    graph.draw_line((1880*rate, mapsize - 210*rate),
                    (1677*rate, mapsize - 216*rate), color="blue", width=4)
    graph.draw_line((1677*rate, mapsize - 216*rate), (915*rate,
                    mapsize - 125*rate), color="blue", width=4)
    directionLines +="Đi thẳng phố Quán Thánh đến ngã rẽ phồ Hòe Nhai phố Quán Thánh\n" +"Rẽ trái vào phố Hòa Nhai\n"
    window["-Direction-"].update(directionLines)
    window.refresh()
    time.sleep(1)
    graph.draw_line((915*rate, mapsize - 125*rate), (845*rate,
                    mapsize - 345*rate), color="blue", width=4)
    directionLines +="Đi thẳng phố Hòe Nhai đến ngã rẽ phố Phan Đình Phùng phố Hòe Nhai\n" +"Rẽ trái vào phố Phan Đình Phùng\n"
    window["-Direction-"].update(directionLines)
    window.refresh()
    time.sleep(1)
    graph.draw_line((845*rate, mapsize - 345*rate), (1110*rate,
                    mapsize - 400*rate), color="blue", width=4)
    return directionLines


def drawNgo8(X1, X2):
    p = changeCoor(890, 921)
    graph.draw_line((X1.vi_tri_x, X1.vi_tri_y), p, color="blue", width=4)
    graph.draw_line(p, (X2.vi_tri_x, X2.vi_tri_y), color="blue", width=4)


def draw_5_9(X1, X2): # y-coordinate decreasing
    data59 = []  
    coor5 = changeCoor(1660, 1010)
    with open('BTL AI\\Toan\\NamChin.txt', 'r', encoding='utf-8') as file:
        data59.append(coor5)
        for line in file:
            line = line.strip()
            if line == '***':
                break
            l = line.split()
            x1, x2 = l[0], l[1]
            x1 = int(x1)
            x2 = int(x2)
            pi = changeCoor(x1, x2)
            data59.append(pi)

    if X1.ten_dinh_nut == 5 and X2.ten_dinh_nut == 9:
        for i in range(len(data59)-1):
            graph.draw_line(data59[i], data59[i+1], color='blue', width=4)
    elif X1.ten_dinh_nut == 5:
        i = len(data59) - 1
        while (data59[i][1] < X2.vi_tri_y):
            i -= 1
        for j in range(i):
            graph.draw_line(data59[j], data59[j+1], color='blue', width=4)
        graph.draw_line(
            data59[i], (X2.vi_tri_x, X2.vi_tri_y), color='blue', width=4)
    elif X2.ten_dinh_nut == 9:
        i = 0
        while (data59[i][1] > X1.vi_tri_y):
            i += 1
        graph.draw_line((X1.vi_tri_x, X1.vi_tri_y),
                        data59[i], color='blue', width=4)
        for j in range(i, len(data59)-1):
            graph.draw_line(data59[j], data59[j+1], color='blue', width=4)
    else:
        i = 0
        while (data59[i][1] > X1.vi_tri_y):
            i += 1
        j = len(data59) - 1
        while (data59[j][1] < X2.vi_tri_y):
            j -= 1

        graph.draw_line((X1.vi_tri_x, X1.vi_tri_y),
                        data59[i], color='blue', width=4)
        for k in range(i, j):
            graph.draw_line(data59[k], data59[k+1], color='blue', width=4)
        graph.draw_line(
            data59[j], (X2.vi_tri_x, X2.vi_tri_y), color='blue', width=4)


# draw dotted line
def draw_dotted_line(start_point, end_point, dot_size=1, gap_size=1, color='blue'):
    dx = end_point[0] - start_point[0]
    dy = end_point[1] - start_point[1]
    distance = max(abs(dx), abs(dy))
    if distance == 0:
        return

    step_x = dx / distance
    step_y = dy / distance

    for i in range(0, distance, dot_size + gap_size):
        x = int(start_point[0] + i * step_x)
        y = int(start_point[1] + i * step_y)
        x_end = int(x + dot_size * step_x)
        y_end = int(y + dot_size * step_y)
        graph.draw_line((x, y), (x_end, y_end), color=color, width=4)


# distance^2 between 2 coordinates (x1, x2) & (x3, x4)
def dist(x1, x2, x3, x4):
    return (x1-x3)**2+(x2-x4)**2


# return the nearest destination
def nearestDes(x1, x2):
    minn = round((mapsize*1.414)**2)  # length of the diagonal
    for pho in list_pho:
        for des in pho.danh_sach_dia_diem:
            x3 = des.vi_tri_x
            x4 = des.vi_tri_y
            distt = dist(x1, x2, x3, x4)
            if distt < minn:
                minn = distt
                nearest = des
    return nearest


##################         Event handler          ###################
while True:
    event, values = window.read()
    # print(event, values)
    match event:
        case sg.WINDOW_CLOSED:
            break

        # mutually dependent comboboxes: Pho -> Des
        case "-ComboPhoDi-":
            index = dicStreet[values["-ComboPhoDi-"]]
            listDes = []
            for d in list_pho[index].danh_sach_dia_diem:
                if "Unknown" not in d.ten_dia_diem:
                    line = d.ten_dia_diem + ", " + d.address
                else:
                    line = d.address
                listDes.append(line)
            window["-ComboDiaDiemDi-"].update(values=listDes)
            
        case "-ComboPhoDen-":
            index = dicStreet[values["-ComboPhoDen-"]]
            listDes = []
            for d in list_pho[index].danh_sach_dia_diem:
                if "Unknown" not in d.ten_dia_diem:
                    line = d.ten_dia_diem + ", " + d.address
                else:
                    line = d.address
                listDes.append(line)
            window["-ComboDiaDiemDen-"].update(values=listDes)

        # Choose on map -> nearDi, nearDen
        case "-ChooseDi-":
            # empty combobox
            if values["-ComboDiaDiemDi-"] != '':
                window["-ComboPhoDi-"].update('')
                window["-ComboDiaDiemDi-"].update('')

            buttonChooseDi = 1
            window["-ChooseDi-"].update(button_color=('white', 'orange'))

            # get coordinate
            event, values = window.read()
            if event == "-GRAPH-":
                chDi = values["-GRAPH-"]
                x1, x2 = chDi[0], chDi[1]

                if in_hang_ma(x1, x2):
                    # draw start point
                    graph.draw_circle(
                        chDi, 2, fill_color=None, line_color="Blue", line_width=3)
                    graph.draw_circle(
                        chDi, 8, fill_color=None, line_color="Blue", line_width=3)
                    # Des: nearDi
                    nearDi = nearestDes(x1, x2)

                else:
                    choose_again()

        case "-ChooseDen-":
            # empty combobox
            if values["-ComboDiaDiemDen-"] != '':
                window["-ComboPhoDen-"].update('')
                window["-ComboDiaDiemDen-"].update('')

            buttonChooseDen = 1
            window["-ChooseDen-"].update(button_color=('white', 'orange'))

            # get coordinate
            event, values = window.read()
            if event == "-GRAPH-":
                chDen = values["-GRAPH-"]
                x1, x2 = chDen[0], chDen[1]

                if in_hang_ma(x1, x2):
                    # draw end point
                    graph.draw_circle(
                        chDen, 4, fill_color='blue', line_color="Blue", line_width=3)
                    graph.draw_image(filename="BTL AI\\Pics\\resized_marker.png", location=(
                        chDen[0]-19, chDen[1]+37))

                    # Des: nearDen
                    nearDen = nearestDes(x1, x2)

                else:
                    choose_again()

        case "Tìm đường":
            # No start/end point
            if values["-ComboDiaDiemDi-"] == '' and buttonChooseDi == 0:
                sg.popup_ok("Hãy chọn điểm xuất phát!",
                            title="Chưa chọn địa điểm!", font=("Arial", 12))
            if values["-ComboDiaDiemDen-"] == '' and buttonChooseDen == 0:
                sg.popup_ok("Hãy chọn đích đến!",
                            title="Chưa chọn địa điểm!", font=("Arial", 12))

            # comboDi, comboDen
            if values["-ComboDiaDiemDi-"] != '' and values["-ComboDiaDiemDen-"] != '':
                xuatPhat = dicDes[values["-ComboDiaDiemDi-"]]
                dichDen = dicDes[values["-ComboDiaDiemDen-"]]

                q1 = (xuatPhat.vi_tri_x, xuatPhat.vi_tri_y)
                q2 = (dichDen.vi_tri_x, dichDen.vi_tri_y)

                if q1 == q2:
                    graph.draw_circle(q1, 2, fill_color=None,
                                      line_color="Blue", line_width=3)
                    graph.draw_circle(q1, 8, fill_color=None,
                                      line_color="Blue", line_width=3)
                    window["-Direction-"].update("ĐÃ ĐẾN!")
                else:
                    draw_way(xuatPhat, dichDen)
            # chooseDi, chooseDen
            elif buttonChooseDi == 1 and buttonChooseDen == 1:
                q1 = (nearDi.vi_tri_x, nearDi.vi_tri_y)
                q2 = (nearDen.vi_tri_x, nearDen.vi_tri_y)
                if q1 == q2:
                    window["-Direction-"].update("Đi bộ là đến!")
                    draw_dotted_line(
                        chDi, chDen, 5, 5, 'blue')
                else:
                    draw_way(nearDi, nearDen)
                    
            # comboDi, chooseDen
            elif values["-ComboDiaDiemDi-"] != '' and buttonChooseDen == 1:
                xuatPhat = dicDes[values["-ComboDiaDiemDi-"]]
                q1 = (xuatPhat.vi_tri_x, xuatPhat.vi_tri_y)
                q2 = (nearDen.vi_tri_x, nearDen.vi_tri_y)
                if q1 == q2:
                    window["-Direction-"].update("Đi bộ là đến!")
                    draw_dotted_line(
                        q1, chDen, 5, 5, 'blue')
                else:
                    draw_way(xuatPhat, nearDen)
                    
            # chooseDi, comboDen
            elif buttonChooseDi == 1 and values["-ComboDiaDiemDen-"] != '':
                dichDen = dicDes[values["-ComboDiaDiemDen-"]]
                q1 = (nearDi.vi_tri_x, nearDi.vi_tri_y)
                q2 = (dichDen.vi_tri_x, dichDen.vi_tri_y)
                if q1 == q2:
                    window["-Direction-"].update("Đi bộ là đến!")
                    draw_dotted_line(
                        chDi, q2, 5, 5, 'blue')
                else:
                    draw_way(nearDi, dichDen)

        case "Reset":
            reset()

window.close()