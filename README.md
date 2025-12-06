<h1 align="center">🎉 Selamat Datang di Repository Taka API 🎉</h1>

<div align="center">
  Etto... gimana ya jelasinnya... Yah sebisaku aja deh 😅<br>
  Silakan ikuti langkah-langkah di bawah ini untuk menjalankan project ini.
</div>

<hr>

<h2>🚀 1. Clone / Download Repository</h2>

<pre><code>git clone https://github.com/username/repo-ini.git
cd taka-api
</code></pre>

<hr>

<h2>🐍 2. Install Python 3</h2>

<p>Untuk Ubuntu/Debian:</p>

<pre><code>sudo apt update
sudo apt install -y python3 python3-pip
</code></pre>

<hr>

<h2>🌱 3. Membuat Virtual Environment (venv)</h2>

<pre><code>python3 -m venv env
</code></pre>

<p>Aktifkan venv:</p>

<pre><code>source env/bin/activate
</code></pre>

<p>Jika berhasil, tampilannya akan seperti ini:</p>

<pre><code>(env) user@bell:~$
</code></pre>

<hr>

<h2>📦 4. Install Dependencies</h2>

<pre><code>pip install -r requirements.txt
</code></pre>

<hr>

<h2>⚙️ 5. Install Node.js & PM2 (Recommended untuk Production)</h2>

<pre><code>curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install -g pm2
</code></pre>

<hr>

<h2>▶️ 6. Menjalankan API Menggunakan PM2 (Production Ready)</h2>

<p><strong>Perbaikan:</strong> Tidak menggunakan <code>--reload</code> karena itu hanya untuk development dan bisa membuat server tidak stabil.</p>

<p>Jalankan API pada port <strong>3030</strong>:</p>

<pre><code>pm2 start "uvicorn main:app --host 0.0.0.0 --port 3030" --name taka-api
</code></pre>

<p>Perintah penting lainnya:</p>

<pre><code># Melihat log
pm2 logs taka-api

# Restart app
pm2 restart taka-api

# Stop app
pm2 stop taka-api
</code></pre>

<hr>

<h2 align="center">✅ Selesai!</h2>

<div align="center">
  Udah deh~ Semoga paham ya!<br>
  Kalau ada salah atau kurang, <i>cmiiw</i> ya 🙏✨
</div>

<hr>