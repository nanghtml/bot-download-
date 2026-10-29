# Telegram Downloader Bot

Bot ទាញយកវីដេអូ/សំឡេងពី social media ដោយប្រើ `yt-dlp`។

## ការដំឡើង

1. បង្កើត bot ជាមួយ **@BotFather** លើ Telegram រួចចម្លង token
2. ដំឡើង **ffmpeg** (ចាំបាច់សម្រាប់ MP3 និងបញ្ចូលវីដេអូ+សំឡេង)
   - Ubuntu/Debian: `sudo apt install ffmpeg`
   - macOS: `brew install ffmpeg`
   - Windows: https://ffmpeg.org/download.html
3. ដំឡើង dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. កំណត់ token ហើយរត់៖
   ```bash
   # Linux / macOS
   export BOT_TOKEN="123456:ABC..."
   python bot.py

   # Windows (PowerShell)
   $env:BOT_TOKEN="123456:ABC..."
   python bot.py
   ```

## ការប្រើប្រាស់

ផ្ញើ link ទៅ bot → ជ្រើសរើស 720p / គុណភាពល្អបំផុត / MP3។

## ជម្រើសបន្ថែម

- `MAX_MB` : ទំហំអតិបរមា (លំនាំដើម 50)។ បើរត់ Local Bot API Server អាចដាក់ដល់ 2000។
- `cookies.txt` : ដាក់ក្នុងថតតែមួយជាមួយ `bot.py` សម្រាប់ខ្លឹមសារ Instagram/Facebook ដែលត្រូវការចូលគណនី។
- Update yt-dlp ជាប្រចាំ (`pip install -U yt-dlp`) ព្រោះគេហទំព័រផ្លាស់ប្តូរញឹកញាប់។

## Deploy

ប្រើ VPS, Railway ឬ Render ហើយកំណត់ `BOT_TOKEN` ជា environment variable។
ត្រូវប្រាកដថា server មាន ffmpeg។

## ចំណាំច្បាប់

សូមទាញយកតែខ្លឹមសារដែលអ្នកមានសិទ្ធិ ឬអនុញ្ញាតឱ្យទាញយក។
