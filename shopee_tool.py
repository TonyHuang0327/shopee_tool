import tkinter as tk
from tkinter import filedialog, messagebox
import csv

def input_product(title, description, price, stock, image_path):
    """將商品資料顯示在消息框中"""
    product = {"title": title, "description": description, "price": price, "stock": stock, "image": image_path}
    messagebox.showinfo("商品資料已輸入", product)

def bulk_upload():
    """從 CSV 文件讀取商品資料並顯示在 GUI 中"""
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return
    
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        products = [row for row in reader]

    # 假設每次上傳一個商品
    if products:
        product = products[0]  # 取第一個商品進行展示
        title_entry.delete(0, tk.END)  # 清空輸入框
        title_entry.insert(0, product['name'])  # 商品名稱
        description_entry.delete(0, tk.END)
        description_entry.insert(0, product['description'])  # 商品描述
        price_entry.delete(0, tk.END)
        price_entry.insert(0, ', '.join(product['price']))  # 產品價格，使用逗號分隔多個價格
        stock_entry.delete(0, tk.END)
        stock_entry.insert(0, "0")  # 庫存數量預設為 0，留待後續處理
        messagebox.showinfo("批量上傳完成", f"已讀取商品: {product['name']}")

# 設計 GUI
root = tk.Tk()
root.title("商品上架小幫手")

tk.Label(root, text="商品名稱").grid(row=0, column=0)
title_entry = tk.Entry(root)
title_entry.grid(row=0, column=1)

tk.Label(root, text="商品描述").grid(row=1, column=0)
description_entry = tk.Entry(root)
description_entry.grid(row=1, column=1)

tk.Label(root, text="價格").grid(row=2, column=0)
price_entry = tk.Entry(root)
price_entry.grid(row=2, column=1)

tk.Label(root, text="庫存數量").grid(row=3, column=0)
stock_entry = tk.Entry(root)
stock_entry.grid(row=3, column=1)

tk.Button(root, text="輸入商品資料", command=lambda: input_product(
    title_entry.get(),
    description_entry.get(),
    price_entry.get(),
    stock_entry.get(),
    ""  # 圖片路徑留空，根據需要再添加
)).grid(row=4, column=0, pady=10)

tk.Button(root, text="批量上傳", command=bulk_upload).grid(row=4, column=1, pady=10)

root.mainloop()
