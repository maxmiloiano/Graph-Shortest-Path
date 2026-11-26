
import tkinter as tk
from tkinter import ttk, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import heapq

# ==========================================
# 1. DATASET GRAF
# ==========================================

G = nx.Graph()

lokasi = {
    "A": "Gerbang Kampus",
    "B": "Area Parkir",
    "C": "Perpustakaan",
    "D": "Laboratorium",
    "E": "Kantin",
    "F": "Gedung Rektorat"
}

# Hubungan antarlokasi dan bobot jarak (meter)
data_edge = [
    ("A", "B", 4),
    ("A", "C", 2),
    ("B", "C", 1),
    ("B", "D", 5),
    ("C", "D", 8),
    ("C", "E", 10),
    ("D", "E", 2),
    ("D", "F", 6),
    ("E", "F", 3)
]

G.add_nodes_from(lokasi.keys())

for u, v, w in data_edge:
    G.add_edge(u, v, weight=w)


# ==========================================
# 2. ALGORITMA DIJKSTRA
# ==========================================

def dijkstra(graph, start, end):

    jarak = {node: float("inf") for node in graph.nodes}
    sebelumnya = {node: None for node in graph.nodes}

    jarak[start] = 0

    priority_queue = [(0, start)]

    while priority_queue:

        jarak_sekarang, node = heapq.heappop(priority_queue)

        if jarak_sekarang > jarak[node]:
            continue

        if node == end:
            break

        for tetangga in graph.neighbors(node):

            bobot = graph[node][tetangga]["weight"]

            jarak_baru = jarak_sekarang + bobot

            if jarak_baru < jarak[tetangga]:

                jarak[tetangga] = jarak_baru
                sebelumnya[tetangga] = node

                heapq.heappush(
                    priority_queue,
                    (jarak_baru, tetangga)
                )

    # Memeriksa apakah tujuan dapat dijangkau
    if jarak[end] == float("inf"):
        return None, float("inf")

    # Rekonstruksi jalur terpendek
    jalur = []
    node = end

    while node is not None:
        jalur.append(node)
        node = sebelumnya[node]

    jalur.reverse()

    return jalur, jarak[end]


# ==========================================
# 3. FUNGSI TAMBAH NODE
# ==========================================

def tambah_node():

    kode = entry_kode.get().strip().upper()
    nama = entry_nama.get().strip()

    if not kode or not nama:
        messagebox.showwarning(
            "Peringatan",
            "Kode dan nama lokasi harus diisi!"
        )
        return

    if kode in G.nodes:
        messagebox.showwarning(
            "Peringatan",
            "Kode lokasi sudah tersedia!"
        )
        return

    G.add_node(kode)
    lokasi[kode] = nama

    update_combobox()
    gambar_graf()

    entry_kode.delete(0, tk.END)
    entry_nama.delete(0, tk.END)

    messagebox.showinfo(
        "Berhasil",
        f"Lokasi {nama} berhasil ditambahkan."
    )


# ==========================================
# 4. FUNGSI TAMBAH EDGE
# ==========================================

def tambah_edge():

    asal = combo_asal_edge.get()
    tujuan = combo_tujuan_edge.get()

    try:
        bobot = float(entry_bobot.get())
    except ValueError:
        messagebox.showerror(
            "Error",
            "Bobot harus berupa angka!"
        )
        return

    if asal == tujuan:
        messagebox.showwarning(
            "Peringatan",
            "Lokasi asal dan tujuan tidak boleh sama!"
        )
        return

    if bobot <= 0:
        messagebox.showwarning(
            "Peringatan",
            "Bobot harus lebih besar dari 0!"
        )
        return

    if not asal or not tujuan:
        messagebox.showwarning(
            "Peringatan",
            "Pilih lokasi asal dan tujuan!"
        )
        return

    G.add_edge(asal, tujuan, weight=bobot)

    gambar_graf()

    entry_bobot.delete(0, tk.END)

    messagebox.showinfo(
        "Berhasil",
        "Hubungan antarlokasi berhasil ditambahkan."
    )


