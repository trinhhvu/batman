# AuraOS — Design System & Page Collection

Tổng hợp toàn bộ các trang giao diện của **AuraOS**, một hệ điều hành web theo phong cách Fluidic Professional / Glassmorphism. Mỗi phần bên dưới chứa mô tả và code HTML đầy đủ của từng trang.

---

## Mục lục

1. [Dashboard](#1-dashboard)
2. [Downloads](#2-downloads)
3. [Library](#3-library)
4. [Scanner (Channel Scanner)](#4-scanner)
5. [Research & Trend](#5-research--trend)
6. [Downloader (Video Downloader)](#6-downloader)
7. [Settings](#7-settings)
8. [Dashboard v2 (Glassmorphism nâng cao)](#8-dashboard-v2)
9. [Downloads v2 (Bo góc lớn hơn)](#9-downloads-v2)
10. [Library v2 (Bo góc nâng cao)](#10-library-v2)
11. [Settings v2 (Bo góc nâng cao)](#11-settings-v2)
12. [Analyze — Real-time Intelligence](#12-analyze--real-time-intelligence)

---

## Design Tokens chung

| Token | Giá trị |
|---|---|
| `primary` | `#000000` |
| `background` | `#faf9fe` |
| `surface-container-lowest` | `#ffffff` |
| `surface-container` | `#eeedf3` |
| `on-surface` | `#1a1b1f` |
| `on-surface-variant` | `#444748` |
| `outline` | `#747878` |
| `error` | `#ba1a1a` |
| Font Display | Hanken Grotesk |
| Font Body | Inter |

---

## 1. Dashboard

**Mô tả:** Trang chủ của AuraOS. Hiển thị lời chào buổi sáng, trạng thái hệ thống (CPU, RAM, Network), nút bắt đầu phiên tập trung (Focus Session), danh sách hoạt động gần đây, và thông tin dung lượng lưu trữ. Layout dạng Bento Grid 12 cột.

```html
<!-- Dashboard - AuraOS -->
<!DOCTYPE html>

<html lang="en"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>AuraOS Dashboard</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@500;600&family=Inter:wght@400;600&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
<script id="tailwind-config">
        tailwind.config = {
          darkMode: "class",
          theme: {
            extend: {
              "colors": {
                      "surface-dim": "#dad9df","on-error-container": "#93000a","on-surface-variant": "#444748","primary-fixed": "#e5e2e1","on-primary": "#ffffff","secondary": "#5d5e60","secondary-fixed": "#e2e2e4","inverse-on-surface": "#f1f0f5","outline": "#747878","tertiary-fixed-dim": "#c6c6cc","secondary-container": "#dfdfe1","surface-container": "#eeedf3","tertiary": "#000000","surface-container-lowest": "#ffffff","error-container": "#ffdad6","on-secondary-fixed-variant": "#454749","tertiary-container": "#1a1c20","background": "#faf9fe","on-primary-fixed-variant": "#474646","outline-variant": "#c4c7c7","surface-container-high": "#e9e7ed","surface-container-highest": "#e3e2e7","on-surface": "#1a1b1f","on-secondary": "#ffffff","surface-variant": "#e3e2e7","primary-container": "#1c1b1b","on-error": "#ffffff","surface": "#faf9fe","secondary-fixed-dim": "#c6c6c8","tertiary-fixed": "#e2e2e8","inverse-primary": "#c8c6c5","on-tertiary": "#ffffff","on-tertiary-fixed": "#1a1c20","on-secondary-container": "#616365","on-tertiary-container": "#828389","primary": "#000000","inverse-surface": "#2f3034","on-primary-fixed": "#1c1b1b","on-primary-container": "#858383","surface-bright": "#faf9fe","primary-fixed-dim": "#c8c6c5","surface-container-low": "#f4f3f8","on-secondary-fixed": "#1a1c1d","surface-tint": "#5f5e5e","on-background": "#1a1b1f","on-tertiary-fixed-variant": "#45474b","error": "#ba1a1a"
              },
              "borderRadius": {"DEFAULT": "0.25rem","lg": "0.5rem","xl": "0.75rem","full": "9999px","card": "24px"},
              "spacing": {"element-gap": "12px","margin-sm": "16px","margin-lg": "64px","container-padding": "40px","unit": "8px","gutter": "24px","margin-md": "32px"},
              "fontFamily": {"headline-md": ["Hanken Grotesk"],"body-md": ["Inter"],"body-lg": ["Inter"],"display": ["Hanken Grotesk"],"label-sm": ["Inter"],"headline-lg": ["Hanken Grotesk"]},
              "fontSize": {"headline-md": ["24px",{"lineHeight": "1.3","fontWeight": "500"}],"body-md": ["15px",{"lineHeight": "1.5","fontWeight": "400"}],"body-lg": ["18px",{"lineHeight": "1.6","fontWeight": "400"}],"display": ["48px",{"lineHeight": "1.1","letterSpacing": "-0.02em","fontWeight": "600"}],"label-sm": ["12px",{"lineHeight": "1","letterSpacing": "0.05em","fontWeight": "600"}],"headline-lg": ["32px",{"lineHeight": "1.2","letterSpacing": "-0.01em","fontWeight": "600"}]},
              boxShadow: {'level-2': '0px 12px 32px rgba(0,0,0,0.04)','level-3': '0px 24px 48px rgba(0,0,0,0.08)'}
      },
          },
        }
    </script>
<style>
        .liquid-bg { background: radial-gradient(circle at 50% 50%, rgba(227, 226, 231, 0.4) 0%, rgba(250, 249, 254, 1) 70%); }
        .card-anim { animation: slideUpFade 0.6s ease-out forwards; }
        @keyframes slideUpFade { 0% { transform: translateY(8px); opacity: 0; } 100% { transform: translateY(0); opacity: 1; } }
        .ghost-divider { background: linear-gradient(to right, transparent, rgba(0,0,0,0.05) 20px, rgba(0,0,0,0.05) calc(100% - 20px), transparent); height: 1px; width: 100%; }
        ::-webkit-scrollbar { width: 6px; } ::-webkit-scrollbar-track { background: transparent; } ::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.1); border-radius: 10px; } ::-webkit-scrollbar-thumb:hover { background: rgba(0,0,0,0.2); }
    </style>
</head>
<body class="bg-background text-on-surface font-body-md text-body-md min-h-screen overflow-hidden liquid-bg flex flex-col relative aspect-[16/9] mx-auto max-w-[1920px]">
<nav class="flex justify-between items-center w-full px-container-padding h-[32px] z-50 bg-transparent fixed top-0 left-0 right-0">
<div class="flex items-center gap-element-gap"><span class="font-headline-md text-headline-md font-semibold text-primary dark:text-on-primary-fixed">AuraOS</span></div>
<div class="flex items-center gap-unit">
<button class="p-1 rounded-full text-on-surface-variant hover:bg-surface-container-highest/50 transition-colors duration-300 opacity-80 ease-out"><span class="material-symbols-outlined text-[16px]" style="font-variation-settings: 'FILL' 0;">remove</span></button>
<button class="p-1 rounded-full text-on-surface-variant hover:bg-surface-container-highest/50 transition-colors duration-300 opacity-80 ease-out"><span class="material-symbols-outlined text-[16px]" style="font-variation-settings: 'FILL' 0;">check_box_outline_blank</span></button>
<button class="p-1 rounded-full text-on-surface-variant hover:bg-surface-container-highest/50 transition-colors duration-300 opacity-80 ease-out hover:text-error"><span class="material-symbols-outlined text-[16px]" style="font-variation-settings: 'FILL' 0;">close</span></button>
</div>
</nav>
<div class="flex flex-1 pt-[32px] h-screen overflow-hidden">
<aside class="fixed left-0 top-0 h-full flex flex-col py-margin-lg px-margin-sm z-40 bg-white/60 dark:bg-tertiary-container/60 backdrop-blur-[40px] docked w-64 flat no shadows pt-[64px]">
<div class="mb-margin-lg px-unit flex items-center gap-element-gap">
<div class="w-10 h-10 rounded-full overflow-hidden shrink-0 bg-surface-container-high border border-outline/10"><img alt="User Profile" class="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuBMIE4XrjHezx5WD6zHzzNSeZP4uRdzq8M76IBkVItX6CyODOpTkdjYOeSS_txeXC3UmwYMuZRtpvkiVVcLhtkFRdT3K2gURzPhG2wEmqYrXNl7v2NFzRfMrkKnnvHE4S5j6ceOiLJnJy__9TczSO71RkI4GEi5O5ZJFz8wjU03O8097hmPBnUPYRFw6L_chbDsmxQxCfpCvZY03VlnS2xE9J4KUNN_DrmehkcH1nw5BhaaGA_bsdrLZMJL_46NuXvKD1VKCMQXGquQ"/></div>
<div><h2 class="font-label-sm text-label-sm text-on-surface">Pro Workspace</h2><p class="font-body-md text-[11px] text-on-surface-variant opacity-70">Zen Mode Active</p></div>
</div>
<nav class="flex flex-col gap-unit flex-1">
<a class="flex items-center gap-element-gap px-3 py-2 rounded-lg relative text-primary font-bold before:content-[''] before:absolute before:left-0 before:w-1 before:h-6 before:bg-primary before:rounded-full hover:bg-surface-container-high/40 transition-all duration-300 ease-out scale-[0.98]" href="#"><span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;">dashboard</span><span class="font-body-md text-body-md">Dashboard</span></a>
<a class="flex items-center gap-element-gap px-3 py-2 rounded-lg text-on-surface-variant hover:bg-surface-container-high/40 transition-all duration-300 ease-out" href="#"><span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 0;">download_for_offline</span><span class="font-body-md text-body-md">Downloads</span></a>
<a class="flex items-center gap-element-gap px-3 py-2 rounded-lg text-on-surface-variant hover:bg-surface-container-high/40 transition-all duration-300 ease-out" href="#"><span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 0;">library_books</span><span class="font-body-md text-body-md">Library</span></a>
<a class="flex items-center gap-element-gap px-3 py-2 rounded-lg text-on-surface-variant hover:bg-surface-container-high/40 transition-all duration-300 ease-out mt-auto" href="#"><span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 0;">settings</span><span class="font-body-md text-body-md">Settings</span></a>
</nav>
</aside>
<main class="ml-64 flex-1 p-container-padding overflow-y-auto h-full">
<header class="mb-margin-md card-anim" style="animation-delay: 0.1s;">
<h1 class="font-display text-display text-on-surface">Good Morning.</h1>
<p class="font-body-lg text-body-lg text-on-surface-variant mt-2">System operating smoothly in Zen Mode.</p>
</header>
<div class="grid grid-cols-12 gap-gutter">
<div class="col-span-12 lg:col-span-8 bg-surface-container-lowest rounded-card shadow-level-2 p-margin-md flex flex-col justify-between card-anim relative overflow-hidden" style="animation-delay: 0.2s; min-height: 280px;">
<div class="absolute -right-20 -top-20 w-64 h-64 bg-surface-container rounded-full blur-[60px] opacity-50 pointer-events-none"></div>
<div class="relative z-10">
<div class="flex justify-between items-start mb-6">
<div><h3 class="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider mb-1">System Status</h3><p class="font-headline-md text-headline-md text-on-surface">Optimal Performance</p></div>
<span class="material-symbols-outlined text-primary bg-surface-container-low p-2 rounded-full" style="font-variation-settings: 'FILL' 1;">speed</span>
</div>
<div class="grid grid-cols-3 gap-element-gap mt-auto pt-8 border-t border-surface-variant/50">
<div><p class="font-label-sm text-label-sm text-on-surface-variant mb-1">CPU Load</p><p class="font-headline-md text-headline-md font-semibold">12%</p></div>
<div><p class="font-label-sm text-label-sm text-on-surface-variant mb-1">Memory</p><p class="font-headline-md text-headline-md font-semibold">4.2 GB</p></div>
<div><p class="font-label-sm text-label-sm text-on-surface-variant mb-1">Network</p><p class="font-headline-md text-headline-md font-semibold">Stable</p></div>
</div>
</div>
</div>
<div class="col-span-12 lg:col-span-4 bg-primary text-on-primary rounded-card shadow-level-2 p-margin-md flex flex-col card-anim" style="animation-delay: 0.3s; min-height: 280px;">
<div class="flex justify-between items-center mb-auto"><span class="material-symbols-outlined text-[32px]" style="font-variation-settings: 'FILL' 0;">bolt</span></div>
<div>
<h3 class="font-headline-md text-headline-md mb-2">Focus Session</h3>
<p class="font-body-md text-body-md text-on-primary/80 mb-6">Block distractions and optimize background processes for deep work.</p>
<button class="w-full bg-white/10 hover:bg-white/20 text-on-primary py-3 px-6 rounded-xl font-body-md font-semibold transition-all duration-300 ease-out flex justify-center items-center gap-2"><span>Start Session</span><span class="material-symbols-outlined text-[18px]">arrow_forward</span></button>
</div>
</div>
<div class="col-span-12 lg:col-span-6 bg-surface-container-lowest rounded-card shadow-level-2 p-margin-md card-anim" style="animation-delay: 0.4s;">
<div class="flex justify-between items-center mb-6"><h3 class="font-headline-md text-headline-md text-on-surface">Recent Activity</h3><button class="text-on-surface-variant hover:text-primary transition-colors"><span class="material-symbols-outlined">more_horiz</span></button></div>
<div class="flex flex-col">
<div class="py-4 flex items-center gap-4"><div class="w-10 h-10 rounded-full bg-surface-container flex items-center justify-center shrink-0"><span class="material-symbols-outlined text-on-surface-variant text-[20px]">description</span></div><div class="flex-1"><p class="font-body-md text-on-surface font-semibold">Q3 Report Draft.docx</p><p class="font-label-sm text-label-sm text-on-surface-variant mt-1">Edited 10 mins ago</p></div></div>
<div class="ghost-divider"></div>
<div class="py-4 flex items-center gap-4"><div class="w-10 h-10 rounded-full bg-surface-container flex items-center justify-center shrink-0"><span class="material-symbols-outlined text-on-surface-variant text-[20px]">folder_shared</span></div><div class="flex-1"><p class="font-body-md text-on-surface font-semibold">Design Assets</p><p class="font-label-sm text-label-sm text-on-surface-variant mt-1">Synced to cloud</p></div></div>
<div class="ghost-divider"></div>
<div class="py-4 flex items-center gap-4"><div class="w-10 h-10 rounded-full bg-surface-container flex items-center justify-center shrink-0"><span class="material-symbols-outlined text-on-surface-variant text-[20px]">system_update</span></div><div class="flex-1"><p class="font-body-md text-on-surface font-semibold">System Update</p><p class="font-label-sm text-label-sm text-on-surface-variant mt-1">Completed successfully</p></div></div>
</div>
</div>
<div class="col-span-12 lg:col-span-6 bg-surface-container-lowest rounded-card shadow-level-2 p-margin-md card-anim" style="animation-delay: 0.5s;">
<div class="flex justify-between items-center mb-6"><h3 class="font-headline-md text-headline-md text-on-surface">Storage</h3><span class="font-label-sm text-label-sm text-on-surface-variant">256 GB Total</span></div>
<div class="flex items-end gap-2 mb-8"><span class="font-display text-display text-on-surface leading-none">184</span><span class="font-body-lg text-body-lg text-on-surface-variant mb-1">GB Free</span></div>
<div class="w-full h-3 bg-surface-container rounded-full overflow-hidden mb-6 flex"><div class="bg-primary h-full rounded-full" style="width: 45%;"></div><div class="bg-outline/30 h-full rounded-full ml-1" style="width: 15%;"></div></div>
<div class="flex gap-6">
<div class="flex items-center gap-2"><div class="w-3 h-3 rounded-full bg-primary"></div><span class="font-label-sm text-label-sm text-on-surface-variant">System</span></div>
<div class="flex items-center gap-2"><div class="w-3 h-3 rounded-full bg-outline/30"></div><span class="font-label-sm text-label-sm text-on-surface-variant">Apps</span></div>
<div class="flex items-center gap-2"><div class="w-3 h-3 rounded-full bg-surface-container"></div><span class="font-label-sm text-label-sm text-on-surface-variant">Free</span></div>
</div>
</div>
</div>
<div class="h-margin-lg"></div>
</main>
</div>
</body></html>
```

---

## 2. Downloads

**Mô tả:** Trang quản lý tải xuống. Hiển thị hàng đợi đang tải (Active Queue) với thanh tiến trình, danh sách tệp đã hoàn thành gần đây, và thẻ thông tin dung lượng ổ cứng. Có tính năng tìm kiếm và nút Pause All.

```html
<!-- Downloads - AuraOS -->
<!DOCTYPE html>

<html lang="en"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>AuraOS - Downloads</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@500;600&family=Inter:wght@400;600&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
<style>
        .material-symbols-outlined { font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24; }
        body { background-color: #faf9fe; background-image: radial-gradient(at 0% 0%, hsla(253,16%,7%,0.05) 0, transparent 50%), radial-gradient(at 50% 0%, hsla(225,39%,30%,0.05) 0, transparent 50%), radial-gradient(at 100% 0%, hsla(339,49%,30%,0.05) 0, transparent 50%); background-attachment: fixed; }
        .soft-sunk { background-color: #F5F5F7; transition: all 0.3s ease-out; }
        .soft-sunk:focus-within { background-color: #ffffff; box-shadow: 0 0 0 1px #121212, 0 0 12px rgba(0,0,0,0.05); }
    </style>
<script id="tailwind-config">
        tailwind.config = {
          darkMode: "class",
          theme: { extend: { "colors": { "surface-dim": "#dad9df","on-error-container": "#93000a","on-surface-variant": "#444748","primary-fixed": "#e5e2e1","on-primary": "#ffffff","secondary": "#5d5e60","secondary-fixed": "#e2e2e4","inverse-on-surface": "#f1f0f5","outline": "#747878","tertiary-fixed-dim": "#c6c6cc","secondary-container": "#dfdfe1","surface-container": "#eeedf3","tertiary": "#000000","surface-container-lowest": "#ffffff","error-container": "#ffdad6","on-secondary-fixed-variant": "#454749","tertiary-container": "#1a1c20","background": "#faf9fe","on-primary-fixed-variant": "#474646","outline-variant": "#c4c7c7","surface-container-high": "#e9e7ed","surface-container-highest": "#e3e2e7","on-surface": "#1a1b1f","on-secondary": "#ffffff","surface-variant": "#e3e2e7","primary-container": "#1c1b1b","on-error": "#ffffff","surface": "#faf9fe","secondary-fixed-dim": "#c6c6c8","tertiary-fixed": "#e2e2e8","inverse-primary": "#c8c6c5","on-tertiary": "#ffffff","on-tertiary-fixed": "#1a1c20","on-secondary-container": "#616365","on-tertiary-container": "#828389","primary": "#000000","inverse-surface": "#2f3034","on-primary-fixed": "#1c1b1b","on-primary-container": "#858383","surface-bright": "#faf9fe","primary-fixed-dim": "#c8c6c5","surface-container-low": "#f4f3f8","on-secondary-fixed": "#1a1c1d","surface-tint": "#5f5e5e","on-background": "#1a1b1f","on-tertiary-fixed-variant": "#45474b","error": "#ba1a1a" }, "borderRadius": {"DEFAULT": "0.25rem","lg": "0.5rem","xl": "0.75rem","full": "9999px"}, "spacing": {"element-gap": "12px","margin-sm": "16px","margin-lg": "64px","container-padding": "40px","unit": "8px","gutter": "24px","margin-md": "32px"}, "fontFamily": {"headline-md": ["Hanken Grotesk"],"body-md": ["Inter"],"body-lg": ["Inter"],"display": ["Hanken Grotesk"],"label-sm": ["Inter"],"headline-lg": ["Hanken Grotesk"]}, "fontSize": {"headline-md": ["24px",{"lineHeight": "1.3","fontWeight": "500"}],"body-md": ["15px",{"lineHeight": "1.5","fontWeight": "400"}],"body-lg": ["18px",{"lineHeight": "1.6","fontWeight": "400"}],"display": ["48px",{"lineHeight": "1.1","letterSpacing": "-0.02em","fontWeight": "600"}],"label-sm": ["12px",{"lineHeight": "1","letterSpacing": "0.05em","fontWeight": "600"}],"headline-lg": ["32px",{"lineHeight": "1.2","letterSpacing": "-0.01em","fontWeight": "600"}]} } },
        }
      </script>
</head>
<body class="bg-background text-on-background min-h-screen flex flex-col font-body-md overflow-hidden antialiased">
<nav class="bg-transparent flex justify-between items-center w-full px-container-padding h-8 z-50 fixed top-0 left-0 right-0">
<div class="flex items-center gap-element-gap"><span class="font-headline-md text-headline-md font-semibold text-primary">AuraOS</span></div>
<div class="flex items-center gap-unit text-on-surface">
<button class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-surface-container-highest/50 transition-colors duration-300"><span class="material-symbols-outlined text-[16px]">remove</span></button>
<button class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-surface-container-highest/50 transition-colors duration-300"><span class="material-symbols-outlined text-[16px]">check_box_outline_blank</span></button>
<button class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-surface-container-highest/50 transition-colors duration-300 hover:text-error hover:bg-error-container/50"><span class="material-symbols-outlined text-[16px]">close</span></button>
</div>
</nav>
<div class="flex flex-1 pt-[32px] h-screen w-full relative">
<aside class="fixed left-0 top-0 h-full flex flex-col py-margin-lg px-margin-sm z-40 w-64 bg-white/60 backdrop-blur-[40px] hidden md:flex border-r border-transparent">
<div class="mb-margin-lg px-unit mt-margin-md">
<div class="flex items-center gap-unit mb-unit">
<div class="w-10 h-10 rounded-full bg-surface-container-highest overflow-hidden"><img alt="User Profile" class="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuANIucniQZD2w1okcalZ_fti5jGgnHDhiTJRn6WHLy1LOJ-g8YYmXykXkEo1qv37mHpJyc9pdskLVG7viU7OL3GH8358Asa_yqt6uTtSoVmJqJJzBridqJ_3KG9xe9TQG_Qk4z1yXIlrsNIGcPq79HKHIvT5wFESE1C-gQkFg4UWQJA_GIODtFgQI4bJicd8OAWSATnM72qT7zKLaCCbWiy6vBD8XiKz1id5rMKBeaCHr_I1Zsh4FD8aCo0k-c0Ov5enY0nViuwku-1"/></div>
<div><h2 class="font-headline-md text-headline-md text-primary text-[18px]">Pro Workspace</h2><p class="font-label-sm text-label-sm text-on-surface-variant">Zen Mode Active</p></div>
</div>
</div>
<nav class="flex-1 space-y-unit">
<a class="flex items-center gap-element-gap px-unit py-2 rounded-lg text-on-surface-variant hover:bg-surface-container-high/40 transition-all duration-300 ease-out font-body-md text-body-md" href="#"><span class="material-symbols-outlined">dashboard</span>Dashboard</a>
<a class="flex items-center gap-element-gap px-unit py-2 rounded-lg relative text-primary font-bold before:content-[''] before:absolute before:left-[-16px] before:w-1 before:h-6 before:bg-primary before:rounded-full hover:bg-surface-container-high/40 transition-all duration-300 ease-out font-body-md text-body-md bg-surface-container-high/20" href="#"><span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;">download_for_offline</span>Downloads</a>
<a class="flex items-center gap-element-gap px-unit py-2 rounded-lg text-on-surface-variant hover:bg-surface-container-high/40 transition-all duration-300 ease-out font-body-md text-body-md" href="#"><span class="material-symbols-outlined">library_books</span>Library</a>
<a class="flex items-center gap-element-gap px-unit py-2 rounded-lg text-on-surface-variant hover:bg-surface-container-high/40 transition-all duration-300 ease-out font-body-md text-body-md mt-auto" href="#"><span class="material-symbols-outlined">settings</span>Settings</a>
</nav>
</aside>
<main class="flex-1 md:ml-64 p-container-padding overflow-y-auto w-full h-full pb-margin-lg">
<div class="max-w-5xl mx-auto w-full">
<header class="mb-margin-md flex justify-between items-end">
<div><h1 class="font-display text-display text-primary">Downloads</h1><p class="font-body-lg text-body-lg text-on-surface-variant mt-unit">2 Active, 3 Completed</p></div>
<div class="flex gap-element-gap">
<div class="soft-sunk rounded-full px-4 py-2 flex items-center gap-unit w-64"><span class="material-symbols-outlined text-outline">search</span><input class="bg-transparent border-none focus:ring-0 text-body-md w-full p-0 text-on-surface placeholder:text-outline-variant" placeholder="Search files..." type="text"/></div>
<button class="bg-primary text-on-primary font-label-sm text-label-sm px-6 py-2 rounded-lg hover:opacity-90 transition-opacity duration-300 flex items-center gap-unit shadow-[0_4px_14px_rgba(0,0,0,0.1)]"><span class="material-symbols-outlined text-[18px]">pause_circle</span>Pause All</button>
</div>
</header>
<div class="grid grid-cols-1 lg:grid-cols-12 gap-gutter">
<div class="lg:col-span-8 flex flex-col gap-element-gap">
<h3 class="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider mb-unit">Active Queue</h3>
<div class="bg-surface-container-lowest rounded-[24px] p-gutter shadow-[0px_12px_32px_rgba(0,0,0,0.04)] flex flex-col gap-margin-sm border border-surface-variant/50 relative overflow-hidden">
<div class="absolute inset-0 bg-gradient-to-r from-surface-container-lowest via-surface-container-low to-surface-container-lowest opacity-50 animate-pulse pointer-events-none w-[75%]"></div>
<div class="flex justify-between items-start relative z-10">
<div class="flex items-center gap-margin-sm"><div class="w-12 h-12 rounded-xl bg-surface-container flex items-center justify-center text-primary"><span class="material-symbols-outlined text-[24px]">folder_zip</span></div><div><h4 class="font-headline-md text-headline-md text-[18px] text-on-surface">Project_Aura_Assets_v2.zip</h4><p class="font-body-md text-body-md text-on-surface-variant">Downloading... 3.2 GB / 4.5 GB</p></div></div>
<button class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-surface-container-highest/50 transition-colors text-on-surface-variant"><span class="material-symbols-outlined">pause</span></button>
</div>
<div class="w-full relative z-10"><div class="flex justify-between font-label-sm text-label-sm text-on-surface-variant mb-unit"><span>75%</span><span>2 mins left</span></div><div class="h-2 w-full bg-surface-container rounded-full overflow-hidden"><div class="h-full bg-primary rounded-full" style="width: 75%;"></div></div></div>
</div>
<div class="bg-surface-container-lowest rounded-[24px] p-gutter shadow-[0px_12px_32px_rgba(0,0,0,0.04)] flex flex-col gap-margin-sm border border-surface-variant/50 relative overflow-hidden">
<div class="absolute inset-0 bg-gradient-to-r from-surface-container-lowest via-surface-container-low to-surface-container-lowest opacity-50 animate-pulse pointer-events-none w-[30%]"></div>
<div class="flex justify-between items-start relative z-10">
<div class="flex items-center gap-margin-sm"><div class="w-12 h-12 rounded-xl bg-surface-container flex items-center justify-center text-primary"><span class="material-symbols-outlined text-[24px]">movie</span></div><div><h4 class="font-headline-md text-headline-md text-[18px] text-on-surface">Design_System_Walkthrough.mp4</h4><p class="font-body-md text-body-md text-on-surface-variant">Downloading... 150 MB / 500 MB</p></div></div>
<button class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-surface-container-highest/50 transition-colors text-on-surface-variant"><span class="material-symbols-outlined">pause</span></button>
</div>
<div class="w-full relative z-10"><div class="flex justify-between font-label-sm text-label-sm text-on-surface-variant mb-unit"><span>30%</span><span>8 mins left</span></div><div class="h-2 w-full bg-surface-container rounded-full overflow-hidden"><div class="h-full bg-primary rounded-full" style="width: 30%;"></div></div></div>
</div>
</div>
<div class="lg:col-span-4 flex flex-col gap-element-gap">
<h3 class="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider mb-unit">Recently Completed</h3>
<div class="bg-surface-container-lowest rounded-[24px] p-margin-sm shadow-[0px_12px_32px_rgba(0,0,0,0.04)] flex flex-col gap-0 border border-surface-variant/50">
<div class="flex items-center justify-between p-unit hover:bg-surface-container-low rounded-xl transition-colors cursor-pointer group"><div class="flex items-center gap-unit"><div class="w-10 h-10 rounded-lg bg-surface-container flex items-center justify-center text-on-surface-variant group-hover:text-primary transition-colors"><span class="material-symbols-outlined text-[20px]">image</span></div><div class="overflow-hidden"><h5 class="font-body-md text-body-md text-on-surface font-medium truncate w-40">Hero_Background.png</h5><p class="font-label-sm text-label-sm text-outline font-normal">2.4 MB • Today</p></div></div><button class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-surface-container-highest transition-colors opacity-0 group-hover:opacity-100 text-on-surface-variant"><span class="material-symbols-outlined text-[18px]">more_vert</span></button></div>
<hr class="border-t border-surface-variant mx-unit my-1 opacity-50"/>
<div class="flex items-center justify-between p-unit hover:bg-surface-container-low rounded-xl transition-colors cursor-pointer group"><div class="flex items-center gap-unit"><div class="w-10 h-10 rounded-lg bg-surface-container flex items-center justify-center text-on-surface-variant group-hover:text-primary transition-colors"><span class="material-symbols-outlined text-[20px]">description</span></div><div class="overflow-hidden"><h5 class="font-body-md text-body-md text-on-surface font-medium truncate w-40">Q3_Report_Final.pdf</h5><p class="font-label-sm text-label-sm text-outline font-normal">8.1 MB • Yesterday</p></div></div><button class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-surface-container-highest transition-colors opacity-0 group-hover:opacity-100 text-on-surface-variant"><span class="material-symbols-outlined text-[18px]">more_vert</span></button></div>
<hr class="border-t border-surface-variant mx-unit my-1 opacity-50"/>
<div class="flex items-center justify-between p-unit hover:bg-surface-container-low rounded-xl transition-colors cursor-pointer group"><div class="flex items-center gap-unit"><div class="w-10 h-10 rounded-lg bg-surface-container flex items-center justify-center text-on-surface-variant group-hover:text-primary transition-colors"><span class="material-symbols-outlined text-[20px]">audio_file</span></div><div class="overflow-hidden"><h5 class="font-body-md text-body-md text-on-surface font-medium truncate w-40">Ambient_Loop.wav</h5><p class="font-label-sm text-label-sm text-outline font-normal">45 MB • Yesterday</p></div></div><button class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-surface-container-highest transition-colors opacity-0 group-hover:opacity-100 text-on-surface-variant"><span class="material-symbols-outlined text-[18px]">more_vert</span></button></div>
</div>
<div class="bg-surface-container-lowest rounded-[24px] p-margin-sm shadow-[0px_12px_32px_rgba(0,0,0,0.04)] border border-surface-variant/50 mt-unit"><div class="flex items-center gap-unit mb-margin-sm"><span class="material-symbols-outlined text-outline">hard_drive</span><h4 class="font-body-md text-body-md font-medium text-on-surface">Local Storage</h4></div><div class="h-2 w-full bg-surface-container rounded-full overflow-hidden mb-unit"><div class="h-full bg-outline rounded-full" style="width: 82%;"></div></div><p class="font-label-sm text-label-sm text-on-surface-variant">410 GB used of 500 GB</p></div>
</div>
</div>
</div>
</main>
</div>
</body></html>
```

---

## 3. Library

**Mô tả:** Thư viện tệp đã tải về. Hiển thị lưới nội dung 12 cột gồm hình ảnh, tài liệu PDF, video (với play overlay khi hover), thư mục collection, và hình thu nhỏ. Có bộ lọc theo loại tệp (All / Images / Documents / Videos).

```html
<!-- Library - AuraOS -->
<!DOCTYPE html>

<html class="light" lang="en"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>AuraOS - Library</title>
<link href="https://fonts.googleapis.com" rel="preconnect"/>
<link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect"/>
<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@500;600;700;800&family=Inter:wght@400;600&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<script id="tailwind-config">
      tailwind.config = {
        darkMode: "class",
        theme: { extend: { colors: { "surface-dim": "#dad9df","on-error-container": "#93000a","on-surface-variant": "#444748","primary-fixed": "#e5e2e1","on-primary": "#ffffff","secondary": "#5d5e60","secondary-fixed": "#e2e2e4","inverse-on-surface": "#f1f0f5","outline": "#747878","tertiary-fixed-dim": "#c6c6cc","secondary-container": "#dfdfe1","surface-container": "#eeedf3","tertiary": "#000000","surface-container-lowest": "#ffffff","error-container": "#ffdad6","on-secondary-fixed-variant": "#454749","tertiary-container": "#1a1c20","background": "#faf9fe","on-primary-fixed-variant": "#474646","outline-variant": "#c4c7c7","surface-container-high": "#e9e7ed","surface-container-highest": "#e3e2e7","on-surface": "#1a1b1f","on-secondary": "#ffffff","surface-variant": "#e3e2e7","primary-container": "#1c1b1b","on-error": "#ffffff","surface": "#faf9fe","secondary-fixed-dim": "#c6c6c8","tertiary-fixed": "#e2e2e8","inverse-primary": "#c8c6c5","on-tertiary": "#ffffff","on-tertiary-fixed": "#1a1c20","on-secondary-container": "#616365","on-tertiary-container": "#828389","primary": "#000000","inverse-surface": "#2f3034","on-primary-fixed": "#1c1b1b","on-primary-container": "#858383","surface-bright": "#faf9fe","primary-fixed-dim": "#c8c6c5","surface-container-low": "#f4f3f8","on-secondary-fixed": "#1a1c1d","surface-tint": "#5f5e5e","on-background": "#1a1b1f","on-tertiary-fixed-variant": "#45474b","error": "#ba1a1a" }, borderRadius: {"DEFAULT": "0.25rem","lg": "0.5rem","xl": "0.75rem","full": "9999px"}, spacing: {"element-gap": "12px","margin-sm": "16px","margin-lg": "64px","container-padding": "40px","unit": "8px","gutter": "24px","margin-md": "32px"}, fontFamily: {"headline-md": ["Hanken Grotesk"],"body-md": ["Inter"],"body-lg": ["Inter"],"display": ["Hanken Grotesk"],"label-sm": ["Inter"],"headline-lg": ["Hanken Grotesk"]}, fontSize: {"headline-md": ["24px",{"lineHeight": "1.3","fontWeight": "500"}],"body-md": ["15px",{"lineHeight": "1.5","fontWeight": "400"}],"body-lg": ["18px",{"lineHeight": "1.6","fontWeight": "400"}],"display": ["48px",{"lineHeight": "1.1","letterSpacing": "-0.02em","fontWeight": "600"}],"label-sm": ["12px",{"lineHeight": "1","letterSpacing": "0.05em","fontWeight": "600"}],"headline-lg": ["32px",{"lineHeight": "1.2","letterSpacing": "-0.01em","fontWeight": "600"}]} } }
      }
    </script>
<style>
        body { background-color: #faf9fe; background-image: radial-gradient(at 0% 0%, hsla(253,16%,7%,0.03) 0, transparent 50%), radial-gradient(at 50% 0%, hsla(225,39%,30%,0.03) 0, transparent 50%), radial-gradient(at 100% 0%, hsla(339,49%,30%,0.03) 0, transparent 50%); background-attachment: fixed; overflow-x: hidden; }
        .glass-card { box-shadow: 0px 12px 32px rgba(0,0,0,0.04); transition: all 0.3s ease-out; }
        .glass-card:hover { box-shadow: 0px 16px 40px rgba(0,0,0,0.06); transform: translateY(-2px); }
        ::-webkit-scrollbar { width: 6px; } ::-webkit-scrollbar-track { background: transparent; } ::-webkit-scrollbar-thumb { background: #dfdfe1; border-radius: 10px; }
    </style>
</head>
<body class="min-h-screen text-on-surface font-body-md antialiased flex flex-col">
<header class="bg-transparent text-on-surface font-headline-md text-headline-md h-[32px] flat flex justify-between items-center w-full px-container-padding z-50 fixed">
<div class="flex items-center gap-element-gap"><span class="font-headline-md text-headline-md font-semibold text-primary">AuraOS</span></div>
<div class="flex items-center gap-margin-sm h-full">
<div class="relative flex items-center h-6 mr-margin-md"><span class="material-symbols-outlined absolute left-2 text-[16px] text-on-surface-variant z-10 pointer-events-none">search</span><input class="h-full w-64 bg-surface-container-low text-label-sm font-label-sm text-on-surface placeholder:text-outline border-0 focus:ring-0 focus:bg-surface-container-lowest rounded-lg pl-8 pr-3 transition-all duration-300 ease-out outline-none" placeholder="Search files..." type="text"/></div>
<button class="hover:bg-surface-container-highest/50 w-8 h-8 flex items-center justify-center rounded-DEFAULT text-on-surface-variant opacity-80"><span class="material-symbols-outlined text-[16px]">remove</span></button>
<button class="hover:bg-surface-container-highest/50 w-8 h-8 flex items-center justify-center rounded-DEFAULT text-on-surface-variant opacity-80"><span class="material-symbols-outlined text-[16px]">check_box_outline_blank</span></button>
<button class="hover:bg-surface-container-highest/50 w-8 h-8 flex items-center justify-center rounded-DEFAULT text-on-surface-variant opacity-80 hover:text-on-error hover:bg-error"><span class="material-symbols-outlined text-[16px]">close</span></button>
</div>
</header>
<div class="flex flex-1 pt-[32px]">
<nav class="bg-white/60 backdrop-blur-[40px] h-full w-64 fixed left-0 top-0 flex flex-col py-margin-lg px-margin-sm z-40 border-r border-surface-container-highest/30">
<div class="flex items-center gap-unit mb-margin-lg px-unit"><div class="w-10 h-10 rounded-full bg-surface-container-high overflow-hidden shrink-0 border border-surface-container-highest"><img alt="User Profile" class="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuAPReEq3pPVU-2UBM2bcN_aFA2UQ-xZO9KmrVb8Ifs4MuMfXaUbDM45HWdJmZyWExTrpnN4qHctk-9b3qQhGhnW4xJ7cMV65XuflKkAmU9mA0L6409gW7nibs664lzfxlrj02EsJqnShfnBgNMH1iT2eVEa_871I3m1A_VInU_PisZWSomfFTKoW7PaXk0uEUEqG21CTyX2tgdo2wkF2C03KLBv_rNLtjaitBZ7inVquKGpAPpwSywp6JKD0MYmkNcN9EEuPU1WdLWs"/></div><div class="flex flex-col"><span class="font-label-sm text-label-sm text-primary">Pro Workspace</span><span class="text-[10px] font-body-md text-on-surface-variant mt-0.5">Zen Mode Active</span></div></div>
<div class="flex flex-col gap-unit">
<a class="flex items-center gap-element-gap px-3 py-2.5 rounded-lg text-on-surface-variant hover:bg-surface-container-high/40 transition-all duration-300 ease-out group" href="#"><span class="material-symbols-outlined text-[20px] group-hover:text-primary transition-colors">dashboard</span><span class="font-body-md text-body-md">Dashboard</span></a>
<a class="flex items-center gap-element-gap px-3 py-2.5 rounded-lg text-on-surface-variant hover:bg-surface-container-high/40 transition-all duration-300 ease-out group" href="#"><span class="material-symbols-outlined text-[20px] group-hover:text-primary transition-colors">download_for_offline</span><span class="font-body-md text-body-md">Downloads</span></a>
<a class="flex items-center gap-element-gap px-3 py-2.5 rounded-lg bg-surface-container-high/20 hover:bg-surface-container-high/40 transition-all duration-300 ease-out scale-[0.98] relative text-primary font-bold before:content-[''] before:absolute before:left-0 before:w-1 before:h-6 before:bg-primary before:rounded-full" href="#"><span class="material-symbols-outlined text-[20px]" style="font-variation-settings: 'FILL' 1;">library_books</span><span class="font-body-md text-body-md">Library</span></a>
<a class="flex items-center gap-element-gap px-3 py-2.5 rounded-lg text-on-surface-variant hover:bg-surface-container-high/40 transition-all duration-300 ease-out group mt-margin-sm" href="#"><span class="material-symbols-outlined text-[20px] group-hover:text-primary transition-colors">settings</span><span class="font-body-md text-body-md">Settings</span></a>
</div>
</nav>
<main class="ml-64 flex-1 flex flex-col p-container-padding max-w-[1600px] mx-auto w-full">
<div class="flex justify-between items-end mb-margin-md">
<div><h1 class="font-display text-display text-primary tracking-tight">Library</h1><p class="font-body-md text-body-md text-on-surface-variant mt-2">Manage your downloaded assets and documents.</p></div>
<div class="flex gap-unit bg-surface-container-lowest p-1 rounded-xl glass-card">
<button class="px-4 py-1.5 rounded-lg bg-surface-container text-primary font-label-sm text-label-sm transition-all duration-300">All Files</button>
<button class="px-4 py-1.5 rounded-lg text-on-surface-variant hover:bg-surface-container-lowest hover:text-primary font-label-sm text-label-sm transition-all duration-300">Images</button>
<button class="px-4 py-1.5 rounded-lg text-on-surface-variant hover:bg-surface-container-lowest hover:text-primary font-label-sm text-label-sm transition-all duration-300">Documents</button>
<button class="px-4 py-1.5 rounded-lg text-on-surface-variant hover:bg-surface-container-lowest hover:text-primary font-label-sm text-label-sm transition-all duration-300">Videos</button>
</div>
</div>
<div class="grid grid-cols-12 gap-gutter">
<div class="col-span-12 md:col-span-6 lg:col-span-4 glass-card bg-surface-container-lowest rounded-xl overflow-hidden flex flex-col group cursor-pointer">
<div class="h-48 relative overflow-hidden bg-surface-container-low"><img alt="Abstract liquid art" class="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-700 ease-out" src="https://lh3.googleusercontent.com/aida-public/AB6AXuA2uvmtHHz4HH-DLM8Zz6jygE2ugEG7v9R6w5rTUmVGa_PrH4QgGcfBwWwvxFx7T8weKcPEc0q_MfBBodI_ms_EI5l9an93-u8fKfqUE5EYsrf2hwEfZwHEArHmnabdnsRm8faVLCWQ397oxx-cWQRzOQ4JPu-tnsNkFNKYqJ5j37cAo6EF9EXjOfTe2Yo-GeREoszHI-rQ2uOKpjG8Np-ZPJ2wRNB1FtC8z71lkht_uf9p3aUD46WPrS-qLGt-n8NsDDe9w_2xyQJU"/><div class="absolute top-3 right-3 bg-surface-container-lowest/80 backdrop-blur-md px-2 py-1 rounded-DEFAULT flex items-center gap-1"><span class="material-symbols-outlined text-[14px]">image</span></div></div>
<div class="p-4 flex-1 flex flex-col justify-between"><div><h3 class="font-headline-md text-[16px] text-primary truncate">Atmospheric_Liquid_Render_V2.png</h3><p class="font-body-md text-[13px] text-on-surface-variant mt-1">Added 2 hours ago • 4.2 MB</p></div></div>
</div>
<div class="col-span-12 md:col-span-6 lg:col-span-4 glass-card bg-surface-container-lowest rounded-xl overflow-hidden flex flex-col group cursor-pointer">
<div class="h-48 relative bg-surface-container-low flex items-center justify-center p-6"><div class="w-full h-full bg-surface-container-lowest rounded-lg shadow-sm border border-surface-container flex flex-col p-4 relative overflow-hidden"><div class="w-3/4 h-2 bg-surface-container rounded-full mb-3"></div><div class="w-full h-2 bg-surface-container rounded-full mb-2"></div><div class="w-5/6 h-2 bg-surface-container rounded-full mb-2"></div><div class="w-full h-2 bg-surface-container rounded-full mb-2"></div><div class="w-4/5 h-2 bg-surface-container rounded-full mb-2"></div><div class="absolute top-3 right-3 bg-primary/5 px-2 py-1 rounded-DEFAULT flex items-center gap-1"><span class="material-symbols-outlined text-[14px] text-primary">description</span></div></div></div>
<div class="p-4 flex-1 flex flex-col justify-between"><div><h3 class="font-headline-md text-[16px] text-primary truncate">Q3_Design_System_Guidelines.pdf</h3><p class="font-body-md text-[13px] text-on-surface-variant mt-1">Added yesterday • 1.8 MB</p></div></div>
</div>
<div class="col-span-12 md:col-span-6 lg:col-span-4 glass-card bg-surface-container-lowest rounded-xl overflow-hidden flex flex-col group cursor-pointer">
<div class="h-48 relative overflow-hidden bg-surface-container-low"><img alt="Server room layout" class="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-700 ease-out" src="https://lh3.googleusercontent.com/aida-public/AB6AXuAd9VWZIEvCOHuZ7q70LMi3G354URnjkjaeFhYASE-PIVPvDWJrI0KGrHsOXR81qUD2UxYQPDHkih9bkZYuR5BKi4WvseddKg7Uvuxj6GZTFRmu8lnzKDXDfQtKw53rIXfORG6hXdoZuFPAbNlyxKz9u0x5gb4ezLH26AOk6c-NMVg5VdWshfQtytUAoUhVP4-hRw8_wBo1M2AQkKQ6_kpNeMensdzSnDhTZ6LnIT3izeAkYziN3-XvSurRV2Jjk7-0oZtSv8cz95mg"/><div class="absolute inset-0 bg-primary/10 group-hover:bg-transparent transition-colors duration-500"></div><div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300"><div class="w-12 h-12 bg-surface-container-lowest/90 backdrop-blur-md rounded-full flex items-center justify-center shadow-lg"><span class="material-symbols-outlined text-primary text-[24px]" style="font-variation-settings: 'FILL' 1;">play_arrow</span></div></div><div class="absolute bottom-3 right-3 bg-surface-container-lowest/80 backdrop-blur-md px-2 py-1 rounded-DEFAULT flex items-center gap-1"><span class="font-label-sm text-[10px] text-primary">02:45</span></div><div class="absolute top-3 right-3 bg-surface-container-lowest/80 backdrop-blur-md px-2 py-1 rounded-DEFAULT flex items-center gap-1"><span class="material-symbols-outlined text-[14px]">movie</span></div></div>
<div class="p-4 flex-1 flex flex-col justify-between"><div><h3 class="font-headline-md text-[16px] text-primary truncate">Onboarding_Walkthrough_Final.mp4</h3><p class="font-body-md text-[13px] text-on-surface-variant mt-1">Added 3 days ago • 142 MB</p></div></div>
</div>
<div class="col-span-12 md:col-span-6 glass-card bg-surface-container-lowest rounded-xl overflow-hidden flex p-4 items-center gap-gutter group cursor-pointer">
<div class="w-24 h-24 rounded-lg bg-surface-container-low flex items-center justify-center shrink-0 border border-surface-container group-hover:border-outline-variant transition-colors"><span class="material-symbols-outlined text-[32px] text-on-surface-variant group-hover:text-primary transition-colors" style="font-variation-settings: 'FILL' 1;">folder_open</span></div>
<div class="flex-1 min-w-0"><h3 class="font-headline-md text-[18px] text-primary truncate mb-1">Project_Alpha_Assets</h3><p class="font-body-md text-[14px] text-on-surface-variant mb-3">124 items • Images, Vectors, Fonts</p><div class="flex -space-x-2"><div class="w-6 h-6 rounded-full bg-surface-container border-2 border-surface-container-lowest z-30"></div><div class="w-6 h-6 rounded-full bg-surface-container-high border-2 border-surface-container-lowest z-20"></div><div class="w-6 h-6 rounded-full bg-surface-variant border-2 border-surface-container-lowest z-10 flex items-center justify-center"><span class="text-[8px] font-label-sm text-primary">+</span></div></div></div>
<button class="w-10 h-10 rounded-full hover:bg-surface-container flex items-center justify-center text-on-surface-variant transition-colors"><span class="material-symbols-outlined text-[20px]">more_vert</span></button>
</div>
<div class="col-span-12 sm:col-span-6 lg:col-span-3 glass-card bg-surface-container-lowest rounded-xl overflow-hidden flex flex-col group cursor-pointer"><div class="h-32 relative overflow-hidden bg-surface-container-low"><img alt="Minimalist architecture" class="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-700 ease-out" src="https://lh3.googleusercontent.com/aida-public/AB6AXuBXYzUjRZue934Vpg5nM3xmwS72fJAboWM2aMY13wUnRuHbSAgMiMMAv92nniVoCJZYhrc1kRagEn70UCs1emByg2sDj26AHiCMhrsxEk_lPdbymspWbhc4PwH5hu563Gp5DcUKEsD5BlPwGx2UcbVHYQL2PZHP1b32aS8PkZ0qu7zYmZ4CC0WhEa3fJMZz7p1mbi3gI7z-akD3DDABhwaSGtf65FnzYCVMIY577LtWAEUqvfrex0uP8-3GeRrMvB4EOr6mTkYa28oL"/></div><div class="p-3"><h3 class="font-body-md font-semibold text-[14px] text-primary truncate">Structure_Ref_01.jpg</h3><p class="font-body-md text-[12px] text-on-surface-variant mt-0.5">800 KB</p></div></div>
<div class="col-span-12 sm:col-span-6 lg:col-span-3 glass-card bg-surface-container-lowest rounded-xl overflow-hidden flex flex-col group cursor-pointer"><div class="h-32 relative overflow-hidden bg-surface-container-low"><img alt="Soft texture" class="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-700 ease-out" src="https://lh3.googleusercontent.com/aida-public/AB6AXuCtmrnp_lCGffGCeqkFpd8qnmb3nMxpyVam8N_pIPLCYAh123HLYVJoNvliFKb4tBePiq1i-I9j7XDl77P8rc86Gi34hh36c5JIZAol_uY8Q1VjmC5FYtIOSj22UYzcrzIHtEMznFEncecWNXwctYaXjcy3UcMF4tX4LcTMvk0e4J-xpnrZ6pXIPX7zZGpuLxLe_k8pL3Lw3Yka_WYz8wy8ayBWSaJBJ30Iv2tmfpoQI_NrmDvDwxWKXIr87Rzej5mSN4HLtP7-Y-mx"/></div><div class="p-3"><h3 class="font-body-md font-semibold text-[14px] text-primary truncate">Texture_Base_Light.jpg</h3><p class="font-body-md text-[12px] text-on-surface-variant mt-0.5">1.2 MB</p></div></div>
</div>
<div class="h-margin-lg"></div>
</main>
</div>
</body></html>
```

---

## 4. Scanner

**Mô tả:** Channel Scanner của BATMAN V3 (tích hợp trong AuraOS). Cho phép dán URL kênh Dailymotion để quét video mới nhất. Có thanh điều hướng tab ngang (Analyze / Download / Scanner / Research), ô nhập URL, bộ chọn số lượng video, nút quét, và khu vực kết quả phía dưới.

```html
<!-- Scanner - AuraOS -->
<!DOCTYPE html>

<html lang="en"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Batman V3 - Channel Scanner</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com" rel="preconnect"/>
<link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect"/>
<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@300;400;500;600;700&display=swap" rel="stylesheet"/>
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet"/>
<script>
    tailwind.config = {
      theme: {
        extend: {
          fontFamily: { sans: ['"Hanken Grotesk"', 'sans-serif'] },
          colors: {
            surface: '#faf9fe','surface-dim': '#dad9df','surface-bright': '#faf9fe','surface-container-lowest': '#ffffff','surface-container-low': '#f4f3f8','surface-container': '#eeedf3','surface-container-high': '#e9e8ed','surface-container-highest': '#e3e2e8',
            primary: '#595992','on-primary': '#ffffff','primary-container': '#e0e0ff','on-primary-container': '#15154b',
            secondary: '#5c5d72','on-secondary': '#ffffff','secondary-container': '#e1e0f9','on-secondary-container': '#181a2c',
            outline: '#777680','outline-variant': '#c7c5d0',error: '#ba1a1a','on-error': '#ffffff','error-container': '#ffdad6','on-error-container': '#410002',
            background: '#faf9fe','on-background': '#1b1b1f','on-surface': '#1b1b1f','on-surface-variant': '#46464f'
          },
          borderRadius: { 'none': '0','sm': '0.125rem',DEFAULT: '0.5rem','md': '0.5rem','lg': '0.75rem','xl': '1rem','2xl': '1.5rem','3xl': '2rem','full': '9999px' }
        }
      }
    }
  </script>
<style>
    body { background-color: #faf9fe; color: #1b1b1f; }
    ::-webkit-scrollbar { width: 8px; height: 8px; } ::-webkit-scrollbar-track { background: #f4f3f8; border-radius: 0.5rem; } ::-webkit-scrollbar-thumb { background: #c7c5d0; border-radius: 0.5rem; } ::-webkit-scrollbar-thumb:hover { background: #777680; }
  </style>
</head>
<body class="h-screen w-screen flex flex-col overflow-hidden text-sm">
<header class="h-14 border-b border-outline-variant bg-surface-container flex items-center justify-between px-4 shrink-0 z-10">
<div class="flex items-center gap-4"><div class="flex flex-col"><span class="font-bold text-base text-primary">BATMAN V3</span><span class="text-[10px] text-on-surface-variant uppercase tracking-wider">Final Super Mạnh Mẽ</span></div></div>
<nav class="flex gap-2">
<a class="px-4 py-2 rounded-md flex items-center gap-2 text-on-surface-variant hover:bg-surface-container-high transition-colors" href="#"><i class="fa-solid fa-chart-line text-xs"></i><span class="font-medium">Analyze</span></a>
<a class="px-4 py-2 rounded-md flex items-center gap-2 text-on-surface-variant hover:bg-surface-container-high transition-colors" href="#"><i class="fa-solid fa-download text-xs"></i><span class="font-medium">Download</span></a>
<a class="px-4 py-2 rounded-md bg-primary-container text-on-primary-container flex items-center gap-2 transition-colors" href="#"><i class="fa-solid fa-satellite-dish text-xs"></i><span class="font-medium">Scanner</span></a>
<a class="px-4 py-2 rounded-md flex items-center gap-2 text-on-surface-variant hover:bg-surface-container-high transition-colors" href="#"><i class="fa-solid fa-search text-xs"></i><span class="font-medium">Research</span></a>
</nav>
<div class="flex items-center gap-4 text-xs text-on-surface-variant"><div class="flex items-center gap-1"><i class="fa-solid fa-map-marker-alt text-[10px]"></i><span>IP Info</span></div><span>v3.0 Unified</span></div>
</header>
<div class="flex flex-1 overflow-hidden">
<main class="flex-1 flex flex-col bg-surface overflow-hidden relative">
<div class="p-6 pb-2 shrink-0">
<h1 class="text-lg font-bold text-on-surface mb-2">Channel Scanner</h1>
<p class="text-on-surface-variant text-sm mb-6">Paste a channel URL to scan the latest videos. Select and download them.</p>
<div class="flex items-center justify-between mb-4">
<div class="flex items-center gap-2 text-sm"><i class="fa-solid fa-folder text-yellow-500"></i><span class="text-secondary font-medium">C:/Users/trinh/Downloads/DAILYMOTION/194</span></div>
<button class="px-4 py-1.5 border border-outline-variant text-on-surface rounded-md hover:bg-surface-container-highest transition-colors font-medium text-xs">Change Folder</button>
</div>
<div class="flex gap-4 items-center">
<div class="relative flex-1"><input class="w-full bg-surface-container-low border border-outline-variant rounded-md px-4 py-2.5 text-sm text-on-surface placeholder:text-on-surface-variant/50 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary" placeholder="Paste Channel URL..." type="text"/></div>
<div class="flex items-center gap-2 bg-surface-container-low border border-outline-variant rounded-md px-3 py-1.5"><input class="w-12 bg-transparent border-none p-0 text-sm text-center text-on-surface focus:ring-0" type="number" value="20"/><div class="flex flex-col"><button class="text-on-surface-variant hover:text-on-surface h-3 flex items-center justify-center"><i class="fa-solid fa-caret-up text-[10px]"></i></button><button class="text-on-surface-variant hover:text-on-surface h-3 flex items-center justify-center"><i class="fa-solid fa-caret-down text-[10px]"></i></button></div></div>
<button class="bg-primary text-on-primary px-6 py-2.5 rounded-md font-semibold hover:bg-primary/90 transition-colors whitespace-nowrap shadow-sm">SCAN CHANNEL</button>
</div>
</div>
<div class="flex-1 p-6 overflow-y-auto"></div>
<div class="p-4 border-t border-outline-variant bg-surface-container flex gap-4 items-center shrink-0">
<button class="bg-error text-on-error px-6 py-2.5 rounded-md font-semibold hover:bg-error/90 transition-colors flex items-center gap-2 shadow-sm shrink-0"><i class="fa-solid fa-trash-can text-sm"></i>CLEAR ALL</button>
<button class="flex-1 bg-primary text-on-primary py-2.5 rounded-md font-semibold hover:bg-primary/90 transition-colors shadow-sm text-center">DOWNLOAD SELECTED VIDEOS</button>
</div>
<div class="h-8 bg-surface-container-highest border-t border-outline-variant flex items-center px-4 shrink-0 text-xs text-on-surface-variant gap-2"><i class="fa-solid fa-rocket text-[10px]"></i><span>Ready</span></div>
</main>
</div>
</body></html>
```

---

## 5. Research & Trend

**Mô tả:** Trang nghiên cứu xu hướng Dailymotion. Cho phép tìm kiếm theo từ khóa, lọc theo Trending / Latest / Most Viewed. Kết quả hiển thị dạng lưới 2 cột với thẻ video chi tiết: thumbnail, thống kê lượt xem (Total / 24H / 1H), trạng thái geoblock, URL và link thumbnail.

```html
<!-- Research - AuraOS -->
<!DOCTYPE html>

<html lang="en"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Research &amp; Trend - Fluidic Professional</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet"/>
<script>
    tailwind.config = {
      theme: {
        extend: {
          fontFamily: { sans: ['"Hanken Grotesk"', 'sans-serif'] },
          colors: {
            surface: '#faf9fe','surface-dim': '#dad9df','surface-bright': '#faf9fe','surface-container-lowest': '#ffffff','surface-container-low': '#f4f3f8','surface-container': '#eeedf2','surface-container-high': '#e8e8ed','surface-container-highest': '#e3e2e7',
            primary: '#595992','on-primary': '#ffffff','primary-container': '#e1dfff','on-primary-container': '#15144b',
            secondary: '#5d5d72','on-secondary': '#ffffff','secondary-container': '#e3e0f9','on-secondary-container': '#1a1a2c',
            tertiary: '#795369','on-tertiary': '#ffffff','tertiary-container': '#ffd8ec','on-tertiary-container': '#2f1124',
            error: '#ba1a1a','on-error': '#ffffff','error-container': '#ffdad6','on-error-container': '#410002',
            background: '#faf9fe','on-background': '#1b1b1f','on-surface': '#1b1b1f','on-surface-variant': '#47464f',outline: '#777680','outline-variant': '#c8c5d0'
          },
          borderRadius: { 'none': '0','sm': '2px',DEFAULT: '4px','md': '6px','lg': '8px','xl': '12px','2xl': '16px','3xl': '24px','full': '9999px' }
        }
      }
    }
  </script>
<style>
    body { background-color: #faf9fe; color: #1b1b1f; }
    .card-shadow { box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24); }
  </style>
</head>
<body class="flex h-screen overflow-hidden font-sans antialiased text-on-background bg-background">
<aside class="w-64 flex-shrink-0 border-r border-outline-variant bg-surface-container-low flex flex-col justify-between">
<div>
<div class="h-16 flex items-center px-6 border-b border-outline-variant"><span class="text-lg font-bold text-primary">BATMAN V3</span></div>
<nav class="p-4 space-y-1">
<a class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors" href="#"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewbox="0 0 24 24"><path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg><span class="font-medium text-sm">Analyze</span></a>
<a class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors" href="#"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewbox="0 0 24 24"><path d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg><span class="font-medium text-sm">Download</span></a>
<a class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors" href="#"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewbox="0 0 24 24"><path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path><path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg><span class="font-medium text-sm">Scanner</span></a>
<a class="flex items-center gap-3 px-3 py-2.5 rounded-lg bg-primary-container text-on-primary-container font-semibold transition-colors" href="#"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewbox="0 0 24 24"><path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg><span class="font-medium text-sm">Research</span></a>
</nav>
</div>
<div class="p-4 border-t border-outline-variant"><div class="flex items-center gap-2 text-sm text-on-surface-variant"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewbox="0 0 24 24"><path d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg><span>v3.0 Unified</span></div></div>
</aside>
<div class="flex-1 flex flex-col min-w-0 overflow-hidden">
<header class="h-16 flex-shrink-0 border-b border-outline-variant bg-surface flex items-center justify-between px-6">
<h1 class="text-xl font-semibold text-on-surface">Research &amp; Trend</h1>
<div class="flex items-center gap-4"><button class="flex items-center gap-2 text-sm font-medium text-on-surface-variant hover:text-on-surface transition-colors"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewbox="0 0 24 24"><path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>IP Info</button></div>
</header>
<main class="flex-1 overflow-y-auto bg-surface-container-lowest p-6">
<div class="max-w-7xl mx-auto space-y-6">
<section class="bg-surface-container-low rounded-xl p-5 border border-outline-variant">
<p class="text-sm text-on-surface-variant mb-4">Search Dailymotion for trending keywords, filter by views, and discover competitor content.</p>
<div class="flex flex-wrap items-center gap-4">
<div class="flex-1 min-w-[200px]"><input class="w-full bg-surface border border-outline-variant rounded-lg px-4 py-2 text-sm text-on-surface focus:border-primary focus:ring-1 focus:ring-primary" placeholder="Enter keyword..." type="text" value="full"/></div>
<div class="relative"><select class="appearance-none bg-surface border border-outline-variant rounded-lg pl-4 pr-10 py-2 text-sm text-on-surface focus:border-primary focus:ring-1 focus:ring-primary cursor-pointer"><option>🔥 Trending</option><option>Latest</option><option>Most Viewed</option></select><div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-on-surface-variant"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewbox="0 0 24 24"><path d="M19 9l-7 7-7-7" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg></div></div>
<button class="bg-primary hover:bg-primary/90 text-on-primary font-medium text-sm px-6 py-2 rounded-lg transition-colors">SEARCH</button>
<button class="bg-error-container hover:bg-error-container/80 text-on-error-container font-medium text-sm px-6 py-2 rounded-lg transition-colors">CLEAR</button>
<span class="text-sm text-on-surface-variant font-medium ml-2">Complete. 20 videos loaded.</span>
</div>
</section>
<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
<article class="bg-surface border border-outline-variant rounded-xl overflow-hidden flex flex-col hover:shadow-md transition-shadow">
<div class="relative h-56 bg-surface-container-highest"><img alt="The Wolfless Carpenter" class="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuAtokqeUd7A1DVdXCOQp08FJ7g-ROLQxkclU_TfmwIk_I27CgJB9-8xecJcywl9bnGpBcQxgsSFVn4vJQknIC18pPgJzvyPAFpamXXd4-j9db0MsBqNWXkE6lfLXCYB3LaROKkIOU3BirqtLQKRwB30iwDzfvsniQ99rerwzdqFcZ59e1rKCfZAUziVU-JzjqbG9YmHRdqNnHAC-PaJiACI7gpM7NKxp2gJ2V8FxsKe2AU6WBruQdvd2cQ231uWrHS34Ts0NUT-AdeI"/><div class="absolute top-3 right-3 bg-primary/90 text-on-primary w-8 h-8 rounded-full flex items-center justify-center cursor-pointer shadow-sm"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewbox="0 0 24 24"><path d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg></div></div>
<div class="p-5 flex-1 flex flex-col gap-4">
<div class="flex justify-between items-start gap-4"><div><h2 class="text-base font-bold text-on-surface line-clamp-2 leading-tight mb-1">THE WOLFLESS CARPENTER RULES THE WORLD - FULL EPISODE</h2><p class="text-sm text-on-surface-variant"><span class="font-medium text-primary cursor-pointer hover:underline">fun</span> • x31iasq</p></div><button class="flex-shrink-0 flex items-center gap-1.5 px-3 py-1.5 border border-outline-variant rounded-md text-xs font-semibold text-on-surface hover:bg-surface-container transition-colors"><svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewbox="0 0 24 24"><path d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>TITLE</button></div>
<div class="grid grid-cols-3 gap-3">
<div class="bg-surface-container-low rounded-lg p-3 border border-outline-variant text-center"><div class="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">TOTAL</div><div class="text-lg font-bold text-on-surface">46,517</div></div>
<div class="bg-surface-container-low rounded-lg p-3 border border-outline-variant text-center"><div class="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">24H</div><div class="text-lg font-bold text-[#2e7d32]">20,743</div></div>
<div class="bg-surface-container-low rounded-lg p-3 border border-outline-variant text-center"><div class="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">1H</div><div class="text-lg font-bold text-primary">834</div></div>
</div>
<div class="bg-[#fbc02d]/20 border border-[#fbc02d]/50 rounded-lg p-3"><div class="text-xs font-bold text-[#f57f17] uppercase mb-0.5">STATUS: NO GEOBLOCK</div><div class="text-[11px] text-[#f57f17]/80">Signal clear. Content is available globally.</div></div>
<div class="mt-auto space-y-3 pt-2">
<div class="text-xs text-on-surface-variant">Updated: 2026-05-05 11:08:30</div>
<div class="flex items-center justify-between gap-3 bg-surface-container-lowest border border-outline-variant rounded-lg p-2.5"><div class="flex items-center gap-2 overflow-hidden"><span class="text-xs font-semibold text-on-surface-variant whitespace-nowrap">URL:</span><a class="text-xs text-primary hover:underline truncate" href="#">https://www.dailymotion.com/video/xa8487k</a></div><button class="flex-shrink-0 flex items-center gap-1.5 px-2.5 py-1 border border-outline-variant rounded text-[10px] font-bold text-on-surface hover:bg-surface-container transition-colors"><svg class="w-3 h-3" fill="none" stroke="currentColor" viewbox="0 0 24 24"><path d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>URL</button></div>
<div class="flex items-center justify-between gap-3 bg-surface-container-lowest border border-outline-variant rounded-lg p-2.5"><div class="flex items-center gap-2 overflow-hidden"><span class="text-xs font-semibold text-on-surface-variant whitespace-nowrap">Thumb:</span><a class="text-xs text-primary hover:underline truncate" href="#">https://s2.dmcdn.net/v/asdAG1f-Nc9Ll8f8K/x720...</a></div><button class="flex-shrink-0 flex items-center gap-1.5 px-2.5 py-1 border border-outline-variant rounded text-[10px] font-bold text-on-surface hover:bg-surface-container transition-colors"><svg class="w-3 h-3" fill="none" stroke="currentColor" viewbox="0 0 24 24"><path d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>THUMB</button></div>
</div>
</div>
</article>
<article class="bg-surface border border-outline-variant rounded-xl overflow-hidden flex flex-col hover:shadow-md transition-shadow">
<div class="relative h-56 bg-surface-container-highest"><img alt="AMA Supercross" class="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuAiOf0g9einO2t8MycWtxA8LO0_uhNINGnkc7UNfiUYPuW67BRsiFR-iwNdOG0WAYJPvaaoqIUe3AqNkvkOXLV5z1V3VduY08LjPWk1fhox46mckMbOlKRqrXnc5g-qxRjkeRJjWUFy2COasT80e1kwPk1Z3RncwjEh4hDjXwH558TrnMBDQRJlbBxI0-aS26vlH76VkvwE72vsL3QH4yVNWDz3mLA9DEkpyRrAT-XGBF4AnntdMuT51ptwtfdSmvCxXKvAb4HVS9NJ"/><div class="absolute top-3 right-3 bg-primary/90 text-on-primary w-8 h-8 rounded-full flex items-center justify-center cursor-pointer shadow-sm"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewbox="0 0 24 24"><path d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg></div></div>
<div class="p-5 flex-1 flex flex-col gap-4">
<div class="flex justify-between items-start gap-4"><div><h2 class="text-base font-bold text-on-surface line-clamp-2 leading-tight mb-1">AMA SUPERCROSS 2026 SALT LAKE CITY 250SX MAIN EVENT SHOWDOWN FULL RACE</h2><p class="text-sm text-on-surface-variant"><span class="font-medium text-primary cursor-pointer hover:underline">sport</span> • x4xsfae</p></div><button class="flex-shrink-0 flex items-center gap-1.5 px-3 py-1.5 border border-outline-variant rounded-md text-xs font-semibold text-on-surface hover:bg-surface-container transition-colors"><svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewbox="0 0 24 24"><path d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>TITLE</button></div>
<div class="grid grid-cols-3 gap-3">
<div class="bg-surface-container-low rounded-lg p-3 border border-outline-variant text-center"><div class="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">TOTAL</div><div class="text-lg font-bold text-on-surface">11,465</div></div>
<div class="bg-surface-container-low rounded-lg p-3 border border-outline-variant text-center"><div class="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">24H</div><div class="text-lg font-bold text-[#2e7d32]">11,198</div></div>
<div class="bg-surface-container-low rounded-lg p-3 border border-outline-variant text-center"><div class="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">1H</div><div class="text-lg font-bold text-primary">13</div></div>
</div>
<div class="bg-[#fbc02d]/20 border border-[#fbc02d]/50 rounded-lg p-3"><div class="text-xs font-bold text-[#f57f17] uppercase mb-0.5">STATUS: NO GEOBLOCK</div><div class="text-[11px] text-[#f57f17]/80">Signal clear. Content is available globally.</div></div>
<div class="mt-auto space-y-3 pt-2">
<div class="text-xs text-on-surface-variant">Updated: 2026-05-10 09:06:10</div>
<div class="flex items-center justify-between gap-3 bg-surface-container-lowest border border-outline-variant rounded-lg p-2.5"><div class="flex items-center gap-2 overflow-hidden"><span class="text-xs font-semibold text-on-surface-variant whitespace-nowrap">URL:</span><a class="text-xs text-primary hover:underline truncate" href="#">https://www.dailymotion.com/video/xa8xj70</a></div><button class="flex-shrink-0 flex items-center gap-1.5 px-2.5 py-1 border border-outline-variant rounded text-[10px] font-bold text-on-surface hover:bg-surface-container transition-colors"><svg class="w-3 h-3" fill="none" stroke="currentColor" viewbox="0 0 24 24"><path d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>URL</button></div>
<div class="flex items-center justify-between gap-3 bg-surface-container-lowest border border-outline-variant rounded-lg p-2.5"><div class="flex items-center gap-2 overflow-hidden"><span class="text-xs font-semibold text-on-surface-variant whitespace-nowrap">Thumb:</span><a class="text-xs text-primary hover:underline truncate" href="#">https://s2.dmcdn.net/v/axvjS1g00VUlyZqTY/x720...</a></div><button class="flex-shrink-0 flex items-center gap-1.5 px-2.5 py-1 border border-outline-variant rounded text-[10px] font-bold text-on-surface hover:bg-surface-container transition-colors"><svg class="w-3 h-3" fill="none" stroke="currentColor" viewbox="0 0 24 24"><path d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>THUMB</button></div>
</div>
</div>
</article>
</div>
</div>
</main>
</div>
</body></html>
```

---

## 6. Downloader

**Mô tả:** Video Downloader — nhập URL Dailymotion, phân tích và tải xuống. Có khu vực xem trước video (preview area tối), chọn chất lượng (Best / 1080p / 720p...), nút ADD TO QUEUE. Phần bên phải là hàng đợi tải xuống (Download Queue) với trạng thái rỗng và nút START QUEUE DOWNLOAD.

```html
<!-- Downloader - AuraOS -->
<!DOCTYPE html>

<html lang="en"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Video Downloader - Fluidic Professional</title>
<link href="https://fonts.googleapis.com" rel="preconnect"/>
<link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect"/>
<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet"/>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<script data-purpose="tailwind-config">
    tailwind.config = {
      theme: {
        extend: {
          fontFamily: { sans: ['"Hanken Grotesk"', 'sans-serif'] },
          colors: {
            fluidic: { surface: '#faf9fe',surfaceDim: '#dad9df',surfaceBright: '#faf9fe',surfaceLowest: '#ffffff',surfaceLow: '#f4f3f8',primary: '#121212',textMain: '#1e2022',textMuted: '#687076',border: '#e6e8eb' }
          },
          borderRadius: { 'fluidic': '0.5rem' }
        }
      }
    }
  </script>
<style>
    .no-scrollbar::-webkit-scrollbar { display: none; }
    .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
  </style>
</head>
<body class="bg-fluidic-surfaceLow text-fluidic-textMain font-sans h-screen flex overflow-hidden">
<aside class="w-16 bg-fluidic-surfaceLowest border-r border-fluidic-border flex flex-col items-center py-4 gap-6 z-20 flex-shrink-0">
<button class="w-10 h-10 rounded-fluidic bg-fluidic-surfaceLow flex items-center justify-center hover:bg-fluidic-surfaceDim transition-colors"><svg class="w-6 h-6 text-fluidic-primary" fill="none" stroke="currentColor" viewbox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h16" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg></button>
<nav class="flex flex-col gap-4 mt-4 w-full px-3">
<a class="w-10 h-10 rounded-fluidic flex items-center justify-center text-fluidic-textMuted hover:bg-fluidic-surfaceLow hover:text-fluidic-primary transition-colors" href="#" title="Home"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewbox="0 0 24 24"><path d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg></a>
<a class="w-10 h-10 rounded-fluidic flex items-center justify-center text-fluidic-textMuted hover:bg-fluidic-surfaceLow hover:text-fluidic-primary transition-colors" href="#" title="Settings"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewbox="0 0 24 24"><path d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path><path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg></a>
</nav>
</aside>
<div class="flex-1 flex flex-col min-w-0">
<header class="h-16 bg-fluidic-surfaceLowest border-b border-fluidic-border flex items-center justify-between px-6 z-10 flex-shrink-0">
<div class="flex items-center gap-8">
<div class="flex flex-col"><h1 class="text-sm font-bold text-fluidic-primary leading-tight">BATMAN V3</h1><span class="text-[10px] text-fluidic-textMuted uppercase tracking-wider font-semibold">Final Super Mạnh Mẽ</span></div>
<nav class="flex items-center gap-1 bg-fluidic-surfaceLow p-1 rounded-fluidic">
<a class="px-4 py-1.5 text-sm font-medium text-fluidic-textMuted hover:text-fluidic-primary rounded-[6px] transition-colors flex items-center gap-2" href="#"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewbox="0 0 24 24"><path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>Analyze</a>
<a class="px-4 py-1.5 text-sm font-medium bg-fluidic-surfaceLowest text-fluidic-primary shadow-sm rounded-[6px] transition-colors flex items-center gap-2" href="#"><svg class="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewbox="0 0 24 24"><path d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>Download</a>
<a class="px-4 py-1.5 text-sm font-medium text-fluidic-textMuted hover:text-fluidic-primary rounded-[6px] transition-colors flex items-center gap-2" href="#"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewbox="0 0 24 24"><path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>Scanner</a>
<a class="px-4 py-1.5 text-sm font-medium text-fluidic-textMuted hover:text-fluidic-primary rounded-[6px] transition-colors flex items-center gap-2" href="#"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewbox="0 0 24 24"><path d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>Research</a>
</nav>
</div>
<div class="flex items-center gap-4 text-xs font-medium text-fluidic-textMuted"><div class="flex items-center gap-1.5"><div class="w-2 h-2 rounded-full bg-pink-500"></div>IP Info</div><span>v3.0 Unified</span></div>
</header>
<main class="flex-1 flex overflow-hidden p-6 gap-6 bg-fluidic-surface">
<section class="flex-1 flex flex-col bg-fluidic-surfaceLowest rounded-fluidic border border-fluidic-border shadow-sm overflow-y-auto no-scrollbar">
<div class="p-6 flex flex-col gap-6 h-full">
<div><h2 class="text-lg font-bold text-fluidic-primary mb-1">Video Downloader</h2><p class="text-sm text-fluidic-textMuted">Paste a Dailymotion URL to analyze and download in high quality.</p></div>
<div class="flex items-center gap-3"><div class="flex-1 relative"><input aria-label="Video URL" class="w-full bg-fluidic-surfaceLow border border-fluidic-border text-sm rounded-fluidic px-4 py-2.5 focus:outline-none focus:border-fluidic-primary focus:ring-1 focus:ring-fluidic-primary transition-all placeholder-fluidic-textMuted" placeholder="Paste Dailymotion URL here..." type="text"/></div><button class="bg-fluidic-primary text-white text-sm font-semibold px-6 py-2.5 rounded-fluidic hover:bg-black transition-colors shadow-sm whitespace-nowrap">ANALYZE</button></div>
<div class="flex items-center justify-between p-3 bg-fluidic-surfaceLow rounded-fluidic border border-fluidic-border/50"><div class="flex items-center gap-2 overflow-hidden"><svg class="w-5 h-5 text-yellow-500 flex-shrink-0" fill="currentColor" viewbox="0 0 20 20"><path d="M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z"></path></svg><span class="text-sm font-medium text-fluidic-textMain truncate">C:/Users/trinh/Downloads/DAILYMOTION/194</span></div><button class="text-xs font-semibold text-fluidic-textMuted hover:text-fluidic-primary px-3 py-1.5 border border-fluidic-border rounded-[6px] bg-fluidic-surfaceLowest transition-colors flex-shrink-0">Change Folder</button></div>
<div class="w-full aspect-video bg-[#0a0a0a] rounded-fluidic border border-fluidic-border flex items-center justify-center overflow-hidden shadow-inner relative"><span class="text-fluidic-textMuted text-sm font-medium select-none flex flex-col items-center gap-2"><svg class="w-8 h-8 opacity-50" fill="none" stroke="currentColor" viewbox="0 0 24 24"><path d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>Preview Area</span></div>
<div class="mt-auto pt-4 border-t border-fluidic-border">
<h3 class="text-sm font-bold text-fluidic-primary mb-3">No video selected</h3>
<div class="flex items-center gap-4">
<div class="w-64 relative"><select aria-label="Video Quality" class="w-full appearance-none bg-fluidic-surfaceLow border border-fluidic-border text-sm text-fluidic-textMain rounded-fluidic px-4 py-2.5 focus:outline-none focus:border-fluidic-primary focus:ring-1 focus:ring-fluidic-primary pr-10 cursor-pointer"><option>Best Available</option><option>1080p60</option><option>720p60</option><option>480p</option></select><div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-fluidic-textMuted"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewbox="0 0 24 24"><path d="M19 9l-7 7-7-7" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg></div></div>
<button class="ml-auto bg-fluidic-primary text-white text-sm font-semibold px-6 py-2.5 rounded-fluidic hover:bg-black transition-colors shadow-sm">ADD TO QUEUE</button>
</div>
</div>
<div class="pt-4 flex items-center"><span class="text-xs font-semibold text-emerald-600 flex items-center gap-1.5"><span class="w-1.5 h-1.5 rounded-full bg-emerald-500 block"></span>Ready</span></div>
</div>
</section>
<aside class="w-80 flex flex-col bg-fluidic-surfaceLowest rounded-fluidic border border-fluidic-border shadow-sm overflow-hidden flex-shrink-0">
<div class="p-4 border-b border-fluidic-border bg-fluidic-surfaceBright"><h2 class="text-sm font-bold text-fluidic-primary">Download Queue</h2></div>
<div class="flex-1 p-4 overflow-y-auto bg-fluidic-surfaceBright/50 flex flex-col items-center justify-center text-center"><div class="w-12 h-12 rounded-full bg-fluidic-surfaceLow flex items-center justify-center mb-3"><svg class="w-6 h-6 text-fluidic-textMuted" fill="none" stroke="currentColor" viewbox="0 0 24 24"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg></div><p class="text-sm font-medium text-fluidic-textMain">Queue is empty</p><p class="text-xs text-fluidic-textMuted mt-1">Add videos to start downloading</p></div>
<div class="p-4 border-t border-fluidic-border bg-fluidic-surfaceLowest mt-auto"><button class="w-full bg-fluidic-primary text-white text-sm font-semibold px-4 py-3 rounded-fluidic hover:bg-black transition-colors shadow-sm flex items-center justify-center gap-2"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewbox="0 0 24 24"><path d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path><path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>START QUEUE DOWNLOAD</button></div>
</aside>
</main>
</div>
</body></html>
```

---

## 7. Settings

**Mô tả:** Trang cài đặt AuraOS. Bố cục Bento gồm 3 section: **General** (toggle thông báo, tự khởi động, chọn ngôn ngữ), **Appearance** (chọn theme Light/Dark/System, thanh trượt Interface Scale và Glassmorphism Intensity), và **Account** (thông tin hồ sơ, nút Manage Subscription và Sign Out).

```html
<!-- Settings - AuraOS -->
<!DOCTYPE html>

<html lang="en"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>AuraOS Settings</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@500;600&family=Inter:wght@400;600&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
<script id="tailwind-config">
        tailwind.config = {
            darkMode: "class",
            theme: { extend: { "colors": { "surface-dim": "#dad9df","on-error-container": "#93000a","on-surface-variant": "#444748","primary-fixed": "#e5e2e1","on-primary": "#ffffff","secondary": "#5d5e60","secondary-fixed": "#e2e2e4","inverse-on-surface": "#f1f0f5","outline": "#747878","tertiary-fixed-dim": "#c6c6cc","secondary-container": "#dfdfe1","surface-container": "#eeedf3","tertiary": "#000000","surface-container-lowest": "#ffffff","error-container": "#ffdad6","on-secondary-fixed-variant": "#454749","tertiary-container": "#1a1c20","background": "#faf9fe","on-primary-fixed-variant": "#474646","outline-variant": "#c4c7c7","surface-container-high": "#e9e7ed","surface-container-highest": "#e3e2e7","on-surface": "#1a1b1f","on-secondary": "#ffffff","surface-variant": "#e3e2e7","primary-container": "#1c1b1b","on-error": "#ffffff","surface": "#faf9fe","secondary-fixed-dim": "#c6c6c8","tertiary-fixed": "#e2e2e8","inverse-primary": "#c8c6c5","on-tertiary": "#ffffff","on-tertiary-fixed": "#1a1c20","on-secondary-container": "#616365","on-tertiary-container": "#828389","primary": "#000000","inverse-surface": "#2f3034","on-primary-fixed": "#1c1b1b","on-primary-container": "#858383","surface-bright": "#faf9fe","primary-fixed-dim": "#c8c6c5","surface-container-low": "#f4f3f8","on-secondary-fixed": "#1a1c1d","surface-tint": "#5f5e5e","on-background": "#1a1b1f","on-tertiary-fixed-variant": "#45474b","error": "#ba1a1a" }, "borderRadius": {"DEFAULT": "0.25rem","lg": "0.5rem","xl": "0.75rem","full": "9999px"}, "spacing": {"element-gap": "12px","margin-sm": "16px","margin-lg": "64px","container-padding": "40px","unit": "8px","gutter": "24px","margin-md": "32px"}, "fontFamily": {"headline-md": ["Hanken Grotesk"],"body-md": ["Inter"],"body-lg": ["Inter"],"display": ["Hanken Grotesk"],"label-sm": ["Inter"],"headline-lg": ["Hanken Grotesk"]}, "fontSize": {"headline-md": ["24px",{"lineHeight": "1.3","fontWeight": "500"}],"body-md": ["15px",{"lineHeight": "1.5","fontWeight": "400"}],"body-lg": ["18px",{"lineHeight": "1.6","fontWeight": "400"}],"display": ["48px",{"lineHeight": "1.1","letterSpacing": "-0.02em","fontWeight": "600"}],"label-sm": ["12px",{"lineHeight": "1","letterSpacing": "0.05em","fontWeight": "600"}],"headline-lg": ["32px",{"lineHeight": "1.2","letterSpacing": "-0.01em","fontWeight": "600"}]} } }
        }
    </script>
<style>
        .material-symbols-outlined { font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24; }
        .material-symbols-outlined.fill { font-variation-settings: 'FILL' 1; }
        .toggle-checkbox:checked { right: 0; border-color: #000000; }
        .toggle-checkbox:checked + .toggle-label { background-color: #000000; }
        .toggle-checkbox:checked + .toggle-label:after { transform: translateX(100%); border-color: white; }
        .toggle-label { width: 44px; height: 24px; background-color: #c4c7c7; border-radius: 9999px; position: relative; cursor: pointer; transition: background-color 0.3s ease-out; }
        .toggle-label:after { content: ''; position: absolute; top: 2px; left: 2px; width: 20px; height: 20px; background-color: white; border-radius: 50%; transition: transform 0.3s ease-out; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }
        input[type=range] { -webkit-appearance: none; width: 100%; background: transparent; }
        input[type=range]::-webkit-slider-thumb { -webkit-appearance: none; height: 20px; width: 20px; border-radius: 50%; background: #ffffff; cursor: pointer; margin-top: -8px; box-shadow: 0 2px 8px rgba(0,0,0,0.15); border: 1px solid #e3e2e7; }
        input[type=range]::-webkit-slider-runnable-track { width: 100%; height: 4px; cursor: pointer; background: #e3e2e7; border-radius: 9999px; }
        ::-webkit-scrollbar { width: 6px; } ::-webkit-scrollbar-track { background: transparent; } ::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.1); border-radius: 10px; }
    </style>
</head>
<body class="bg-surface text-on-surface font-body-md text-body-md h-screen w-screen overflow-hidden flex relative">
<div class="absolute inset-0 z-0 pointer-events-none overflow-hidden opacity-60"><div class="absolute top-[-10%] left-[-10%] w-[50vw] h-[50vw] rounded-full bg-surface-container-high blur-[120px] mix-blend-multiply"></div><div class="absolute bottom-[-10%] right-[-10%] w-[60vw] h-[60vw] rounded-full bg-secondary-fixed blur-[150px] mix-blend-multiply"></div><div class="absolute top-[20%] right-[20%] w-[40vw] h-[40vw] rounded-full bg-surface-container blur-[100px] mix-blend-multiply opacity-50"></div></div>
<header class="absolute top-0 left-0 w-full flex justify-between items-center px-container-padding h-[32px] z-50 bg-transparent"><div class="flex items-center gap-element-gap"><span class="font-headline-md text-headline-md font-semibold text-primary">AuraOS</span></div><div class="flex items-center gap-unit text-on-surface-variant"><button class="hover:bg-surface-container-highest/50 w-8 h-8 flex items-center justify-center rounded-DEFAULT"><span class="material-symbols-outlined text-[18px]">remove</span></button><button class="hover:bg-surface-container-highest/50 w-8 h-8 flex items-center justify-center rounded-DEFAULT"><span class="material-symbols-outlined text-[16px]">check_box_outline_blank</span></button><button class="hover:bg-error-container hover:text-on-error-container w-8 h-8 flex items-center justify-center rounded-DEFAULT"><span class="material-symbols-outlined text-[18px]">close</span></button></div></header>
<nav class="fixed left-0 top-0 h-full w-64 bg-white/60 backdrop-blur-[40px] flex flex-col py-margin-lg px-margin-sm z-40 border-r border-white/20">
<div class="flex items-center gap-element-gap mb-margin-lg px-unit"><div class="w-10 h-10 rounded-full overflow-hidden bg-surface-container-highest flex-shrink-0"><img alt="User Profile" class="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuA0HH08XxB2w_BKqMALdbHLf9XwQIYNCV7LmfB_RZNQN9nnOWkArqtjmFDIiN5g9ILRBW5HOr7IzSgEKVt7xqC_HLXMV5oPPibQfSigUdKMILSgpnVTaLtT10dzSpXZzznB5DS86x5EJB8Fbr4GX4L34buT1iQKeq5V-YWMWWWQwQ_Zq3kvW8E9oKMfsiSpjRsiF6tvNA-xKlva7hH93fywhGyQ_7tsnUQNTiPQLvp7i8seHWur9ZrP_TgE2Qt6xTM3hY2G16Ne7O_u"/></div><div class="flex flex-col"><span class="font-headline-md text-[16px] leading-tight font-semibold text-primary">Pro Workspace</span><span class="font-label-sm text-label-sm text-on-surface-variant mt-1">Zen Mode Active</span></div></div>
<div class="flex flex-col gap-2">
<a class="flex items-center gap-element-gap px-unit py-2 rounded-lg text-on-surface-variant hover:bg-surface-container-high/40 transition-all duration-300 ease-out group" href="#"><span class="material-symbols-outlined text-[20px] group-hover:text-primary transition-colors">dashboard</span><span class="font-body-md text-body-md font-medium">Dashboard</span></a>
<a class="flex items-center gap-element-gap px-unit py-2 rounded-lg text-on-surface-variant hover:bg-surface-container-high/40 transition-all duration-300 ease-out group" href="#"><span class="material-symbols-outlined text-[20px] group-hover:text-primary transition-colors">download_for_offline</span><span class="font-body-md text-body-md font-medium">Downloads</span></a>
<a class="flex items-center gap-element-gap px-unit py-2 rounded-lg text-on-surface-variant hover:bg-surface-container-high/40 transition-all duration-300 ease-out group" href="#"><span class="material-symbols-outlined text-[20px] group-hover:text-primary transition-colors">library_books</span><span class="font-body-md text-body-md font-medium">Library</span></a>
<a class="flex items-center gap-element-gap px-unit py-2 rounded-lg bg-surface-container-highest/30 relative text-primary font-bold before:content-[''] before:absolute before:left-[-16px] before:w-1 before:h-6 before:bg-primary before:rounded-full active:scale-[0.98] transition-all duration-300 ease-out" href="#"><span class="material-symbols-outlined text-[20px] fill">settings</span><span class="font-body-md text-body-md">Settings</span></a>
</div>
</nav>
<main class="flex-1 ml-64 pt-[64px] pb-gutter px-container-padding h-full overflow-y-auto z-10 relative">
<div class="max-w-4xl mx-auto w-full">
<header class="mb-margin-md flex flex-col gap-unit"><h1 class="font-display text-display text-primary">Settings</h1><p class="font-body-lg text-body-lg text-on-surface-variant">Manage your workspace preferences and account details.</p></header>
<div class="grid grid-cols-1 md:grid-cols-12 gap-gutter pb-margin-lg">
<section class="col-span-1 md:col-span-12 bg-surface-container-lowest/80 backdrop-blur-md rounded-xl p-gutter shadow-[0px_12px_32px_rgba(0,0,0,0.04)] border border-white/50">
<h2 class="font-headline-md text-[20px] text-primary mb-margin-sm flex items-center gap-2"><span class="material-symbols-outlined text-on-surface-variant">tune</span>General</h2>
<div class="flex flex-col gap-0">
<div class="flex items-center justify-between py-4"><div class="flex flex-col"><span class="font-body-md text-body-md font-medium text-on-surface">System Notifications</span><span class="font-body-md text-[13px] text-on-surface-variant">Allow AuraOS to send desktop alerts.</span></div><div class="relative inline-block w-11 mr-2 align-middle select-none"><input checked="" class="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer opacity-0 z-10" id="toggle1" type="checkbox"/><label class="toggle-label block overflow-hidden h-6 rounded-full bg-outline-variant cursor-pointer" for="toggle1"></label></div></div>
<div class="h-[1px] w-full bg-outline-variant/20"></div>
<div class="flex items-center justify-between py-4"><div class="flex flex-col"><span class="font-body-md text-body-md font-medium text-on-surface">Start on Login</span><span class="font-body-md text-[13px] text-on-surface-variant">Launch Pro Workspace automatically.</span></div><div class="relative inline-block w-11 mr-2 align-middle select-none"><input class="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer opacity-0 z-10" id="toggle2" type="checkbox"/><label class="toggle-label block overflow-hidden h-6 rounded-full bg-outline-variant cursor-pointer" for="toggle2"></label></div></div>
<div class="h-[1px] w-full bg-outline-variant/20"></div>
<div class="flex items-center justify-between py-4"><div class="flex flex-col"><span class="font-body-md text-body-md font-medium text-on-surface">Language</span><span class="font-body-md text-[13px] text-on-surface-variant">Display language for the interface.</span></div><select class="bg-surface-container-low border-none rounded-lg px-4 py-2 font-body-md text-body-md text-on-surface focus:ring-1 focus:ring-primary focus:bg-white transition-all shadow-sm cursor-pointer outline-none min-w-[120px]"><option>English (US)</option><option>Spanish</option><option>French</option></select></div>
</div>
</section>
<section class="col-span-1 md:col-span-7 bg-surface-container-lowest/80 backdrop-blur-md rounded-xl p-gutter shadow-[0px_12px_32px_rgba(0,0,0,0.04)] border border-white/50">
<h2 class="font-headline-md text-[20px] text-primary mb-margin-sm flex items-center gap-2"><span class="material-symbols-outlined text-on-surface-variant">palette</span>Appearance</h2>
<div class="flex flex-col gap-6 mt-4">
<div><span class="block font-body-md text-body-md font-medium text-on-surface mb-3">Theme Mode</span><div class="flex gap-4"><button class="flex-1 py-3 px-4 rounded-xl border border-primary bg-surface-container-lowest text-primary flex items-center justify-center gap-2 transition-all"><span class="material-symbols-outlined text-[18px]">light_mode</span>Light</button><button class="flex-1 py-3 px-4 rounded-xl border border-transparent bg-surface-container text-on-surface-variant hover:bg-surface-variant transition-all flex items-center justify-center gap-2"><span class="material-symbols-outlined text-[18px]">dark_mode</span>Dark</button><button class="flex-1 py-3 px-4 rounded-xl border border-transparent bg-surface-container text-on-surface-variant hover:bg-surface-variant transition-all flex items-center justify-center gap-2"><span class="material-symbols-outlined text-[18px]">desktop_windows</span>System</button></div></div>
<div class="mt-2"><div class="flex justify-between mb-2"><span class="font-body-md text-body-md font-medium text-on-surface">Interface Scale</span><span class="font-body-md text-[13px] text-on-surface-variant">100%</span></div><input class="w-full" max="150" min="80" type="range" value="100"/></div>
<div class="mt-2"><div class="flex justify-between mb-2"><span class="font-body-md text-body-md font-medium text-on-surface">Glassmorphism Intensity</span><span class="font-body-md text-[13px] text-on-surface-variant">Medium</span></div><input class="w-full" max="100" min="0" type="range" value="60"/></div>
</div>
</section>
<section class="col-span-1 md:col-span-5 bg-surface-container-lowest/80 backdrop-blur-md rounded-xl p-gutter shadow-[0px_12px_32px_rgba(0,0,0,0.04)] border border-white/50 flex flex-col justify-between">
<div><h2 class="font-headline-md text-[20px] text-primary mb-margin-sm flex items-center gap-2"><span class="material-symbols-outlined text-on-surface-variant">account_circle</span>Account</h2>
<div class="flex items-center gap-4 mt-6 p-4 rounded-xl bg-surface-container-low border border-outline-variant/20"><div class="w-14 h-14 rounded-full overflow-hidden flex-shrink-0 shadow-sm"><img alt="User Profile" class="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuAgXrouFrJ3o9ySfwHY9wW7THGI_FUytSjLOWG3Ai2xu_ciaAtjvmEBe5CEqeJNvTXA77igJKk61MkXT_ZhagkJzHBMkgba89ARlUsOMsC5Po5fVCXdRKg4fhs3M43H6uOWreGV0EUE5Z5CH5xARPnIJ1RlFlR326xp8qv9wHgtufEKnkHJF6Kmvv-YWWM-Sn823rcTEBXdz0RY_AmrnCdi0VWIlr0yzUQzWyB8Ub-KlQ37yQia885aM8YPxrdbb7tJZRPKjewqvwAZ"/></div><div class="flex flex-col"><span class="font-headline-md text-[16px] leading-tight font-semibold text-primary">Alex Mercer</span><span class="font-body-md text-[14px] text-on-surface-variant mt-1">alex.mercer@auraos.design</span><span class="inline-flex items-center px-2 py-0.5 mt-2 rounded-full bg-secondary-container/50 text-on-secondary-container font-label-sm text-[10px] w-max">PRO PLAN</span></div></div></div>
<div class="flex flex-col gap-3 mt-8"><button class="w-full py-3 px-4 bg-primary text-on-primary rounded-xl font-body-md text-body-md font-medium hover:opacity-90 transition-opacity flex items-center justify-center gap-2 shadow-sm">Manage Subscription</button><button class="w-full py-3 px-4 bg-surface-variant text-on-surface rounded-xl font-body-md text-body-md font-medium hover:bg-outline-variant/30 transition-colors flex items-center justify-center gap-2">Sign Out</button></div>
</section>
</div>
</div>
</main>
</body></html>
```

---

## 8. Dashboard v2

**Mô tả:** Phiên bản nâng cấp của Dashboard với Glassmorphism mạnh hơn — `backdrop-blur-xl`, bo góc lớn hơn (`rounded-card: 32px`), khoảng cách rộng hơn, và hiệu ứng kính trong suốt `bg-surface-container-lowest/80` cho mọi card. Focus Session card dùng `bg-primary/90 backdrop-blur-[40px]`.

> *Code tương tự Dashboard v1, chỉ khác các giá trị spacing, borderRadius và backdrop-blur. Tham khảo phần cuối tài liệu gốc với tiêu đề "Dashboard - AuraOS" thứ hai có `"card": "32px"` và `"container-padding": "48px"`.*

---

## 9. Downloads v2

**Mô tả:** Phiên bản Downloads với bo góc nâng cấp (`rounded-[32px]`) và thanh tiến trình mỏng hơn (`h-1.5`). Các item đã hoàn thành dùng `rounded-[16px]` khi hover. Storage card cũng dùng `rounded-[32px]`.

> *Code tương tự Downloads v1, với các giá trị `rounded` lớn hơn. Tham khảo phần "Downloads - AuraOS" thứ hai trong tài liệu gốc.*

---

## 10. Library v2

**Mô tả:** Phiên bản Library nâng cấp — card dùng `rounded-3xl p-2` với thumbnail bên trong dùng `rounded-2xl`. Bộ lọc dùng `bg-white/40 backdrop-blur-xl border border-white/60 rounded-2xl`. Hover effect card có `transform: translateY(-2px)`.

> *Code tương tự Library v1 với bo góc và glassmorphism nâng cao. Tham khảo "Library - AuraOS" thứ hai trong tài liệu gốc.*

---

## 11. Settings v2

**Mô tả:** Phiên bản Settings nâng cấp — General section dùng `rounded-[32px]` cho card chính và `rounded-[24px]` cho từng hàng setting. Appearance section tách thành các khối riêng với `rounded-[24px]`. Account section dùng nút hình pill `rounded-full`. Language dropdown dùng `rounded-full px-6`.

> *Code tương tự Settings v1 với bo góc lớn hơn và padding rộng hơn. Tham khảo "Settings - AuraOS" thứ hai (file cuối) trong tài liệu gốc.*

---

## 12. Analyze — Real-time Intelligence

**Mô tả:** Trang phân tích video Dailymotion theo thời gian thực. Dùng design token màu `primary: #505bc9` (tím xanh) thay vì đen. Có ô nhập URL với icon tìm kiếm, 3 nút hành động (SCAN VIDEO / IMPORT BATCH / CLEAR ALL), và khu vực empty state với icon analytics và đường viền nét đứt.

```html
<!-- Analyze - AuraOS -->
<!DOCTYPE html>

<html class="h-full" lang="en"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Real-time Intelligence - AuraOS</title>
<link href="https://fonts.googleapis.com" rel="preconnect"/>
<link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect"/>
<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet"/>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet"/>
<script data-purpose="tailwind-config">
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          fontFamily: { sans: ['"Hanken Grotesk"', 'sans-serif'] },
          colors: {
            surface: '#faf9fe','surface-dim': '#dad9df','surface-bright': '#faf9fe','surface-container-lowest': '#ffffff','surface-container-low': '#f4f3f8','surface-container': '#eeeef3','surface-container-high': '#e8e8ed','surface-container-highest': '#e2e2e7',
            'on-surface': '#1b1b1f','on-surface-variant': '#46464f',outline: '#777680','outline-variant': '#c7c5d0',
            primary: '#505bc9','on-primary': '#ffffff','primary-container': '#e0e0ff','on-primary-container': '#050a41',
            secondary: '#5c5d72','on-secondary': '#ffffff','secondary-container': '#e1e0f9','on-secondary-container': '#191a2c',
            tertiary: '#78536b','on-tertiary': '#ffffff','tertiary-container': '#ffd7f0','on-tertiary-container': '#2e1126',
            error: '#ba1a1a','on-error': '#ffffff','error-container': '#ffdad6','on-error-container': '#410002',
            background: '#faf9fe','on-background': '#1b1b1f'
          },
          borderRadius: { 'none': '0','sm': '4px',DEFAULT: '8px','md': '8px','lg': '12px','xl': '16px','2xl': '24px','3xl': '32px','full': '9999px' },
          boxShadow: { 'sm': '0 1px 2px 0 rgb(0 0 0 / 0.05)',DEFAULT: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)','md': '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)','lg': '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)','fluidic': '0 4px 20px -2px rgba(27, 27, 31, 0.05)' }
        }
      }
    }
  </script>
<style>
    .fluidic-hover { transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1); }
    .fluidic-hover:hover { transform: translateY(-2px); box-shadow: 0 4px 20px -2px rgba(27, 27, 31, 0.05); background-color: #f4f3f8; }
    .fluidic-button:hover { opacity: 0.9; transform: scale(1.02); }
    .fluidic-button:active { transform: scale(0.98); }
    .fluidic-input { transition: all 0.3s ease; background-color: #f4f3f8; border-color: #e8e8ed; }
    .fluidic-input:focus { background-color: #faf9fe; border-color: #505bc9; box-shadow: 0 0 0 4px #e0e0ff; }
    .glass-nav { background-color: rgba(255, 255, 255, 0.6); backdrop-filter: blur(40px); -webkit-backdrop-filter: blur(40px); border-right: 1px solid #e8e8ed; }
  </style>
</head>
<body class="bg-background text-on-background font-sans h-full overflow-hidden flex antialiased">
<nav class="glass-nav w-64 h-full flex-shrink-0 flex flex-col py-6 px-4 z-40 relative">
<div class="mb-8 px-4 flex items-center gap-3"><span class="material-symbols-outlined text-primary text-3xl">view_in_ar</span><h1 class="text-xl font-bold text-primary tracking-tight">AuraOS</h1></div>
<div class="mb-8 px-4 flex items-center gap-4 fluidic-hover rounded-xl p-3 cursor-pointer"><div class="w-10 h-10 rounded-full bg-primary-container text-on-primary-container flex items-center justify-center overflow-hidden flex-shrink-0"><img alt="User Profile" class="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuDtnVOIDNvoxlQwD3N4UvXcm4WrZaIBVv9AFQvy0U3ssRHI5hLAXKDE1ISA-NhWLFUMrrSaistheMRUP6K-Q_IzxTx_zERuZ5rKSny43zI2UOsBSQxO3ZZAmCfrlnRXQKxnZu8xHIk7-6hctIzj3Cwghz4pnsC2ZEoehs7bksqp4ZZ31PoJ6GzMa8ayQc2LXd2kQeb5w9SpvAnd6C-I3Qj0qo-uxvmyEab6ivnA6jCpt8EeKCUUm4xfvztf1DUzMlQxIS6v8ndbRjku"/></div><div class="flex flex-col overflow-hidden"><span class="text-sm font-semibold truncate text-on-surface">Pro Workspace</span><span class="text-xs text-on-surface-variant truncate">Zen Mode Active</span></div></div>
<div class="flex-1 flex flex-col gap-1 overflow-y-auto">
<a class="flex items-center gap-3 px-4 py-3 rounded-lg bg-surface-container text-primary font-semibold relative before:content-[''] before:absolute before:left-0 before:w-1 before:h-6 before:bg-primary before:rounded-full fluidic-hover" href="#"><span class="material-symbols-outlined text-[20px]">dashboard</span><span class="text-sm">Dashboard</span></a>
<a class="flex items-center gap-3 px-4 py-3 rounded-lg text-on-surface-variant hover:text-on-surface fluidic-hover" href="#"><span class="material-symbols-outlined text-[20px]">download_for_offline</span><span class="text-sm">Downloads</span></a>
<a class="flex items-center gap-3 px-4 py-3 rounded-lg text-on-surface-variant hover:text-on-surface fluidic-hover" href="#"><span class="material-symbols-outlined text-[20px]">library_books</span><span class="text-sm">Library</span></a>
<a class="flex items-center gap-3 px-4 py-3 rounded-lg text-on-surface-variant hover:text-on-surface fluidic-hover" href="#"><span class="material-symbols-outlined text-[20px]">settings</span><span class="text-sm">Settings</span></a>
</div>
<div class="mt-auto px-4 pt-4 border-t border-surface-container-high"><button class="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high/40 transition-colors duration-300"><span class="material-symbols-outlined text-[20px]">logout</span><span class="text-sm font-medium">Log out</span></button></div>
</nav>
<div class="flex-1 flex flex-col h-full overflow-hidden relative bg-surface">
<header class="h-12 w-full bg-surface/80 backdrop-blur-md flex items-center justify-between px-6 z-30 border-b border-surface-container-high sticky top-0">
<div class="flex items-center text-sm font-medium text-on-surface-variant">BATMAN V3 <span class="mx-2 text-outline-variant">/</span> Analyze</div>
<div class="flex items-center gap-2 text-on-surface-variant"><button class="p-1.5 rounded-md hover:bg-surface-container-highest/50 transition-colors duration-300"><span class="material-symbols-outlined text-[20px]">remove</span></button><button class="p-1.5 rounded-md hover:bg-surface-container-highest/50 transition-colors duration-300"><span class="material-symbols-outlined text-[20px]">check_box_outline_blank</span></button><button class="p-1.5 rounded-md hover:bg-surface-container-highest/50 hover:text-error transition-colors duration-300"><span class="material-symbols-outlined text-[20px]">close</span></button></div>
</header>
<main class="flex-1 overflow-y-auto p-8 lg:p-12">
<div class="max-w-4xl mx-auto space-y-8">
<div><h2 class="text-2xl font-bold text-on-surface mb-2">Real-time Intelligence</h2><p class="text-on-surface-variant text-base">Scan Dailymotion videos. Analyze views, geoblock status, and metadata.</p></div>
<div class="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
<div class="relative flex-1 w-full max-w-lg"><div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none"><span class="material-symbols-outlined text-outline-variant">search</span></div><input class="fluidic-input block w-full pl-10 pr-3 py-3 border border-surface-container-high rounded-xl text-on-surface placeholder-outline-variant focus:outline-none sm:text-sm" placeholder="Enter URL or Video ID..." type="text"/></div>
<div class="flex flex-wrap gap-3">
<button class="fluidic-button bg-primary text-on-primary font-medium text-sm px-6 py-3 rounded-xl shadow-sm hover:shadow-md transition-all flex items-center gap-2"><span class="material-symbols-outlined text-[18px]">travel_explore</span>SCAN VIDEO</button>
<button class="fluidic-button bg-surface-container-high text-on-surface font-medium text-sm px-6 py-3 rounded-xl border border-surface-container-highest hover:bg-surface-container-highest transition-all flex items-center gap-2"><span class="material-symbols-outlined text-[18px]">upload_file</span>IMPORT BATCH</button>
<button class="fluidic-button bg-error-container text-on-error-container font-medium text-sm px-6 py-3 rounded-xl hover:bg-[#ffcdc9] transition-all flex items-center gap-2"><span class="material-symbols-outlined text-[18px]">delete_sweep</span>CLEAR ALL</button>
</div>
</div>
<div class="mt-12 rounded-2xl border-2 border-dashed border-surface-container-high p-12 text-center flex flex-col items-center justify-center text-on-surface-variant bg-surface-container-low/50"><span class="material-symbols-outlined text-4xl mb-4 text-outline-variant">analytics</span><h3 class="text-lg font-medium text-on-surface mb-1">Ready to Analyze</h3><p class="text-sm">Enter a video URL or ID above to begin scanning.</p></div>
</div>
</main>
</div>
</body></html>
```

---

*Tổng hợp: 12 trang giao diện AuraOS / BATMAN V3 — Fluidic Professional Design System*
