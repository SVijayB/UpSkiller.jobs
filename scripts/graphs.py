import networkx as nx
import matplotlib.pyplot as plt

# Define the roadmap as a tree-like structure
edges = [
    ("Arrays & Hashing", "Two Pointers"),
    ("Arrays & Hashing", "Stack"),
    ("Two Pointers", "Binary Search"),
    ("Two Pointers", "Sliding Window"),
    ("Stack", "Linked List"),
    ("Binary Search", "Trees"),
    ("Sliding Window", "Trees"),
]

# Create a directed graph
G = nx.DiGraph()
G.add_edges_from(edges)

# Plot the graph
plt.figure(figsize=(12, 8))
pos = nx.spring_layout(G, seed=42, k=0.5)  # Layout for better visualization
nx.draw(
    G,
    pos,
    with_labels=True,
    node_size=4000,
    node_color="royalblue",
    font_size=10,
    font_color="white",
    edge_color="gray",
    arrows=True,
)

plt.title("DSA Roadmap")
plt.show()
