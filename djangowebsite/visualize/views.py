from django.shortcuts import render
from django.http import JsonResponse
import pandas as pd
import os
import json
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for servers
import matplotlib.pyplot as plt
from random import randint
from math import sqrt
from django.views.decorators.csrf import csrf_exempt

def home(request):
    # Assuming introduction.txt is in the root project directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    intro_path = os.path.join(os.path.dirname(base_dir), 'introduction.txt')

    with open(intro_path, 'r', encoding='utf-8') as f:
        introduction = f.read()

    return render(request, 'index.html', {'introduction': introduction})

def euclidean_dist(p1, p2):
    return sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

@csrf_exempt
def generate_frames(request):
    frame_dir = "media/frames"
    if os.path.exists(frame_dir):
        for f in os.listdir(frame_dir):
            os.remove(os.path.join(frame_dir, f))
    else:
        os.makedirs(frame_dir)

    body = json.loads(request.body)
    points = body["points"]
    epsilon = float(body["epsilon"])
    minPts = int(body["minPts"])

    df = pd.DataFrame(points)
    length = len(df)
    x = df['x'].tolist()
    y = df['y'].tolist()

    cluster_id = 0
    labels = [-1] * length
    unvisited_index = list(range(length))
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'cyan', 'magenta', 'yellow', 'brown', 'pink']
    point_colors = ['black'] * length
    frame_count = 0

    def save_frame(title, highlight_idx=None, circle_indices=None):
        nonlocal frame_count
        plt.figure(figsize=(5, 5))
        plt.scatter(df['x'], df['y'], s=40, c=point_colors)
        ax = plt.gca()

        if highlight_idx is not None:
            selected = df.iloc[highlight_idx]
            plt.scatter(selected['x'], selected['y'], facecolors='none', edgecolors='yellow', s=300, linewidths=2)
            circ = plt.Circle((selected['x'], selected['y']), epsilon, color='yellow', fill=False, linestyle='--')
            ax.add_patch(circ)

        if circle_indices:
            for idx in circle_indices:
                pt = df.iloc[idx]
                circ = plt.Circle((pt['x'], pt['y']), epsilon, color='gray', fill=False, linestyle=':')
                ax.add_patch(circ)

        plt.title(title)
        plt.xlim(0, 400)
        plt.ylim(0, 400)
        ax.set_aspect('equal')
        plt.gca().invert_yaxis()
        plt.savefig(f'{frame_dir}/frame_{frame_count}.png')
        plt.close()
        frame_count += 1

    while unvisited_index:
        random_point_index = randint(0, len(unvisited_index) - 1)
        starting_point_index = unvisited_index[random_point_index]

        save_frame(f"Before Cluster {cluster_id}", highlight_idx=starting_point_index)

        coord = df.iloc[starting_point_index]
        neighbors = []
        for i in range(length):
            if i != starting_point_index:
                if euclidean_dist([x[i], y[i]], [coord['x'], coord['y']]) <= epsilon:
                    neighbors.append(i)

        if len(neighbors) < minPts:
            labels[starting_point_index] = -1
            unvisited_index.remove(starting_point_index)
            continue

        cluster_id += 1
        unvisited_index.remove(starting_point_index)
        labels[starting_point_index] = cluster_id
        point_colors[starting_point_index] = colors[(cluster_id - 1) % len(colors)]
        queue = neighbors.copy()

        save_frame(f"Core point for Cluster {cluster_id}", highlight_idx=starting_point_index, circle_indices=neighbors)

        while queue:
            neighbors_index = queue.pop(0)
            save_frame(f"Expanding from point {neighbors_index}", highlight_idx=neighbors_index)
            if neighbors_index in unvisited_index:
                unvisited_index.remove(neighbors_index)
                labels[neighbors_index] = cluster_id
                point_colors[neighbors_index] = colors[(cluster_id - 1) % len(colors)]

                coord = df.iloc[neighbors_index]
                next_neighbors = []
                for i in range(length):
                    if i != neighbors_index and euclidean_dist([x[i], y[i]], [coord['x'], coord['y']]) <= epsilon:
                        next_neighbors.append(i)

                save_frame(f"Checking neighbors of point {neighbors_index}", highlight_idx=neighbors_index, circle_indices=next_neighbors)

                if len(next_neighbors) >= minPts:
                    queue.extend(next_neighbors)

        save_frame(f"After forming Cluster {cluster_id}")

    return JsonResponse({"frames": frame_count})
