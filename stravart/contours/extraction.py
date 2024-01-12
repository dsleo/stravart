import cv2
import numpy as np
import matplotlib.pyplot as plt

def plot_contours(image, contours):
    cv2.drawContours(image, contours, -1, (0, 255, 0), 2)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    plt.imshow(image_rgb)
    plt.title("Largest Contour in Red")
    plt.show()

def get_contour(image_path, show=False):
    """Extract contours from an image"""
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Could not open or find the image")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (9, 9), 0)
    edged = cv2.Canny(blurred, 10, 100)

    # Find contours using full hierarchy
    contours, _ = cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    if show:
        plot_contours(image, contours)

    return contours

def find(parent, i):
    if parent[i] == i:
        return i
    return find(parent, parent[i])

def union(parent, rank, x, y):
    xroot = find(parent, x)
    yroot = find(parent, y)

    if rank[xroot] < rank[yroot]:
        parent[xroot] = yroot
    elif rank[xroot] > rank[yroot]:
        parent[yroot] = xroot
    else:
        parent[yroot] = xroot
        rank[xroot] += 1

def contours_share_point(contour1, contour2):
    return any(np.any(np.all(point == contour2, axis=2)) for point in contour1)

def min_distance(contour1, contour2):
        c1 = contour1.reshape(-1, 2)
        c2 = contour2.reshape(-1, 2)
        return np.min([np.linalg.norm(x-y) for x in c1 for y in c2])

def intersect(contour1, contour2):
    # Find the point of intersection between two contours
    for point in contour1:
        if point in contour2:
            return point
    return None

def merge_contours(contours):
    n = len(contours)
    parent = [i for i in range(n)]
    rank = [0] * n

    # Merge contours with shared points
    for i in range(n):
        for j in range(i + 1, n):
            if contours_share_point(contours[i], contours[j]):
                union(parent, rank, i, j)

    # Merge contours in the same set
    merged_contours = {}
    for i in range(n):
        idx = find(parent, i)
        if idx in merged_contours:
            # Find the intersection point and insert the second contour from there
            intersection_point = intersect(merged_contours[idx], contours[i])
            intersection_idx = merged_contours[idx].index(intersection_point)
            merged_contours[idx] = np.insert(merged_contours[idx], intersection_idx + 1, contours[i], axis=0)
        else:
            merged_contours[idx] = contours[i]

    return [merged for merged in merged_contours.values()]


def get_contours_distance(contours):
    num_contours = len(contours)
    contour_distances = np.zeros((num_contours, num_contours))
    for i in range(num_contours):
        for j in range(i + 1, num_contours):  # Start from i+1 to avoid self-comparison
            distance = min_distance(contours[i], contours[j])
            contour_distances[i, j] = distance
            contour_distances[j, i] = distance
    return contour_distances

def merge_contours_from_specific(contours, contour_ix, threshold):
    n = len(contours)
    if n <= 1 or contour_ix >= n:
        return contours

    start_contour = contours[contour_ix]
    merged_contours = [start_contour]

    # Function to merge contours based on distance to the start contour
    def should_merge_with_start(contour):
        return min_distance(start_contour, contour) < threshold

    # Merge contours that are close to the start contour
    for i, contour in enumerate(contours):
        if i != contour_ix and should_merge_with_start(contour):
            merged_contours.append(contour)

    # Combine all merged contours into one
    final_contour = np.vstack(merged_contours)

    return final_contour

def get_largest_contour(contours, threshold):
    merged_contours = merge_contours(contours)
    contour_ix  = max(range(len(merged_contours)), key=lambda i: len(merged_contours[i]))

    return merge_contours_from_specific(contours=contours, contour_ix=contour_ix, threshold=threshold)