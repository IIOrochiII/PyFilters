# Program by Daniel Postołowicz 2025

import math
from PIL import Image, ImageTk, ImageOps, ImageFilter, ImageEnhance
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import filedialog, ttk, messagebox


class ImageProcessor:
    def __init__(self):
        self.image = None
        self.image2 = None

    def load_image(self, path):
        self.image = Image.open(path)
        if self.image.mode != 'RGB':
            self.image = self.image.convert('RGB')
        return self.image

    def load_second_image(self, path):
        self.image2 = Image.open(path)
        if self.image2.mode != 'RGB':
            self.image2 = self.image2.convert('RGB')
        return self.image2

    def save_image(self, path, image):
        if image is not None:
            image.save(path)
            return True
        return False

    def linear_transform(self, alpha=1.0, beta=0):
        if self.image is None:
            return None
        return Image.eval(self.image, lambda x: min(max(alpha * x + beta, 0), 255))

    def power_transform(self, gamma=1.0):
        if self.image is None:
            return None
        return Image.eval(self.image, lambda x: int(255 * (x / 255) ** gamma))

    def blend_images(self, mode='transparency', alpha=0.5):
        if self.image is None or self.image2 is None:
            return None
        img1 = self.image.copy()
        img2 = self.image2.copy()
        if img1.size != img2.size:
            img2 = img2.resize(img1.size)

        def additive(p1, p2):
            return tuple(min(p1[i] / 255 + p2[i] / 255, 1) * 255 for i in range(3))

        def subtractive(p1, p2):
            return tuple(max(p1[i] / 255 + p2[i] / 255 - 1, 0) * 255 for i in range(3))

        def difference(p1, p2):
            return tuple(abs(p1[i] / 255 - p2[i] / 255) * 255 for i in range(3))

        def multiply(p1, p2):
            return tuple((p1[i] / 255 * p2[i] / 255) * 255 for i in range(3))

        def screen(p1, p2):
            return tuple((1 - (1 - p1[i] / 255) * (1 - p2[i] / 255)) * 255 for i in range(3))

        def negation(p1, p2):
            return tuple((1 - abs(1 - p1[i] / 255 - p2[i] / 255)) * 255 for i in range(3))

        def darken(p1, p2):
            return tuple(min(p1[i], p2[i]) for i in range(3))

        def lighten(p1, p2):
            return tuple(max(p1[i], p2[i]) for i in range(3))

        def exclusion(p1, p2):
            return tuple((p1[i] / 255 + p2[i] / 255 - 2 * p1[i] / 255 * p2[i] / 255) * 255 for i in range(3))

        def overlay(p1, p2):
            result = []
            for i in range(3):
                a, b = p1[i] / 255, p2[i] / 255
                if a < 0.5:
                    val = 2 * a * b
                else:
                    val = 1 - 2 * (1 - a) * (1 - b)
                result.append(val * 255)
            return tuple(result)

        def hard_light(p1, p2):
            result = []
            for i in range(3):
                a, b = p1[i] / 255, p2[i] / 255
                if b < 0.5:
                    val = 2 * a * b
                else:
                    val = 1 - 2 * (1 - a) * (1 - b)
                result.append(val * 255)
            return tuple(result)

        def soft_light(p1, p2):
            result = []
            for i in range(3):
                a, b = p1[i] / 255, p2[i] / 255
                if b < 0.5:
                    val = 2 * a * b + a * a * (1 - 2 * b)
                else:
                    val = math.sqrt(a) * (2 * b - 1) + (2 * a) * (1 - b)
                result.append(max(min(val, 1), 0) * 255)
            return tuple(result)

        def color_dodge(p1, p2):
            result = []
            for i in range(3):
                a, b = p1[i] / 255, p2[i] / 255
                if b == 1:
                    val = 1
                else:
                    val = min(a / (1 - b), 1)
                result.append(val * 255)
            return tuple(result)

        def color_burn(p1, p2):
            result = []
            for i in range(3):
                a, b = p1[i] / 255, p2[i] / 255
                if b == 0:
                    val = 0
                else:
                    val = max(1 - (1 - a) / b, 0)
                result.append(val * 255)
            return tuple(result)

        def reflect(p1, p2):
            result = []
            for i in range(3):
                a, b = p1[i] / 255, p2[i] / 255
                if b == 1:
                    val = 1
                else:
                    val = min(a * a / (1 - b), 1)
                result.append(val * 255)
            return tuple(result)

        def transparency(p1, p2):
            return tuple(((1 - alpha) * p2[i] + alpha * p1[i]) for i in range(3))

        blend_funcs = {
            'additive': additive,
            'subtractive': subtractive,
            'difference': difference,
            'multiply': multiply,
            'screen': screen,
            'negation': negation,
            'darken': darken,
            'lighten': lighten,
            'exclusion': exclusion,
            'overlay': overlay,
            'hard_light': hard_light,
            'soft_light': soft_light,
            'color_dodge': color_dodge,
            'color_burn': color_burn,
            'reflect': reflect,
            'transparency': transparency,
        }

        func = blend_funcs.get(mode, transparency)
        pixels1 = img1.load()
        pixels2 = img2.load()
        width, height = img1.size

        result = Image.new('RGB', (width, height))
        result_pixels = result.load()

        for y in range(height):
            for x in range(width):
                result_pixels[x, y] = tuple(int(v) for v in func(pixels1[x, y], pixels2[x, y]))

        return result

    def adjust_contrast(self, contrast=1.0):
        if self.image is None:
            return None
        img = self.image.convert('RGB')
        width, height = img.size
        pixels = img.load()
        new_img = img.copy()
        new_pixels = new_img.load()
        for x in range(width):
            for y in range(height):
                r, g, b = pixels[x, y]
                r = int(min(255, max(0, 128 + contrast * (r - 128))))
                g = int(min(255, max(0, 128 + contrast * (g - 128))))
                b = int(min(255, max(0, 128 + contrast * (b - 128))))
                new_pixels[x, y] = (r, g, b)
        if self.image.mode != 'RGB':
            new_img = new_img.convert(self.image.mode)
        return new_img

    def generate_histogram(self, image=None):
        img = image if image is not None else self.image
        if img is None:
            return None
        hist_r = [0] * 256
        hist_g = [0] * 256
        hist_b = [0] * 256
        pixels = img.load()
        width, height = img.size
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                hist_r[r] += 1
                hist_g[g] += 1
                hist_b[b] += 1

        # Normalizacja histogramów
        max_val = max(max(hist_r), max(hist_g), max(hist_b))
        if max_val > 0:
            hist_r = [v / max_val for v in hist_r]
            hist_g = [v / max_val for v in hist_g]
            hist_b = [v / max_val for v in hist_b]

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(hist_r, color='r', label='Red')
        ax.plot(hist_g, color='g', label='Green')
        ax.plot(hist_b, color='b', label='Blue')
        ax.set_title('Znormalizowany histogram składowych RGB')
        ax.set_xlabel('Wartość piksela')
        ax.set_ylabel('Znormalizowana liczba pikseli')
        ax.legend()
        plt.tight_layout()
        return fig

    def equalize_histogram(self):
        if self.image is None:
            return None
        return ImageOps.equalize(self.image)

    def scale_histogram(self, min_out=0, max_out=255):
        if self.image is None:
            return None
        pixels = self.image.load()
        width, height = self.image.size
        min_r = min_g = min_b = 255
        max_r = max_g = max_b = 0
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                min_r = min(min_r, r)
                min_g = min(min_g, g)
                min_b = min(min_b, b)
                max_r = max(max_r, r)
                max_g = max(max_g, g)
                max_b = max(max_b, b)
        result = Image.new('RGB', (width, height))
        result_pixels = result.load()
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                new_r = int((r - min_r) * (max_out - min_out) / (max_r - min_r + 1e-10) + min_out)
                new_g = int((g - min_g) * (max_out - min_out) / (max_g - min_g + 1e-10) + min_out)
                new_b = int((b - min_b) * (max_out - min_out) / (max_b - min_b + 1e-10) + min_out)
                result_pixels[x, y] = (
                    max(min(new_r, 255), 0),
                    max(min(new_g, 255), 0),
                    max(min(new_b, 255), 0)
                )
        return result

    def pad_image(self, image, kernel_size, padding_type='replicate'):
        """
        Dopełnia obraz zgodnie z wybraną strategią.
        :param image: Obraz wejściowy (PIL Image)
        :param kernel_size: Rozmiar jądra filtru
        :param padding_type: Typ dopełniania ('replicate', 'reflect', 'zero')
        :return: Dopełniony obraz
        """
        width, height = image.size
        pad = kernel_size // 2
        mode = image.mode
        padded = Image.new(mode, (width + 2 * pad, height + 2 * pad))
        pixels = image.load()
        padded_pixels = padded.load()

        for y in range(-pad, height + pad):
            for x in range(-pad, width + pad):
                if padding_type == 'replicate':
                    src_x = max(0, min(x, width - 1))
                    src_y = max(0, min(y, height - 1))
                elif padding_type == 'reflect':
                    src_x = width - 1 - x if x >= width else abs(x) if x < 0 else x
                    src_y = height - 1 - y if y >= height else abs(y) if y < 0 else y
                elif padding_type == 'zero':
                    if x < 0 or x >= width or y < 0 or y >= height:
                        if mode == 'RGB':
                            padded_pixels[x + pad, y + pad] = (0, 0, 0)
                        else:  # mode == 'L'
                            padded_pixels[x + pad, y + pad] = 0
                        continue
                else:
                    raise ValueError("Nieznany typ dopełniania")
                padded_pixels[x + pad, y + pad] = pixels[src_x, src_y]

        return padded

    def low_pass_filter(self, kernel_size=3):
        if self.image is None:
            return None
        if kernel_size % 2 == 0:
            kernel_size += 1
        if kernel_size < 3:
            kernel_size = 3
        padded = self.pad_image(self.image, kernel_size, padding_type='replicate')
        width, height = self.image.size
        pad = kernel_size // 2
        new_img = self.image.copy()
        new_pixels = new_img.load()
        padded_pixels = padded.load()
        for x in range(width):
            for y in range(height):
                r_sum, g_sum, b_sum, count = 0, 0, 0, 0
                for i in range(-pad, pad + 1):
                    for j in range(-pad, pad + 1):
                        r, g, b = padded_pixels[x + i + pad, y + j + pad]
                        r_sum += r
                        g_sum += g
                        b_sum += b
                        count += 1
                r_avg = int(r_sum / count)
                g_avg = int(g_sum / count)
                b_avg = int(b_sum / count)
                new_pixels[x, y] = (r_avg, g_avg, b_avg)
        if self.image.mode != 'RGB':
            new_img = new_img.convert(self.image.mode)
        return new_img

    def high_pass_filter(self, operator='sobel', direction='both'):
        if self.image is None:
            return None
        gray = self.image.convert('L')
        kernels = {
            'roberts': {
                'x': [[0, 0, 0], [0, 1, 0], [0, 0, -1]],
                'y': [[0, 0, 0], [0, 0, 1], [0, -1, 0]]
            },
            'prewitt': {
                'x': [[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]],
                'y': [[-1, -1, -1], [0, 0, 0], [1, 1, 1]]
            },
            'sobel': {
                'x': [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]],
                'y': [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]
            },
            'laplace': {
                '4neighbors': [[0, -1, 0], [-1, 4, -1], [0, -1, 0]],
                '8neighbors': [[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]],
                'diagonal': [[-2, 1, -2], [1, 4, 1], [-2, 1, -2]]
            }
        }
        if operator not in kernels:
            raise ValueError(f"Nieznany operator: {operator}")

        if operator == 'laplace':
            if direction not in kernels['laplace']:
                raise ValueError(f"Nieprawidłowy kierunek dla operatora Laplace: {direction}")
            kernel = kernels['laplace'][direction]
            result = self._apply_kernel(gray, kernel)
        else:
            if direction not in kernels[operator]:
                raise ValueError(f"Nieprawidłowy kierunek dla operatora {operator}: {direction}")
            if direction == 'both':
                kernel_x = kernels[operator]['x']
                kernel_y = kernels[operator]['y']
                grad_x = self._apply_kernel(gray, kernel_x)
                grad_y = self._apply_kernel(gray, kernel_y)
                width, height = gray.size
                result = Image.new('L', (width, height))
                result_pixels = result.load()
                # Normalizacja wyników gradientów
                max_val = 0
                temp_vals = []
                for y in range(height):
                    for x in range(width):
                        gx = grad_x.getpixel((x, y))
                        gy = grad_y.getpixel((x, y))
                        # Oblicz magnitudę gradientu: sqrt(gx^2 + gy^2)
                        val = math.sqrt(gx * gx + gy * gy)
                        temp_vals.append(val)
                        max_val = max(max_val, val)
                # Normalizacja do zakresu 0-255
                if max_val > 0:
                    for y in range(height):
                        for x in range(width):
                            idx = y * width + x
                            val = int((temp_vals[idx] / max_val) * 255)
                            result_pixels[x, y] = min(val, 255)
                else:
                    # Jeśli max_val == 0, ustawiamy obraz na czarny
                    for y in range(height):
                        for x in range(width):
                            result_pixels[x, y] = 0
            else:
                kernel = kernels[operator][direction]
                result = self._apply_kernel(gray, kernel)
        return result.convert('RGB')

    def _apply_kernel(self, image, kernel):
        if not image:
            raise ValueError("Obraz wejściowy nie może być pusty")

        width, height = image.size
        kernel_size = len(kernel)
        pad = kernel_size // 2
        padded = self.pad_image(image, kernel_size, padding_type='replicate')

        # Wymiary dopełnionego obrazu
        padded_width, padded_height = padded.size

        result = Image.new('L', (width, height))
        result_pixels = result.load()
        padded_pixels = padded.load()

        # Iterujemy po pikselach oryginalnego obrazu
        for y in range(height):
            for x in range(width):
                val = 0
                # Iterujemy po jądrze
                for ky in range(-pad, pad + 1):
                    for kx in range(-pad, pad + 1):
                        # Obliczamy indeksy w dopełnionym obrazie
                        px = x + kx + pad
                        py = y + ky + pad

                        # Sprawdzamy, czy indeksy mieszczą się w granicach dopełnionego obrazu
                        if 0 <= px < padded_width and 0 <= py < padded_height:
                            pixel = padded_pixels[px, py]
                            # Obliczamy indeks jądra
                            kernel_y = ky + pad
                            kernel_x = kx + pad
                            val += pixel * kernel[kernel_y][kernel_x]
                        else:
                            # Jeśli indeksy są poza zakresem, pomijamy piksel
                            continue
                # Przeskalowanie wartości do zakresu 0-255
                # Najpierw znajdujemy min i max wartości, aby przeskalować
                result_pixels[x, y] = min(max(int(val), 0), 255)

        return result

    def statistical_filter(self, filter_type='median', kernel_size=3):
        if self.image is None:
            return None
        if kernel_size % 2 == 0:
            kernel_size += 1
        if kernel_size < 3:
            kernel_size = 3
        padded = self.pad_image(self.image, kernel_size, padding_type='replicate')
        width, height = self.image.size
        pad = kernel_size // 2
        new_img = self.image.copy()
        new_pixels = new_img.load()
        padded_pixels = padded.load()
        for x in range(width):
            for y in range(height):
                r_values, g_values, b_values = [], [], []
                for i in range(-pad, pad + 1):
                    for j in range(-pad, pad + 1):
                        r, g, b = padded_pixels[x + i + pad, y + j + pad]
                        r_values.append(r)
                        g_values.append(g)
                        b_values.append(b)
                if filter_type == 'median':
                    r_new = int(sorted(r_values)[len(r_values) // 2])
                    g_new = int(sorted(g_values)[len(g_values) // 2])
                    b_new = int(sorted(b_values)[len(b_values) // 2])
                elif filter_type == 'min':
                    r_new = int(min(r_values))
                    g_new = int(min(g_values))
                    b_new = int(min(b_values))
                elif filter_type == 'max':
                    r_new = int(max(r_values))
                    g_new = int(max(g_values))
                    b_new = int(max(b_values))
                else:
                    r_new, g_new, b_new = new_pixels[x, y]
                new_pixels[x, y] = (r_new, g_new, b_new)
        if self.image.mode != 'RGB':
            new_img = new_img.convert(self.image.mode)
        return new_img


class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Przetwarzanie Obrazów Cyfrowych")
        self.processor = ImageProcessor()
        self.current_image = None
        self.main_container = ttk.Frame(root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(self.main_container)
        self.scrollbar = ttk.Scrollbar(self.main_container, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.create_widgets()

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def create_widgets(self):
        self.image_frame = ttk.Frame(self.scrollable_frame)
        self.image_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.original_label = ttk.Label(self.image_frame, text="Oryginalny obraz")
        self.original_label.grid(row=0, column=0, padx=5, pady=5)
        self.original_canvas = tk.Canvas(self.image_frame, width=400, height=300, bg='white')
        self.original_canvas.grid(row=1, column=0, padx=5, pady=5)
        self.second_label = ttk.Label(self.image_frame, text="Drugi obraz")
        self.second_label.grid(row=0, column=1, padx=5, pady=5)
        self.second_canvas = tk.Canvas(self.image_frame, width=400, height=300, bg='white')
        self.second_canvas.grid(row=1, column=1, padx=5, pady=5)
        self.processed_label = ttk.Label(self.image_frame, text="Przetworzony obraz")
        self.processed_label.grid(row=0, column=2, padx=5, pady=5)
        self.processed_canvas = tk.Canvas(self.image_frame, width=400, height=300, bg='white')
        self.processed_canvas.grid(row=1, column=2, padx=5, pady=5)
        self.original_hist_label = ttk.Label(self.image_frame, text="Znormalizowany histogram oryginalny")
        self.original_hist_label.grid(row=2, column=0, padx=5, pady=5)
        self.original_hist_canvas = tk.Canvas(self.image_frame, width=400, height=300, bg='white')
        self.original_hist_canvas.grid(row=3, column=0, padx=5, pady=5)
        self.second_hist_label = ttk.Label(self.image_frame, text="Znormalizowany histogram drugiego obrazu")
        self.second_hist_label.grid(row=2, column=1, padx=5, pady=5)
        self.second_hist_canvas = tk.Canvas(self.image_frame, width=400, height=300, bg='white')
        self.second_hist_canvas.grid(row=3, column=1, padx=5, pady=5)
        self.processed_hist_label = ttk.Label(self.image_frame, text="Znormalizowany histogram przetworzony")
        self.processed_hist_label.grid(row=2, column=2, padx=5, pady=5)
        self.processed_hist_canvas = tk.Canvas(self.image_frame, width=400, height=300, bg='white')
        self.processed_hist_canvas.grid(row=3, column=2, padx=5, pady=5)
        self.control_frame = ttk.Frame(self.scrollable_frame)
        self.control_frame.pack(fill=tk.X, padx=10, pady=10)
        btn_frame = ttk.Frame(self.control_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="Wczytaj obraz", command=self.load_image).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Wczytaj drugi obraz", command=self.load_second_image).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Zapisz obraz", command=self.save_image).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="Wyczyść", command=self.clear_all).grid(row=0, column=3, padx=5)
        ttk.Button(btn_frame, text="Wyczyść wybory", command=self.clear_selections).grid(row=0, column=4, padx=5)
        transform_frame = ttk.Frame(self.control_frame)
        transform_frame.pack(fill=tk.X, pady=5)
        ttk.Label(transform_frame, text="Transformacje:").pack(side=tk.LEFT, padx=5)
        self.transform_var = tk.StringVar()
        self.transform_combobox = ttk.Combobox(transform_frame, textvariable=self.transform_var,
                                               values=["Liniowa", "Potęgowa", "Mieszanie", "Kontrast",
                                                       "Wyrównanie histogramu", "Skalowanie histogramu"])
        self.transform_combobox.pack(side=tk.LEFT, padx=5)
        self.transform_combobox.bind("<<ComboboxSelected>>", self.show_transform_params)
        self.transform_params_frame = ttk.Frame(self.control_frame)
        self.transform_params_frame.pack(fill=tk.X, padx=10, pady=5)
        filter_frame = ttk.Frame(self.control_frame)
        filter_frame.pack(fill=tk.X, pady=5)
        ttk.Label(filter_frame, text="Filtry:").pack(side=tk.LEFT, padx=5)
        self.filter_var = tk.StringVar()
        self.filter_combobox = ttk.Combobox(filter_frame, textvariable=self.filter_var,
                                            values=["Dolnoprzepustowy", "Górnoprzepustowy", "Statystyczny"])
        self.filter_combobox.pack(side=tk.LEFT, padx=5)
        self.filter_combobox.bind("<<ComboboxSelected>>", self.show_filter_params)
        self.filter_params_frame = ttk.Frame(self.control_frame)
        self.filter_params_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(self.control_frame, text="Zastosuj", command=self.apply_processing).pack(pady=10)

    def clear_all(self):
        self.processor.image = None
        self.processor.image2 = None
        self.current_image = None
        self.original_canvas.delete("all")
        self.second_canvas.delete("all")
        self.processed_canvas.delete("all")
        for widget in self.original_hist_canvas.winfo_children():
            widget.destroy()
        for widget in self.second_hist_canvas.winfo_children():
            widget.destroy()
        for widget in self.processed_hist_canvas.winfo_children():
            widget.destroy()
        self.clear_selections()

    def clear_selections(self):
        self.transform_var.set('')
        for widget in self.transform_params_frame.winfo_children():
            widget.destroy()
        self.filter_var.set('')
        for widget in self.filter_params_frame.winfo_children():
            widget.destroy()

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
        if file_path:
            self.processor.load_image(file_path)
            self.display_image(self.processor.image, self.original_canvas)
            self.display_histogram(self.processor.image, self.original_hist_canvas, "Oryginalny")

    def load_second_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
        if file_path:
            self.processor.load_second_image(file_path)
            self.display_image(self.processor.image2, self.second_canvas)
            self.display_histogram(self.processor.image2, self.second_hist_canvas, "Drugi obraz")

    def save_image(self):
        if self.current_image is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     filetypes=[("PNG files", "*.png"),
                                                                ("JPEG files", "*.jpg"),
                                                                ("All files", "*.*")])
            if file_path:
                self.processor.save_image(file_path, self.current_image)

    def display_image(self, image, canvas):
        if image is not None:
            w, h = image.size
            ratio = min(400 / w, 300 / h)
            new_w, new_h = int(w * ratio), int(h * ratio)
            resized = image.resize((new_w, new_h))
            img_tk = ImageTk.PhotoImage(resized)
            canvas.delete("all")
            canvas.create_image(200, 150, image=img_tk)
            canvas.image = img_tk

    def display_histogram(self, image, canvas, title=""):
        fig = self.processor.generate_histogram(image)
        if fig:
            for widget in canvas.winfo_children():
                widget.destroy()
            fig.axes[0].set_title(f'Znormalizowany histogram składowych RGB - {title}')
            fig.tight_layout()
            canvas_fig = FigureCanvasTkAgg(fig, master=canvas)
            canvas_fig.draw()
            canvas_fig.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            canvas.figure = fig
            canvas.canvas = canvas_fig

    def show_transform_params(self, event):
        for widget in self.transform_params_frame.winfo_children():
            widget.destroy()
        transform_type = self.transform_var.get()
        if transform_type == "Liniowa":
            ttk.Label(self.transform_params_frame, text="Alpha:").grid(row=0, column=0)
            self.alpha_var = tk.DoubleVar(value=1.0)
            ttk.Scale(self.transform_params_frame, from_=0.1, to=3.0, variable=self.alpha_var,
                      orient=tk.HORIZONTAL).grid(row=0, column=1)
            ttk.Label(self.transform_params_frame, text="Beta:").grid(row=1, column=0)
            self.beta_var = tk.IntVar(value=0)
            ttk.Scale(self.transform_params_frame, from_=-100, to=100, variable=self.beta_var,
                      orient=tk.HORIZONTAL).grid(row=1, column=1)
        elif transform_type == "Potęgowa":
            ttk.Label(self.transform_params_frame, text="Gamma:").grid(row=0, column=0)
            self.gamma_var = tk.DoubleVar(value=1.0)
            ttk.Scale(self.transform_params_frame, from_=0.1, to=3.0, variable=self.gamma_var,
                      orient=tk.HORIZONTAL).grid(row=0, column=1)
        elif transform_type == "Mieszanie":
            ttk.Label(self.transform_params_frame, text="Tryb:").grid(row=0, column=0)
            self.blend_mode_var = tk.StringVar()
            blend_modes = [
                'additive', 'subtractive', 'difference', 'multiply', 'screen', 'negation',
                'darken', 'lighten', 'exclusion', 'overlay', 'hard_light', 'soft_light',
                'color_dodge', 'color_burn', 'reflect', 'transparency'
            ]
            ttk.Combobox(self.transform_params_frame, textvariable=self.blend_mode_var, values=blend_modes).grid(row=0,
                                                                                                                 column=1)
            ttk.Label(self.transform_params_frame, text="Alpha:").grid(row=1, column=0)
            self.blend_alpha_var = tk.DoubleVar(value=0.5)
            ttk.Scale(self.transform_params_frame, from_=0.0, to=1.0, variable=self.blend_alpha_var,
                      orient=tk.HORIZONTAL).grid(row=1, column=1)
        elif transform_type == "Kontrast":
            ttk.Label(self.transform_params_frame, text="Kontrast:").grid(row=0, column=0)
            self.contrast_var = tk.DoubleVar(value=1.0)
            ttk.Scale(self.transform_params_frame, from_=0.1, to=3.0, variable=self.contrast_var,
                      orient=tk.HORIZONTAL).grid(row=0, column=1)
        elif transform_type == "Skalowanie histogramu":
            ttk.Label(self.transform_params_frame, text="Min:").grid(row=0, column=0)
            self.hist_min_var = tk.IntVar(value=0)
            ttk.Scale(self.transform_params_frame, from_=0, to=255, variable=self.hist_min_var,
                      orient=tk.HORIZONTAL).grid(row=0, column=1)
            ttk.Label(self.transform_params_frame, text="Max:").grid(row=1, column=0)
            self.hist_max_var = tk.IntVar(value=255)
            ttk.Scale(self.transform_params_frame, from_=0, to=255, variable=self.hist_max_var,
                      orient=tk.HORIZONTAL).grid(row=1, column=1)

    def show_filter_params(self, event):
        for widget in self.filter_params_frame.winfo_children():
            widget.destroy()
        filter_type = self.filter_var.get()
        if filter_type == "Dolnoprzepustowy":
            ttk.Label(self.filter_params_frame, text="Rozmiar jądra:").grid(row=0, column=0)
            self.lpf_size_var = tk.IntVar(value=3)
            ttk.Combobox(self.filter_params_frame, textvariable=self.lpf_size_var, values=[3, 5, 7, 9]).grid(row=0,
                                                                                                             column=1)
        elif filter_type == "Górnoprzepustowy":
            ttk.Label(self.filter_params_frame, text="Operator:").grid(row=0, column=0)
            self.hpf_operator_var = tk.StringVar(value="Sobel")
            ttk.Combobox(self.filter_params_frame, textvariable=self.hpf_operator_var,
                         values=["Roberts", "Prewitt", "Sobel", "Laplace"]).grid(row=0, column=1)
            ttk.Label(self.filter_params_frame, text="Kierunek:").grid(row=1, column=0)
            self.hpf_direction_var = tk.StringVar(value="both")
            directions = {
                "Roberts": ["x", "y", "both"],
                "Prewitt": ["x", "y", "both"],
                "Sobel": ["x", "y", "both"],
                "Laplace": ["4neighbors", "8neighbors", "diagonal"]
            }
            self.hpf_direction_combobox = ttk.Combobox(self.filter_params_frame, textvariable=self.hpf_direction_var)
            self.hpf_direction_combobox.grid(row=1, column=1)

            def update_directions(*args):
                op = self.hpf_operator_var.get()
                if op in directions:
                    self.hpf_direction_combobox['values'] = directions[op]
                    self.hpf_direction_var.set(directions[op][0])

            self.hpf_operator_var.trace_add('write', update_directions)
            update_directions()
        elif filter_type == "Statystyczny":
            ttk.Label(self.filter_params_frame, text="Typ:").grid(row=0, column=0)
            self.stat_filter_type_var = tk.StringVar(value="median")
            ttk.Combobox(self.filter_params_frame, textvariable=self.stat_filter_type_var,
                         values=["min", "max", "median"]).grid(row=0, column=1)
            ttk.Label(self.filter_params_frame, text="Rozmiar jądra:").grid(row=1, column=0)
            self.stat_filter_size_var = tk.IntVar(value=3)
            ttk.Combobox(self.filter_params_frame, textvariable=self.stat_filter_size_var, values=[3, 5, 7]).grid(row=1,
                                                                                                                  column=1)

    def apply_processing(self):
        if self.processor.image is None:
            messagebox.showwarning("Ostrzeżenie", "Najpierw wczytaj obraz!")
            return

        try:
            # Reset current_image to ensure we start fresh
            self.current_image = self.processor.image.copy()

            # Apply transform if selected
            transform_type = self.transform_var.get()
            if transform_type:
                if transform_type == "Liniowa":
                    alpha = self.alpha_var.get()
                    beta = self.beta_var.get()
                    self.current_image = self.processor.linear_transform(alpha, beta)
                elif transform_type == "Potęgowa":
                    gamma = self.gamma_var.get()
                    self.current_image = self.processor.power_transform(gamma)
                elif transform_type == "Mieszanie":
                    if self.processor.image2 is None:
                        messagebox.showwarning("Ostrzeżenie", "Najpierw wczytaj drugi obraz!")
                        return
                    mode = self.blend_mode_var.get()
                    alpha = self.blend_alpha_var.get()
                    self.current_image = self.processor.blend_images(mode, alpha)
                elif transform_type == "Kontrast":
                    contrast = self.contrast_var.get()
                    self.current_image = self.processor.adjust_contrast(contrast)
                elif transform_type == "Wyrównanie histogramu":
                    self.current_image = self.processor.equalize_histogram()
                elif transform_type == "Skalowanie histogramu":
                    min_out = self.hist_min_var.get()
                    max_out = self.hist_max_var.get()
                    self.current_image = self.processor.scale_histogram(min_out, max_out)

            # Apply filter if selected
            filter_type = self.filter_var.get()
            if filter_type:
                if filter_type == "Dolnoprzepustowy":
                    size = self.lpf_size_var.get()
                    self.current_image = self.processor.low_pass_filter(size)
                elif filter_type == "Górnoprzepustowy":
                    operator = self.hpf_operator_var.get().lower()
                    direction = self.hpf_direction_var.get()
                    print(f"Applying high-pass filter with operator={operator}, direction={direction}")
                    self.current_image = self.processor.high_pass_filter(operator, direction)
                elif filter_type == "Statystyczny":
                    stat_filter_type = self.stat_filter_type_var.get()
                    size = self.stat_filter_size_var.get()
                    self.current_image = self.processor.statistical_filter(stat_filter_type, size)

            if self.current_image is not None:
                self.display_image(self.current_image, self.processed_canvas)
                self.display_histogram(self.current_image, self.processed_hist_canvas, "Przetworzony")
            else:
                messagebox.showerror("Błąd", "Nie udało się przetworzyć obrazu.")

        except Exception as e:
            messagebox.showerror("Błąd przetwarzania", f"Wystąpił błąd podczas przetwarzania obrazu:\n{str(e)}")
            raise  # Podniesienie wyjątku w celu debugowania


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()
