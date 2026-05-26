import numpy as np

from vector_db.vector_loader import (
    index
)

def search_dissimilar_vectors(
    query_vector,
    top_k=5
):

    query = np.array(
        [query_vector],
        dtype="float32"
    )

    distances, indices = index.search(
        query,
        100
    )

    results = []

    for i in range(len(indices[0])):

        results.append({

    "logo_id": int(indices[0][i]),

    "logo_name": f"logo_{indices[0][i]}",

    "distance": float(distances[0][i]),

    "similarity_score": round(
        1 / (1 + distances[0][i]),
        4
    ),

    "thumbnail":

    f"/static/logo/{indices[0][i]}.png"
})

    # 거리 큰 순 = 비유사
    results.sort(
        key=lambda x: x["distance"],
        reverse=True
    )

    return results[:top_k]