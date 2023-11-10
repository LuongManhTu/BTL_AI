# def compare_distances(A, B, C): # C -> AB
#     # vector AB
#     AB_x = B[0] - A[0]
#     AB_y = B[1] - A[1]

#     # vector AC
#     AC_x = C[0] - A[0]
#     AC_y = C[1] - A[1]

#     # dot product of AB and AC
#     dot_product = AB_x * AC_x + AB_y * AC_y

#     # length of vector AB
#     length_AB = (AB_x ** 2 + AB_y ** 2) ** 0.5

#     # distance from point C to the line AB
#     distance_AB = abs(AB_x * AC_y - AB_y * AC_x) / length_AB

#     # distance from point C to the line perpendicular to AB passing through B
#     distance_B = abs(dot_product) / length_AB

#     if distance_AB > distance_B:
#         return 1
#     else:
#         return 0

# # 1 left - 2 right - 0 straight
# def orientation(A, B, C):
#     x1, y1 = A
#     x2, y2 = B
#     x3, y3 = C

#     if compare_distances(A, B, C):
#         v1 = (x2 - x1, y2 - y1)
#         v2 = (x3 - x2, y3 - y2)

#         cross_product = v1[0] * v2[1] - v1[1] * v2[0]

#         if cross_product > 0:
#             return 1
#         elif cross_product < 0:
#             return 2
#     else:
#         return 0

tu = "abc, pấc,sdádasd, "
print(tu.rstrip(", "))