# ==========================================
# 5. UPDATE PILIHAN LOKASI
# ==========================================

def update_combobox():

    nodes = list(G.nodes)

    combo_awal["values"] = nodes
    combo_akhir["values"] = nodes
    combo_asal_edge["values"] = nodes
    combo_tujuan_edge["values"] = nodes

    if nodes:
        if combo_awal.get() not in nodes:
            combo_awal.set(nodes[0])

        if combo_akhir.get() not in nodes:
            combo_akhir.set(nodes[-1])

        if combo_asal_edge.get() not in nodes:
            combo_asal_edge.set(nodes[0])

        if combo_tujuan_edge.get() not in nodes:
            combo_tujuan_edge.set(nodes[-1])


# ==========================================
# 6. VISUALISASI GRAF
# ==========================================

def gambar_graf(jalur=None):

    ax.clear()

    if len(G.nodes) == 0:
        canvas.draw()
        return

    posisi = nx.spring_layout(G, seed=42, k=1.5)

    # Warna normal setiap node
    warna_node = ["skyblue"] * len(G.nodes)

    # Menandai node pada jalur terpendek
    if jalur:
        for i, node in enumerate(G.nodes):
            if node in jalur:
                warna_node[i] = "orange"

    # Menggambar node
    nx.draw_networkx_nodes(
        G,
        posisi,
        node_color=warna_node,
        node_size=1800,
        ax=ax
    )

    # Menggambar edge normal
    nx.draw_networkx_edges(
        G,
        posisi,
        edge_color="gray",
        width=2,
        ax=ax
    )

    # Menggambar jalur terpendek
    if jalur and len(jalur) > 1:

        edge_jalur = list(zip(jalur[:-1], jalur[1:]))

        nx.draw_networkx_edges(
            G,
            posisi,
            edgelist=edge_jalur,
            edge_color="red",
            width=4,
            ax=ax
        )

    # Label node
    label_node = {
        node: f"{node}\n{lokasi.get(node, node)}"
        for node in G.nodes
    }

    nx.draw_networkx_labels(
        G,
        posisi,
        labels=label_node,
        font_size=8,
        font_weight="bold",
        ax=ax
    )

    # Menampilkan bobot edge
    label_edge = nx.get_edge_attributes(G, "weight")

    nx.draw_networkx_edge_labels(
        G,
        posisi,
        edge_labels=label_edge,
        font_size=9,
        ax=ax
    )

    ax.set_title(
        "Visualisasi Graf Pencarian Jalur Terpendek",
        fontsize=13,
        fontweight="bold"
    )

    ax.axis("off")

    canvas.draw()


# ==========================================
# 7. PROSES PENCARIAN JALUR TERPENDEK
# ==========================================

def cari_jalur():

    awal = combo_awal.get()
    akhir = combo_akhir.get()

    if not awal or not akhir:
        messagebox.showwarning(
            "Peringatan",
            "Silakan pilih lokasi awal dan tujuan!"
        )
        return

    jalur, total_jarak = dijkstra(G, awal, akhir)

    if jalur is None:
        hasil_label.config(
            text="Tidak ditemukan jalur menuju tujuan."
        )
        gambar_graf()
        return

    nama_jalur = [
        f"{node} ({lokasi.get(node, node)})"
        for node in jalur
    ]

    hasil = " → ".join(nama_jalur)

    hasil_label.config(
        text=(
            f"Jalur Terpendek:\n{hasil}\n\n"
            f"Total Jarak: {total_jarak:g} meter\n"
            f"Jumlah Simpul: {len(jalur)}"
        )
    )

    gambar_graf(jalur)


# ==========================================
# 8. MEMBUAT GUI APLIKASI
# ==========================================

root = tk.Tk()

root.title("Graph Shortest Path - Dijkstra")
root.geometry("1200x750")
root.configure(bg="#f0f2f5")

