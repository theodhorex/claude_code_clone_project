# Claude Code Clone Project

Prototype sederhana untuk memulai project cloningan **Claude Code** tanpa dependency tambahan.

## Fitur awal

- Antarmuka chat sederhana bergaya coding assistant
- Panel context file agar terasa seperti tool untuk bantu coding
- Slash command dasar:
  - `/help`
  - `/add <path>`
  - `/plan`
  - `/run`
  - `/clear`
- Semua file bisa langsung dibuka di browser

## Cara menjalankan

Opsi paling mudah:

1. Buka file `/home/runner/work/claude_code_clone_project/claude_code_clone_project/index.html` di browser

Atau jalankan web server lokal:

```bash
cd /home/runner/work/claude_code_clone_project/claude_code_clone_project
python3 -m http.server 8000
```

Lalu buka `http://localhost:8000`.

## Tujuan

Repo ini sekarang menjadi pondasi awal untuk mengembangkan cloningan Claude Code: ada UI awal, alur command, dan area context project yang nanti bisa dihubungkan ke backend AI sungguhan.