judul = tk.Label(
    root,
    text="APLIKASI PENCARIAN JALUR TERPENDEK",
    font=("Arial", 18, "bold"),
    bg="#f0f2f5",
    fg="#1a237e"
)

judul.pack(pady=15)

container = tk.Frame(root, bg="#f0f2f5")
container.pack(fill="both", expand=True, padx=15, pady=10)

# ------------------------------------------
# PANEL KIRI
# ------------------------------------------

panel = tk.Frame(
    container,
    bg="white",
    padx=15,
    pady=15,
    relief="groove",
    bd=1
)

panel.pack(side="left", fill="y", padx=(0, 15))

# Pencarian jalur
tk.Label(
    panel,
    text="PENCARIAN JALUR",
    font=("Arial", 12, "bold"),
    bg="white"
).pack(pady=8)

tk.Label(panel, text="Lokasi Awal", bg="white").pack(anchor="w")

combo_awal = ttk.Combobox(
    panel,
    state="readonly",
    width=25
)
combo_awal.pack(pady=5)

tk.Label(panel, text="Lokasi Tujuan", bg="white").pack(anchor="w")

combo_akhir = ttk.Combobox(
    panel,
    state="readonly",
    width=25
)
combo_akhir.pack(pady=5)

tk.Button(
    panel,
    text="CARI JALUR TERPENDEK",
    command=cari_jalur,
    bg="#1565c0",
    fg="white",
    font=("Arial", 10, "bold"),
    width=25
).pack(pady=12)

hasil_label = tk.Label(
    panel,
    text="Hasil pencarian akan muncul di sini.",
    bg="#e3f2fd",
    justify="left",
    wraplength=250,
    padx=10,
    pady=12
)
hasil_label.pack(fill="x", pady=5)

# Tambah node
tk.Label(
    panel,
    text="TAMBAH LOKASI (NODE)",
    font=("Arial", 11, "bold"),
    bg="white"
).pack(pady=(20, 8))

tk.Label(panel, text="Kode Lokasi", bg="white").pack(anchor="w")

entry_kode = tk.Entry(panel, width=28)
entry_kode.pack(pady=4)

tk.Label(panel, text="Nama Lokasi", bg="white").pack(anchor="w")

entry_nama = tk.Entry(panel, width=28)
entry_nama.pack(pady=4)

tk.Button(
    panel,
    text="TAMBAH NODE",
    command=tambah_node,
    bg="#2e7d32",
    fg="white",
    width=25
).pack(pady=8)

# Tambah edge
tk.Label(
    panel,
    text="TAMBAH HUBUNGAN (EDGE)",
    font=("Arial", 11, "bold"),
    bg="white"
).pack(pady=(15, 8))

tk.Label(panel, text="Lokasi Asal", bg="white").pack(anchor="w")

combo_asal_edge = ttk.Combobox(
    panel,
    state="readonly",
    width=25
)
combo_asal_edge.pack(pady=4)

tk.Label(panel, text="Lokasi Tujuan", bg="white").pack(anchor="w")

combo_tujuan_edge = ttk.Combobox(
    panel,
    state="readonly",
    width=25
)
combo_tujuan_edge.pack(pady=4)

tk.Label(panel, text="Bobot / Jarak (meter)", bg="white").pack(anchor="w")

entry_bobot = tk.Entry(panel, width=28)
entry_bobot.pack(pady=4)

tk.Button(
    panel,
    text="TAMBAH EDGE",
    command=tambah_edge,
    bg="#ef6c00",
    fg="white",
    width=25
).pack(pady=8)


# ------------------------------------------
# PANEL KANAN: GRAF
# ------------------------------------------

frame_graf = tk.Frame(container, bg="white")
frame_graf.pack(side="right", fill="both", expand=True)

fig, ax = plt.subplots(figsize=(8, 6))

canvas = FigureCanvasTkAgg(
    fig,
    master=frame_graf
)

canvas.get_tk_widget().pack(
    fill="both",
    expand=True
)

# Inisialisasi aplikasi
update_combobox()
gambar_graf()

root.mainloop()
